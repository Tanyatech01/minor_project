import csv
import psycopg2
import random
from web3 import Web3

w = Web3()

def run():
    conn = psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")
    k = conn.cursor()
    k.execute("DELETE FROM p")

    with open('products.csv', 'r', encoding='utf-8') as f:
        r = csv.reader(f)
        next(r)
        batch = []
        for row in r:
            try:
                # Extraction: Adjust indices based on your CSV structure
                pid, n, cat, pr, b = row[0], row[3], row[4], row[6], row[13]
                batch.append([pid, n, b or "Generic", pr, cat, "Pending", "Hub", "Retailer", "Final"])

                if len(batch) == 5:
                    block_str = "".join([str(x) for sub in batch for x in sub])
                    block_hash = w.keccak(text=block_str).hex()
                    for item in batch:
                        k.execute("INSERT INTO p (pid, n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                  (item[0], item[1], item[2], item[3], item[4], item[5], block_hash, item[6], item[7], item[8]))
                    batch = []
                    conn.commit()
            except: continue
    conn.close()
    print("Data Ingestion Complete.")

if __name__ == "__main__":
    run()