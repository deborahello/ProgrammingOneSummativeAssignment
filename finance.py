#invalid operation helps to catch invalid decimal conversions
# I use decimal for accurate money computation
from decimal import Decimal, InvalidOperation 

import pandas as pd


def parse_money(value, field_name="Amount"):
    #Read finite money with at most two decimal places; never round input slightly

    #convert the value to text, remove extra spaces, then convert it to Decimal, reject special value such as infinity or NaN
    try:
        amount= Decimal(str(value).strip())                             
        if not amount.is_finite():                                      
            raise ValueError(f"{field_name} must be a finite number.")

        #Convert the monetary value to two decimal places
        cents= amount.quantize(Decimal("0.01"))

         #Reject value that contain more than two decimal places                         
        if amount != cents:                                            
            raise ValueError(f"{field_name} must have at most decimal places.")
        return cents
    except (InvalidOperation,TypeError) as error:
        raise ValueError(f"{field_name} must be a valid monetary amount") from error



class Finance:

    COLUMNS = ["sale_id", "amount", "date"]

    def __init__(self, income_df=None):
        self.income_df= income_df if income_df is not None else pd.DataFrame(columns=self.COLUMNS)

        #It is used to store the amount received and the customer's change after payment
        self.amount_received=Decimal("0")                         
        self.change= Decimal("0")                                  

    def record_income(self, sale_summary):

         #It creates one income record using information from a completed sale 
        row= { "sale_id": sale_summary["sale_id"], "amount": str(sale_summary["total"]),"date": sale_summary["sale_date"],}

        #It adds the new income record to the existing income DataFrame
        self.income_df= pd.concat([self.income_df, pd.DataFrame([row])], ignore_index= True)  

    def process_payment(self,total, amount_received):

        # Validates and convert both values into a proper decimal points 
        total = parse_money(total, "Total")
        amount_received = parse_money(amount_received,"amount recieved")

        # Total sale must be greater than 0
        if total <= 0:
            raise ValueError("Total must be greater than zero.")

        # Payment is rejected if the customer has not paid enough
        if amount_received < total :
            raise ValueError(f"Insufficient payment. {total - amount_received:.2f} more is needed.")

        # It finally stores the payment and gives correct change to the customer
        self.amount_received = amount_received
        self.change = amount_received - total
        return self.change






    
    