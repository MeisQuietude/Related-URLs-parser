import logging
import typing

import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm
import sqlalchemy.orm.decl_api


logger = logging.getLogger(__name__)


def build_postgresql_engine_url(
    host: str,
    port: int,
    database: str,
    username: typing.Optional[str] = None,
    password: typing.Optional[str] = None,
) -> str:
    if username and password:
        return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    return f"postgresql+psycopg2://{host}:{port}/{database}"


DbTableBase = sqlalchemy.orm.declarative_base()


class DbTableSite(DbTableBase):
    __tablename__ = "site"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    scheme = sqlalchemy.Column(sqlalchemy.String)
    hostname = sqlalchemy.Column(sqlalchemy.String, unique=True)
    port = sqlalchemy.Column(sqlalchemy.Integer)
    ref_pages = sqlalchemy.orm.relationship("DbTablePage", back_populates="ref_site")


class DbTablePage(DbTableBase):
    __tablename__ = "page"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    url_path = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    html = sqlalchemy.Column(sqlalchemy.Text)
    ref_site_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('site.id'))
    ref_site = sqlalchemy.orm.relationship('DbTableSite', back_populates="ref_pages")


class DatabaseApiClient:
    __tables__ = (DbTableSite, DbTablePage)

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
    ) -> None:
        engine_url = build_postgresql_engine_url(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
        )
        self._engine = sqlalchemy.create_engine(url=engine_url, future=True)

        self._create_tables()
        self._register_events()

        self.session: sqlalchemy.orm.Session = sqlalchemy.orm.sessionmaker(self._engine)()

    def _create_tables(self) -> None:
        for table in self.__tables__:
            table.__table__.create(bind=self._engine, checkfirst=True)

    def _register_events(self) -> None:
        for table in self.__tables__:
            @sqlalchemy.event.listens_for(table, "after_insert")
            def _(
                mapper: sqlalchemy.orm.Mapper,
                connect: sqlalchemy.engine.Connection,
                target: sqlalchemy.orm.InstanceState
            ):
                logger.debug(f"'{table.__tablename__}': the row inserted: {str(target.id)}")

            @sqlalchemy.event.listens_for(table, "after_update")
            def _(
                mapper: sqlalchemy.orm.Mapper,
                connect: sqlalchemy.engine.Connection,
                target: sqlalchemy.orm.InstanceState
            ):
                logger.debug(f"'{table.__tablename__}': the row updated: {str(target.id)}")
