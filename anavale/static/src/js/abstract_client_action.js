odoo.define('anavale.ClientAction', function (require) {
    'use strict';
    var ClientActionBarcode = require('stock_barcode.ClientAction');
    var core = require('web.core');
    var _t = core._t;
    console.log("=======");
    ClientActionBarcode.include({
        events: _.defaults({
        }, ClientActionBarcode.prototype.events),
        init: function () {
            return this._super.apply(this, arguments);
        },
        /**
     * Handle what needs to be done when a lot is scanned.
     *
     * @param {string} barcode scanned barcode
     * @param {Object} linesActions
     * @returns {Promise}
     */
    _step_lot: async function (barcode, linesActions) {
        if (! this.groups.group_production_lot || !this.requireLotNumber)  {
            return Promise.reject();
        }
        this.currentStep = 'lot';
        var errorMessage;
        var self = this;

        // Bypass this step if needed.
        var product = await this._isProduct(barcode)
        if (product) {
            return this._step_product(barcode, linesActions);
        } else if (this.locationsByBarcode[barcode]) {
            return this._step_destination(barcode, linesActions);
        }

        var getProductFromLastScannedLine = function () {
            if (self.scannedLines.length) {
                var idOrVirtualId = self.scannedLines[self.scannedLines.length - 1];
                var line = _.find(self._getLines(self.currentState), function (line) {
                    return line.virtual_id === idOrVirtualId || line.id === idOrVirtualId;
                });
                if (line) {
                    var product = self.productsByBarcode[line.product_barcode || line.product_id.barcode];
                    // Product was added by lot or package
                    if (!product) {
                        return false;
                    }
                    product.barcode = line.product_barcode || line.product_id.barcode;
                    return product;
                }
            }
            return false;
        };

        var getProductFromCurrentPage = function () {
            return _.map(self.pages[self.currentPageIndex].lines, function (line) {
                return line.product_id.id;
            });
        };

        var getProductFromOperation = function () {
            return _.map(self._getLines(self.currentState), function (line) {
                return line.product_id.id;
            });
        };

        var readProductQuant = function (product_id, lots) {
            var advanceSettings = self.groups.group_tracking_lot || self.groups.group_tracking_owner;
            var product_barcode = _.findKey(self.productsByBarcode, function (product) {
                return product.id === product_id;
            });
            var product = false;
            var prom = Promise.resolve();

            if (product_barcode) {
                product = self.productsByBarcode[product_barcode];
                product.barcode = product_barcode;
            }

            if (!product || advanceSettings) {
                var lot_ids = _.map(lots, function (lot) {
                    return lot.id;
                });
                prom = self._rpc({
                    model: 'product.product',
                    method: 'read_product_and_package',
                    args: [product_id],
                    kwargs: {
                        lot_ids: advanceSettings ? lot_ids : false,
                        fetch_product: !(product),
                    },
                });
            }

            return prom.then(function (res) {
                product = product || res.product;
                var lot = _.find(lots, function (lot) {
                    return lot.product_id[0] === product.id;
                });
                var data = {
                    lot_id: lot.id,
                    lot_name: lot.display_name,
                    product: product
                };
                if (res && res.quant) {
                    data.package_id = res.quant.package_id;
                    data.owner_id = res.quant.owner_id;
                }
                return Promise.resolve(data);
            });
        };

        var getLotInfo = function (lots) {
            var products_in_lots = _.map(lots, function (lot) {
                return lot.product_id[0];
            });
            var products = getProductFromLastScannedLine();
            var product_id = _.intersection(products, products_in_lots);
            if (! product_id.length) {
                products = getProductFromCurrentPage();
                product_id = _.intersection(products, products_in_lots);
            }
            if (! product_id.length) {
                products = getProductFromOperation();
                product_id = _.intersection(products, products_in_lots);
            }
            if (! product_id.length) {
                product_id = [lots[0].product_id[0]];
            }
            return readProductQuant(product_id[0], lots);
        };

        var searchRead = function (barcode) {
            // Check before if it exists reservation with the lot.
            var lines_with_lot = _.filter(self.currentState.move_line_ids, function (line) {
                return (line.lot_id && line.lot_id[1] === barcode) || line.lot_name === barcode;
            });
            var line_with_lot;
            if (lines_with_lot.length > 0) {
                var line_index = 0;
                // Get last scanned product if several products have the same lot name
                var last_product = lines_with_lot.length > 1 && getProductFromLastScannedLine();
                if (last_product) {
                    var last_product_index = _.findIndex(lines_with_lot, function (line) {
                        return line.product_id && line.product_id.id === last_product.id;
                    });
                    if (last_product_index > -1) {
                        line_index = last_product_index;
                    }
                }
                line_with_lot = lines_with_lot[line_index];
            }
            var def;
            if (line_with_lot) {
                def = Promise.resolve([{
                    name: barcode,
                    display_name: barcode,
                    id: line_with_lot.lot_id[0],
                    product_id: [line_with_lot.product_id.id, line_with_lot.display_name],
                }]);
            } else {
                def = self._rpc({
                    model: 'stock.production.lot',
                    method: 'search_read',
                    domain: [['name', '=', barcode]],
                });
            }
            return def.then(function (res) {
                if (! res.length) {
                    errorMessage = _t('Los códigos de barras no coinciden con la orden de entrega, por favor consultar al administrador.');
                    return Promise.reject(errorMessage);
                }
                else{
                    var lot_id = res[0].id
                    if (! self.currentState.lot_ids.some(element => element === lot_id)){
                        errorMessage = _t('Los códigos de barras no coinciden con la orden de entrega, por favor consultar al administrador.');
                        return Promise.reject(errorMessage);
                    }
                }
                return getLotInfo(res);
            });
        };

        var create = function (barcode, product) {
            return self._rpc({
                model: 'stock.production.lot',
                method: 'create',
                args: [{
                    'name': barcode,
                    'product_id': product.id,
                    'company_id': self.currentState.company_id[0],
                }],
            });
        };

        var def;
        if (this.currentState.use_create_lots &&
            ! this.currentState.use_existing_lots) {
            // Do not create lot if product is not set. It could happens by a
            // direct lot scan from product or source location step.
            var product = getProductFromLastScannedLine();
            if (! product  || product.tracking === "none") {
                return Promise.reject();
            }
            def = Promise.resolve({lot_name: barcode, product: product});
        } else if (! this.currentState.use_create_lots &&
                    this.currentState.use_existing_lots) {
            def = searchRead(barcode);
        } else {
            def = searchRead(barcode).then(function (res) {
                return Promise.resolve(res);
            }, function (errorMessage) {
                var product = getProductFromLastScannedLine();
                if (product && product.tracking !== "none") {
                    return create(barcode, product).then(function (lot_id) {
                        return Promise.resolve({lot_id: lot_id, lot_name: barcode, product: product});
                    });
                }
                return Promise.reject(errorMessage);
            });
        }
        return def.then(function (lot_info) {
            var product = lot_info.product;
            if (product.tracking === 'serial' && self._lot_name_used(product, barcode)){
                errorMessage = _t('The scanned serial number is already used.');
                return Promise.reject(errorMessage);
            }
            var res = self._incrementLines({
                'product': product,
                'barcode': lot_info.product.barcode,
                'lot_id': lot_info.lot_id,
                'lot_name': lot_info.lot_name,
                'owner_id': lot_info.owner_id,
                'package_id': lot_info.package_id,
            });
            if (res.isNewLine) {
                function handle_line(){
                    self.scannedLines.push(res.lineDescription.virtual_id);
                    linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                }

                if (self.actionParams.model === 'stock.inventory') {
                    // TODO deduplicate: this code is almost the same as in _step_product
                    return self._rpc({
                        model: 'product.product',
                        method: 'get_theoretical_quantity',
                        args: [
                            res.lineDescription.product_id.id,
                            res.lineDescription.location_id.id,
                            res.lineDescription.prod_lot_id[0],
                        ],
                    }).then(function (theoretical_qty) {
                        res.lineDescription.theoretical_qty = theoretical_qty;
                        handle_line();
                        return Promise.resolve({linesActions: linesActions});
                    });
                }
                handle_line();

            } else {
                if (self.scannedLines.indexOf(res.lineDescription.id) === -1) {
                    self.scannedLines.push(res.lineDescription.id || res.lineDescription.virtual_id);
                }
                linesActions.push([self.linesWidget.incrementProduct, [res.id || res.virtualId, 1, self.actionParams.model]]);
                linesActions.push([self.linesWidget.setLotName, [res.id || res.virtualId, barcode]]);
            }
            return Promise.resolve({linesActions: linesActions});
        });
    },
    });
});