
from emoji import emojize
import random
import settings
import pprint

from clarifai.rest import ClarifaiApp
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


def is_cat(file_name):
    img_has_cat = False
    app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(response)
    if response['status']['code'] == 10000:
        for concept in response['outputs'][0]['data']['concepts']:
            if concept['name'] == 'cat':
                img_has_cat = True
    return img_has_cat
if __name__ == '__main__':
    print(is_cat('img/osl1.jpg'))