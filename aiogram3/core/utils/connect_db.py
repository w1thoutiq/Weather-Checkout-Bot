import sqlalchemy
from core.utils.session_db import SqlAlchemyBase


class User(SqlAlchemyBase):

    def __int__(self, id: int, username: str, cities: str, status: bool):
        self.id = id
        self.username = username
        self.city = cities
        self.active = status

    __tablename__ = 'base'

    username = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=True
    )
    id = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False,
        primary_key=True,
        unique=True
    )
    city = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=True
    )
    active = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False
    )


class Alert(SqlAlchemyBase):

    def __int__(self, id: int, username: str, city: str):
        self.id = id
        self.username = username
        self.city = city

    __tablename__ = 'alerts_base'

    id = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False,
        primary_key=True,
        unique=True
    )
    username = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=True
    )
    city = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=True
    )


class AlertGraph(SqlAlchemyBase):
    def __int__(
            self,
            city: str,
            am12: int,
            am3: int,
            am6: int,
            am9: int,
            pm12: int,
            pm3: int,
            pm6: int,
            pm9: int
    ):
        self.city = city
        self.am12 = am12
        self.am3 = am3
        self.am6 = am6
        self.am9 = am9
        self.pm12 = pm12
        self.pm3 = pm3
        self.pm6 = pm6
        self.pm9 = pm9

    __tablename__ = 'temperature_graph'

    city = sqlalchemy.Column(
        sqlalchemy.TEXT,
        nullable=False,
        unique=True,
        primary_key=True
    )
    am12 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    am3 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    am6 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    am9 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    pm12 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    pm3 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    pm6 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    pm9 = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)


def __repr__(self):
    return '<User %r>' % self.username
