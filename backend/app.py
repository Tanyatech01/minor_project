from flask import Flask, render_template, request, redirect, session
import psycopg2
import pickle
import os
import json
from web3 import Web3

w = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w.eth.default_account = w.eth.accounts[0]

with open('../blockchain/build/contracts/s.json') as f:
    artifact = json.load(f)
    abi = artifact['abi']

raw = "0x42b784Fb086f7863b126294a3BefF0Dae723C38f"
caddr = w.to_checksum_address(raw)
contract = w.eth.contract(address=caddr, abi=abi)

a = Flask(__name__)
a.secret_key = "supplychain"

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

def setup():
    c = cn()
    k = c.cursor()
    k.execute("CREATE TABLE IF NOT EXISTS users (uname TEXT UNIQUE, pwd TEXT)")
    c.commit()
    c.close()

setup()

d = os.path.dirname(__file__)
model = pickle.load(open(os.path.join(d, 'model.pkl'), 'rb'))
leb = pickle.load(open(os.path.join(d, 'le_b.pkl'), 'rb'))
lec = pickle.load(open(os.path.join(d, 'le_c.pkl'), 'rb'))

@a.route('/')
def home():
    return render_template('index.html')

@a.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u = request.form.get('u')
        p = request.form.get('p')
        c = cn()
        k = c.cursor()
        try:
            k.execute("INSERT INTO users (uname, pwd) VALUES (%s, %s)", (u, p))
            c.commit()
            c.close()
            return redirect('/login')
        except:
            c.close()
            return render_template('signup.html', err="Username taken")
    return render_template('signup.html', err=None)

@a.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('u')
        p = request.form.get('p')
        if u == 'admin' and p == 'admin123':
            session['role'] = 'admin'
            return redirect('/admin')
        c = cn()
        k = c.cursor()
        k.execute("SELECT * FROM users WHERE uname=%s AND pwd=%s", (u, p))
        user = k.fetchone()
        c.close()
        if user:
            session['role'] = 'user'
            return redirect('/')
        return render_template('login.html', err="Invalid Credentials")
    return render_template('login.html', err=None)

@a.route('/')
def landing_page():
    if 'role' not in session:
        return redirect('/login')
    p = request.args.get('p', 1, type=int)
    off = (p - 1) * 5
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, s, hand, sell FROM p ORDER BY id DESC LIMIT 5 OFFSET %s", (off,))
    ddata = k.fetchall()
    c.close()
    return render_template('user.html', data=ddata, p=p)

@a.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')
    p = request.args.get('p', 1, type=int)
    off = (p - 1) * 5
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, s, hand, sell, cons, h FROM p ORDER BY id DESC LIMIT 5 OFFSET %s", (off,))
    ddata = k.fetchall()
    c.close()
    return render_template('admin.html', data=ddata, p=p)

@a.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'role' not in session:
        return redirect('/login')
    res = None
    if request.method == 'POST':
        try:
            brand = request.form.get('brand')
            cat = request.form.get('cat')
            price = float(request.form.get('price'))
            bn = leb.transform([brand])[0]
            cn = lec.transform([cat])[0]
            pval = model.predict([[bn, cn, price]])
            res = "Verified" if pval[0] == 1 else "NonVerified"
        except:
            res = "Error"
    return render_template('predict.html', result=res)

@a.route('/add_product', methods=['GET', 'POST'])
def addproduct():
    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        n = request.form.get('n')
        b = request.form.get('b')
        pr = float(request.form.get('pr'))
        cat = request.form.get('cat')

        try:
            bn = leb.transform([b])[0]
            cn = lec.transform([cat])[0]
            pval = model.predict([[bn, cn, pr]])
            s = "Verified" if pval[0] == 1 else "NonVerified"
        except:
            s = "NonVerified"

        bdata = f"{n}{b}{pr}{cat}{s}"
        h = w.keccak(text=bdata).hex()

        try:
            is_v = True if s == "Verified" else False
            pid = int(os.urandom(2).hex(), 16)
            
            contract.functions.add(pid, n, is_v).transact()

            c = cn()
            k = c.cursor()
            k.execute("""
                INSERT INTO p (pid, n, b, pr, cat, s, h, hand, sell, cons)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (pid, n, b, pr, cat, s, h, "Main Hub", "Authorized Seller", "New Entry"))
            c.commit()
            c.close()
            return redirect('/admin')
        except Exception as e:
            print(e)
            return redirect('/admin')

    return render_template('add_product.html')

@a.route('/v/<int:pid>')
def v_p(pid):
    try:
        # Fetch from mapping 'm' in your smart contract
        d = contract.functions.m(pid).call()
        
        if d[1] == "":
            return render_template('v.html', msg="ID Not Registered", d=None)
            
        res = {
            "id": d[0],
            "n": d[1],
            "v": "Verified" if d[2] else "Non-Verified"
        }
        return render_template('v.html', msg=None, d=res)
    except:
        return render_template('v.html', msg="System Error", d=None)
    
@a.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        pid = request.form.get('pid')
        return redirect(f'/v/{pid}')
    return render_template('verify_input.html')

@a.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    a.run(debug=True)