#test product class
import unittest
from decimal import Decimal
from product import Product


#Checks that the shop's item records behave correctly, both for normal and problematic entries.
class TestProduct(unittest.TestCase):

    #A normal item, like a bottle of soda with a brand, should be rocrde correctly.
    def test_valid_product_creation(self):
        p = Product("P001", "Coca-Cola 2L", "25.50", 100, brand="Coca-Cola")
        self.assertEqual(p.product_id, "P001")
        self.assertEqual(p.price, Decimal("25.50"))
        self.assertEqual(p.quantity, 100)


    #In case a product ID is written with lowercase P, it should still be recorded as uppercase
    def test_id_is_normalised_to_uppercase(self):
        p = Product("p001", "Milk", "3.00", 10)
        self.assertEqual(p.product_id, "P001")


    #The shop should refuse to add an item that has no id to identify it.
    def test_empty_id_rejected(self):
        with self.assertRaises(ValueError):
            Product("", "Bread", "5.00")


    #Optional fiels being strings
    def test_optional_fields_default_to_empty_string(self):
        p = Product("P030", "Chips", "1.50", 20)
        self.assertEqual(p.category, "")
        self.assertEqual(p.brand, "")

    # A price input should still be recorded correctly.
    # Simulates input() always returning a string
    def test_price_accepts_string_number_from_user_input(self): 
        p = Product("P010", "Water", "1.00")
        self.assertEqual(p.price, Decimal("1.00"))


    #The shop should refuse to record an item with zero price.
    def test_zero_price_rejected(self):
        with self.assertRaises(ValueError):
            Product("P002", "Bread", "0")


    #The shop should refuse to give an item a price below zero.
    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            Product("P003", "Bread", "-5.00")


    #The shop should refuse a price that isn't actually a number, like "cheap". 
    def test_non_numeric_price_rejected(self):
        with self.assertRaises(ValueError):
            Product("P011", "Bread", "cheap")


    #The shop should refuse a negative quantity input.
    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValueError):
            Product("P004", "Bread", "5.00", -3)


    #The shop should refuse a non-numeric quantity like 'many'.
    def test_non_numeric_quantity_rejected(self):
        with self.assertRaises(ValueError):
            Product("P005", "Bread", "5.00", "many")


    #The date should have the agreed format
    def test_valid_date_format_accepted(self):
        p = Product("P020", "Yogurt", "2.00", 5, entry_date="30/08/2026")
        self.assertEqual(p.entry_date, "30/08/2026")


    # confirms the human-friendly wording, not the raw %d/%m/%Y code
    def test_invalid_date_error_message_is_readable(self):
        with self.assertRaises(ValueError) as context:
            Product("P007", "Bread", "5.00", 10, entry_date="not-a-date")
        self.assertIn("DD/MM/YYYY", str(context.exception))



if __name__ == "__main__":
    unittest.main()
