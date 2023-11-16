odoo.define('gauge_field', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField'); //class is a base class for Odoo widgets that provides basic functionality for displaying and editing fields in Odoo forms.
    var fieldRegistry = require('web.field_registry'); // object is used to register new field widgets.
    
    var gauge_field = AbstractField.extend({
        className: 'o_int_gauge', // => costante !
        // tagName: '<canvas>', //property specifies the HTML tag name for the widget's element.
        supportedFieldTypes: ['float'], //property specifies the field types that the widget supports.
        // init method initializes some internal properties, 
        // including the totalColors property, 
        // which specifies the number of colors that the widget should display
        //
        init: function () {
            //...
            this._super.apply(this, arguments);
        },

        _render: function () {
            // Svuota il contenitore
            this.$el.empty();
            //Aggiungi un elemento <div> con l'id #chart
            const chart = document.createElement('canvas');
            chart.id = 'chart';
            this.$el.append(chart);

            // Crea il grafico a indicatore
            const ctx = this.$el.find('#chart').get(0).getContext('2d');
            
            const config = {
                    type: 'gauge',
                    data: {
                    //labels: ['Success', 'Warning', 'Warning', 'Error'],
                        datasets: [{
                            data: [10,12,20,5],
                            value: this.value.data,
                            backgroundColor: ['green', 'yellow', 'orange', 'red'],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        title: {
                            display: true,
                            text: 'Gauge chart'
                        },
                        layout: {
                            padding: {
                            bottom: 30
                            }
                        },
                        needle: {
                            // Needle circle radius as the percentage of the chart area width
                            radiusPercentage: 2,
                            // Needle width as the percentage of the chart area width
                            widthPercentage: 3.2,
                            // Needle length as the percentage of the interval between inner radius (0%) and outer radius (100%) of the arc
                            lengthPercentage: 80,
                            // The color of the needle
                            color: 'rgba(0, 0, 0, 1)'
                        },
                        valueLabel: {
                            formatter: Math.round
                        }
                    }
                };
          
            this.gauge = new Chart(ctx, config);
            
        },
    
    });

    //var $target = $(ev.currentTarget);
    //var data = $target.data();
    //this._setValue(data.val.toString());
    
    fieldRegistry.add('int_gauge', gauge_field);
    
    //Finally, the function returns an object that contains the colorField widget.
    return {
        gauge_field: gauge_field,
    };
});
    