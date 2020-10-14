from config.postgres.model_base import BaseAuthor, BaseEvent, \
    BaseKey, BaseSetting, BaseSyllable, BaseType, BaseWordSpell, BaseWordSource
from config.postgres.model_telegram import TelegramWord, TelegramDefinition


class DictionaryBase:
    """Workaround for separating classes and making inheritance selections"""


class Author(DictionaryBase, BaseAuthor):
    __mapper_args__ = {
        'polymorphic_identity': "authors",
    }


class Event(DictionaryBase, BaseEvent):
    pass


class Key(DictionaryBase, BaseKey):
    pass


class Setting(DictionaryBase, BaseSetting):
    pass


class Syllable(DictionaryBase, BaseSyllable):
    pass


class Type(DictionaryBase, BaseType):
    pass


class Definition(DictionaryBase, TelegramDefinition):
    pass


class Word(DictionaryBase, TelegramWord):
    pass


class WordSpell(DictionaryBase, BaseWordSpell):
    pass


class WordSource(BaseWordSource):
    pass
