from datetime import datetime


from core.utils.simple_func import get_weather
from core.utils.connect_db import AlertGraph, User
from core.utils.session_db import create_session

time = str(datetime.now().hour)
city = set()

time_of_dict = {
    '00': AlertGraph.am12,
    '03': AlertGraph.am3,
    '06': AlertGraph.am6,
    '9': AlertGraph.am9,
    '12': AlertGraph.pm12,
    '15': AlertGraph.pm3,
    '18': AlertGraph.pm6,
    '21': AlertGraph.pm9
}


# print(time_of_dict[time])
# print(time_dict.values(),'|', time_dict.keys())
# print(time_dict['pm12'])


async def graph():
    global city, time
    with create_session() as db:
        for ct in city:
            db.query(AlertGraph).where(AlertGraph.city == str(ct)).update(
                {time_of_dict[time]: get_weather(ct, for_graph=True)}
            )


async def temperature_graph():
    global city
    with create_session() as db:
        db.query(AlertGraph).delete()
        city_from_base = [city[0].split(', ') for city in db.query(User.city).all()]
        for i in city_from_base:
            for x in i:
                city.add(x)
        city.remove('')
        for ct in city:
            db.add(AlertGraph(
                city=ct
            ))
                # db.query(AlertGraph).where(AlertGraph.city == str(ct)).update(
                #     {})
        db.commit()
