from app.logger import log
import re

from urllib import request, error
from bs4 import BeautifulSoup


def get_data(url: str, parser: str = "lxml", headers: dict = None) -> dict[str, bool | str | BeautifulSoup]:
    """
    This function downloads and parses content of URL site
    :url: address of needed site or directory
    :return: dict with elements:
             > :"result":  *bool* with result of downloading process
             > :"content": *BeautifulSoup* with elements if Result is True
                            OR
                           *str* with error message if Result is False
    """
    cntnt, rslt, msg = "content", "result", "message"
    pattern_http = "^http"
    m_l = {
        "start": "Начинаем загрузку данных с сайта",
        "error": "Не удалось получить данные:\n\t>> Адрес:\t%s\n\t>> Ошибка:\t%s",
        "get_site": "Пробуем скачать данные с ресурса",
        "url_check": "Проверяем, являются ли введенные данные адресом веб-страницы",
        "url_correct": "Введен корректный адрес веб-страницы:\t%s",
        "path_check": "Проверяем, являются ли введенные данные адресом файла \n\t>> Адрес:\t%s",
        "parse": "Пробуем обработать полученные данные",
        "agent": "Содержиимое строки headers:\n\t>>\t%s",
        "success": "Данные с сайта успешно загружены"
    }

    log.info(m_l["start"])
    log.debug(m_l["url_check"])

    if re.match(pattern_http, url):
        log.debug(m_l["url_correct"], url)
        try:
            log.debug(m_l["get_site"])
            request_to_site = request.Request(url=url, headers=headers if headers else {})
            response = request.urlopen(request_to_site)
        except (error.URLError, error.HTTPError) as err:
            log.error(m_l["error"], url, err)
            log.error(m_l["agent"], headers)
            return {rslt: False, cntnt: str(err), msg: 5152}

        try:
            log.debug(m_l["parse"])
            site_data = BeautifulSoup(response, parser)
        except error.HTTPError as err:
            log.error(m_l["error"], *(url, err))
            return {rslt: False, cntnt: str(err), msg: 5152}
    else:

        log.debug(m_l["path_check"], url)
        try:
            log.debug(m_l["get_site"])
            site_data = BeautifulSoup(open(url), parser)
        except (FileNotFoundError, UnicodeDecodeError) as err:
            log.error(m_l["error"], *(url, err))
            return {rslt: False, cntnt: str(err), msg: 5152}

    log.info(m_l["success"])
    return {rslt: True, cntnt: site_data, msg: None}
