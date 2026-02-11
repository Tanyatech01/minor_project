import psycopg2

def cn():
    return psycopg2.connect(host="127.0.0.1", dbname="s_chain", user="postgres", password="India@#123", port="5432")

def it():
    c = cn()
    k = c.cursor()
    k.execute("DROP TABLE IF EXISTS p;")
    k.execute("""
        CREATE TABLE p (
            id SERIAL PRIMARY KEY,
            pid TEXT,
            n TEXT,
            b TEXT,
            pr TEXT,
            cat TEXT,
            s TEXT,
            h TEXT,
            pred TEXT,
            hand TEXT,
            sell TEXT,
            cons TEXT
        );
    """)
    c.commit()
    c.close()
    print("Table Ready for Full Supply Chain")

if __name__ == "__main__":
    it()