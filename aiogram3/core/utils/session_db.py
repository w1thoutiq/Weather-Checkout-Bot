import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


# import sqlalchemy
# from data.db_session import SqlAlchemyBase
#
#
# class User(SqlAlchemyBase):
#     __tablename__ = 'user'
#
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=True)
#     is_bot = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     first_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     language_code = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#
#
# def __repr__(self):
#     return '<User %r>' % self.username
#
#
# def add_user(username, first_name, is_bot, language_code, id, db):
#     user = User(username=username, first_name=first_name, is_bot=is_bot, language_code=language_code, id=id)
#     db.add(user)
#     db.commit()




# async with db_session.create_session() as db:
#     db.query(User).filter(User.id == message.from_user.id).one()


#db = db_session.create_session()
    # obj = User()
    # obj.id = message.from_user.id
    # obj.first_name = message.from_user.first_name
    # obj.username = message.from_user.username
    # obj.language_code = message.from_user.language_code
    # obj.is_bot = message.from_user.is_bot
    # db.add(obj)
    # db.close()
    # await message
