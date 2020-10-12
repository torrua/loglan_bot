from datetime import datetime
from typing import List, Set

from config.postgres import db


class InitBase:
    """
    Init class for common methods
    """

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items() if not str(k).startswith("_")})

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def export(self):
        """
        Export record data from DB
        Should be redefine in model's class
        :return:
        """

    def import_(self):
        """
        Import txt data to DB
        Should be redefine in model's class
        :return:
        """


class DBBase:
    """Common methods and attributes for basic models"""
    created = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    updated = db.Column(db.TIMESTAMP, onupdate=db.func.now())
    __table__ = None
    __mapper__ = None

    def save(self) -> None:
        """
        Add record to DB
        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self, data) -> None:
        """
        Update record in DB
        :param data:
        :return:
        """
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self) -> None:
        """
        Delete record from DB
        :return:
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls) -> List:
        """
        Get all model objects from DB
        :return:
        """
        return cls.query.all()

    @classmethod
    def attributes_all(cls) -> Set[str]:
        """
        :return:
        """
        return {key for key in cls.__mapper__.attrs.keys() if not key.startswith("_")}

    @classmethod
    def attributes_basic(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.attributes_all() - cls.relationships())

    @classmethod
    def attributes_extended(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.attributes_all() - cls.foreign_keys())

    @classmethod
    def relationships(cls) -> Set[str]:
        """
        :return:
        """
        return {key for key in cls.__mapper__.relationships.keys() if not key.startswith("_")}

    @classmethod
    def foreign_keys(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.attributes_all() - cls.relationships() - cls.non_foreign_keys())

    @classmethod
    def non_foreign_keys(cls) -> Set[str]:
        """
        :return:
        """
        return {column.name for column in cls.__table__.columns
                if not (column.foreign_keys or column.name.startswith("_"))}
