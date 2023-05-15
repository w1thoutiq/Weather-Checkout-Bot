import sqlite3

con = sqlite3.connect('DataBase.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS base(
    username TEXT,
    id BIGINT unique,
    city TEXT,
    active BOOLEAN
    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS alerts_base(
    id BIGINT unique,
    username TEXT,
    city TEXT
    )""")

con.commit()
