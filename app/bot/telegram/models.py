# -*- coding: utf-8 -*-
"""Model of LOD database for Telegram"""

from collections import defaultdict

from loglan_core.addons.definition_selector import DefinitionSelector
from loglan_core.addons.word_selector import WordSelector
from loglan_core import Word, Definition

from app.bot.telegram.keyboards import WordKeyboard


def export(definition: Definition) -> str:
    """
    Convert definition's data to str for sending as a telegram messages
    :return: Adopted for posting in telegram string
    """
    d_usage = (
        f"<b>{definition.usage.replace('%', '—')}</b> " if definition.usage else ""
    )
    d_body = (
        definition.body.replace("<", "&#60;")
        .replace(">", "&#62;")
        .replace("«", "<i>")
        .replace("»", "</i>")
        .replace("{", "<code>")
        .replace("}", "</code>")
        .replace("....", "….")
        .replace("...", "…")
        .replace("--", "—")
    )

    d_case_tags = f" [{definition.case_tags}]" if definition.case_tags else ""
    return f"{d_usage}{definition.grammar} {d_body}{d_case_tags}"


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

    def export_as_str(self) -> str:
        """
        Convert word's data to str for sending as a telegram messages
        :return: List of str with technical info, definitions, used_in part
        """
        w_affixes = self.format_affixes()
        w_match = self.match + " " if self.match else ""
        w_year = self.format_year()
        w_orig = self.format_origin()
        w_authors = self.format_authors()
        w_type = self.type.type_ + " "
        w_rank = self.format_rank()

        word_str = (
            f"<b>{self.name}</b>{w_affixes},"
            f"\n{w_match}{w_type}{w_authors}{w_year}{w_rank}{w_orig}"
        )
        definitions = "\n\n".join([export(d) for d in self.definitions])
        return f"{word_str}\n\n{definitions}"

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
            DefinitionSelector()
            .by_key(key=request, language=language)
            .all(session=session)
        )

        for definition in definitions:
            result[definition.source_word.name].append(export(definition))

        new = "\n"
        word_items = [
            f"/{word_name},\n{new.join(definitions)}\n"
            for word_name, definitions in result.items()
        ]
        return new.join(word_items).strip()

    async def send_card_to_user(self, bot, user_id: int | str):
        """
        :param bot:
        :param user_id:
        :return:
        """
        await bot.send_message(
            chat_id=user_id,
            text=self.export_as_str(),
            reply_markup=WordKeyboard(self).keyboard_cpx(),
        )
