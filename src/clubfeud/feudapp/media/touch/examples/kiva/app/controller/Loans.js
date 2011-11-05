/**
 * @class Kiva.controller.Loans
 * @extends Ext.app.Controller
 * 
 * The only controller in this simple application - this simply sets up the fullscreen viewport panel
 * and renders a detailed overlay whenever a Loan is tapped on.
 */
Ext.define('Kiva.controller.Loans', {
    extend: 'Ext.app.Controller',

    config: {
        profile: Ext.os.deviceType.toLowerCase()
    },

    views : [
        'Main',
        'Detail',
        'LoanFilter'
    ],

    stores: [
        'Loans'
    ],

    refs: [
        {
            ref     : 'main',
            selector: 'mainview',
            autoCreate: true,
            xtype   : 'mainview'
        },
        {
            ref     : 'detail',
            selector: 'detail'
        },
        {
            ref : 'loansList',
            selector: 'loanslist'
        },
        {
            ref: 'loanFilter',
            selector: 'loanfilter'
        },
        {
            ref: 'refreshButton',
            selector: 'button[iconCls=refresh]'
        }
    ],

    init: function() {
        this.getMainView().create();

        this.control({
            'loanslist': {
                select: this.onListTap
            },
            'detail': {
                hideanimationstart: this.onDetailHideAnimationStart
            },
            'searchfield': {
                change: function(field) {
                    this.doFilter({
                        q: field.getValue()
                    });
                }
            },
            'selectfield': {
                change: function(field) {
                    var config = {};
                    config[field.getName()] = field.getValue();
                    this.doFilter(config);
                }
            },
            'button[iconCls=refresh]': {
                tap: this.onRefreshButtonTap
            }
        });

        this.getLoansStore().on({
            scope: this,

            beforeload: this.onBeforeStoreLoad,
            load      : this.onStoreLoad
        });
    },

    onListTap: function(list, loan) {
        if (!this.getDetail()) {
            this.getDetailView().create();
        }

        var view = this.getDetail();
        view.setLoan(loan);
        
        if (this.getProfile() == "phone") {
            view.setWidth(null);
            view.setHeight('85%');
            view.setTop(null);
            view.setLeft(0);
        }

        view.show();
    },

    onDetailHideAnimationStart: function() {
        this.getLoansList().deselectAll();
    },

    onRefreshButtonTap: function() {
        this.getLoansStore().load();
    },

    onBeforeStoreLoad: function() {
        this.getRefreshButton().setDisabled(true);
    },

    onStoreLoad: function() {
        this.getRefreshButton().setDisabled(false);  
    },

    /**
     * @private
     * Listener for the 'filter' event fired by the listView set up in the 'list' action. This simply
     * gets the form values that the user wants to filter on and tells the Store to filter using them.
     */
    doFilter: function(values, form) {
        var store   = this.getLoansStore(),
            filters = [],
            field;
        
        Ext.iterate(values, function(field, value) {
            filters.push(new Ext.util.Filter({
                property: field,
                value   : value
            }));
        });
        
        store.clearFilter();
        store.filter(filters);
    }

    // onSearchTap: function(item) {
        
    // },

    // onSearch: function(field, e) {
    //     var keyCode = e.event.keyCode;

    //     if (keyCode == 13) {
    //         var value = field.getValue();
    //         this.fireAction('search', [value], 'doSearch');
    //     }
    // },

    // doSearch: function(search) {
    //     var model = this.getModel('Search'),
    //         list = this.getTweetList(),
    //         searchesStore = this.getSearchesStore(),
    //         query, store;
        
    //     if (!(search instanceof Twitter.model.Search)) {
    //         query = search.replace("%20", " ");
    //         search = new model({
    //             query: query
    //         });
    //     }

    //     searchesStore.add(search);

    //     store = search.tweets();
    //     list.setStore(store);
    //     store.load();
    // }
});


// Ext.regController("loans", {

//     /**
//      * Renders the Viewport and sets up listeners to show details when a Loan is tapped on. This
//      * is only expected to be called once - at application startup. This is initially called inside
//      * the app.js launch function.
//      */
//     list: function() {
//         this.listView = this.render({
//             xtype: 'kivaMain',
//             listeners: {
//                 scope : this,
//                 filter: this.onFilter,
//                 selectionchange: this.onSelected
//             }
//         }, Ext.getBody()).down('.loansList');
//     },

//     /**
//      * Shows a details overlay for a given Loan. This creates a single reusable detailView and simply
//      * updates it each time a Loan is tapped on.
//      */
//     show: function(options) {
//         var view = this.detailView;
        
//         if (!view) {
//             this.detailView = this.render({
//                 xtype: 'loanShow',
//                 listeners: {
//                     scope: this,
//                     hide : function() {
//                         this.listView.getSelectionModel().deselectAll();
//                     }
//                 }
//             }, false);
            
//             view = this.detailView;
//         }
        
//         view.setLoan(options.instance);
//         view.show();
//     },
    
    
//     /**
//      * @private
//      * Causes the Loan details overlay to be shown if there is a Loan selected
//      */
//     onSelected: function(selectionModel, records) {
//         var loan = records[0];
        
//         if (loan) {
//             this.show({
//                 instance: loan
//             });
//         }
//     }
// });