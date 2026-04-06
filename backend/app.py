import csv
import hashlib
import io
import json
import os
import pickle
import random

import psycopg2
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from web3 import Web3

w = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w.eth.default_account = w.eth.accounts[0]
with open("../blockchain/build/contracts/s.json") as f:
    artifact = json.load(f)
    abi = artifact["abi"]
caddr = w.to_checksum_address("0x9C3cAEd760d5eaE675f993421473d35b5E446EaF")
contract = w.eth.contract(address=caddr, abi=abi)

a = Flask(__name__)
a.secret_key = "supplychainsecurekey"
o_d = {}


def cn():
    return psycopg2.connect(
        host="127.0.0.1",
        dbname="s_chain",
        user="postgres",
        password="India@#123",
        port="5432",
    )


d = os.path.dirname(__file__)
model = pickle.load(open(os.path.join(d, "model.pkl"), "rb"))
leb = pickle.load(open(os.path.join(d, "le_b.pkl"), "rb"))
lec = pickle.load(open(os.path.join(d, "le_c.pkl"), "rb"))


@a.route("/")
def home():
    if "role" not in session:
        return render_template("preview.html", err=None)
    return redirect(
        url_for("admin") if session["role"] == "admin" else url_for("user_dashboard")
    )


@a.route("/signup", methods=["POST"])
def signup():
    u, e, p = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    k.execute("SELECT * FROM admins WHERE uname=%s", (u,))
    if k.fetchone():
        c.close()
        return render_template("preview.html", err="Restricted Username")
    try:
        k.execute(
            "INSERT INTO users (uname, email, pwd, st) VALUES (%s, %s, %s, %s)",
            (u, e, p, "Pending"),
        )
        c.commit()
        c.close()
        return render_template(
            "preview.html", msg="Registration Submitted Awaiting Admin Approval"
        )
    except:
        c.close()
        return render_template("preview.html", err="Username or Email Taken")


@a.route("/login", methods=["POST"])
def login():
    u, p = request.form.get("u"), request.form.get("p")
    c = cn()
    k = c.cursor()
    k.execute("SELECT * FROM admins WHERE uname=%s AND pwd=%s", (u, p))
    adm = k.fetchone()
    if adm:
        session["role"] = "admin"
        session["uname"] = u
        c.close()
        return redirect(url_for("admin"))
    k.execute("SELECT st FROM users WHERE uname=%s AND pwd=%s", (u, p))
    usr = k.fetchone()
    c.close()
    if usr:
        if usr[0] == "Pending":
            return render_template("preview.html", err="Account Pending Admin Approval")
        session["role"] = "user"
        session["uname"] = u
        return redirect(url_for("user_dashboard"))
    return render_template("preview.html", err="Invalid Credentials")


@a.route("/user_dashboard")
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT id, n, pr, cat, s, hand FROM p ORDER BY id DESC")
    rows = k.fetchall()
    c.close()
    cd = [[str(i) for i in r] for r in rows]
    return render_template("user.html", data=cd, uname=session["uname"])


@a.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT COUNT(*) FROM p")
    if k.fetchone()[0] == 0:
        pp = os.path.join(os.path.dirname(__file__), "products.csv")
        if os.path.exists(pp):
            with open(pp, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                next(r)
                for row in r:
                    try:
                        clean_cat = (
                            row[4].replace('["', "").replace('"]', "").split(" >> ")[0]
                        )
                        k.execute(
                            "INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                row[3],
                                row[13],
                                row[6],
                                clean_cat,
                                "LEGIT",
                                row[0],
                                "Warehouse Hub",
                                "Retailer",
                                "Active",
                            ),
                        )
                    except:
                        continue
            c.commit()
    k.execute(
        "SELECT id, n, b, pr, cat, s, h, hand, sell, cons FROM p ORDER BY id DESC"
    )
    p_rows = k.fetchall()
    k.execute("SELECT id, uname, email, pwd, st FROM users ORDER BY id ASC")
    u_rows = k.fetchall()
    k.execute("SELECT id, uname, email, pwd, role FROM admins ORDER BY id ASC")
    a_rows = k.fetchall()
    c.close()
    p_data = [[str(i) for i in r] for r in p_rows]
    u_data = [[str(u[0]), u[1], u[2], u[3].encode("utf-8").hex(), u[4]] for u in u_rows]
    a_data = [[str(x[0]), x[1], x[2], x[3].encode("utf-8").hex(), x[4]] for x in a_rows]
    return render_template("admin.html", data=p_data, users=u_data, admins=a_data)


@a.route("/add_product", methods=["POST"])
def add_product():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    pp = os.path.join(os.path.dirname(__file__), "products.csv")

    if "csv_file" in request.files and request.files["csv_file"].filename != "":
        f = request.files["csv_file"]
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        r = csv.reader(stream)
        next(r, None)
        with open(pp, "a", encoding="utf-8", newline="") as wf:
            wr = csv.writer(wf)
            for row in r:
                if len(row) >= 14:
                    try:
                        nn = row[3]
                        bb = row[13]
                        pr = row[6]
                        clean_cat = (
                            row[4].replace('["', "").replace('"]', "").split(" >> ")[0]
                        )
                        hh = row[0]
                        k.execute(
                            "INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                nn,
                                bb,
                                pr,
                                clean_cat,
                                "LEGIT",
                                hh,
                                "Warehouse Hub",
                                "Retailer",
                                "Active",
                            ),
                        )
                        wr.writerow(row)
                    except:
                        continue
    else:
        nn = request.form.get("n")
        bb = request.form.get("b")
        pr = request.form.get("pr")
        cat = request.form.get("cat")
        hh = hashlib.sha256((nn + bb + pr).encode()).hexdigest()[:16]
        k.execute(
            "INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nn, bb, pr, cat, "LEGIT", hh, "Warehouse Hub", "Retailer", "Active"),
        )
        with open(pp, "a", encoding="utf-8", newline="") as wf:
            wr = csv.writer(wf)
            wr.writerow(
                [
                    hh,
                    "URL",
                    "URL",
                    nn,
                    cat,
                    "PID",
                    pr,
                    pr,
                    pr,
                    "DESC",
                    "100",
                    "0",
                    "0",
                    bb,
                    "SPEC",
                ]
            )

    c.commit()
    c.close()
    return redirect(url_for("admin"))


@a.route("/decommission/<int:pid>")
def decommission(pid):
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT n, b, pr, cat, sell, cons FROM p WHERE id=%s", (pid,))
    row = k.fetchone()
    if row:
        nn, bb, pr, cat, sell, cons = row
        new_hash = hashlib.sha256(
            (nn + bb + pr + str(random.random())).encode()
        ).hexdigest()[:16]
        k.execute(
            "INSERT INTO p (n, b, pr, cat, s, h, hand, sell, cons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nn, bb, pr, cat, "DECOMMISSIONED", new_hash, "CANCELLED", sell, cons),
        )
        c.commit()
    c.close()
    return redirect(url_for("admin"))


@a.route("/add_u", methods=["POST"])
def add_u():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    u, e, p = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    try:
        k.execute(
            "INSERT INTO users (uname, email, pwd, st) VALUES (%s, %s, %s, %s)",
            (u, e, p, "Approved"),
        )
        c.commit()
    except:
        pass
    c.close()
    return redirect(url_for("admin"))


@a.route("/apv_u/<int:uid>")
def apv_u(uid):
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("UPDATE users SET st='Approved' WHERE id=%s", (uid,))
    c.commit()
    c.close()
    return redirect(url_for("admin"))


@a.route("/del_u/<int:uid>")
def del_u(uid):
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("DELETE FROM users WHERE id=%s", (uid,))
    c.commit()
    c.close()
    return redirect(url_for("admin"))


@a.route("/add_a", methods=["POST"])
def add_a():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    u, e, p = request.form.get("u"), request.form.get("e"), request.form.get("p")
    c = cn()
    k = c.cursor()
    try:
        k.execute(
            "INSERT INTO admins (uname, email, pwd, role) VALUES (%s, %s, %s, %s)",
            (u, e, p, "Sub-Admin"),
        )
        c.commit()
    except:
        pass
    c.close()
    return redirect(url_for("admin"))


@a.route("/del_a/<int:aid>")
def del_a(aid):
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    c = cn()
    k = c.cursor()
    k.execute("SELECT role FROM admins WHERE id=%s", (aid,))
    res = k.fetchone()
    if res and res[0] != "Master":
        k.execute("DELETE FROM admins WHERE id=%s", (aid,))
        c.commit()
    c.close()
    return redirect(url_for("admin"))


@a.route("/req_otp", methods=["POST"])
def req_otp():
    if session.get("role") != "admin":
        return jsonify({"status": "error"})
    e = request.form.get("e")
    otp = str(random.randint(100000, 999999))
    o_d[e] = otp
    print(f"\nSYSTEM OTP GENERATED FOR {e} : {otp}\n")
    return jsonify({"status": "success"})


@a.route("/rst_p", methods=["POST"])
def rst_p():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    e, o, p, t = (
        request.form.get("e"),
        request.form.get("o"),
        request.form.get("p"),
        request.form.get("t"),
    )
    if o_d.get(e) == o:
        c = cn()
        k = c.cursor()
        if t == "user":
            k.execute("UPDATE users SET pwd=%s WHERE email=%s", (p, e))
        else:
            k.execute("UPDATE admins SET pwd=%s WHERE email=%s", (p, e))
        c.commit()
        c.close()
        o_d.pop(e, None)
    return redirect(url_for("admin"))


@a.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    a.run(debug=True)
