# -*- coding:utf-8 -*-
"""
SettingSchema module
"""

from loglan_core import Setting

from app.api.schemas import ma


class SettingSchema(ma.SQLAlchemyAutoSchema):  # pylint: disable=too-many-ancestors
    class Meta:
        model = Setting
        exclude = ("created", "updated")


setting_schema_nested = SettingSchema(only=Setting.attributes_basic())
setting_schema_full = SettingSchema(only=Setting.attributes_extended())

blue_print_export = (Setting, setting_schema_nested, setting_schema_full)
