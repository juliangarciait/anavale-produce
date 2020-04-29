odoo.define('percent_field.basic_fields', function (require) {
    "use strict";
    var ks_field_registry = require('web.field_registry');
    var ks_basic_fields = require('web.basic_fields');
    var ks_FieldFloat = ks_basic_fields.FieldFloat;
    var Widget = require('web.Widget');

    /*
     *extending the default float field
     */
    var ks_FieldPercent = ks_FieldFloat.extend({

        // formatType is used to determine which format (and parse) functions
        formatType:'Percent',
        /**
         * to override to indicate which field types are supported by the widget
         *
         * @type Array<String>
         */
        supportedFieldTypes: ['float'],
    });

    //registering percent field
    ks_field_registry
        .add('Percent', ks_FieldPercent);
    return {
        ks_FieldPercent: ks_FieldPercent
    };
});

