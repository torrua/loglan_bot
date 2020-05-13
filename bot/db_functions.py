# -*- coding: utf-8 -*-
# pylint: disable = E1101

"""
Working with a database
"""

from typing import List
from bot import DEFAULT_LANGUAGE, Key, t_connect_keys
from bot.model_dictionary_telegram import TelegramWord as Word, \
    TelegramDefinition as Definition


def word_by_name(request: str) -> List[Word]:
    """
    Get all Word objects for which the 'name' attribute matches the request
    :param request: Requested string
    :return: List of Words
    """
    return Word.query.filter(Word.name.in_([request, request.lower(), request.upper()])).all()


def key_by_name(request: str) -> Key:
    """
    Get a Key object for which the 'word' attribute matches the request
    :param request: Requested string
    :return: Key object
    """
    return Key.query.filter(Key.word.in_([request, request.lower(), request.upper()])).first()


def definitions_by_key(request: str) -> List[Definition]:
    """
    Get all Definitions containing the request as a key.
    :param request: Requested string
    :return: Список объектов Definitions
    """
    request = key_by_name(request)

    return request.definitions if request else request


def loglan_cards_by_key(request: str, language: str = DEFAULT_LANGUAGE) -> dict:
    """
    Get a dictionary of all the loglan words matching the user request
    :param request: Requested string
    :param language: Key language
    :return: A dictionary where the loglan word is the key,
        and the value is a list with definitions prepared for Telegram
    """

    words = Word.query.join(Definition).join(t_connect_keys, Key) \
        .filter(Key.word.in_([request, request.lower(), request.upper()]))\
        .filter(Key.language == language).order_by(Word.name).all()

    result = {}

    for word in words:
        result[word.name] = []
        for definition in word.get_definitions():
            keys = [key.word for key in definition.keys]
            if request in keys or request.lower() in keys or request.upper() in keys:
                result[word.name].append(definition.export())

    return result


def translation_by_key(request: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    We get information about loglan words by key in a foreign language
    :param request: Requested string
    :param language: Key language
    :return: Search results string formatted for sending to Telegram
    """
    result = loglan_cards_by_key(request, language)
    new = '\n'
    message = new.join([f"/{word_name},{new}{new.join(definitions)}{new}"
                        for word_name, definitions in result.items()]).strip()
    return message


if __name__ == "__main__":
    pass
