# -*- coding: utf-8 -*-
from typing import List
from bot import Word, Definition


class TelegramDefinition(Definition):
    def export(self):
        """
        Convert definition's data to str for sending as a telegram messages
        :return: Adopted for posting in telegram string
        """
        d_usage = f"<b>{self.usage.replace('%', '—')}</b> " if self.usage else ""
        d_grammar = f"({self.slots if self.slots is not None else ''}{self.grammar_code}) "
        d_body = self.body \
            .replace('<', '&#60;').replace('>', '&#62;') \
            .replace('«', '<i>').replace('»', '</i>') \
            .replace('≤', '<code>').replace('≥', '</code>')

        d_case_tags = f" [{self.case_tags}]" if self.case_tags else ""
        return f"{d_usage}{d_grammar}{d_body}{d_case_tags}"


class TelegramWord(Word):
    def export(self) -> List[str]:
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

        # Definitions TODO maybe extract from method
        definitions_str = "\n\n".join([d.export() for d in self.get_definitions()])

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

    def get_definitions(self) -> List[TelegramDefinition]:
        """
        Get all definitions of the word.
        :return: List of Definition objects ordered by Definition.position
        """
        return TelegramDefinition.query.filter(TelegramDefinition.WID == self.WID)\
            .order_by(TelegramDefinition.position.asc()).all()
