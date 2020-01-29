
import string
import json
from glob import glob
import random
from datetime import datetime
import copy
import logging
import ephem
import os

from utils import *
from telegram.ext import Updater, CommandHandler,RegexHandler, MessageHandler, Filters, ConversationHandler
import extended_calculator

GAME = 1

with open('cities_dict.json', 'r', encoding='utf-8') as f:
    CITIES = json.load(f) 
ALL_CITY = copy.deepcopy(CITIES)

for k, v in CITIES.items():
    CITIES[k] = set(v)

for k, v in ALL_CITY.items():
    ALL_CITY[k] = set(v)


def calc(bot, update, user_data):
	command, *expession = update.message.text.split()
	expession = ''.join(expession)
	result = extended_calculator.calculator(expession)
	update.message.reply_text(result, reply_markup=get_keyboard())


def random_dunkey(bot, update, user_data):
    dunky = random.choice(glob('img/osl*.jpg') + glob('img/osl*.jpeg'))
    bot.send_photo(chat_id=update.message.chat.id, photo=open(dunky, 'rb'))
    

def talk_to_me(bot, update, user_data):
    upc = update.message.chat
    word_from_user = update.message.text
    break_word = ''.join([random.choice(['?','*','@', '%', '<', '>', '!', '$']) if i%2 else v for i,v in enumerate(word_from_user)])

    if len(word_from_user) > 5: 
        update.message.reply_text(f'{break_word}  <----  \\~.~/\nслишком много букав, я еще так молод, чтобы это понять!', reply_markup=get_keyboard())
    else:
        update.message.reply_text(f'Что, что ты({get_user_emo(user_data)}) сказал? Мне показалось или это было:\n{word_from_user}', reply_markup=get_keyboard())
    logging.info(f'User: {upc.username}, Chat id: {upc.id}, Message:{update.message.text}')


def greet_user(bot, update, user_data):
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
    command,planet = update.message.text.split()
  
    try:   
        const = ephem.constellation(getattr(ephem, planet.lower().capitalize())(current_time))[1]
    except AttributeError:
        const = 'I do not know that planet'
        
    update.message.reply_text(const, reply_markup=get_keyboard())
    

def word_count(bot, update, user_data):
    command, *text = update.message.text.split()
    if not text:
        update.message.reply_text('You were enter anything', reply_markup=get_keyboard())
    else:
        len_correct_text = len([i for i in text if i not in string.punctuation and not i.isdigit()])
        update.message.reply_text(f'{len_correct_text} word(s)', reply_markup=get_keyboard())      


def next_full_moon(bot, update, user_data):
    command,date = update.message.text.split()
    moon = ephem.next_full_moon(date)
    update.message.reply_text(moon, reply_markup=get_keyboard())


def city_play(bot, update, user_data):
    update.message.reply_text('Привет, загадывай город!)\nДля выхода из игры отправляй /cancel', reply_markup=get_keyboard())

    return GAME


def city_game_end(bot, update, user_data):
    update.message.reply_text('Bye!', reply_markup=get_keyboard())
    return ConversationHandler.END

       
def change_avatar(bot, update, user_data):
    if 'emo' in user_data:
         del user_data['emo']
    emo = get_user_emo(user_data)
    update.message.reply_text('Аватар изменен', reply_markup=get_keyboard())
    

def get_contact(bot, update, user_data):
    print(update.message.contact)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)), reply_markup=get_keyboard())


def get_location(bot, update, user_data):
    print(update.message.location)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)), reply_markup=get_keyboard())


def city_game(bot, update, user_data):
    text = update.message.text.title().strip()
    user_text_first_letter = text[0]
    user_text_without_bad_ending = check_last_letter(text)
    
    if not user_data: 
        user_data['cities'] = CITIES 
        user_data['all_city'] = ALL_CITY
        user_data['check'] = 'stub'
      
    get_city = user_data['all_city'].get(user_text_first_letter)
    if get_city is None:
        update.message.reply_text(f'Не знаю городов на букву {user_text_first_letter}', reply_markup=get_keyboard())
    elif text not in get_city:
        update.message.reply_text('Я про такой город не слышал.', reply_markup=get_keyboard())
    elif text not in user_data['cities'][user_text_first_letter]:
        update.message.reply_text('Такой город уже был назван', reply_markup=get_keyboard())
    elif user_text_without_bad_ending[0] != user_data['check'] and user_data['check'] != 'stub':
        update.message.reply_text('Не дури меня старина:)', reply_markup=get_keyboard())
    else:
        text_last_letter =   user_text_without_bad_ending[-1].upper()
        bot_word = random.sample(user_data['cities'][text_last_letter],1)[0]
        update.message.reply_text(f'{bot_word}, твой ход старина:)', reply_markup=get_keyboard())
        bot_word_without_bad_ending = check_last_letter(bot_word)
        user_data['cities'][user_text_without_bad_ending[0]].discard(text)
        user_data['cities'][bot_word_without_bad_ending[0]].discard(bot_word)
        user_data['check'] = bot_word_without_bad_ending[-1].upper()

    return GAME


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