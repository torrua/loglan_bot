from __future__ import annotations

import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from app.logger import log


def get_data(url: str) -> str | BeautifulSoup:
    """
    This function downloads and parses content of URL site
    :url: address of needed site or directory
    :return: *BeautifulSoup* OR
        *str* with error message if Result is False
    """
    pattern_http = "^http"
    m_l = {
        "start": "Начинаем загрузку данных с сайта",
        "error": "Не удалось получить данные:\n\t>> Адрес:\t%s\n\t>> Ошибка:\t%s",
        "get_site": "Пробуем скачать данные с ресурса",
        "url_check": "Проверяем, являются ли введенные данные адресом веб-страницы",
        "url_correct": "Введен корректный адрес веб-страницы:\t%s",
        "parse": "Пробуем обработать полученные данные",
        "success": "Данные с сайта успешно загружены",
    }

    log.info(m_l["start"])
    log.debug(m_l["url_check"])

    if not re.match(pattern_http, url):
        raise ValueError()

    log.debug(m_l["url_correct"], url)
    log.debug(m_l["get_site"])

    try:
        with urlopen(Request(url=url)) as response:
            log.debug(m_l["parse"])
            soup = BeautifulSoup(response, "lxml")
            log.info(m_l["success"])
            return soup

    except HTTPError as err:
        log.error(m_l["error"], url, err)
        raise err
