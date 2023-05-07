import sqlite3

con = sqlite3.connect('DataBase.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS base(
    username TEXT,
    id BIGINT unique,
    city TEXT,
    active BOOLEAN
    )""")

con.commit()
