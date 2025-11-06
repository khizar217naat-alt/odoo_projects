import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useRef } from "@odoo/owl";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.showDiscountInput = false;
        this.discountInputRef = useRef("percentInput");
    },

    togglePercentInput(state) {
        this.showDiscountInput = state;
        this.render();
        if (state) {
            setTimeout(() => {
                if (this.discountInputRef.el) {
                    this.discountInputRef.el.focus();
                }
            }, 50);
        }
    },

    onPercentKey(ev) {
        if (ev.key === "Enter") {
            const value = parseFloat(ev.target.value);
            if (!isNaN(value) && value >= 0) {
                const order = this.pos.get_order();
                const line = order?.get_selected_orderline();
                if (order && line) {
                    const lineTotal = line.get_price_with_tax();
                    if (lineTotal > 0) {
                        // If discount >= line price -> free product
                        if (value >= lineTotal) {
                            line.set_discount_amount(lineTotal);
                            line.set_unit_price(0);   // Make product FREE
                        } else {
                            const discountAmount = value;

                            // Set discount amount only on selected line
                            if (line.set_discount_amount) {
                                line.set_discount_amount(discountAmount);
                            } else {
                                line.discount_amount = discountAmount;
                            }

                            // Adjust unit price based on discount
                            const newPrice = Math.max(
                                0,
                                line.get_unit_price() - (discountAmount / line.get_quantity())
                            );
                            line.set_unit_price(newPrice);
                        }

                        // Refresh totals
                        order.recomputeOrderData();
                    }
                }
            }
            this.togglePercentInput(false);
        }
    },

});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                discount_amount: { type: String, optional: true }, // 👈 add it here
            },
        },
    },
});

// Extend PosOrderline to support discount_amount in display and a setter
patch(PosOrderline.prototype, {
    props: {
        ...PosOrderline.props,
        discount_amount: { type: String, optional: true },
    },

    set_discount_amount(amount) {
        const parsed = typeof amount === "number" ? amount : parseFloat(amount);
        const val = isNaN(parsed) ? 0 : Math.max(0, parsed);
        this.discount_amount = val;
        this.setDirty();
    },

    getDisplayData() {
        const data = super.getDisplayData();

        if (this.get_unit_price() === 0) {
            data.price = "FREE";
        }

        const formattedDiscountAmount = this.discount_amount
            ? formatCurrency(this.discount_amount, this.currency)
            : "";
        return {
            ...data,
            discount_amount: formattedDiscountAmount,
        };
    },

});
