import config
import telebot
import dbworker
import requests
import time
from bs4 import BeautifulSoup
from time import sleep
from telebot import types


#  Heroku
import os
from flask import Flask, request
import re
server = Flask(__name__)


# вытаскиваем токен бота из файла с конфигурациями
bot = telebot.TeleBot(config.token)


##### Вспомогательные функции


# парсинг для футбола
def get_links_f():
    url_f = requests.get(config.url_f).text
    football = BeautifulSoup(url_f, 'lxml')


    def get_dirty(soup):
        # получаем ссылку по кнопке главной "купить билеты"

        game_screen = soup.find('div', {'class': 'game-screen tickets-screen'})
        game_screen = game_screen.find(
            'div', {'class': 'row game-screen__top tickets-screen__top'}
        )
        dirty_link = game_screen.find(
            'div', {'class': 'col-xs-12 controls'}
        )
        return str(dirty_link.find('a'))


    def get_link(dirty_link, start, end):
        # из "грязной" версии забираем чистую URL

        i_beg = dirty_link.find(start)
        i_end = dirty_link.rfind(end)
        if i_beg != -1 and i_end != -1:
            return dirty_link[i_beg+len(start):i_end]
        return False


    dirty_link = get_dirty(football)  # returns string
    ticket_link = get_link(dirty_link, config.start_f, config.end_f)
    if 'void(0)' in ticket_link:
        mess = 'Нет билетов'
    else:
        mess = ticket_link

    return mess


# парсинг для хоккея
def get_links_h():
    url_f = requests.get(config.url_h).text
    hockey = BeautifulSoup(url_f, 'lxml')

    def get_dirty(soup):
        game_screen = soup.find('div', {'class': 'layout-wrapper'})
        game_screen = game_screen.find(
            'div', {'class': 'content'}
        )
        tables = game_screen.find(
            'div', {'class': 'innerpage'}
        )

        table = tables.find('table',
                            {'id': 'tickets'})

        return str(table.find('td'))


    def get_link(dirty_link, start, end):
        i_beg = dirty_link.find(start)
        i_end = dirty_link.rfind(end)
        if i_beg != -1 and i_end != -1:
            return dirty_link[i_beg+len(start):i_end]
        return False

    dirty_link = get_dirty(hockey)  # returns string
    ticket_link = get_link(dirty_link, config.start_h, config.end_h)
    if "Мероприятий не запланировано" in ticket_link:
        mess = 'Нет билетов'
    else:
        mess = "Зайдите на сайт http://tickets.hc-avto.ru/"

    return mess


# регулярные обновления без уведомлений
def cmd_update_internal(message):
    state = dbworker.get_current_state(message.chat.id)
    if state != config.States.S_F.value and state != config.States.S_H.value:
        return

    if state == config.States.S_F.value:
        mess = get_links_f()
        img_link = 'http://old.fc-ural.ru/UPLOAD/2015/01/04/oboi2015_(3)_1000_0.jpg'

    elif state == config.States.S_H.value:
        mess = get_links_h()
        img_link = 'http://1723.ru/forums/uploads/post-1-1576389069.jpg'

    if mess != 'Нет билетов':
        bot.send_message(message.chat.id, "ОГО! Билеты!!!")
        bot.send_photo(chat_id=message.chat.id, photo=img_link)
        bot.send_message(message.chat.id, mess)
        return True

    return False


##### Команды


# По команде /start стартуем
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(message.chat.id, "Привет, я помогу отследить билеты в Екатеринбурге. Хотели бы вы получать информацию"
                                      " о появлении билетов автоматически? Напишите, пожалуйста, \"Да\" или \"Нет\".")

    dbworker.set_state(message.chat.id, config.States.S_ST.value)  # делаем смену статуса


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Давайте начнем сначала.\n"
                                      "Используйте команды /info или /commands чтобы вспомнить, что я умею =)")
    dbworker.set_state(message.chat.id, "-1")  # делаем смену статуса на несуществующий
    cmd_start(message)


# По команде /update обновим хоккей или футбол
@bot.message_handler(commands=["update"])
def cmd_update(message):
    state = dbworker.get_current_state(message.chat.id)
    if state != config.States.S_F.value and state != config.States.S_H.value:
        bot.send_message(message.chat.id, 'Нечего обновлять. Выберите, что бы вы хотели отследить после команды /start\n')
        return

    bot.send_message(message.chat.id, "Обновляю...")

    if state == config.States.S_F.value:
        mess = get_links_f()
        img_link = 'http://old.fc-ural.ru/UPLOAD/2015/01/04/oboi2015_(3)_1000_0.jpg'

    elif state == config.States.S_H.value:
        mess = get_links_h()
        img_link = 'http://1723.ru/forums/uploads/post-1-1576389069.jpg'

    if mess != 'Нет билетов':
        bot.send_photo(chat_id=message.chat.id, photo=img_link)
        return True

    bot.send_message(message.chat.id, mess)
    return False


# По команде /info будем выводить то, зачем нужен бот и что он может
@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "Я бот для любителей спорта в Екатеринбурге.\n"
                     "Если вы выберете, что отслеживать, то, я пришлю вам информацию о "
                     "появлении билетов на матчи ФК Урал или ХК Автомобилист соответсвенно.")
    bot.send_message(message.chat.id, "Для вывода всех доступных комманд напишите /commands.\n")


# По команде /commands будем выводить все команды и их объяснение
@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - используется для удаления данных и перезапуска.\n"
                                      "/start - используется для начала диалога.\n"
                                      "/info - используется для получения общей информации о боте\n"
                                      "/update - используется для обновления информации об интересующих вас спортивных ивентах\n"
                                      "/commands - если вы здесь, то вы знаете, зачем эта команда.\n"
                     )


##### Состояния и реакции
# Отслеживать?  -> как долго? -> как часто? -> футбол или хоккей? -> отслеживать футбол
#               ----------------------------->       ^^^^^^       -> отслеживать хоккей


# Старт, ловим ответ да/нет на /start
@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ST.value)
def start_func(message):
    if re.sub(r'[^\w\s]', '', message.text.lower()) == 'да':
        bot.send_message(message.chat.id, "Как долго проверять билеты? Напишите, пожалуйтса, количетсво дней.")
        dbworker.set_state(message.chat.id, config.States.S_LONG.value)
        return
    elif re.sub(r'[^\w\s]', '', message.text.lower()) == 'нет':
        bot.send_message(message.chat.id, 'Хорошо. Отправьте любой смайлик для подтверждения =)')
        dbworker.set_state(message.chat.id, config.States.S_TEAM.value)
        return
    else:
        bot.send_message(message.chat.id, 'Попробуйте еще раз!')


# После ответа на вопрос о продолжительности поиска
@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_LONG.value)
def user_entering_length(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Напоминаю, что нужно ввести целое число дней.")
        return

    # сохраняем в БД long
    dbworker.set_long(message.chat.id, message.text)

    bot.send_message(message.chat.id, "Как часто проверять билеты? Напишите, пожалуйста, количетсво часов.")

    dbworker.set_state(message.chat.id, config.States.S_FREQ.value)  # делаем смену статуса на "как часто"


# После ответа на вопрос о частоте поиска
@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_FREQ.value)
def user_entering_length(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Напоминаю, что нужно ввести целое число часов.")
        return

    # сохраняем в БД freq
    dbworker.set_freq(message.chat.id, message.text)

    bot.send_message(message.chat.id, "Отлично! Отправьте любой смайлик для подтверждения =)")

    dbworker.set_state(message.chat.id, config.States.S_TEAM.value)  # делаем смену статуса на вопрос с выбором команды


# Выбор команды с кнопками
@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_TEAM.value)
def choose_team(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button_f = types.InlineKeyboardButton(text="ФК Урал", callback_data="f")
    callback_button_h = types.InlineKeyboardButton(text="ХК Автомобилист", callback_data="h")
    keyboard.add(callback_button_f)
    keyboard.add(callback_button_h)
    bot.send_message(message.chat.id, "Вы хотите сходить на матч ФК Урал или ХК Автомобилист?",
                     reply_markup=keyboard)


# реакция на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == 'f':
            dbworker.set_state(call.message.chat.id, config.States.S_F.value)
            img_link = 'http://old.fc-ural.ru/UPLOAD/2013/03/26/ural-rotor-014_1000_0.jpg'
        elif call.data == 'h':
            dbworker.set_state(call.message.chat.id, config.States.S_H.value)
            img_link = 'https://s00.yaplakal.com/pics/pics_original/6/1/0/9566016.jpg'
        else:
            return

    # чтобы кнопки пропали делаем edit_message =)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Вы хотите сходить на матч ФК Урал или ХК Автомобилист?")
    bot.send_message(call.message.chat.id, "Отлично, я запомню")
    bot.send_photo(chat_id=call.message.chat.id, photo=img_link)
    bot.send_message(call.message.chat.id, "Поверим билеты прямо сейчас!")
    is_end = cmd_update(call.message)

    # получаем из БД long и freq
    how_long = int(dbworker.get_long(call.message.chat.id))
    how_freq = int(dbworker.get_freq(call.message.chat.id))

    if how_long > 0 and how_freq > 0:
        bot.send_message(call.message.chat.id, "Отлично! Теперь я буду проверять кажды(й/e) " + str(how_freq) \
                         + " час/часа/часов " + str(how_long) + " день/дня/дней. ")

        first_start = time.time()
        start = time.time()
        while start - first_start < how_long * 24 * 3600 and not is_end:
            start = time.time()
            while time.time() < start + 60 * how_freq:
                pass
            is_end = cmd_update_internal(call.message)


# "Старт" с любого символа
@bot.message_handler(content_types=["text"])
def send_to_start(message):
    if dbworker.get_current_state(message.chat.id) == config.States.S_ST.value:
        bot.send_message(message.chat.id, "Отслеживай появление билетов на спортивные мероприятия!\n"
                                        "Напишите /start для начала работы\n"
                                        "Напишите /info для информации о боте")


#################    для запуска через Heroku
@server.route('/' + config.token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    sleep(3)
    bot.set_webhook(url=config.app_link + config.token)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

#################  для локального запуска
#if __name__ == '__main__':
    #bot.infinity_polling()



