# -*- coding:utf-8 -*-
# pylint: disable=R0903, E1101

"""
Model of user database
"""

from config.postgres import db
from config.postgres.common_base import InitBase, DBBase
from config import DEFAULT_LANGUAGE

db.metadata.clear()


class BasicUser:
    """
    Basic User data
    """
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_invited = db.Column(db.Boolean, default=True, nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)


class TelegramUser:
    """
    Telegram User data
    https://core.telegram.org/bots/api#user
    """
    id = db.Column(db.Integer, nullable=False, unique=True)
    is_bot = db.Column(db.Boolean, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=True)
    username = db.Column(db.String, nullable=True)
    language_code = db.Column(db.String, nullable=True)

    @property
    def info_card(self):
        """
        :return:
        """
        return f"{self.first_name}" \
               f"{f' {self.last_name} ' if self.last_name else ' '}" \
               f"({self.id})" \
               f"{f' @{self.username}' if self.username else ''}"


class User(db.Model, BasicUser, TelegramUser, InitBase, DBBase):
    """
    User model
    """
    __tablename__ = 'users'
    __bind_key__ = 'user_database'
    settings = db.relationship("Settings", uselist=False,
                               back_populates="user", cascade="all, delete-orphan")


class Settings(db.Model, InitBase, DBBase):
    """
    Settings Model
    """
    __tablename__ = 'settings'
    __bind_key__ = 'user_database'

    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship("User", back_populates="settings",
                           cascade="all, delete-orphan", single_parent=True)
    language = db.Column(db.String, nullable=False, default=DEFAULT_LANGUAGE)
    trigger = db.Column(db.String)


if __name__ == "__main__":
    db.create_all(bind="user_database")
