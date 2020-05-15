# -*- coding:utf-8 -*-
# pylint: disable=R0903, E1101

"""
Model of user database
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, \
    TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app import db
from app import DEFAULT_LANGUAGE

db.metadata.clear()


class Basic:
    """
    Basic class for all others
    """
    # __abstract__ = True
    created = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    updated = Column(TIMESTAMP, onupdate=func.now())

    def __init__(self, *initial_data, **kwargs):
        """Constructor"""
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self) -> dict:
        return self.__dict__

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items()
                    if not k.startswith("_sa_")})

    def export(self):
        """
        :return:
        """


class BasicUser:
    """
    Basic User data
    """
    rid = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_invited = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)


class TelegramUser:
    """
    Telegram User data
    https://core.telegram.org/bots/api#user
    """
    id = Column(Integer, nullable=False, unique=True)
    is_bot = Column(Boolean, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language_code = Column(String, nullable=True)

    @property
    def info_card(self):
        """
        :return:
        """
        return f"{self.first_name}" \
               f"{f' {self.last_name} ' if self.last_name else ' '}" \
               f"({self.id})" \
               f"{f' @{self.username}' if self.username else ''}"


class User(db.Model, BasicUser, TelegramUser, Basic, ):
    """
    User model
    """
    __tablename__ = 'users'
    __bind_key__ = 'user_database'
    settings = relationship("Settings", uselist=False,
                            back_populates="user", cascade="all, delete-orphan")


class Settings(db.Model, Basic):
    """
    Settings Model
    """
    __tablename__ = 'settings'
    __bind_key__ = 'user_database'

    rid = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    user = relationship("User", back_populates="settings",
                        cascade="all, delete-orphan", single_parent=True)
    language = Column(String, nullable=False, default=DEFAULT_LANGUAGE)
    trigger = Column(String)


if __name__ == "__main__":
    db.create_all(bind="user_database")
