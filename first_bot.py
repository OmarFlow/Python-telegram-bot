import logging

from telegram.ext import Updater, CommandHandler, RegexHandler,\
     MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.ext import messagequeue as mq

import settings
from handlers import (
    send_updates,
    city_play,
    city_game,
    city_game_end,
    game,
    anketa_start,
    anketa_skip_comment,
    anketa_dontknow,
    anketa_rating,
    anketa_get_name,
    anketa_comment,
    greet_user,
    random_dunkey,
    planet_naming,
    word_count,
    calc,
    next_full_moon,
    subscribe,
    unsubscribe,
    set_alarm,
    change_avatar,
    inline_button_pressed,
    get_contact,
    get_location,
    talk_to_me,
    check_user_photo
)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)

subscribers = set()


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    logging.info('Я проснулся')
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True

    dp = mybot.dispatcher

    mybot.job_queue.run_repeating(send_updates, interval=5)

    conv_city_game = ConversationHandler(
        entry_points=[CommandHandler('city_play',
                                     city_play, pass_user_data=True)],

        states={
            game: [MessageHandler(Filters.text,
                                  city_game, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel',
                                  city_game_end, pass_user_data=True)]
    )

    conv_anketa = ConversationHandler(
        entry_points=[RegexHandler('^(Заполнить анкету)$',
                                   anketa_start, pass_user_data=True)],

        states={
            'name': [MessageHandler(Filters.text,
                                    anketa_get_name, pass_user_data=True)],

            'rating': [RegexHandler('^(1|2|3|4|5)$',
                                    anketa_rating, pass_user_data=True)],

            'comment': [MessageHandler(Filters.text,
                                       anketa_comment, pass_user_data=True),
                        CommandHandler('skip',
                                       anketa_skip_comment,
                                       pass_user_data=True)
                        ],
        },

        fallbacks=[MessageHandler(
            Filters.text | Filters.video | Filters.photo | Filters.document,
            anketa_dontknow,
            pass_user_data=True)
        ]
    )

    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(conv_city_game)
    dp.add_handler(conv_anketa)
    dp.add_handler(CommandHandler('dunkey',
                                  random_dunkey, pass_user_data=True))
    dp.add_handler(CommandHandler('planet',
                                  planet_naming, pass_user_data=True))
    dp.add_handler(CommandHandler('wordcount',
                                  word_count, pass_user_data=True))
    dp.add_handler(CommandHandler('next_full_moon',
                                  next_full_moon, pass_user_data=True))
    dp.add_handler(CommandHandler('calc', calc, pass_user_data=True))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dp.add_handler(
        CommandHandler("alarm",
                       set_alarm, pass_args=True, pass_job_queue=True)
    )

    dp.add_handler(RegexHandler(
        '^(Лицезреть ослика)$',
        random_dunkey,
        pass_user_data=True)
    )
    dp.add_handler(RegexHandler(
        '^(Сменить аву)$',
        change_avatar,
        pass_user_data=True)
    )

    dp.add_handler(CallbackQueryHandler(inline_button_pressed))

    dp.add_handler(MessageHandler(Filters.contact,
                                  get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location,
                                  get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.photo,
                                  check_user_photo, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text,
                                  talk_to_me, pass_user_data=True))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
