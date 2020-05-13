# -*- coding: utf-8 -*-
"""
Model of LOD postgresql database
"""

from __future__ import annotations
from typing import List
from sqlalchemy.orm import backref
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
    db.Column('AID', db.ForeignKey('author.AID'), primary_key=True),
    db.Column('WID', db.ForeignKey('word.WID'), primary_key=True), )

t_connect_words = db.Table(
    'connect_words', db.metadata,
    db.Column('parent_id', db.ForeignKey('word.WID'), primary_key=True),
    db.Column('child_id', db.ForeignKey('word.WID'), primary_key=True), )


t_connect_keys = db.Table(
    'connect_keys', db.metadata,
    db.Column('KID', db.ForeignKey('key.KID'), primary_key=True),
    db.Column('DID', db.ForeignKey('definition.DID'), primary_key=True), )


class BaseFunctions:
    """
    Base class for common methods
    """

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __init__(self, dictionary: dict):
        self.__dict__.update(dictionary)

    def export(self):
        """Export object data"""
        pass


class Author(BaseFunctions, db.Model):
    """
    Author model
    """
    __Tablename__ = t_name_authors

    AID = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(256), unique=True, nullable=False)
    full_name = db.Column(db.String(256))
    notes = db.Column(db.String(256))


class Event(BaseFunctions, db.Model):
    """
    Event model
    """
    __Tablename__ = t_name_events
    EID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    annotation = db.Column(db.Text, nullable=False)
    suffix = db.Column(db.Text, nullable=False)


class Key(BaseFunctions, db.Model):
    """
    Key model
    """
    __Tablename__ = t_name_keys
    KID = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(256), unique=True, nullable=False)
    language = db.Column(db.String(256))


class Setting(BaseFunctions, db.Model):
    """
    Setting model
    """
    __Tablename__ = t_name_settings

    SID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True)
    db_version = db.Column(db.Integer, nullable=False)
    last_word_id = db.Column(db.Integer, nullable=False)


class Syllable(BaseFunctions, db.Model):
    """
    Syllable model
    """
    __Tablename__ = t_name_syllables

    SYID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)


class Type(BaseFunctions, db.Model):
    """
    Type model
    """
    __Tablename__ = t_name_types

    TID = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    type_x = db.Column(db.Text, nullable=False)
    group = db.Column(db.Text)
    parentable = db.Column(db.Boolean, nullable=False)


class Definition(BaseFunctions, db.Model):
    """
    Definition model
    """
    __Tablename__ = t_name_definitions

    DID = db.Column(db.Integer, primary_key=True)
    WID = db.Column(db.Integer, db.ForeignKey('word.WID'), nullable=False)
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

    word = db.relationship("Word")

    def add_key(self, key: Key) -> bool:
        """

        :param key:
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

    WID = db.Column(db.Integer, primary_key=True)
    WID_old = db.Column(db.Integer, nullable=False)  # Compatibility with the previous database
    name = db.Column(db.String(64), nullable=False)
    origin = db.Column(db.String(256))
    origin_x = db.Column(db.String(256))

    type_id = db.Column("type", db.ForeignKey('type.TID'), nullable=False)
    type = db.relationship(Type.__name__,
                           backref=backref("words", uselist=False))

    event_start_id = db.Column("event_start", db.ForeignKey("event.EID"), nullable=False)
    event_start = db.relationship("Event", foreign_keys=[event_start_id])

    event_end_id = db.Column("event_end", db.ForeignKey("event.EID"))
    event_end = db.relationship("Event", foreign_keys=[event_end_id])

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
        primaryjoin=(t_connect_words.c.parent_id == WID),
        secondaryjoin=(t_connect_words.c.child_id == WID),
        backref=db.backref('parents_id', lazy='dynamic'),
        lazy='dynamic')

    def __is_parented(self, child: Word) -> bool:
        """
        Check, if this word is already added as a parent for this 'child'
        :param child: Word object
        :return: bool
        """
        return self.__derivatives.filter(t_connect_words.c.child_id == child.WID).count() > 0

    def add_child(self, child: Word) -> str:
        """
        Add derivative for the source word.
        Get words from Used In and add relationship in database.
        :param child: Word object
        :return: None
        """
        if not self.__is_parented(child):
            self.__derivatives.append(child)
        return child.name

    def add_author(self, author: Author) -> str:
        """
        Connect Author object with Word object.
        :param author: Author object
        :return:
        """
        if not self.authors.filter(Author.abbreviation == author.abbreviation).count() > 0:
            self.authors.append(author)
        return author.abbreviation

    def get_definitions(self) -> List[Definition]:
        """
        Get all definitions of the word.
        :return: List of Definition objects ordered by Definition.position
        """
        return Definition.query.filter(Definition.WID == self.WID)\
            .order_by(Definition.position.asc()).all()

    def get_parents(self) -> List[Word]:
        """
        Get all parents of the Complex predicates, Little words or Affixes.
        :return: List of Word objects.
        """
        return self.parents_id.all()  # if self.type in self.__parentable else []

    def get_derivatives(self,
                        word_type: str = None,
                        word_type_x: str = None,
                        word_group: str = None) -> List[Word]:
        """
        Get all derivatives of the word, depending on its parameters.
        :param word_type:
        :param word_type_x:
        :param word_group:
        :return:
        """
        result = self.__derivatives.filter(self.WID == t_connect_words.c.parent_id)

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
        Get all the complexes that exist for this word.
        :return: list of Word objects.
        """
        return self.get_derivatives(word_group="Cpx")

    def get_afx(self) -> List[Word]:
        """
        Get all the affixes that exist for this word.
        Only primitives have affixes.
        :return: list of Word objects.
        """
        return self.get_derivatives(word_type="Afx")

    @property
    def complexes(self):
        return self.get_cpx()

    @property
    def affixes(self):
        return self.get_afx()

    @property
    def parents(self):
        return self.get_parents()


class WordSpell(BaseFunctions):
    __Tablename__ = t_name_word_spells


class XWord(BaseFunctions):
    __Tablename__ = t_name_x_words


if __name__ == "__main__":
    db.create_all()
