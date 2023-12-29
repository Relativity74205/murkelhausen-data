import logging
from datetime import datetime, date
from typing import Iterable

from pydantic import BaseModel
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
        echo=False,  # TODO make configurable in config
        connect_args={"options": f"-csearch_path={schema}"},
    )

    return engine


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)


def save_objects(objects: Iterable[Base], upsert: bool = True):
    # TODO: replace with ID check, that is: compare timestamps in objects with timestamps in database; https://stackoverflow.com/a/26018934
    engine = get_engine()
    with Session(engine) as session:
        if upsert:
            for o in objects:
                session.merge(o)
        else:
            session.add_all(objects)
        session.commit()
