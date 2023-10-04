import os
from distutils.util import strtobool

from flask import request, Blueprint, Response, json
from loglan_core.addons.key_selector import KeySelector
from loglan_core.addons.word_selector import WordSelector
from sqlalchemy import select

from app.api.schemas.author import blue_print_export as bp_author
from app.api.schemas.definition import blue_print_export as bp_definition
from app.api.schemas.event import blue_print_export as bp_event
from app.api.schemas.key import blue_print_export as bp_key
from app.api.schemas.setting import blue_print_export as bp_setting
from app.api.schemas.syllable import blue_print_export as bp_syllable
from app.api.schemas.type import blue_print_export as bp_type
from app.api.schemas.word import blue_print_export as bp_word
from app.engine import Session

API_PATH = os.getenv("API_PATH", "/api")
API_VERSION = os.getenv("API_VERSION", "/v1")


def universal_get(session, schema_full, schema_nested, model, many: bool = True):
    """
    Return entity from DB through GET request
    :param session:
    :param schema_full:
    :param schema_nested:
    :param model:
    :param many:
    :return:
    """
    args = {**request.args}

    detailed = bool(strtobool(args.pop("detailed", "False")))
    statement, skipped_args = get_statement(model, args)

    result = session.execute(statement)
    model_entities = result.scalars().all() if many else [result.scalar()]

    count = len(model_entities)
    schema = schema_full if detailed else schema_nested
    data = schema.dump(model_entities, many=many)

    return Response(
        mimetype="application/json",
        response=json.dumps(
            {
                "result": True,
                "data": data,
                "count": count,
                "skipped_arguments": skipped_args,
            }
        ),
        status=200,
    )


def get_statement(model, args):
    event_id = args.pop("event_id", None)
    case_sensitive = bool(strtobool(args.pop("case_sensitive", "False")))
    model_args, skipped_args = separate_arguments(model, args)
    statement = filter_statement_by_event_id(model, event_id)

    if model_args:
        for attr, value in model_args.items():
            if str(value).isdigit():
                value = int(value)
                statement = statement.filter(getattr(model, attr) == value)
                continue

            value = value.replace("*", "%")
            name_attr = getattr(model, attr)
            name_filter = (
                name_attr.like(value) if case_sensitive else name_attr.ilike(value)
            )

            statement = statement.filter(name_filter)

    return statement, skipped_args


def filter_statement_by_event_id(model, event_id):
    api_section = request.path.strip("/").split("/")[-1]
    if event_id:
        if api_section == "words":
            return WordSelector().by_event(event_id=int(event_id))
        if api_section == "keys":
            return KeySelector().by_event(event_id=int(event_id))
    return select(model)


def separate_arguments(model, args):
    skipped_args = {}
    model_args = {}
    for parameter, value in args.items():
        if parameter in model.attributes_all():
            model_args[parameter] = value
        else:
            skipped_args[parameter] = value
    return model_args, skipped_args


def get_api_properties(entity):
    entity_name = entity.__tablename__.lower().removesuffix("s")
    section_name = f"/{entity_name}s"
    api_name = f"{entity_name}_api"
    blueprint = Blueprint(api_name, __name__)
    data = (blueprint, section_name)
    return blueprint, data


def create_blueprint_data(session, entity, schema_nested, schema_full):
    api_blueprint, api_data = get_api_properties(entity)

    @api_blueprint.route("/", methods=["GET"])
    def entity_get():
        """
        Get Entity by Entity's parameters Function
        """
        with session:
            return universal_get(session, schema_full, schema_nested, entity)

    return api_data


dictionary_bp_data = [
    bp_author,
    bp_definition,
    bp_event,
    bp_key,
    bp_setting,
    bp_syllable,
    bp_type,
    bp_word,
]

with Session() as app_session:
    dictionary_api_data = [
        create_blueprint_data(app_session, *data) for data in dictionary_bp_data
    ]

blueprints = [
    {"blueprint": api[0], "url_prefix": f"{API_PATH}{API_VERSION}{api[1]}"}
    for api in dictionary_api_data
]
