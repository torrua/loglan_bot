# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from collections import defaultdict

from loglan_core.addons.definition_selector import DefinitionSelector
from loglan_core.addons.word_selector import WordSelector
from loglan_core import Word, Definition

from app.bot.telegram.keyboards import WordKeyboard


class TelegramDefinition(Definition):
    """Definition class extensions for Telegram"""

    def export(self):
        """
        Convert definition's data to str for sending as a telegram messages
        :return: Adopted for posting in telegram string
        """
        d_usage = f"<b>{self.usage.replace('%', '—')}</b> " if self.usage else ""
        d_grammar = (
            f"({self.slots if self.slots is not None else ''}{self.grammar_code}) "
        )
        d_body = (
            self.body.replace("<", "&#60;")
            .replace(">", "&#62;")
            .replace("«", "<i>")
            .replace("»", "</i>")
            .replace("{", "<code>")
            .replace("}", "</code>")
            .replace("....", "….")
            .replace("...", "…")
        )

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"


class TelegramWord(Word):
    """Word class extensions for Telegram"""

    def format_affixes(self):
        return (
            f" ({' '.join([w.name for w in self.affixes]).strip()})"
            if self.affixes
            else ""
        )

    def format_year(self):
        return "'" + str(self.year.year)[-2:] + " " if self.year else ""

    def format_origin(self):
        if self.origin or self.origin_x:
            return (
                f"\n<i>&#60;{self.origin}"
                f"{' = ' + self.origin_x if self.origin_x else ''}&#62;</i>"
            )
        return ""

    def format_authors(self):
        return (
            "/".join([a.abbreviation for a in self.authors]) + " "
            if self.authors
            else ""
        )

    def format_rank(self):
        return self.rank + " " if self.rank else ""

    def export_as_str(self, session) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """
        w_affixes = self.format_affixes()
        w_match = self.match + " " if self.match else ""
        w_year = self.format_year()
        w_orig = self.format_origin()
        w_authors = self.format_authors()
        w_type = self.type.type + " "
        w_rank = self.format_rank()

        word_str = (
            f"<b>{self.name}</b>{w_affixes},"
            f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"
        )
        return f"{word_str}\n\n{self.get_definitions(session=session)}"

    def get_definitions(self, session) -> str:
        """
        Get all definitions of the word
        :param session: Session
        :return: List of Definition objects ordered by position
        """

        definitions = (
            DefinitionSelector(class_=TelegramDefinition)
            .filter(TelegramDefinition.word_id == self.id)
            .order_by(TelegramDefinition.position.asc())
            .all(session=session)
        )

        return "\n\n".join([d.export() for d in definitions])

    @classmethod
    def translation_by_key(cls, session, request: str, language: str = None) -> str:
        """
        We get information about loglan words by key in a foreign language
        :param session: Session
        :param request: Requested string
        :param language: Key language
        :return: Search results string formatted for sending to Telegram
        """

        result = defaultdict(list)
        definitions = (
            DefinitionSelector(class_=TelegramDefinition)
            .by_key(key=request, language=language)
            .all(session=session)
        )

        for definition in definitions:
            result[definition.source_word.name].append(definition.export())

        new = "\n"
        word_items = [
            f"/{word_name},\n{new.join(definitions)}\n"
            for word_name, definitions in result.items()
        ]
        return new.join(word_items).strip()

    async def send_card_to_user(self, session, bot, user_id: int | str):
        """
        :param session:
        :param bot:
        :param user_id:
        :return:
        """
        await bot.send_message(
            chat_id=user_id,
            text=self.export_as_str(session),
            reply_markup=WordKeyboard(self).keyboard_cpx(),
        )

    @classmethod
    def by_request(cls, session, request: str) -> list:
        """
        :param session:
        :param request:
        :return:
        """
        if isinstance(request, int):
            return [
                cls.get_by_id(session, request),
            ]
        return WordSelector(TelegramWord).by_name(request).all(session)
