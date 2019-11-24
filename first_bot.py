from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import random
import settings


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='bot.log'
        ) 



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


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    logging.info('Я проснулся')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    mybot.start_polling()
    mybot.idle()


main()