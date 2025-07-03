import json
import logging
from functools import partial

import redis
from arg_parser import create_parser
from environs import Env
from redis.exceptions import RedisError
from telegram import ReplyKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from quize_bot.questions_loader import load_questions_in_redis

logger = logging.getLogger(__name__)

NEW_QUESTION, ANSWER = range(2)

KEYBOARD = ReplyKeyboardMarkup(
        [["Новый вопрос", "Сдаться"],
         ["Мой счет"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def start(update: Update, context: CallbackContext, redis_connect, filepath):
    user_id = update.effective_chat.id
    redis_connect.delete(f"{user_id}_question")
    redis_connect.set(f"{user_id}_score", 0)
    redis_connect.set(f"{user_id}_incorrect", 0)
    load_questions_in_redis(user_id, redis_connect, filepath)
    context.bot.send_message(
        chat_id=user_id,
        text="Привет! Я бот для викторин!\nЧто бы начать нажми на кнопку «Новый вопрос»\n«/cancel»-для завершения",
        reply_markup=KEYBOARD
    )
    return NEW_QUESTION


def handle_new_question_request(update: Update, context: CallbackContext, redis_connect):
    user_id = update.effective_chat.id
    question_json = redis_connect.lpop(f"{user_id}_question")
    redis_connect.set(f"{user_id}_current_question", question_json)
    question = json.loads(question_json)
    text = "Новый вопрос: \n" + question.get("Вопрос")
    update.message.reply_text(text, reply_markup=KEYBOARD)

    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, redis_connect):
    user_id = update.effective_chat.id
    answer = json.loads(redis_connect.get(f"{user_id}_current_question"))
    user_answer = update.message.text
    correct_answer = answer.get("Ответ")
    if user_answer == correct_answer:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»", reply_markup=KEYBOARD)
        current_score = int(redis_connect.get(f"{user_id}_score"))
        redis_connect.set(f"{user_id}_score", current_score + 1)
        return NEW_QUESTION
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?", reply_markup=KEYBOARD)
        incorrect_score = int(redis_connect.get(f"{user_id}_incorrect"))
        redis_connect.set(f"{user_id}_incorrect", incorrect_score + 1)
        return ANSWER


def handle_surrender(update: Update, context: CallbackContext, redis_connect):
    user_id = update.effective_chat.id
    answer = json.loads(redis_connect.get(f"{user_id}_current_question"))
    text = "Эх, решили так быстро сдаться:\nОтвет: " + answer.get("Ответ")
    update.message.reply_text(text, reply_markup=KEYBOARD)

    question_json = redis_connect.lpop(f"{user_id}_question")
    redis_connect.set(f"{user_id}_current_question", question_json)
    question = json.loads(question_json)
    new_question_text = "Новый вопрос: \n" + question.get("Вопрос")
    update.message.reply_text(new_question_text, reply_markup=KEYBOARD)

    return ANSWER


def handle_sroce(update: Update, context: CallbackContext, redis_connect):
    chat_id = update.effective_chat.id
    current_score = redis_connect.get(f"{chat_id}_score")
    incorrect_score = redis_connect.get(f"{chat_id}_incorrect")
    update.message.reply_text(f"Ваш счёт: \n-угадано: {current_score}\n-не угадано: {incorrect_score}", reply_markup=KEYBOARD)
    return ANSWER


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Пока')
    return ConversationHandler.END


def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()
    redis_host = env.str("REDIS_HOST")
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD")
    tg_token = env.str("TG_TOKEN")
    parser = create_parser()
    parsed_args = parser.parse_args()
    try:
        redis_connect = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            username="default",
            password=redis_password,
        )

        updater = Updater(tg_token)

        dispatcher = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', partial(start, redis_connect=redis_connect, filepath=parsed_args.p))],
            states={
                NEW_QUESTION: [
                    MessageHandler(Filters.text('Мой счет'), partial(handle_sroce, redis_connect=redis_connect)),
                    MessageHandler(Filters.text('Новый вопрос'), partial(handle_new_question_request, redis_connect=redis_connect)),
                ],
                ANSWER: [
                    MessageHandler(Filters.text('Мой счет'), partial(handle_sroce, redis_connect=redis_connect)),
                    MessageHandler(Filters.text('Сдаться'), partial(handle_surrender, redis_connect=redis_connect)),
                    MessageHandler(Filters.text('Новый вопрос'), partial(handle_new_question_request, redis_connect=redis_connect)),
                    MessageHandler(Filters.text & ~Filters.command, partial(handle_solution_attempt, redis_connect=redis_connect)),
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dispatcher.add_handler(conv_handler)    
        updater.start_polling()
        updater.idle()

    except RedisError as error:
        logger.exception(f"Ошибка Redis: {error}")
    except TelegramError as error:
        logger.exception(f"Ошибка Telegram: {error}")
    except Exception as error:
        logger.exception(f"Ошибка: {error}")


if __name__ == '__main__':
    main()
