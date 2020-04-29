odoo.define('percent_field.field_utils_format', function (require) {
    "use strict";
    var ks_field_utils = require('web.field_utils');
    var ks_basic_controller = require('web.BasicController');
    var _t = require('web.core')._t;
    var ks_error_val;
    function formatPercent(value) {
    if(value){
        return value + "%";
        }
     else{
        return 0.0 + "%";
     }
    }

    /**
     * Parse a String containing Percent in language formating
     *
     * @param {string} value
     *                The string to be parsed with the setting of thousands and
     *                decimal separator
     * @returns {float with percent symbol}
     * @throws {Error} if no float is found respecting the language configuration
     */
    function parsePercent(value) {
        var ks_lastChar = value[value.length -1];
        var ks_parsed = value.slice(0, -1);
        if(value){
        if(isNaN(ks_parsed)){
                throw new Error(_.str.sprintf(core._t("'%s' is not a correct float"), value));
           }
        else{
            if(ks_lastChar != "%"){
                if(isNaN(ks_lastChar)){
                    throw new Error(_.str.sprintf(core._t("'%s' is not a correct float"), value));
                }
                else{
                    if( value > 100 ||  value < 0 ){
                        throw new Error(_.str.sprintf(core._t("'%s' is not a correct float"), value));
                    }
                    else{
                        return value;
                    }
                }
            }
            else{
            if( value.slice(0, -1) > 100 ||  value.slice(0, -1) < 0 ){
                throw new Error(_.str.sprintf(core._t("'%s' is not a correct float"), value));
            }
            else{ return ks_parsed;}

            }
        }
        }
       }

    ks_field_utils['format']['Percent'] = formatPercent;
    ks_field_utils['parse']['Percent'] = parsePercent;

    /**
     * Parse a String containing Percent in language formating
     *
     * @param {string} value
     *                The string to be parsed with the setting of thousands and
     *                decimal separator
     * @returns {float with percent symbol}
     * @throws {Error} if no float is found respecting the language configuration
     */
    ks_basic_controller.include({
        _notifyInvalidFields: function (invalidFields) {
            var record = this.model.get(this.handle, {raw: true});
            var fields = record.fields;
            var self = this;
            var call_once = true;
            var if_percent = true;
            var errors = invalidFields.map(function (fieldName) {
                var fieldtype = fields[fieldName].type;
                if(fieldtype==="Percent" )
                {
                    if_percent = false;
                    self.do_warn(_t("Percent field value must be 0 to 100 only"));
                }
                if(call_once && if_percent)
                 {
                   call_once = false;
                   self._super(invalidFields);
                 }
            });
        }
    })


});

