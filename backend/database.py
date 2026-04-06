import psycopg2


def cn():
    return psycopg2.connect(
        host="127.0.0.1",
        dbname="s_chain",
        user="postgres",
        password="India@#123",
        port="5432",
    )


def it():
    c = cn()
    k = c.cursor()
    k.execute("DROP TABLE IF EXISTS p;")
    k.execute("DROP TABLE IF EXISTS users;")
    k.execute("DROP TABLE IF EXISTS admins;")
    k.execute(
        "CREATE TABLE p (id SERIAL PRIMARY KEY, n TEXT, b TEXT, pr TEXT, cat TEXT, s TEXT, h TEXT, hand TEXT, sell TEXT, cons TEXT);"
    )
    k.execute(
        "CREATE TABLE users (id SERIAL PRIMARY KEY, uname TEXT UNIQUE, email TEXT UNIQUE, pwd TEXT, st TEXT);"
    )
    k.execute(
        "CREATE TABLE admins (id SERIAL PRIMARY KEY, uname TEXT UNIQUE, email TEXT UNIQUE, pwd TEXT, role TEXT);"
    )
    k.execute(
        "INSERT INTO admins (uname, email, pwd, role) VALUES ('admin', 'master@sys.com', 'admin123', 'Master');"
    )
    c.commit()
    c.close()


if __name__ == "__main__":
    it()
