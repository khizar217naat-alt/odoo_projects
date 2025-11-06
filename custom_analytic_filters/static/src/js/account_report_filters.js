/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AccountReport } from "@account_reports/components/account_report/account_report";

patch(AccountReport.prototype, {
    async setup() {
        if (super.setup) {
            await super.setup();
        }

        // Initialize options safely
        if (!this.options) {
            this.options = {};
        }

        // Loading state + empty data initially
        this.options.purchase_orders = [];
        this.selectedPurchaseOrderId = null;
        this.isLoadingPO = true;

        // Load purchase orders after component is fully initialized
        await this.loadPurchaseOrders();
    },

    async loadPurchaseOrders() {
        try {
            const result = await this.orm.call("account.move", "get_purchase_orders", []);
            if (!this.options) this.options = {};

            // Map results to dropdown structure
            this.options.purchase_orders = result.map(po => ({
                id: po.id,
                name: po.name,
                analytic_account_name: po.analytic_account_name,
                selected: false,
            }));

            this.isLoadingPO = false;
            this.render();
            console.log("Loaded purchase orders:", this.options.purchase_orders);
        } catch (error) {
            this.isLoadingPO = false;
            console.error("Error loading Purchase Orders:", error);
            this.render();
        }
    },

    selectPurchaseOrder(po) {
        if (!this.options || !this.options.purchase_orders) return;

        // Update selection state
        this.options.purchase_orders.forEach(p => (p.selected = p.id === po.id));
        this.selectedPurchaseOrderId = po.selected ? po.id : null;

        this.render();
        console.log("Selected PO ID:", this.selectedPurchaseOrderId);

        // Reload the report with the PO filter
        this._applyPurchaseOrderFilter();
    },

    _applyPurchaseOrderFilter() {
        // Get current filters
        const currentFilters = this.getFilters();

        // Remove any existing PO filter
        if (currentFilters.purchase_order_id) {
            delete currentFilters.purchase_order_id;
        }

        // Add new PO filter if selected
        if (this.selectedPurchaseOrderId) {
            currentFilters.purchase_order_id = this.selectedPurchaseOrderId;
        }

        // Reload report with updated filters
        this.trigger('update-report', {
            filters: currentFilters
        });
    },

    // Override the getFilters method to include PO filter
    getFilters() {
        const filters = super.getFilters ? super.getFilters() : {};

        if (this.selectedPurchaseOrderId) {
            filters.purchase_order_id = this.selectedPurchaseOrderId;
        }

        return filters;
    }
});