import csv
import psycopg2
import random
from web3 import Web3


w = Web3()            

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

def check(b, p):
    try:
        if float(p) < 500: return "Risky"
    except: pass
    return "Verified"

def predict(p):
    try:
        v = float(p)
        if v < 500: return "Rise"
        if v > 10000: return "Stable"
    except: pass
    opts = ["Drop", "Rise", "Stable"]
    return random.choice(opts)

def run():
    c = cn()
    k = c.cursor()
    print("Starting...")

    logistics = ["BlueDart", "Delhivery", "Ecom Express", "Shadowfax", "FedEx"]
    sellers = ["RetailNet", "Appario Retail", "SuperComNet", "VisionStar", "IndiFlash"]
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"]

    k.execute("DELETE FROM p")
    c.commit()

    with open('products.csv', 'r', encoding='utf-8') as f:
        r = csv.reader(f)
        next(r)
        
        n_count = 0
        for row in r:
            try:
                pid = row[0]
                n = row[3]
                cat = row[4]
                pr = row[6]
                b = row[13]
                if not b: b = "Generic"

                s = check(b, pr)
                fu = predict(pr)
                
                hd = random.choice(logistics)
                sl = random.choice(sellers)
                c_name = "User_" + str(random.randint(100, 999)) + " (" + random.choice(cities) + ")"

                txt = n + s + hd + sl + c_name
                h = w.keccak(text=txt).hex()
                
                k.execute("""
                    INSERT INTO p (pid, n, b, pr, cat, s, h, pred, hand, sell, cons) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, 
                    (pid, n, b, pr, cat, s, h, fu, hd, sl, c_name))
                
                n_count += 1
                if n_count % 100 == 0:
                    c.commit()
                    print(n_count)
            except:
                continue

    c.commit()
    c.close()
    print("Done")

if __name__ == "__main__":
    run()