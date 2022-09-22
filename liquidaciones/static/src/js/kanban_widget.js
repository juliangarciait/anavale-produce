odoo.define('crm_ecosoft.KanbanRecord', function (require) {
"use strict";

    var widget_kanban = require('web.KanbanRecord');
    var DocumentViewer = require('mail.DocumentViewer');

    widget_kanban.include({

        events: _.extend({}, widget_kanban.prototype.events, {
        'click .o_attachment_view': '_onAttachmentView',
        }),
        _onAttachmentView: function (event) {
            event.stopPropagation();
            var activeAttachmentID = this.recordData.id;
            var attachments = [{
                            'filename': this.recordData.name,
                            'id': this.recordData.id,
                            'is_main': true,
                            'mimetype': this.recordData.mimetype,
                            'name': this.recordData.name,
                            'type': this.recordData.mimetype,
                            'url': '',

                        }]
            if (activeAttachmentID) {
                var attachmentViewer = new DocumentViewer(this, attachments, activeAttachmentID);
                attachmentViewer.appendTo($('body'));
            }
        },
    });
});