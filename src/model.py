# coding: utf-8
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import flask.ext.login as flask_login
from swing import config

engine = create_engine(config.DB_CONNECTION)
MapBase = declarative_base(bind = engine)
RawSession = sessionmaker(bind = engine, expire_on_commit=False)
ScopedSession = scoped_session(RawSession)

@contextmanager
def db_session(scoped=True, commit=True):
    """Provide a *thread-safe* transactional scope around a series of operations."""
    session = ScopedSession() if scoped else RawSession()
    try:
        yield session
        if commit:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        # detach all instances in this session
        # and release connection
        session.close()

class User(MapBase,flask_login.UserMixin):

    __tablename__ = "user"
    email = Column(String(64), primary_key=True, nullable=False)
    pwd = Column(String(256), nullable=False)
    nickname = Column(String(128), nullable=False)

    def get_id(self):
        return self.email

def create_tables():
    MapBase.metadata.create_all(engine)

create_tables() 
