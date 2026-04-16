import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def cn():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        host="127.0.0.1", 
        dbname="s_chain", 
        user="postgres", 
        password="2118", 
        port="5757"
    )

def it():
    c = cn()
    k = c.cursor()
    k.execute(
        "CREATE TABLE IF NOT EXISTS p (id SERIAL PRIMARY KEY, n TEXT, b TEXT, pr TEXT, cat TEXT, s TEXT, h TEXT, hand TEXT, sell TEXT, cons TEXT);"
    )
    k.execute(
        "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, uname TEXT UNIQUE, email TEXT UNIQUE, pwd TEXT, st TEXT);"
    )
    k.execute(
        "CREATE TABLE IF NOT EXISTS admins (id SERIAL PRIMARY KEY, uname TEXT UNIQUE, email TEXT UNIQUE, pwd TEXT, role TEXT);"
    )
    k.execute(
        "INSERT INTO admins (uname, email, pwd, role) VALUES ('admin', 'master@sys.com', 'admin123', 'Master') ON CONFLICT (uname) DO NOTHING;"
    )
    c.commit()
    c.close()

if __name__ == "__main__":
    it()