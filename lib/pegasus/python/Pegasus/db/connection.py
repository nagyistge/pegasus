import logging
import getpass
from sqlalchemy import create_engine, orm, event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from Pegasus import user as users

__all__ = ['connect']

log = logging.getLogger(__name__)

# This turns on foreign keys for SQLite3 connections
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(conn, record):
    if isinstance(conn, SQLite3Connection):
        log.debug("Turning on foreign keys")
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

def connect_to_master_db(user=None):
    "Connect to 'user's master database"

    if user is None:
        user = getpass.getuser()

    u = users.get_user_by_username(user)

    dburi = u.get_master_db_url()

    return connect(dburi)

def connect(dburi, echo=False):
    engine = create_engine(dburi, echo=echo, pool_recycle=True)

    # Create all the tables if they don't exist
    # FIXME This should actually happen in the pegasus-db-admin tool
    from Pegasus.db import schema
    schema.metadata.create_all(engine)

    Session = orm.sessionmaker(bind=engine, autoflush=False, autocommit=False,
                               expire_on_commit=False)

    # TODO Check schema

    return orm.scoped_session(Session)

