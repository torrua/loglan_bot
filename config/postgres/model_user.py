# -*- coding:utf-8 -*-
# pylint: disable=R0903, E1101

"""
Model of user database
"""
from __future__ import annotations
from sqlalchemy import inspect

from loglan_db import db
from loglan_db.model_base import InitBase, DBBase
from config import DEFAULT_LANGUAGE
from typing import Optional

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

    def enable(self):
        self.is_active = True
        db.session.commit()

    def disable(self):
        self.is_active = False
        db.session.commit()


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

    @classmethod
    def get_language(cls, language: str):
        """
        :param language:
        :return:
        """
        if not language:
            return DEFAULT_LANGUAGE.lower()

        return language.split("-")[0].lower() if "-" in language else language.lower()


class User(db.Model, BasicUser, TelegramUser, InitBase, DBBase):
    """
    User model
    """
    __tablename__ = 'users'
    __bind_key__ = 'user_database'
    settings = db.relationship("Settings", uselist=False,
                               back_populates="user", cascade="all, delete-orphan")

    def add_default_settings(self):
        settings = Settings()
        settings.user_id = self.id
        settings.language = self.get_language(self.language_code)
        settings.save()

    @classmethod
    def from_db_by(cls, data) -> Optional[User]:
        from bot import msg, cbq

        if isinstance(data, cbq):
            user_id = data.message.chat.id
        elif isinstance(data, msg):
            user_id = data.chat.id
        elif isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            user_id = data
        else:
            return None

        return User.query.filter(User.id == user_id).first()

    @classmethod
    def create_from(cls, request) -> User:
        from bot import cbq

        if isinstance(request, cbq):
            request = request.message

        fields = inspect(User).all_orm_descriptors.keys()
        data = {k: v for k, v in request.from_user.__dict__.items() if k in fields}
        return User(**data)


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

    def reset(self):
        self.language = self.user.get_language(self.user.language_code)
        self.trigger = ""
        self.user.enable()


if __name__ == "__main__":
    db.create_all(bind="user_database")
