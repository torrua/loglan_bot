from loglan_db.model import Author, Event, \
    Key, Setting, Syllable, Type, WordSpell, WordSource
from config.postgres.model_telegram import TelegramWord, TelegramDefinition
from loglan_db.model import DictionaryBase


class Definition(DictionaryBase, TelegramDefinition):
    """Extended class with bot functions support"""


class Word(DictionaryBase, TelegramWord):
    """Extended class with bot functions support"""
