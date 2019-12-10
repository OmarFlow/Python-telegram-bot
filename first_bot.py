import logging
import random
import string
import json
from glob import glob
import random
from datetime import datetime
import copy

from emoji import emojize
import ephem
from telegram.ext import Updater, CommandHandler,RegexHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings
import extended_calculator

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='bot.log'
        ) 

with open('cities_dict.json', 'r', encoding='utf-8') as f:
    CITIES = json.load(f) 
ALL_CITY = copy.deepcopy(CITIES)

for k, v in CITIES.items():
    CITIES[k] = set(v)

for k, v in ALL_CITY.items():
    ALL_CITY[k] = set(v)

GAME = 1

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


def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(random.choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']


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


def check_last_letter(word):
    if word[-1] == 'ы' or word[-1] == 'ь': 
        word = word[:-1]
    return word
        
        
def change_avatar(bot, update, user_data):
    if 'emo' in user_data:
         del user_data['emo']
    emo = get_user_emo(user_data)
    update.message.reply_text('Аватар изменен', reply_markup=get_keyboard())
    

def get_contact(bot, update, user_data):
    print(update.message.contact)
    update.message.reply_text('Спасибо {}'.format(get_user_emo(user_data)), reply_markup=get_keyboard())


def get_keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['Лицезреть ослика', 'Сменить аву'],[contact_button, location_button]], resize_keyboard=True)
    
    return my_keyboard


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
    
    
def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    logging.info('Я проснулся')

    dp = mybot.dispatcher
    
    conv_hendler = ConversationHandler(
    	entry_points=[CommandHandler('city_play', city_play, pass_user_data=True)],

    	states={
    		GAME: [MessageHandler(Filters.text, city_game, pass_user_data=True)]
    	},
    	fallbacks=[CommandHandler('cancel', city_game_end, pass_user_data=True)]
    	)
    
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(conv_hendler)
    dp.add_handler(CommandHandler('dunkey', random_dunkey, pass_user_data=True))
    dp.add_handler(CommandHandler('planet',planet_naming, pass_user_data=True))
    dp.add_handler(CommandHandler('wordcount', word_count, pass_user_data=True))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon, pass_user_data=True))
    dp.add_handler(CommandHandler('calc', calc, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Лицезреть ослика)$', random_dunkey, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Сменить аву)$', change_avatar, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True))
    
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
