import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from simple_salesforce import Salesforce

load_dotenv("./.env")

# Salesforce credentials
username = os.environ.get("SF_USERNAME", "")
password = os.environ.get("SF_PASSWORD", "")
token = os.environ.get("SF_TOKEN", "")

try:
    sf = Salesforce(username=username, password=password, security_token=token)
except Exception as e:
    print("Error connecting to Salesforce:", e)

app = FastAPI()

# Queries
unit_price_query = """SELECT Id, Name, UnitPrice, IsActive, PriceBook2Id FROM PricebookEntry 
                     WHERE Name ='Xtralife' and UnitPrice>0.0 ORDER BY UnitPrice"""
pb_query = """SELECT Id, Name FROM Pricebook2 WHERE Id = '{text}'"""


# normal_query = """SELECT Id, Name, UnitPrice, IsActive, PriceBook2Id FROM PricebookEntry WHERE Name='Xtralife' ORDER BY UnitPrice"""
class OrderItem(BaseModel):
    order_id: str
    product_id: str
    quantity: int
    unit_price: float
    pricebook_entry_id: str


def get_all_price_book():
    result = sf.query(unit_price_query)
    products = []

    for row in result["records"]:
        pb_query_replaced = pb_query.format(text=row["Pricebook2Id"])
        pb_result = sf.query(pb_query_replaced)
        pricebook_name = (
            pb_result["records"][0]["Name"] if pb_result["records"] else "Unknown"
        )

        products.append(
            {
                "Product Name": row["Name"],
                "Unit Price": row["UnitPrice"],
                "Pricebook ID": row["Pricebook2Id"],
                "Pricebook Name": pricebook_name,
            }
        )

        # products.append({
        #     "Product Name": row["Name"],
        #     "Unit Price": row["UnitPrice"],
        #     "PricebookEntry ID": pb_result['records'][0]['Id'],
        #     "Pricebook Name": pricebook_name,
        #     "Pricebook2Id" : row["Pricebook2Id"]#pb_result['records'][0]['Pricebook2Id']
        # })
    return products


pricebookentry_query = """SELECT Id, Name, UnitPrice, Product2Id from PricebookEntry WHERE Name ='Xtralife' AND UnitPrice>0.0 AND Pricebook2ID='{pricebookid}'"""


def create_order_item(order_id, pricebook_id, pricebook_name, quantity):
    # order: use get order skill from wxo
    # product: use get product skills from wxo
    # unit_price:

    pricebookentry_query_replaced = pricebookentry_query.format(
        pricebookid=pricebook_id
    )
    pricebookentry_result = sf.query(pricebookentry_query_replaced)
    try:
        order_item = {
            "OrderId": order_id,
            "Product2Id": pricebookentry_result["records"][0]["Product2Id"],
            "Quantity": quantity,
            "UnitPrice": pricebookentry_result["records"][0][
                "UnitPrice"
            ],  # result['records'][0]["UnitPrice"],
            "PriceBookEntryID": pricebookentry_result["records"][0]["Id"],
        }
    except:
        get_pricebook_id = sf.query(
            f"""SELECT Id, Name FROM Pricebook2 WHERE Name = '{pricebook_name}'"""
        )
        pricebook_id = get_pricebook_id["records"][0]["Id"]
        pricebookentry_query_replaced = pricebookentry_query.format(
            pricebookid=pricebook_id
        )
        pricebookentry_result = sf.query(pricebookentry_query_replaced)
        order_item = {
            "OrderId": order_id,
            "Product2Id": pricebookentry_result["records"][0]["Product2Id"],
            "Quantity": quantity,
            "UnitPrice": pricebookentry_result["records"][0][
                "UnitPrice"
            ],  # result['records'][0]["UnitPrice"],
            "PriceBookEntryID": pricebookentry_result["records"][0]["Id"],
        }

    result = sf.OrderItem.create(order_item)
    return result


# POST method to create an order item


@app.post("/create_order_item/")
def create_product_in_order(order, pricebook_id, pricebook_name, quantity):
    try:
        result = create_order_item(order, pricebook_id, pricebook_name, quantity)
        return {"message": "Order item created successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to create order item: {str(e)}"
        )


@app.get("/pricebooks")
def fetch_price_books():
    return {"price_books": get_all_price_book()}


@app.get("/get_all_orders")
def get_all_orders():
    order_query = """SELECT Id, OrderNumber, TotalAmount from Order"""
    order_result = sf.query(order_query)
    return {"order_result": order_result}


@app.get("/create_orders")
def create_order(account_id, date, Pricebook2Id, name, status="Draft"):
    try:
        neworder = sf.Order.create(
            {
                "AccountId": account_id,  # Account associated with the order, eg '001IU00002pmnF0YAI'
                "EffectiveDate": date,  # Effective date of the order, eg '2025-03-10'
                "Status": status,  # You can set it to 'Draft' initially
                "Pricebook2Id": Pricebook2Id,
            }
        )
    except:
        get_pricebook_id = sf.query(
            f"""SELECT Id, Name FROM Pricebook2 WHERE Name = '{name}'"""
        )
        Pricebook2Id = get_pricebook_id["records"][0]["Id"]
        get_account_id = sf.query(
            f"""SELECT Id, Name FROM Account WHERE Name = '{name}'"""
        )
        account_id = get_account_id["records"][0]["Id"]
        neworder = sf.Order.create(
            {
                "AccountId": account_id,  # Account associated with the order, eg '001IU00002pmnF0YAI'
                "EffectiveDate": date,  # Effective date of the order, eg '2025-03-10'
                "Status": status,  # You can set it to 'Draft' initially
                "Pricebook2Id": Pricebook2Id,
            }
        )

    return {"order_id": neworder["id"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
