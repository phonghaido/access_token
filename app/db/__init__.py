import config
from typing import Annotated

from fastapi import Depends

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base

ENGINE = None

def get_session() -> Session:
    global ENGINE
    connect_args = {}
    if ENGINE is None:
        ENGINE = create_engine(
            config.POSTGRES_DATABASE_CONNECTION,
            pool_recycle=3600,
            pool_timeout=10,
            connect_args=connect_args
        )
        Base.metadata.create_all(ENGINE)

    return sessionmaker(
        bind=ENGINE,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )()

def generate_session() -> Session:
    with get_session() as session:
        yield session
        session.close()

CurrentSession = Annotated[Session, Depends(generate_session)]