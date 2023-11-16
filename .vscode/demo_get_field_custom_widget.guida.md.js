console.log('Hi im work')
odoo.define('sale.ch15_r01_drag', function (require) {
    'use strict';
    var core = require('web.core');
    var QWeb = core.qweb;
    var relational_fields = require('web.relational_fields');
    var registry = require('web.field_registry');
    var rpc = require('web.rpc');
    // var model = new instance.web.Model("oepetstore.message_of_the_day");
    var ContactDragWidget = relational_fields.FieldMany2Many.extend({
        template: "Field.Drag.template",
        events: {
        'click .o_attach': '_onAttach',
        'click .o_attachment_delete': '_onDelete',
        'change .o_input_file': '_onFileChanged',
    },

        willStart: function() {
            console.log(this)
            return Promise.all([
                this._super.apply(this, arguments),
                this._getHtml()
            ]);
        },

        init: function(parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log(parent, name, record, options)
        },

        _getHtml() {
            var self = this;
            let domain = [];
            let field = [];
            self.categories = [];
            return rpc.query({
                model: 'categories',
                method: 'search_read',
                args: [domain, field],
                }).then(function (data) {
                  for (var key in data) {
                    self.categories.push(data[key].category_name)
                }
                self.test = '15'
            }).catch(function (error){
                console.error(`You have this error:${error}`);
            });;
        },

        start: function () {
           this._super.apply(this, arguments);
            console.log(this)
        },


        _onAttach: function () {
        this.$('.o_input_file').click();
        },


        _onDelete: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var fileID = $(ev.currentTarget).data('id');
        var record = _.findWhere(this.value.data, {res_id: fileID});
        if (record) {
            this._setValue({
                operation: 'FORGET',
                ids: [record.id],
            });
            var metadata = this.metadata[record.id];
            if (!metadata || metadata.allowUnlink) {
                this._rpc({
                    model: 'ir.attachment',
                    method: 'unlink',
                    args: [record.res_id],
                });
            }
        }
        },

        _onFileChanged: function (ev) {
            var self = this;
            ev.stopPropagation();

            var files = ev.target.files;
            var attachment_ids = this.value.res_ids;

            // Don't create an attachment if the upload window is cancelled.
            if(files.length === 0)
                return;

            _.each(files, function (file) {
                var record = _.find(self.value.data, function (attachment) {
                    return attachment.data.name === file.name;
                });
                if (record) {
                    var metadata = self.metadata[record.id];
                    if (!metadata || metadata.allowUnlink) {
                        // there is a existing attachment with the same name so we
                        // replace it
                        attachment_ids = _.without(attachment_ids, record.res_id);
                        self._rpc({
                            model: 'ir.attachment',
                            method: 'unlink',
                            args: [record.res_id],
                        });
                    }
                }
                self.uploadingFiles.push(file);
            });

            this._setValue({
                operation: 'REPLACE_WITH',
                ids: attachment_ids,
            });

            // this.$('form.o_form_binary_form').submit();
            this.$('.oe_fileupload').hide();
            ev.target.value = "";
        },


    });

    registry.add('contact.DragWidget', ContactDragWidget)
});