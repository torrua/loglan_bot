# -*- coding: utf-8 -*-
"""
Models of LOD database
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Set

from app import db

# pylint: disable=R0903, E1101, C0103

db.metadata.clear()

t_name_authors = "authors"
t_name_events = "events"
t_name_keys = "keys"
t_name_settings = "settings"
t_name_syllables = "syllables"
t_name_types = "types"
t_name_words = "words"
t_name_definitions = "definitions"
t_name_x_words = "x_words"
t_name_word_spells = "word_spells"


t_connect_authors = db.Table(
    'connect_authors', db.metadata,
    db.Column('AID', db.ForeignKey('author.id'), primary_key=True),
    db.Column('WID', db.ForeignKey('word.id'), primary_key=True), )

t_connect_words = db.Table(
    'connect_words', db.metadata,
    db.Column('parent_id', db.ForeignKey('word.id'), primary_key=True),
    db.Column('child_id', db.ForeignKey('word.id'), primary_key=True), )


t_connect_keys = db.Table(
    'connect_keys', db.metadata,
    db.Column('KID', db.ForeignKey('key.id'), primary_key=True),
    db.Column('DID', db.ForeignKey('definition.id'), primary_key=True), )


class BaseFunctions:
    """
    Base class for common methods
    """

    created = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    updated = db.Column(db.TIMESTAMP, onupdate=db.func.now())

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __init__(self, dictionary: dict):
        self.__dict__.update(dictionary)

    def save(self):
        """
        Add record to DB
        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """
        Update record in DB
        :param data:
        :return:
        """
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        """
        Delete record from DB
        :return:
        """
        db.session.delete(self)
        db.session.commit()

    def export(self):
        """
        Export record data from DB
        Should be redefine in model's class
        :return:
        """

    @classmethod
    def get_all(cls) -> list:
        """
        Get all model objects from DB
        :return:
        """
        return cls.query.all()

    @classmethod
    def non_foreign_keys(cls) -> Set[str]:
        """
        :return:
        """
        return {column.name for column in cls.__table__.columns
                if not (column.foreign_keys or column.name.startswith("_"))}

    @classmethod
    def relationships(cls) -> Set[str]:
        """
        :return:
        """
        return {key for key in cls.__mapper__.relationships.keys() if not key.startswith("_")}

    @classmethod
    def all_attributes(cls) -> Set[str]:
        """
        :return:
        """
        return {key for key in cls.__mapper__.attrs.keys() if not key.startswith("_")}

    @classmethod
    def foreign_keys(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.all_attributes() - cls.relationships() - cls.non_foreign_keys())

    @classmethod
    def attributes_basic(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.all_attributes() - cls.relationships())

    @classmethod
    def attributes_extended(cls) -> Set[str]:
        """
        :return:
        """
        return set(cls.all_attributes() - cls.foreign_keys())


class Author(BaseFunctions, db.Model):
    """
    Author model
    """
    __Tablename__ = t_name_authors

    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(256), unique=True, nullable=False)
    full_name = db.Column(db.String(256))
    notes = db.Column(db.String(256))


class Event(BaseFunctions, db.Model):
    """
    Event model
    """
    __Tablename__ = t_name_events
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    annotation = db.Column(db.Text, nullable=False)
    suffix = db.Column(db.Text, nullable=False)


class Key(BaseFunctions, db.Model):
    """
    Key model
    """
    __Tablename__ = t_name_keys
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(256), unique=True, nullable=False)
    language = db.Column(db.String(256))


class Setting(BaseFunctions, db.Model):
    """
    Setting model
    """
    __Tablename__ = t_name_settings

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=True)
    db_version = db.Column(db.Integer, nullable=False)
    last_word_id = db.Column(db.Integer, nullable=False)


class Syllable(BaseFunctions, db.Model):
    """
    Syllable model
    """
    __Tablename__ = t_name_syllables

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)


class Type(BaseFunctions, db.Model):
    """
    Type model
    """
    __Tablename__ = t_name_types

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    type_x = db.Column(db.Text, nullable=False)
    group = db.Column(db.Text)
    parentable = db.Column(db.Boolean, nullable=False)


class Definition(BaseFunctions, db.Model):
    """
    Definition model
    """
    __Tablename__ = t_name_definitions

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    usage = db.Column(db.Text)
    grammar_code = db.Column(db.Text)
    slots = db.Column(db.Integer)
    case_tags = db.Column(db.Text)
    body = db.Column(db.Text, nullable=False)
    language = db.Column(db.Text)
    notes = db.Column(db.Text)

    keys = db.relationship(Key.__name__, secondary=t_connect_keys,
                           backref="definitions", lazy='dynamic')

    def add_key(self, key: Key) -> bool:
        """
        Connect Key object with Definition object
        :param key: Key object
        :return:
        """

        if key and not self.keys.filter(Key.word == key.word).count() > 0:
            self.keys.append(key)
            return True
        return False


class Word(BaseFunctions, db.Model):
    """
    Word model
    """
    __Tablename__ = t_name_words

    id = db.Column(db.Integer, primary_key=True)
    id_old = db.Column(db.Integer, nullable=False)  # Compatibility with the previous database
    name = db.Column(db.String(64), nullable=False)
    origin = db.Column(db.String(256))
    origin_x = db.Column(db.String(256))

    type_id = db.Column("type", db.ForeignKey('type.id'), nullable=False)
    type = db.relationship(Type.__name__, backref="words")

    event_start_id = db.Column("event_start", db.ForeignKey("event.id"), nullable=False)
    event_start = db.relationship(
        "Event", foreign_keys=[event_start_id], backref="appeared_words")

    event_end_id = db.Column("event_end", db.ForeignKey("event.id"))
    event_end = db.relationship(
        "Event", foreign_keys=[event_end_id], backref="deprecated_words")

    match = db.Column(db.Text)
    rank = db.Column(db.Text)
    year = db.Column(db.Date)
    notes = db.Column(db.JSON)
    TID_old = db.Column(db.Integer)  # references

    authors = db.relationship(Author.__name__,
                              secondary=t_connect_authors,
                              backref="contribution",
                              lazy='dynamic')

    definitions = db.relationship("Definition", backref="source_word", lazy='dynamic')

    # word's derivatives
    __derivatives = db.relationship(
        'Word', secondary=t_connect_words,
        primaryjoin=(t_connect_words.c.parent_id == id),
        secondaryjoin=(t_connect_words.c.child_id == id),
        backref=db.backref('parents', lazy='dynamic'),
        lazy='dynamic')

    def __is_parented(self, child: Word) -> bool:
        """
        Check, if this word is already added as a parent for this 'child'
        :param child: Word object
        :return: bool
        """
        return self.__derivatives.filter(t_connect_words.c.child_id == child.id).count() > 0

    def add_child(self, child: Word) -> str:
        """
        Add derivative for the source word
        Get words from Used In and add relationship in database
        :param child: Word object
        :return: None
        """
        if not self.__is_parented(child):
            self.__derivatives.append(child)
        return child.name

    def add_author(self, author: Author) -> str:
        """
        Connect Author object with Word object
        :param author: Author object
        :return:
        """
        if not self.authors.filter(Author.abbreviation == author.abbreviation).count() > 0:
            self.authors.append(author)
        return author.abbreviation

    def get_definitions(self) -> List[Definition]:
        """
        Get all definitions of the word
        :return: List of Definition objects ordered by Definition.position
        """
        return Definition.query.filter(Definition.id == self.id)\
            .order_by(Definition.position.asc()).all()

    def get_parents(self) -> List[Word]:
        """
        Get all parents of the Complex predicates, Little words or Affixes
        :return: List of Word objects
        """
        return self.parents.all()  # if self.type in self.__parentable else []

    def get_derivatives(self,
                        word_type: str = None,
                        word_type_x: str = None,
                        word_group: str = None) -> List[Word]:
        """
        Get all derivatives of the word, depending on its parameters
        :param word_type:
        :param word_type_x:
        :param word_group:
        :return:
        """
        result = self.__derivatives.filter(self.id == t_connect_words.c.parent_id)

        if word_type or word_type_x or word_group:
            result = result.join(Type)

        if word_type:
            result = result.filter(Type.type == word_type)
        if word_type_x:
            result = result.filter(Type.type_x == word_type_x)
        if word_group:
            result = result.filter(Type.group == word_group)

        return result.order_by(Word.name.asc()).all()

    def get_cpx(self) -> List[Word]:
        """
        Get all the complexes that exist for this word
        Only primitives have affixes
        :return: list of Word objects
        """
        return self.get_derivatives(word_group="Cpx")

    def get_afx(self) -> List[Word]:
        """
        Get all the affixes that exist for this word
        Only primitives have affixes
        :return: list of Word objects
        """
        return self.get_derivatives(word_type="Afx")

    @property
    def complexes(self) -> List[Word]:
        """
        Get list of word's complexes if exist
        :return:
        """
        return self.get_cpx()

    @property
    def affixes(self) -> List[Word]:
        """
        Get list of word's affixes if exist
        :return:
        """
        return self.get_afx()


class WordSpell(BaseFunctions):
    """WordSpell model"""
    __Tablename__ = t_name_word_spells


class XWord(BaseFunctions):
    """XWord model"""
    __Tablename__ = t_name_x_words


if __name__ == "__main__":
    db.create_all()
