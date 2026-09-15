from datetime import datetime
from decimal import Decimal

import pandas as pd

from product import Product


class Sales:
    """Builds a sale and records only successfully completed sales."""

    COLUMNS = [
        "sale_id",
        "product_id",
        "product_name",
        "quantity",
        "unit_price",
        "subtotal",
        "sale_date",
    ]

    def __init__(self, inventory, sales_df=None):
        self.inventory = inventory
        self.current_sale = []
        self.sales_df = sales_df if sales_df is not None else pd.DataFrame(columns=self.COLUMNS)
        self._sale_counter = self._find_last_sale_id()

    def add_item(self, product_id, quantity):
        quantity = Product.validate_quantity(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        product = self.inventory.find_product(product_id)
        if product is None:
            raise ValueError("Product not found.")

        existing_item = next(
            (item for item in self.current_sale if item["product_id"] == product.product_id),
            None,
        )
        current_quantity = existing_item["quantity"] if existing_item else 0
        if not self.inventory.check_stock(product.product_id, current_quantity + quantity):
            raise ValueError("Insufficient stock available.")

        if existing_item:
            existing_item["quantity"] += quantity
            existing_item["subtotal"] = existing_item["unit_price"] * existing_item["quantity"]
            return existing_item

        item = {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "quantity": quantity,
            "unit_price": product.price,
            "subtotal": product.price * quantity,
        }
        self.current_sale.append(item)
        return item

    def calculate_total(self):
        return sum((item["subtotal"] for item in self.current_sale), Decimal("0"))

    def complete_sale(self):
        if not self.current_sale:
            raise ValueError("There are no items in the current sale.")

        for item in self.current_sale:
            if not self.inventory.check_stock(item["product_id"], item["quantity"]):
                raise ValueError(f"Insufficient stock for {item['product_name']}.")

        self._sale_counter += 1
        sale_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        rows = []

        for item in self.current_sale:
            self.inventory.reduce_stock(item["product_id"], item["quantity"])
            rows.append(
                {
                    "sale_id": self._sale_counter,
                    "product_id": item["product_id"],
                    "product_name": item["product_name"],
                    "quantity": item["quantity"],
                    "unit_price": str(item["unit_price"]),
                    "subtotal": str(item["subtotal"]),
                    "sale_date": sale_date,
                }
            )

        summary = {
            "sale_id": self._sale_counter,
            "items": [dict(item) for item in self.current_sale],
            "total": self.calculate_total(),
            "sale_date": sale_date,
        }
        self.sales_df = pd.concat([self.sales_df, pd.DataFrame(rows)], ignore_index=True)
        self.cancel_sale()
        return summary

    def cancel_sale(self):
        self.current_sale.clear()

    def get_sales_history(self):
        return self.sales_df.copy()

    def _find_last_sale_id(self):
        if self.sales_df.empty:
            return 0
        try:
            return max(int(value) for value in self.sales_df["sale_id"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Sales data contains an invalid sale ID.") from error

