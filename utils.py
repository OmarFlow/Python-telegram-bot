from emoji import emojize
import random
import settings
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(random.choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']
    

def get_keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['Лицезреть ослика', 'Сменить аву'],[contact_button, location_button]], resize_keyboard=True)
    
    return my_keyboard


def check_last_letter(word):
    if word[-1] == 'ы' or word[-1] == 'ь': 
        word = word[:-1]
    return word