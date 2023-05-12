# from datetime import datetime as dt
# from aiogram.dispatcher.filters import BoundFilter
# from database import cur, con
# time = dt.now().strftime("%H:%M")


# class CorrectTime(BoundFilter):
#     async def check(self, message):
#         # cur.execute(f"""INSERT INTO alerts_base(id, username, main_city, alerts) VALUES (790528433, 'w1thoutiq', 'Рязань', '06:00')""")
#         # con.commit()
#         cur.execute('SELECT id,alerts FROM alerts_base')
#         alerts = list((i[0], i[1].split(' ')) for i in cur.fetchall())
#         time = []
#         [time.extend(i[1]) for i in alerts]
#         # temp = list(alerts.extend(alert[0].split(' ')) for alert in cur.fetchall())
#         print(alerts)
#         print(time)
#         return True

