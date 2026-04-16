import os
import psycopg2
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_database():
    print("Connecting to database...")
    db_url = os.environ.get("DATABASE_URL")
    c = psycopg2.connect(db_url)
    k = c.cursor()
    
    csv_path = os.path.join(os.path.dirname(__file__), "products.csv")
    
    if not os.path.exists(csv_path):
        print("Error: products.csv not found!")
        return

    print("Reading Flipkart data and populating database...")
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for rw in reader:
            try:
                # Extracting category logic from your original code
                category = rw[4].replace('["', '').replace('"]', '').split(' >> ')[0]
                
                # Inserting directly into the remote Postgres DB
                k.execute(
                    "INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (rw[3], rw[13], rw[6], category, "LEGIT", rw[0], "Warehouse Hub", "Retailer", "Active")
                )
                count += 1
            except Exception as e:
                continue
                
    c.commit()
    c.close()
    print(f"Success! {count} products injected into the remote database.")

if __name__ == "__main__":
    seed_database()