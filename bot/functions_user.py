# -*- coding:utf-8 -*-
"""User Database Query Functions through SQLAlchemy ORM"""


from typing import Optional, Union

from sqlalchemy.exc import IntegrityError, InvalidRequestError, DataError
from sqlalchemy.orm.exc import UnmappedInstanceError

from app import session
from app.model_user import Settings, User
from bot import msg, cbq, DEFAULT_LANGUAGE
from config import log


def get_lang(lang_code: str = DEFAULT_LANGUAGE) -> str:
    """

    :param lang_code:
    :return:
    """

    log.debug('Process the language code <%s>', lang_code)
    if "-" in lang_code:
        lang_code = lang_code.split("-")[0]

    return lang_code.lower() if lang_code else DEFAULT_LANGUAGE


def message_from(request: Union[msg, cbq]) -> msg:
    """
    Gets message body from message or inline button response
    :param request:
    :return:
    """

    log.debug('Get message from the request')
    if isinstance(request, cbq):
        return request.message
    return request


def user_from(request: Union[msg, cbq]) -> User:
    """
    :param request:
    :return:
    """

    log.debug('Get User from the request')
    message = message_from(request)
    return User(**message.from_user.__dict__)


def user_id_from(request: Union[msg, cbq]) -> Optional[str]:
    """
    Gets user_id from message or inline button response
    :param request: Union[msg, cbq]
    :return: user_id
    """

    log.debug('Get User ID from the request')
    if isinstance(request, msg):
        return request.chat.id
    if isinstance(request, cbq):
        return request.message.chat.id

    log.error("Fatal error while getting user ID")
    return None


def db_user_from(data: Union[cbq, msg, int, str]) -> Optional[User]:
    """
    :param data:
    :return:
    """

    log.debug('Get User ID from the DB')
    if isinstance(data, cbq):
        user_id = data.message.chat.id
    elif isinstance(data, msg):
        user_id = data.chat.id
    elif isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
        user_id = data
    else:
        return None
    return User.query.filter(User.id == user_id).first()


def db_action_object_add(obj: Union[User, Settings]) -> bool:
    """
    Universal function to add an object to DB
    :param obj: object added to DB
    :return: bool
    """

    log.debug('Add new object of type "%s" to DB', type(obj))
    try:
        session.add(obj)
    except (AttributeError, UnmappedInstanceError, IntegrityError) as err:
        log.error(err)
        return False
    else:
        try:
            session.commit()
        except IntegrityError:
            log.error('Failed to add object %s to DB', type(obj))
            session.rollback()
            return False
        else:
            log.debug('New object %s added to DB', type(obj))

    return True


def db_action_attr_set(obj: Union[User, Settings], attribute: str, value) -> bool:
    """
    :param obj:
    :param attribute:
    :param value:
    :return:
    """

    log.debug('Apply the value "%s" to the attribute "%s"', value, attribute)
    setattr(obj, attribute, value)

    try:
        session.commit()
    except (InvalidRequestError, IntegrityError, DataError) as err:
        log.debug(err)
        session.rollback()
        return False

    return True


def db_action_settings_delete(user: User):
    """
    Delete user settings
    :param user:
    :return:
    """

    log.info('Delete settings for user <%s>', user.id)
    session.query(Settings).filter(Settings.user_id == user.id).delete()
    session.commit()
    log.info('Settings of user <%s> deleted successfully', user.id)


def db_action_settings_add_default(user: User):
    """
    Add user default settings
    :param user:
    :return:
    """

    log.info('Add default settings for user <%s>', user.id)
    settings = Settings()
    settings.user_id = user.id
    settings.language = get_lang(user.language_code)
    session.add(settings)
    session.commit()
    log.info('Default settings for user <%s> added to DB', user.id)


def db_combo_settings_reset(user: User) -> Optional[User]:
    """
    Combo action to reset user settings
    :param user:
    :return:
    """

    log.info('Reset settings for user <%s>', user.id)
    db_user = db_user_from(user.id)
    db_action_settings_delete(db_user)
    db_action_settings_add_default(db_user)
    db_action_user_enable(db_user)
    log.info('Settings for user <%s> successfully reset', user.id)
    return User.query.filter(User.id == user.id).first()


def db_action_user_delete_by_uid(uid: int):
    """
    Delete telegram user from the database
    May not work if user invited someone
    :param uid:
    :return:
    """

    log.info("Start deleting a user <%s>", uid)
    user = User.query.filter(User.id == uid).first()
    session.delete(user)
    session.commit()
    log.info("User <%s> removed from DB", uid)


def db_action_user_add(user: User):
    """

    :param user:
    :return:
    """

    db_action_object_add(user)


def db_action_user_update(user: User) -> Optional[User]:
    """
    Updating user data in DB
    :param user: User object with information to be uploaded to DB
    :return: User object with updated information
    """

    log.debug('Updating data for user <%s>', user.id)
    user_from_db = User.query.filter(User.id == user.id).first()
    for key, value in user.__dict__.items():
        if not key.startswith("_"):
            setattr(user_from_db, key, value)
    session.commit()
    log.debug('Data for user <%s> updated successfully', user.id)
    return User.query.filter(User.id == user_from_db.id).first()


def db_action_user_enable(user: User):
    """
    Activate User
    :param user:
    :return:
    """

    log.info('Activate user <%s>', user.id)
    user.is_active = True
    session.commit()
    log.info('User <%s> successfully activated', user.id)


def db_action_user_disable(user: User):
    """
    Deactivate User
    :param user:
    :return:
    """

    log.info('Deactivate user <%s>', user.id)
    user.is_active = False
    session.commit()
    log.info('User <%s> successfully deactivated', user.id)


def db_combo_user_create(user: User) -> Optional[User]:
    """
    Combo action to create a new user in DB
    :param user: User object with information to be uploaded to DB
    :return:
    """

    log.info('Create a bot user with ID <%s>', user.id)
    db_action_user_add(user)
    db_action_settings_add_default(user)
    log.info('User <%s> created', user.id)
    return User.query.filter(User.id == user.id).first()


def db_combo_start_command(request: Union[cbq, msg]) -> Optional[User]:
    """
    :param request:
    :return:
    """

    new_user = user_from(request)

    if db_user_from(request):
        return db_combo_settings_reset(new_user)

    return db_combo_user_create(new_user)


if __name__ == "__main__":
    pass
