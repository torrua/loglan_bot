# -*- coding: utf-8 -*-
# pylint: disable = E1101

"""
Working with a database
"""

from typing import List
from app.models import Word, Key, Definition, t_connect_keys


def word_by_name(name: str) -> List[Word]:
    """
    Получаем все объекты Word, у которых атрибут Word.name соответствует переменной.
    :param name: Искомое значение объекта Word.name
    :return: Список объектов Word
    """
    return Word.query.filter(Word.name.in_([name, name.lower(), name.upper()])).all()


def key_by_name(name: str) -> Key:
    """
    Получаем все объекты Key, у которых атрибут Key.word соответствует переменной.
    :param name: Искомое значение объекта Key.word
    :return: Объект Key
    """
    return Key.query.filter(Key.word.in_([name, name.lower(), name.upper()])).first()


def definitions_by_key(key: str) -> List[Definition]:
    """
    Получаем все объекты Definitions с ключом key.
    :param key: Строка с ключом
    :return: Список объектов Definitions
    """
    key = key_by_name(key)

    return key.definitions if key else key


def loglan_words_by_key(key: str) -> dict:
    """
    Получаем список всех слов на логлане, являющихся определениями искомого слова.
    :param key: Строка с искомым словом
    :return: Словарь, в котором ключ - слово на логлане,
             а значение - список с определениями слова.
    """

    words = Word.query.join(Definition).join(t_connect_keys, Key) \
        .filter(Key.word.in_([key, key.lower(), key.upper()])).order_by(Word.name).all()
    result = {}

    for word in words:
        result[word.name] = []
        for definition in word.definitions:
            keys = [key.word for key in definition.keys]
            if key in keys or key.lower() in keys or key.upper() in keys:
                result[word.name].append(definition.convert_for_telegram())

    return result


def translation_by_key(key: str) -> str:
    """
    Получаем информацию о словах на логлне по ключу иностранного (английского) языка.
    :param key: Строка с искомым словом
    :return: Строка с результатами поиска, адаптированная для выдачи в Телеграм
    """
    result = loglan_words_by_key(key)

    message = "\n".join(["/" + word_name + ",\n" + "\n".join(definitions)
                         + "\n" for word_name, definitions in result.items()]).strip()
    return message


if __name__ == "__main__":
    pass
