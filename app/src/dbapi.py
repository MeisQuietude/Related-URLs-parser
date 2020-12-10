from logging import getLogger
from os import environ

from sqlalchemy import create_engine, Table, Column, String, Text
from sqlalchemy.engine import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Mapper, Query
from sqlalchemy.orm.state import InstanceState

Logger = getLogger(__name__)

__db_data = {
    "user": environ.get("POSTGRES_USER"),
    "password": environ.get("POSTGRES_PASSWORD"),
    "database": environ.get("POSTGRES_DB"),
    "host": environ.get("POSTGRES_HOST", "db"),
    "port": environ.get("POSTGRES_PORT", 5432)
}

db = create_engine(
    f"postgresql+psycopg2://"
    f"{__db_data['user']}:{__db_data['password']}"
    f"@{__db_data['host']}:{__db_data['port']}"
    f"/{__db_data['database']}"
)
Base = declarative_base()


class ModelAdvanced(object):
    __table__: Table
    __tablename__: str


class ModelURL(Base, ModelAdvanced):
    __tablename__ = "url"

    name = Column(String, primary_key=True)
    title = Column(String)
    html = Column(Text)

    @staticmethod
    def upsert(**values):
        """
        TODO: change to Insert object with on_conflict_do_update
        """
        query: Query = session.query(ModelURL) \
            .filter(values['name'] == ModelURL.name)

        for record in query:
            del values['name']
            query.update(values)

            break
        else:
            session.add(ModelURL(**values))


@listens_for(ModelURL, "after_insert")
def url_after_insert_hook(
    mapper: Mapper, connect: Connection, target: InstanceState
):
    Logger.debug(f"DB - 'url' inserted: {target.name}")


@listens_for(ModelURL, "after_update")
def url_after_insert_hook(
    mapper: Mapper, connect: Connection, target: InstanceState
):
    Logger.debug(f"DB - 'url' updated: {target.name}")


ModelURL.__table__.create(bind=db, checkfirst=True)

session: Session = sessionmaker(db)()
