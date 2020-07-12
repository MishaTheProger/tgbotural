from enum import Enum

# bot API-token
token = '1023965872:AAGAcMDI54KetdmbLOC7ch8KRhmrNA1iRno'
# Для запуска через Heroku ссылка на приложение
app_link = 'https://glacial-anchorage-14641.herokuapp.com/'

# название БД
db_file = "my_db.vdb"

# ссылка и строки для парсинга футбола
url_f = 'http://fc-ural.ru/bilety/bilety/'
start_f = 'href="'
end_f = '" target='

# ссылка и строки для парсинга хоккея
url_h = 'http://tickets.hc-avto.ru/'
start_h = "<td"
end_h = "</td>"



class States(Enum):
    """
    в БД Vedis хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_ST =   "0"  # Новый диалог
    S_LONG = "3"  # Как долго обновлять?
    S_FREQ = "4"  # Как часто обновлять?
    S_TEAM = "5"  # Выбор команды
    S_F =    "1"  # Футбол
    S_H =    "2"  # Хоккей