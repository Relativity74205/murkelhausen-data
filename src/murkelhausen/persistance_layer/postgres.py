import logging
from datetime import datetime, date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    Session,
    MappedAsDataclass,
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
)

from murkelhausen.config import config

log = logging.getLogger(__name__)


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


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
    Base.metadata.create_all(engine)


def save_objects(objects):
    engine = get_engine()
    with Session(engine) as session:
        session.add_all(objects)
        session.commit()
