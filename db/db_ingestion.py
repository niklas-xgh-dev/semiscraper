import psycopg2
from psycopg2 import sql
from typing import List, Dict
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def insert_product(cur, product: Dict[str, str]):
    cur.execute(
        sql.SQL("INSERT INTO products (name, mpn, sku, description, manufacturer) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (mpn) DO UPDATE SET name = EXCLUDED.name, sku = EXCLUDED.sku, description = EXCLUDED.description, manufacturer = EXCLUDED.manufacturer RETURNING id"),
        (product['Name'], product['MPN'], product['SKU'], product['Description'], product['Manufacturer'])
    )
    return cur.fetchone()[0]

def insert_product_marketplace(cur, product_id: int, product: Dict[str, str], marketplace_name: str):
    cur.execute(
        sql.SQL("INSERT INTO product_marketplace (product_id, marketplace_name, price, currency, unit_pack, stock_status, lead_time, package, packaging) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (product_id, marketplace_name) DO UPDATE SET price = EXCLUDED.price, currency = EXCLUDED.currency, unit_pack = EXCLUDED.unit_pack, stock_status = EXCLUDED.stock_status, lead_time = EXCLUDED.lead_time, package = EXCLUDED.package, packaging = EXCLUDED.packaging RETURNING id"),
        (product_id, marketplace_name, product['Price'], product['Currency'], product['Unit Pack'], product['Stock Status'], product['Lead Time'], product['Package'], product['Packaging'])
    )
    return cur.fetchone()[0]

def insert_product_history(cur, product_marketplace_id: int, product: Dict[str, str]):
    cur.execute(
        sql.SQL("INSERT INTO product_history (product_marketplace_id, price, currency, stock_status, lead_time) VALUES (%s, %s, %s, %s, %s)"),
        (product_marketplace_id, product['Price'], product['Currency'], product['Stock Status'], product['Lead Time'])
    )

def ingest_data(products: List[Dict[str, str]], marketplace_name: str):
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        for product in products:
            product_id = insert_product(cur, product)
            product_marketplace_id = insert_product_marketplace(cur, product_id, product, marketplace_name)
            insert_product_history(cur, product_marketplace_id, product)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # This is for testing purposes
    test_products = [
        {
            'Name': 'Test Product',
            'MPN': 'TEST123',
            'SKU': 'SKU123',
            'Description': 'Test description',
            'Manufacturer': 'Test Manufacturer',
            'Package': 'TO-247',
            'Packaging': 'Tube',
            'Price': '10.99',
            'Currency': 'USD',
            'Unit Pack': '10',
            'Stock Status': 'In Stock',
            'Lead Time': '3 days'
        }
    ]
    ingest_data(test_products, 'TestMarketplace')