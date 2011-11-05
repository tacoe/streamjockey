Ext.require([
    'Ext.Button'
]);

Ext.setup({
    icon: 'icon.png',
    glossOnIcon: false,
    tabletStartupScreen: 'tablet_startup.png',
    phoneStartupScreen: 'phone_startup.png',
    onReady: function() {
        var overlay = Ext.create('Ext.Panel', {
            floating        : true,
            modal           : true,
            hidden          : true,
            width           : 300,
            height          : 200,
            styleHtmlContent: true,
            html: '<p>This is a modal, centered and floating panel. hideOnMaskTap is true by default so ' +
                  'we can tap anywhere outside the overlay to hide it.</p>',
            items: [{
                    docked: 'top',
                    xtype : 'toolbar',
                    title : 'Overlay Title'
            }],
            scrollable: true
        });

        Ext.Viewport.on({
            delegate: 'button',
            tap: function(button) {
                overlay.showBy(button);
            }
        });

        Ext.Viewport.add({
            layout: {
                type: 'vbox',
                pack: 'center',
                align: 'stretch'
            },
            items: [{
                xtype: 'toolbar',
                docked: 'top',
                items: [{
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }]
            }, {
                xtype: 'toolbar',
                items: [{
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }]
            }, {
                xtype: 'toolbar',
                docked: 'bottom',
                items: [{
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }, {flex: 1, xtype: 'component'}, {
                    text: 'Show'
                }]
            }]
        });
    }
});