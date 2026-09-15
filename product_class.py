#Product class
from datetime import datetime
from finance import parse_money


#Represent one item the shop sells.
class Product:
    
    DATE_FORMAT="%d/%m/%Y"

    #Records a new item in the shop, but only if every detail about it makes sense first.
    def __init__(self, product_id, product_name, price, quantity, category="", brand="", size="", supplier="", entry_date=None, expiry_date=None):
        self.product_id=self._validate_id(product_id)
        self.product_name=self._validate_required_text(product_name, "Product name")
        self.category=category._clean_optional_text(category)
        self.brand=brand._clean_optional_text(category)
        self.size=size._clean_optional_text(size)
        self.supplier=supplier._clean_optional_text(supplier)
        self.price=self._validate_price(price)
        self.quantity=self._validate_quantity(quantity)
        self.entry_date=(self._validate_date(entry_date) if entry_date else datetime.now().strftime(self.DATE_FORMAT))
        self.expiry_date=self._validate_date(expiry_date) if expiry_date else None


    #Every item must have its own id so staff can find and track it - empty id is invalid
    @staticmethod
    def _validate_id(product_id):
        product_id = "" if product_id is None else str(product_id).strip().upper()
        if not product_id:
            raise ValueError("Product ID cannot be empty.")
        return product_id

    #Every item must have a proper name so staff can recognise it; empty name is invalid.
    @staticmethod
    def _validate_required_text(value,field_name):
        value = "" if value is None else str(value).strip()
        if not value:
            raise ValueError(f"{field_name} cannot be empty.")
        return value

    #Every optional item like category, brand, size and supplier should have no unnecessary spaces
    @staticmethod
    def _clean_optional_text(value):
        return "" if value is None else str(value).strip()


    #The price must be a real amount of money above zero, not free or negative
    @staticmethod
    def _validate_price(price):
        price = parse_money(price, "Price")
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        return price

    
    #A valid quantity of the product is a whole number
    @staticmethod
    def validate_quantity(quantity):
        try:
            quantity = int(str(quantity).strip())
        except (TypeError, ValueError) as error:
            raise ValueError("Quantity must be a whole number.") from error
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return quantity
    

    #Entry and expiry dates must follow the agreed date format or style.
    @classmethod
    def _validate_date(cls, date_string):
        try:
            datetime.strptime(date_string, cls.DATE_FORMAT)
        except (ValueError, TypeError):
            raise ValueError(f"Date must be in {cls.DATE_FORMAT} format.")
        return date_string
