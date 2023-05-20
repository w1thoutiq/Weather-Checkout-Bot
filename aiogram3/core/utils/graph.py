from datetime import datetime


from core.utils.simple_func import get_weather
from core.utils.connect_db import AlertGraph, User
from core.utils.session_db import create_session, global_init


def get_city_set():
    city_set = set()
    with create_session() as db:
        city_lst = list(ctt[0].split(', ') for ctt in db.query(User.city).all())
        for ct in city_lst:
            city_set.add(ct[0])
    city_set.remove('')
    return city_set


time_of_dict = {
    '00': AlertGraph.am12,
    '03': AlertGraph.am3,
    '06': AlertGraph.am6,
    '09': AlertGraph.am9,
    '12': AlertGraph.pm12,
    '15': AlertGraph.pm3,
    '18': AlertGraph.pm6,
    '21': AlertGraph.pm9
}


def graph():
    with create_session() as db:
        for ct in get_city_set():
            weather = get_weather(ct, for_graph=True)
            db.query(AlertGraph).where(AlertGraph.city == str(ct)).update(
                {time_of_dict[time]: weather}
            )
            db.commit()


async def temperature_graph():
    with create_session() as db:
        db.query(AlertGraph).delete()
        db.commit()
        for ct in get_city_set():
            db.add(AlertGraph(
                city=ct
            ))
            db.commit()



global_init('DataBase.db')
time = str(datetime.now().hour)
city = get_city_set()
