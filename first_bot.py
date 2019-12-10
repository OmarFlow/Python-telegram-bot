from handlers import *


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename='bot.log'
        ) 
    
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
