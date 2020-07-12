import config
from vedis import Vedis


# Запрашиваем из базы статус пользователя
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id].decode()
        except KeyError:  # Если такого ключа/пользователя в базе не оказалось
            return "-1"   # Значение по умолчанию-начало диалога


# Сохраняем текущий статус пользователя в базу
def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            print('Проблемка с юзером!')
            return False


def set_long(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id + 1] = value
            return True
        except:
            print('Проблемка с юзером!')
            return False


def get_long(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id + 1].decode()
        except KeyError:  # Если такого ключа/пользователя в базе не оказалось
            return "-1"   # Значение по умолчанию-начало диалога


def set_freq(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id + 2] = value
            return True
        except:
            print('Проблемка с юзером!')
            return False


def get_freq(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id + 2].decode()
        except KeyError:  # Если такого ключа/пользователя в базе не оказалось
            return "-1"   # Значение по умолчанию-начало диалога