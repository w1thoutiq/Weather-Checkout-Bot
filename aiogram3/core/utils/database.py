# import sqlite3
#
# con = sqlite3.connect('DataBase.db')
# cur = con.cursor()
#
# cur.execute("""CREATE TABLE IF NOT EXISTS base(
#     username TEXT,
#     id BIGINT unique,
#     city TEXT,
#     active BOOLEAN
#     )""")
#
# cur.execute("""CREATE TABLE IF NOT EXISTS alerts_base(
#     id BIGINT unique,
#     username TEXT,
#     city TEXT
#     )""")
#
# con.commit()
#
#
# async def improve_select(
#         what: str,
#         where: str,
#         query_where: str = None,
#         value_where: [str, int] = None,
#         allble: bool = False
# ):
#     if query_where is None and value_where is None:
#         query = f'SELECT {what} FROM {where}'
#         if allble is False:
#             return cur.execute(query).fetchone()[0]
#         else:
#             return cur.execute(query).fetchall()
#     else:
#         query = f'SELECT {what} FROM {where} WHERE {query_where}={value_where};'
#         if allble is False:
#             return cur.execute(query).fetchone()[0]
#         else:
#             return cur.execute(query).fetchall()
#
#
# async def update_status(user: str, value: [int, bool]):
#     query = f'UPDATE base SET active = {value} WHERE id = {user};'
#     cur.execute(query)
#     return con.commit()
