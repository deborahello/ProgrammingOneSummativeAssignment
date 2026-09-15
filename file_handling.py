import pandas as pd
import os

from product import Product
from finance import Finance, parse_money
from sales import Sales



class FileHandling:
    """ This class uses pandas to save and load the system's csv files"""
    PRODUCT_COLUMNS = [
        "product_id", "product_name", "category","brand",  "size", "supplier",
        "price", "quantity","entry_date","expiry_date"
    ]

    def __init__(self,data_directory ="data"):

        #Relative paths always start  beside this program, not in the launch folder
        program_directory = os.path.dirname(os.path.abspath(__file__))
        self.data_directory = os.path.abspath(os.path.join(program_directory,data_directory))
        self.products_file = os.path.join(self.data_directory, "products.csv")
        self.sales_file =os.path.join(self.data_directory, "sales.csv")
        self.income_file = os.path.join(self.data_directory, "income.csv")

    def prepare_directory(self):  

        # called once at start ,when after, the user chooses to open the shop
        os.makedirs( self.data_directory, exist_ok=True)

    def save_changes(self,inventory, sales, finance, pending):

        # only save files whose data changed, then remove them from pending after a successful save
        if "products" in pending:
            self.save_products(inventory.products)
            pending.remove( "products")
        if "sales" in pending:
            self.save_sales(sales.sales_df)
            pending.remove("sales")
        if "income" in pending:
            self.save_income(finance.income_df)
            pending.remove("income")

        
    def load_products(self):

        # Read the csv and rebuild Product objects from each saved row
        dataframe= self._read_csv(self.products_file, self.PRODUCT_COLUMNS)
        products= {}

        for row_number, row in dataframe.iterrows():
            try:
                # cvs column names match the Product constructor's arguments.
                product= Product(**row.to_dict())
            except ValueError as error:
                raise ValueError(f"Invalid product on cvs row {row_number + 2}: {error}") from error

            # Prduct Id must remain unique when rebuilding the inventory
            if product.product_id in products:
                raise ValueError(f" Duplicate product ID {product.product_id} in products.csv.")
            products[product.product_id] = product
        return products

    
    def save_products(self, products):

        # Converts every Product object into a dictionary so apndas can store it as a row
        rows=[vars(product) for product in products.values()]
        dataframe= pd.DataFrame(rows, columns= self.PRODUCT_COLUMNS)
        self._write_dataframe(self.products_file, dataframe, self.PRODUCT_COLUMNS)


    def load_sales(self):        
        dataframe = self._read_csv(self.sales_file, Sales.COLUMNS)

        # Validates every saved sale before allowing it back into the systems
        for index, row in dataframe.iterrows():
            try:
                sale_id= Product.validate_quantity(row["sale_id"])
                quantity= Product.validate_quantity(row["quantity"])
                price= Product._validate_price(row["unit_price"])
                subtotal= parse_money(row["subtotal"], "Subtotal")

                #The saved sub total must matchthe price multiplied by quantity
                if sale_id == 0 or quantity== 0 or subtotal != price* quantity:
                    raise ValueError("Invalid sale ID, quantity, or subtotal.")
            except ValueError as error:
                raise ValueError(f"Invalid sales.csv row {index + 2}: {error}")
        return dataframe

    def save_sales(self,sales_df):
        self._write_dataframe(self.sales_file, sales_df, Sales.COLUMNS)

    def load_income(self):
        dataframe= self._read_csv(self.income_file, Finance.COLUMNS)

        # check that every saved income record containsa valid sale ID and positive amount
        for index, row in dataframe.iterrows():
            try:
                if Product.validate_quantity(row["sale_id"]) ==0:
                    raise ValueError("Sale ID must be positive.")
                if parse_money(row["amount"], "Income") <= 0:
                    raise ValueError("Income must be positive.")
            except ValueError as error:
                raise ValueError(f"Invalid income.csv row {index +2}: {error}") from error
        return dataframe


    def save_income(self,income_df):
        self._write_dataframe(self.income_file, income_df, Finance.COLUMNS)

    @staticmethod
    def _read_csv(filename, required_columns):
        name = os.path.basename(filename)
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as file:
                dataframe = pd.read_csv(file, dtype=str, keep_default_na=False) 
        except FileNotFoundError:
            # A missing file means there is no saved data yet, so return an empty table
            return pd.DataFrame(columns=required_columns)

        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError) as error:
            raise ValueError(f" cannot read {name}. check its csv contents; it was not changed") from error

        # Reject files whose strucutre does not match what the program expects
        if set(dataframe.columns) != set(required_columns):
            raise ValueError(f"{name} must contain exactly these columns: {', '.join(required_columns)}")

        # Reject incomplete or incorrectly structured rows
        if not isinstance(dataframe.index, pd.RangeIndex) or dataframe.isna().any().any():
            raise ValueError(f"{name} contains an incomplete or incorrectly sized row.")
        return dataframe[required_columns]
        

    @staticmethod
    def _write_dataframe( filename, dataframe, columns):

        # Write to temporary file first so the original file is not damaged
        # If saving fails halfway through
        temporary = filename + ".tmp"
        try:
            with open(temporary, "w") as file :
                dataframe[columns].to_csv(file, index=False)

            #Replacing the old csv only after the temporary file successfully
            os.replace(temporary,filename)

        finally:
            # Clean up any temporary file left behind if an error occurs
            if os.path.exists(temporary):
                os.remove(temporary)



