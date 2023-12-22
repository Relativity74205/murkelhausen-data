import logging
from datetime import datetime, date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    Session,
    MappedAsDataclass,
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from murkelhausen.config import config

log = logging.getLogger(__name__)


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


class HeartRateDailyStats(Base):
    __tablename__ = "heart_rate_daily"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    measure_date: Mapped[date]
    resting_heart_rate: Mapped[int]
    min_heart_rate: Mapped[int]
    max_heart_rate: Mapped[int]
    last_seven_days_avg_resting_heart_rate: Mapped[int]


class HeartRate(Base):
    __tablename__ = "heart_rate"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    tstamp: Mapped[datetime]
    heart_rate: Mapped[int]


def get_engine():
    user = config.database.username
    password = config.database.password.get_secret_value()
    host = config.database.host
    port = config.database.port
    database = config.database.database
    schema = config.database.database_schema
    connection_string = (
        f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    )
    engine = create_engine(
        connection_string,
        echo=True,
        connect_args={"options": f"-csearch_path={schema}"},
    )

    return engine


def create_tables():
    engine = get_engine()
    # with Session(engine) as session:
    #     session.execute(text("CREATE TABLE data.foo (a int)"))
    #     session.commit()
    Base.metadata.create_all(engine)


def save_objects(objects):
    engine = get_engine()
    with Session(engine) as session:
        session.add_all(objects)
        session.commit()
