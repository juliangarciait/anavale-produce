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
        _incrementLines: function (params) {
            var line = this._findCandidateLineToIncrement(params);
            var isNewLine = false;
            console.log("esta funcion es mejor?");
            if (line) {
                // Update the line with the processed quantity.
                if (params.product.tracking === 'none' ||
                    params.lot_id ||
                    params.lot_name ||
                    !this.requireLotNumber
                    ) {
                    if (this.actionParams.model === 'stock.picking') {
                        line.qty_done += params.product.qty || 1;
                        if (params.package_id) {
                            line.package_id = params.package_id;
                        }
                        if (params.result_package_id) {
                            line.result_package_id = params.result_package_id;
                        }
                    } else if (this.actionParams.model === 'stock.inventory') {
                        line.product_qty += params.product.qty || 1;
                    }
                }
            } else {
                isNewLine = true;
                // Create a line with the processed quantity.
                if (params.product.tracking === 'none' ||
                    params.lot_id ||
                    params.lot_name ||
                    !this.requireLotNumber
                    ) {
                    line = this._makeNewLine(params.product, params.barcode, params.product.qty || 1, params.package_id, params.result_package_id, params.owner_id);
                } else {
                    line = this._makeNewLine(params.product, params.barcode, 0, params.package_id, params.result_package_id);
                }
                
                this._getLines(this.currentState).push(line);
                this.pages[this.currentPageIndex].lines.push(line);
            }
            if (this.actionParams.model === 'stock.picking') {
                if (params.lot_id) {
                    line.lot_id = [params.lot_id];
                }
                if (params.lot_name) {
                    line.lot_name = params.lot_name;
                }
            } else if (this.actionParams.model === 'stock.inventory') {
                if (params.lot_id) {
                    line.prod_lot_id = [params.lot_id, params.lot_name];
                }
            }
            return {
                'id': line.id,
                'virtualId': line.virtual_id,
                'lineDescription': line,
                'isNewLine': isNewLine,
            };
        },
        _step_product: async function (barcode, linesActions) {
            var self = this;
            this.currentStep = 'product';
            var errorMessage;

            
    
            var product = await this._isProduct(barcode)
            if (product) {
                if (product.tracking !== 'none' && self.requireLotNumber) {
                    this.currentStep = 'lot';
                }
                var res = this._incrementLines({'product': product, 'barcode': barcode});
                if (res.isNewLine) {
                    console.log("nueva linea");
                    console.log(this.currentState);
                    if (this.actionParams.model === 'stock.inventory') {
                        // FIXME sle: add owner_id, prod_lot_id, owner_id, product_uom_id
                        return this._rpc({
                            model: 'product.product',
                            method: 'get_theoretical_quantity',
                            args: [
                                res.lineDescription.product_id.id,
                                res.lineDescription.location_id.id,
                            ],
                        }).then(function (theoretical_qty) {
                            res.lineDescription.theoretical_qty = theoretical_qty;
                            linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                            self.scannedLines.push(res.id || res.virtualId);
                            return Promise.resolve({linesActions: linesActions});
                        });
                    } else {
                        linesActions.push([this.linesWidget.addProduct, [res.lineDescription, this.actionParams.model]]);
                    }
                } else {
                    console.log("no nueva linea");
                    console.log(this.currentState);
                    if (product.tracking === 'none' || !self.requireLotNumber) {
                        linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, product.qty || 1, this.actionParams.model]]);
                    } else {
                        linesActions.push([this.linesWidget.incrementProduct, [res.id || res.virtualId, 0, this.actionParams.model]]);
                    }
                }
                this.scannedLines.push(res.id || res.virtualId);
                return Promise.resolve({linesActions: linesActions});
            } else {
                var success = function (res) {
                    return Promise.resolve({linesActions: res.linesActions});
                };
                var fail = function (specializedErrorMessage) {
                    self.currentStep = 'product';
                    
                    if (specializedErrorMessage){
                        return Promise.reject(specializedErrorMessage);
                    }
                    if (! self.scannedLines.length) {
                        if (self.groups.group_tracking_lot) {
                            errorMessage = _t("You are expected to scan one or more products or a package available at the picking's location");
                        } else {
                            errorMessage = _t('You are expected to scan one or more products.');
                        }
                        return Promise.reject(errorMessage);
                    }
    
                    var destinationLocation = self.locationsByBarcode[barcode];
                    if (destinationLocation) {
                        return self._step_destination(barcode, linesActions);
                    } else {
                        errorMessage = _t('You are expected to scan more products or a destination location.');
                        return Promise.reject(errorMessage);
                    }
                };
                return self._step_lot(barcode, linesActions).then(success, function () {
                    return self._step_package(barcode, linesActions).then(success, fail);
                });
            }
        },
    });
});