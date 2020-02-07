import string
import json
from glob import glob
import random
import logging
from datetime import datetime
import copy
import os

from telegram import ReplyKeyboardRemove, ParseMode,\
    error, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from emoji import emojize
import ephem
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq

from utils import is_cat, get_keyboard, get_user_emo, check_last_letter
from db import db, get_or_create_user, toggle_subscription, get_subscribed
import extended_calculator

game = 1

with open('cities_dict.json', 'r', encoding='utf-8') as f:
    cities = json.load(f)
all_city = copy.deepcopy(cities)

for key, value in cities.items():
    cities[key] = set(value)

for k, v in all_city.items():
    all_city[key] = set(value)


def calc(bot, update, user_data):
    command, *expession = update.message.text.split()
    expession = ''.join(expession)
    result = extended_calculator.calculator(expession)
    update.message.reply_text(result, reply_markup=get_keyboard())


def random_dunkey(bot, update, user_data):
    dunky = random.choice(glob('img/osl*.jpg') + glob('img/osl*.jpeg'))
    inlinekeyboard = [
        [InlineKeyboardButton(emojize(':thumbs_up:'),
                              callback_data='dunkey_good'),
         InlineKeyboardButton(emojize(':thumbs_down:'),
                              callback_data='dunkey_bad')]
    ]

    reply_markup = InlineKeyboardMarkup(inlinekeyboard)

    bot.send_photo(chat_id=update.message.chat.id,
                   photo=open(dunky, 'rb'), reply_markup=reply_markup)


def talk_to_me(bot, update, user_data):
    upc = update.message.chat
    word_from_user = update.message.text
    break_word = ''.join([random.choice(
        ['?', '*', '@', '%', '<', '>', '!', '$']) if index % 2 else
                          value for index, value in enumerate(word_from_user)]
    )

    if len(word_from_user) > 5:
        text = f'{break_word}  <----  \\~.~/\nслишком много букав\
, я еще так молод, чтобы это понять!'

        update.message.reply_text(text, reply_markup=get_keyboard())
    else:
        text = f'Что, что ты({get_user_emo(user_data)}) сказал? \
            Мне показалось или это было:\n{word_from_user}'
        update.message.reply_text(text, reply_markup=get_keyboard())

    logging.info(f'User: {upc.username}, Chat id: {upc.id}, \
        Message:{update.message.text}')


def greet_user(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    upc = update.message.chat
    emo = get_user_emo(user_data)
    user_data['emo'] = emo

    if upc.last_name:
        u_name = f'{upc.first_name} {upc.last_name}'
    else:
        u_name = f'{upc.first_name}'

    text = f'Я бот {emo}, а ты - @{upc.username} , по имени {u_name}'
    update.message.reply_text(text, reply_markup=get_keyboard())
    bot.send_photo(chat_id=upc.id, photo=open('img/hi.jpg', 'rb'))


def planet_naming(bot, update, user_data):
    current_time = datetime.now().strftime('%Y/%m/%d')
    command, planet = update.message.text.split()

    try:
        const = ephem.constellation(getattr(
            ephem, planet.lower().capitalize())(current_time))[1]
    except AttributeError:
        const = 'I do not know that planet'

    update.message.reply_text(const, reply_markup=get_keyboard())


def word_count(bot, update, user_data):
    command, *text = update.message.text.split()
    if not text:
        update.message.reply_text(
            'You were enter anything',
            reply_markup=get_keyboard()
        )
    else:
        len_correct_text = len([1 for word in text if word not in
                                string.punctuation and not word.isdigit()])
        update.message.reply_text(f'{len_correct_text} word(s)',
                                  reply_markup=get_keyboard())


def next_full_moon(bot, update, user_data):
    command, date = update.message.text.split()
    moon = ephem.next_full_moon(date)
    update.message.reply_text(moon, reply_markup=get_keyboard())


def change_avatar(bot, update, user_data):
    if 'emo' in user_data:
        del user_data['emo']
    emo = get_user_emo(user_data)
    update.message.reply_text('Аватар изменен', reply_markup=get_keyboard())


def get_contact(bot, update, user_data):
    print(update.message.contact)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)),
                              reply_markup=get_keyboard())


def get_location(bot, update, user_data):
    print(update.message.location)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)),
                              reply_markup=get_keyboard())


def city_play(bot, update, user_data):
    text = 'Привет, загадывай город!)\nДля выхода из игры отправляй /cancel'
    update.message.reply_text(text, reply_markup=get_keyboard())

    return game


def city_game_end(bot, update, user_data):
    update.message.reply_text('Bye!', reply_markup=get_keyboard())
    return ConversationHandler.END


def city_game(bot, update, user_data):
    text = update.message.text.title().strip()
    user_text_first_letter = text[0]
    user_text_without_bad_ending = check_last_letter(text)

    if not user_data:
        user_data['cities'] = cities
        user_data['all_city'] = all_city
        user_data['check'] = 'stub'

    get_city = user_data['all_city'].get(user_text_first_letter)
    if get_city is None:
        text = f'Не знаю городов на букву {user_text_first_letter}'
        update.message.reply_text(text, reply_markup=get_keyboard())
    elif text not in get_city:
        update.message.reply_text('Я про такой город не слышал.',
                                  reply_markup=get_keyboard())
    elif text not in user_data['cities'][user_text_first_letter]:
        update.message.reply_text('Такой город уже был назван',
                                  reply_markup=get_keyboard())
    elif (user_text_without_bad_ending[0] != user_data['check']
          and user_data['check'] != 'stub'):
        update.message.reply_text('Не дури меня старина:)',
                                  reply_markup=get_keyboard())
    else:
        text_last_letter = user_text_without_bad_ending[-1].upper()
        bot_word = random.sample(user_data['cities'][text_last_letter], 1)[0]
        update.message.reply_text(f'{bot_word}, твой ход старина:)',
                                  reply_markup=get_keyboard())
        bot_word_without_bad_ending = check_last_letter(bot_word)
        user_data['cities'][user_text_without_bad_ending[0]].discard(text)
        user_data['cities'][bot_word_without_bad_ending[0]].discard(bot_word)
        user_data['check'] = bot_word_without_bad_ending[-1].upper()

    return game


def check_user_photo(bot, update, user_data):
    update.message.reply_text('Обрабатываю фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', f'{photo_file.file_id}.jpg')
    photo_file.download(filename)
    update.message.reply_text('Файл сохранен')
    if is_cat(filename):
        update.message.reply_text('Обнаружен шерстяной, добавляю в библиотеку')
        new_filename = os.path.join('img', f'cat_{photo_file.file_id}.jpg')
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text('Шерстяной не обнаружен')


def anketa_start(bot, update, user_data):
    update.message.reply_text('Как вас зовут? Напишите имя и фамилию',
                              reply_markup=ReplyKeyboardRemove())
    return "name"


def anketa_get_name(bot, update, user_data):
    user_name = update.message.text

    if len(user_name.split(' ')) != 2:
        update.message.reply_text('Введите имя и фамилию')
        return 'name'

    user_data['anketa_name'] = user_name
    reply_keyboard = [['1', '2', '3', '4', '5']]

    update.message.reply_text(
        'Понравился ли вам курс? Оцените по шкале от 1 до 5',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )

    return 'rating'


def anketa_rating(bot, update, user_data):
    user_data['anketa_rating'] = update.message.text

    update.message.reply_text("""Оставьте комментарий в свободной форме
    или пропустите этот шаг, введя /skip""")
    return 'comment'


def anketa_comment(bot, update, user_data):
    user_data['anketa_comment'] = update.message.text

    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**user_data)

    update.message.reply_text(user_text,
                              reply_markup=get_keyboard(),
                              parse_mode=ParseMode.HTML)

    return ConversationHandler.END


def anketa_skip_comment(bot, update, user_data):
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}""".format(**user_data)

    update.message.reply_text(user_text,
                              reply_markup=get_keyboard(),
                              parse_mode=ParseMode.HTML)

    return ConversationHandler.END


def anketa_dontknow(bot, update, user_data):
    update.message.reply_text('Я не понимаю')


def subscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text(
        "Вы подписались, наберите /unsubscribe чтобы отписаться")


@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribed(db):
        try:
            bot.sendMessage(chat_id=user['chat_id'], text='yo-yo-yo!')
        except error.BadRequest:
            print(f'Chat {user["chat_id"]} not found')


def unsubscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text(
            "Вы не подписаны, наберите /subscribe чтобы подписаться")


def set_alarm(bot, update, args, job_queue):
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except(IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")


@mq.queuedmessage
def alarm(bot, job):
    bot.sendMessage(chat_id=job.context, text='Сработал будильник')


def inline_button_pressed(bot, update):
    query = update.callback_query

    if query.data in ['dunkey_good', 'dunkey_bad']:
        text = ('Рад, что вам понравилось :-)' if
                query.data == 'dunkey_good' else ':-(')

    bot.edit_message_caption(caption=text, chat_id=query.message.chat.id,
                             message_id=query.message.message_id)
