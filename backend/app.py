import json, os, pickle, psycopg2, csv, random, hashlib, io
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

ru = os.environ.get("RPC_URL")
w = Web3(Web3.HTTPProvider(ru))

pk = os.environ.get("PRIVATE_KEY")
ad = os.environ.get("ACCOUNT_ADDRESS")
if pk and ad:
    w.eth.default_account = w.to_checksum_address(ad)

p = os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'build', 'contracts', 'S.json')
if not os.path.exists(p):
    p = os.path.join(os.path.dirname(__file__), 'S.json')

with open(p, "r") as f:
    c = json.load(f)

a = c['abi']
ca = os.environ.get("CONTRACTADDRESS")
if ca:
    ca = w.to_checksum_address(ca)
    ct = w.eth.contract(address=ca, abi=a)

fl = Flask(__name__)
fl.secret_key = os.environ.get("SECRET_KEY", "scs")
od = {}

def cn():
    du = os.environ.get("DATABASE_URL")
    return psycopg2.connect(du)

d = os.path.dirname(__file__)
md = pickle.load(open(os.path.join(d, "model.pkl"), "rb"))
lb = pickle.load(open(os.path.join(d, "le_b.pkl"), "rb"))
lc = pickle.load(open(os.path.join(d, "le_c.pkl"), "rb"))

@fl.route("/")
def hm():
    if "role" not in session: return render_template("preview.html", err=None)
    return redirect(url_for("adm") if session["role"] == "admin" else url_for("udb"))

@fl.route("/signup", methods=["POST"])
def su():
    u, e, pw = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    k.execute("SELECT * FROM admins WHERE uname=%s", (u,))
    if k.fetchone():
        c.close()
        return render_template("preview.html", err="Restricted Username")
    try:
        k.execute("INSERT INTO users (uname, email, pwd, st) VALUES (%s, %s, %s, %s)", (u, e, pw, "Pending"))
        c.commit()
        c.close()
        return render_template("preview.html", msg="Registration Submitted")
    except:
        c.close()
        return render_template("preview.html", err="Username or Email Taken")

@fl.route("/login", methods=["POST"])
def lg():
    u, pw = request.form.get("u"), request.form.get("p")
    c = cn()
    k = c.cursor()
    k.execute("SELECT * FROM admins WHERE uname=%s AND pwd=%s", (u, pw))
    am = k.fetchone()
    if am:
        session["role"] = "admin"
        session["uname"] = u
        c.close()
        return redirect(url_for("adm"))
    k.execute("SELECT st FROM users WHERE uname=%s AND pwd=%s", (u, pw))
    ur = k.fetchone()
    c.close()
    if ur:
        if ur[0] == "Pending":
            return render_template("preview.html", err="Account Pending")
        session["role"] = "user"
        session["uname"] = u
        return redirect(url_for("udb"))
    return render_template("preview.html", err="Invalid Credentials")

@fl.route("/user_dashboard")
def udb():
    if session.get("role") != "user": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT id, n, pr, cat, s, hand FROM p ORDER BY id DESC")
    r = k.fetchall()
    c.close()
    cd = [[str(i) for i in x] for x in r]
    return render_template("user.html", data=cd, uname=session["uname"])

@fl.route("/admin")
def adm():
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT COUNT(*) FROM p")
    if k.fetchone()[0] == 0:
        pp = os.path.join(os.path.dirname(__file__), "products.csv")
        if os.path.exists(pp):
            with open(pp, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                next(r)
                for rw in r:
                    try:
                        cc = rw[4].replace('["', '').replace('"]', '').split(' >> ')[0]
                        k.execute("INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                  (rw[3], rw[13], rw[6], cc, "LEGIT", rw[0], "Warehouse Hub", "Retailer", "Active"))
                    except: continue
            c.commit()
    k.execute("SELECT id, n, b, pr, cat, s, h, hand, sell, cons FROM p ORDER BY id DESC")
    pr = k.fetchall()
    k.execute("SELECT id, uname, email, pwd, st FROM users ORDER BY id ASC")
    ur = k.fetchall()
    k.execute("SELECT id, uname, email, pwd, role FROM admins ORDER BY id ASC")
    ar = k.fetchall()
    c.close()
    pd = [[str(i) for i in x] for x in pr]
    ud = [[str(u[0]), u[1], u[2], u[3].encode('utf-8').hex(), u[4]] for u in ur]
    ad = [[str(x[0]), x[1], x[2], x[3].encode('utf-8').hex(), x[4]] for x in ar]
    return render_template("admin.html", data=pd, users=ud, admins=ad)

@fl.route("/add_product", methods=["POST"])
def ap():
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    pp = os.path.join(os.path.dirname(__file__), "products.csv")
    
    if "csv_file" in request.files and request.files["csv_file"].filename != "":
        f = request.files["csv_file"]
        sm = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        r = csv.reader(sm)
        next(r, None)
        with open(pp, "a", encoding="utf-8", newline="") as wf:
            wr = csv.writer(wf)
            for rw in r:
                if len(rw) >= 14:
                    try:
                        nn = rw[3]
                        bb = rw[13]
                        pr = rw[6]
                        cc = rw[4].replace('["', '').replace('"]', '').split(' >> ')[0]
                        hh = rw[0]
                        k.execute("INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                  (nn, bb, pr, cc, "LEGIT", hh, "Warehouse Hub", "Retailer", "Active"))
                        wr.writerow(rw)
                    except: continue
    else:
        nn = request.form.get("n")
        bb = request.form.get("b")
        pr = request.form.get("pr")
        cat = request.form.get("cat")
        hh = hashlib.sha256((nn + bb + pr).encode()).hexdigest()[:16]
        
        nc = w.eth.get_transaction_count(ad)
        tx = ct.functions.add(int(hh, 16), nn, True).build_transaction({
            'from': ad,
            'nonce': nc,
            'gas': 500000,
            'gasPrice': w.to_wei('50', 'gwei')
        })
        stx = w.eth.account.sign_transaction(tx, pk)
        w.eth.send_raw_transaction(stx.rawTransaction)

        k.execute("INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                  (nn, bb, pr, cat, "LEGIT", hh, "Warehouse Hub", "Retailer", "Active"))
        with open(pp, "a", encoding="utf-8", newline="") as wf:
            wr = csv.writer(wf)
            wr.writerow([hh, "URL", "URL", nn, cat, "PID", pr, pr, pr, "DESC", "100", "0", "0", bb, "SPEC"])
            
    c.commit()
    c.close()
    return redirect(url_for("adm"))

@fl.route("/decommission/<int:pid>")
def dc(pid):
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, cat, sell, cons FROM p WHERE id=%s", (pid,))
    rw = k.fetchone()
    if rw:
        nn, bb, pr, cat, sell, cons = rw
        nh = hashlib.sha256((nn + bb + pr + str(random.random())).encode()).hexdigest()[:16]
        k.execute("INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                  (nn, bb, pr, cat, "DECOMMISSIONED", nh, "CANCELLED", sell, cons))
        c.commit()
    c.close()
    return redirect(url_for("adm"))

@fl.route("/add_u", methods=["POST"])
def au():
    if session.get("role") != "admin": return redirect(url_for("hm"))
    u, e, pw = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    try:
        k.execute("INSERT INTO users (uname, email, pwd, st) VALUES (%s, %s, %s, %s)", (u, e, pw, "Approved"))
        c.commit()
    except: pass
    c.close()
    return redirect(url_for("adm"))

@fl.route("/apv_u/<int:uid>")
def apu(uid):
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("UPDATE users SET st='Approved' WHERE id=%s", (uid,))
    c.commit()
    c.close()
    return redirect(url_for("adm"))

@fl.route("/del_u/<int:uid>")
def du(uid):
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("DELETE FROM users WHERE id=%s", (uid,))
    c.commit()
    c.close()
    return redirect(url_for("adm"))

@fl.route("/add_a", methods=["POST"])
def aa():
    if session.get("role") != "admin": return redirect(url_for("hm"))
    u, e, pw = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    try:
        k.execute("INSERT INTO admins (uname, email, pwd, role) VALUES (%s, %s, %s, %s)", (u, e, pw, "Sub-Admin"))
        c.commit()
    except: pass
    c.close()
    return redirect(url_for("adm"))

@fl.route("/del_a/<int:aid>")
def da(aid):
    if session.get("role") != "admin": return redirect(url_for("hm"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT role FROM admins WHERE id=%s", (aid,))
    rs = k.fetchone()
    if rs and rs[0] != "Master":
        k.execute("DELETE FROM admins WHERE id=%s", (aid,))
        c.commit()
    c.close()
    return redirect(url_for("adm"))

@fl.route("/req_otp", methods=["POST"])
def ro():
    if session.get("role") != "admin": return jsonify({"status": "error"})
    e = request.form.get("e")
    op = str(random.randint(100000, 999999))
    od[e] = op
    return jsonify({"status": "success"})

@fl.route("/rst_p", methods=["POST"])
def rp():
    if session.get("role") != "admin": return redirect(url_for("hm"))
    e, o, pw, t = request.form.get("e"), request.form.get("o"), request.form.get("p"), request.form.get("t")
    if od.get(e) == o:
        c = cn()
        k = c.cursor()
        if t == "user":
            k.execute("UPDATE users SET pwd=%s WHERE email=%s", (pw, e))
        else:
            k.execute("UPDATE admins SET pwd=%s WHERE email=%s", (pw, e))
        c.commit()
        c.close()
        od.pop(e, None)
    return redirect(url_for("adm"))

@fl.route("/logout")
def lo():
    session.clear()
    return redirect(url_for("hm"))

if __name__ == "__main__":
    fl.run(debug=False)