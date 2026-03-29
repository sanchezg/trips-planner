from __future__ import annotations

import factory
from factory.alchemy import SQLAlchemyModelFactory


class SQLAlchemySessionFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"


class UTCDateTimeFactory(factory.Factory):
    class Meta:
        abstract = True
