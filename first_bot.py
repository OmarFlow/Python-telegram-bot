from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import random
import string
from datetime import datetime
import settings
import ephem
import extended_calculator


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='bot.log'
        ) 

GAME = 1


def calc(bot, update):
	command, *expession = update.message.text.split()
	expession = ''.join(expession)
	result = extended_calculator.calculator(expession)
	update.message.reply_text(result)


def talk_to_me(bot, update):
    upc = update.message.chat
    word_from_user = update.message.text
    break_word = ''.join([random.choice(['?','*','@', '%', '<', '>', '!', '$']) if i%2 else v for i,v in enumerate(word_from_user)])

    if len(word_from_user) > 5: 
        update.message.reply_text(f'{break_word}  <----  \\~.~/\nслишком много букав, я еще так молод, чтобы это понять!')
    else:
        update.message.reply_text(f'Что, что ты сказал? Мне показалось или это было:\n{word_from_user}')
    logging.info(f'User: {upc.username}, Chat id: {upc.id}, Message:{update.message.text}')


def greet_user(bot, update):
    upc = update.message.chat

    if upc.last_name:
        u_name = f'{upc.first_name} {upc.last_name}'
    else:
        u_name = f'{upc.first_name}'

    text = f'Я бот, а ты - @{upc.username} , по имени {u_name}'

    update.message.reply_text(text)
    bot.send_photo(chat_id=upc.id, photo=open('img/hi.jpg', 'rb'))


def planet_naming(bot, update):
    current_time = datetime.now().strftime('%Y/%m/%d')
    command,planet = update.message.text.split()
  
    try:   
        const = ephem.constellation(getattr(ephem, planet.lower().capitalize())(current_time))[1]
    except AttributeError:
        const = 'I do not know that planet'
        
    update.message.reply_text(const)
    

def word_count(bot, update):
    command, *text = update.message.text.split()
    if not text:
        update.message.reply_text('You were enter anything')
    else:
        len_correct_text = len([i for i in text if i not in string.punctuation and not i.isdigit()])
        update.message.reply_text(f'{len_correct_text} word(s)')      


def next_full_moon(bot, update):
    command,date = update.message.text.split()
    x = ephem.next_full_moon(date)
    update.message.reply_text(x)


def city_play(bot, update):
    update.message.reply_text('Привет! Ты в игре\n Чтобы выйти отправляй /cancel')

    return GAME


def city_game_end(bot, update):
	pass

def city_game(bot, update):
	t = update.message.text
	# with open('cities.json', 'r', encoding='utf-8') as city:
	# 	cities = json.load(city)
	#print(cities)
	# user_text = update.message.text    
	# any()
	update.message.reply_text(t)
	


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    logging.info('Я проснулся')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet',planet_naming))
    dp.add_handler(CommandHandler('wordcount', word_count))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    dp.add_handler(CommandHandler('calc', calc))

    conv_hendler = ConversationHandler(
    	entry_points=[CommandHandler('city_play', city_play)],

    	states={
    		GAME: [MessageHandler(Filters.text, city_game)]
    	},
    	fallbacks=[CommandHandler('cancel', city_game_end)]
    	)

    dp.add_handler(conv_hendler)
    
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()