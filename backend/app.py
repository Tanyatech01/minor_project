from flask import Flask, render_template
import psycopg2

a = Flask(__name__)

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

@a.route('/')
def home():
    c = cn()
    k = c.cursor()
    k.execute("SELECT * FROM p ORDER BY id DESC LIMIT 50")
    d = k.fetchall()
    c.close()
    return render_template('index.html', data=d)

if __name__ == '__main__':
    a.run(debug=True)