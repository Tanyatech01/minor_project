import csv
import psycopg2
import random
from web3 import Web3

w = Web3()

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

def check():
    v = ["Verified", "Non-Verified"]
    return random.choice(v)

def run():
    c = cn()
    k = c.cursor()
    l_list = ["BlueDart", "Delhivery", "Ecom Express", "Shadowfax", "FedEx"]
    s_list = ["RetailNet", "Appario Retail", "SuperComNet", "VisionStar", "IndiFlash"]
    c_list = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"]
    
    k.execute("DELETE FROM p")
    c.commit()

    with open('products.csv', 'r', encoding='utf-8') as f:
        r = csv.reader(f)
        next(r)
        
        batch = []
        for row in r:
            try:
                # Prepare product data
                pid, n, cat, pr, b = row[0], row[3], row[4], row[6], row[13]
                if not b: b = "Generic"
                s = check()
                hd = random.choice(l_list)
                sl = random.choice(s_list)
                u = "User_" + str(random.randint(100, 999)) + " (" + random.choice(c_list) + ")"
                
                # Add to current batch
                batch.append([pid, n, b, pr, cat, s, hd, sl, u])

                # Once we have 5 items, generate 1 hash and save
                if len(batch) == 5:
                    # Create 1 hash for the whole block string
                    block_data = "".join([str(i) for item in batch for i in item])
                    block_hash = w.keccak(text=block_data).hex()

                    for p_item in batch:
                        k.execute("""
                            INSERT INTO p (pid, n, b, pr, cat, s, h, hand, sell, cons) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (p_item[0], p_item[1], p_item[2], p_item[3], p_item[4], p_item[5], block_hash, p_item[6], p_item[7], p_item[8]))
                    
                    batch = [] # Reset for next block
                    c.commit()
            except: continue
            
    c.close()
    print("Blocks Created Successfully")

if __name__ == "__main__":
    run()