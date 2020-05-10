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


class Author(BaseFunctions, db.Model):
    """
    Author model
    """
    __Tablename__ = t_name_authors

    AID = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(256), unique=True, nullable=False)
    full_name = db.Column(db.String(256))
    notes = db.Column(db.String(256))

    def export_as_string(self):
        """
        Prepare Author data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.abbreviation}@{self.full_name}@{self.notes}"


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

    def export_as_string(self):
        """
        Prepare Event data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.EID}@{self.name}" \
               f"@{self.date.strftime('%m/%d/%Y')}@{self.definition}" \
               f"@{self.annotation}@{self.suffix}"


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

    def export_as_string(self):
        """
        Prepare Settings data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.date.strftime('%d.%m.%Y %H:%M:%S')}@{self.db_version}@{self.last_word_id}"


class Syllable(BaseFunctions, db.Model):
    """
    Syllable model
    """
    __Tablename__ = t_name_syllables

    SYID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)

    def export_as_string(self):
        """
        Prepare Syllable data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.name}"


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

    def export_as_string(self):
        """
        Prepare Type data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.type}@{self.type_x}@{self.group}@{self.parentable}"


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

    def convert_for_telegram(self) -> str:
        """
        Convert definition's data to str for sending as a telegram messages
        :return: Adopted for posting in telegram string
        """
        d_usage = f"<b>{self.usage.replace('%', '—')}</b> " if self.usage else ""
        d_grammar = f"({self.slots if self.slots is not None else ''}{self.grammar_code}) "
        d_body = self.body \
            .replace('<', '&#60;').replace('>', '&#62;')\
            .replace('«', '<i>').replace('»', '</i>') \
            .replace('≤', '<code>').replace('≥', '</code>')

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"

    def export_as_string(self):
        """
        Prepare Definition data for exporting to text file
        :return: Formatted basic string
        """
        return f"{self.word.WID_old}@{self.position}@{self.usage}" \
               f"@{self.slots if self.slots else ''}" \
               f"{self.grammar_code if self.grammar_code else ''}" \
               f"@{self.body}@@{self.case_tags}"


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

    def export_as_string(self):
        """
        Prepare Word data for exporting to text file
        :return: Formatted basic string
        """
        notes = self.notes if self.notes else {}

        w_affixes = self.get_afx()
        affixes = ' '.join(sorted([afx.name for afx in w_affixes])) if w_affixes else ""

        w_match = self.match
        match = w_match if w_match else ""

        w_source = self.authors.all()
        # print(self) if not self.authors.all() else None
        source = '/'.join(sorted([auth.abbreviation for auth in w_source]))\
            if len(w_source) > 1 else w_source[0].abbreviation
        source = source + (" "+notes["author"] if notes.get("author", False) else "")

        year = str(self.year.year) + (" "+notes["year"] if notes.get("year", False) else "")

        rank = self.rank + (" "+notes["rank"] if notes.get("rank", False) else "")

        w_usedin = self.get_cpx()
        usedin = ' | '.join(sorted([cpx.name for cpx in w_usedin])) if w_usedin else ""

        w_tid_old = self.TID_old
        tid_old = w_tid_old if self.TID_old else ""

        return f"{self.WID_old}@{self.type.type}@{self.type.type_x}@{affixes}" \
               f"@{match}@{source}@{year}@{rank}" \
               f"@{self.origin}@{self.origin_x}@{usedin}@{tid_old}"

    def export_spell_as_string(self):
        """
        Prepare Word Spell data for exporting to text file
        :return: Formatted basic string
        """
        code_name = "".join(["0" if symbol.isupper() else "5" for symbol in self.name])

        return f"{self.WID_old}@{self.name}@{self.name.lower()}@{code_name}" \
               f"@{self.event_start_id}@{self.event_end_id if self.event_end else 9999}@"

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

    def get_telegram_card(self) -> List[str]:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """
        def split_list(a_list):
            half = len(a_list) // 2
            return [a_list[:half], a_list[half:]]

        # Word
        list_of_afx = ["" + w.name for w in self.get_afx()]
        w_affixes = f" ({' '.join(list_of_afx)})" if list_of_afx else ""
        w_match = self.match + " " if self.match else ""
        w_year = "'" + str(self.year.year)[-2:] + " "
        w_origin_x = " = " + self.origin_x if self.origin_x else ""
        w_orig = "\n<i>&#60;" + self.origin + w_origin_x + "&#62;</i>" \
            if self.origin or w_origin_x else ""
        w_authors = '/'.join([a.abbreviation for a in self.authors]) + " "
        w_type = self.type.type + " "
        w_rank = self.rank + " " if self.rank else ""
        word_str = f"<b>{self.name}</b>{w_affixes}," \
            f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"

        # Definitions
        definitions_str = "\n\n".join([d.convert_for_telegram() for d in self.definitions])

        # Used in
        list_of_all_cpx = ["/" + w.name for w in self.get_cpx()]

        # Divide the list if the text does not place in one message
        split_cpx = split_list(list_of_all_cpx) if \
            len("; ".join(list_of_all_cpx)) > 3900 else [list_of_all_cpx, ]

        used_in_str = ["\n\nUsed in: " + "; ".join(list_cpx)
                       if list_cpx else "" for list_cpx in split_cpx]

        # Combine
        result = [word_str, definitions_str, *used_in_str]
        return [element for element in result if element]


class WordSpell:
    __Tablename__ = t_name_word_spells
    pass


class XWord:
    __Tablename__ = t_name_x_words
    pass


if __name__ == "__main__":
    db.create_all()
