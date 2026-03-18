from flask import Flask, render_template, request, redirect, session
import psycopg2
import pickle
import os

a = Flask(__name__)
a.secret_key = "supply_chain_secret_key"

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

def setup_db():
    c = cn()
    k = c.cursor()
    k.execute("CREATE TABLE IF NOT EXISTS users (uname TEXT UNIQUE, pwd TEXT)")
    c.commit()
    c.close()

setup_db()

d = os.path.dirname(__file__)
model = pickle.load(open(os.path.join(d, 'model.pkl'), 'rb'))
le_b = pickle.load(open(os.path.join(d, 'le_b.pkl'), 'rb'))
le_c = pickle.load(open(os.path.join(d, 'le_c.pkl'), 'rb'))

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
def home():
    if 'role' not in session:
        return redirect('/login')
    p = request.args.get('p', 1, type=int)
    off = (p - 1) * 5
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, s, hand, sell FROM p ORDER BY id DESC LIMIT 5 OFFSET %s", (off,))
    d_data = k.fetchall()
    c.close()
    return render_template('user.html', data=d_data, p=p)

@a.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')
    p = request.args.get('p', 1, type=int)
    off = (p - 1) * 5
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, s, hand, sell, cons, h FROM p ORDER BY id DESC LIMIT 5 OFFSET %s", (off,))
    d_data = k.fetchall()
    c.close()
    return render_template('admin.html', data=d_data, p=p)

@a.route('/predict', methods=['GET', 'POST'])
def predict_window():
    if 'role' not in session:
        return redirect('/login')
    res = None
    if request.method == 'POST':
        try:
            brand = request.form.get('brand')
            cat = request.form.get('cat')
            price = float(request.form.get('price'))
            b_n = le_b.transform([brand])[0]
            c_n = le_c.transform([cat])[0]
            p_val = model.predict([[b_n, c_n, price]])
            res = "Verified" if p_val[0] == 1 else "Non-Verified"
        except:
            res = "Error"
    return render_template('predict.html', result=res)
@a.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if session.get('role') != 'admin':
        return redirect('/login')
    
    ai_suggestion = None
    if request.method == 'POST':
        n = request.form.get('n')
        b = request.form.get('b')
        pr = float(request.form.get('pr'))
        cat = request.form.get('cat')
        
        
        try:
            b_n = le_b.transform([b])[0]
            c_n = le_c.transform([cat])[0]
            p_val = model.predict([[b_n, c_n, pr]])
            s = "Verified" if p_val[0] == 1 else "Non-Verified"
        except:
            s = "Non-Verified" 

        
        from web3 import Web3
        w = Web3()
        block_data = f"{n}{b}{pr}{cat}{s}"
        h = w.keccak(text=block_data).hex()

        
        c = cn()
        k = c.cursor()
        k.execute("""
            INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (n, b, pr, cat, s, h, "Main Hub", "Authorized Seller", "New Entry"))
        c.commit()
        c.close()
        return redirect('/admin')
        
    return render_template('add_product.html')

@a.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    a.run(debug=True)