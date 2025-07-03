import json
import logging
from functools import partial

import redis
import vk_api
from arg_parser import create_parser
from environs import Env
from questions_loader import load_questions_in_redis
from redis.exceptions import RedisError
from vk_api.exceptions import VkApiError
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

logger = logging.getLogger(__name__)


def send_start(event, vk, keyboard, redis_connect, filepath):
    redis_connect.delete(f"{event.user_id}_question")
    redis_connect.set(f"{event.user_id}_score", 0)
    redis_connect.set(f"{event.user_id}_incorrect", 0)
    load_questions_in_redis(event.user_id, redis_connect, filepath)
    vk.messages.send(
        user_id=event.user_id,
        message="Привет! Я бот для викторин!\nЧто бы начать нажми на кнопку «Новый вопрос»\n«Стоп»-для завершения",
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def send_new_question(event, vk, keyboard, redis_connect):
    current_question = redis_connect.lpop(f"{event.user_id}_question")
    redis_connect.set(f"{event.user_id}_current_question", current_question)
    new_question = json.loads(current_question)
    text = "Новый вопрос: \n" + new_question.get("Вопрос")
    vk.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def send_solution_attempt(event, vk, keyboard, redis_connect):
    answer = json.loads(redis_connect.get(f"{event.user_id}_current_question"))
    user_answer = event.text
    correct_answer = answer.get("Ответ")
    if user_answer == correct_answer:
        vk.messages.send(
            user_id=event.user_id,
            message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
        current_score = int(redis_connect.get(f"{event.user_id}_score"))
        redis_connect.set(f"{event.user_id}_score", current_score + 1)
    else:
        vk.messages.send(
            user_id=event.user_id,
            message="Неправильно… Попробуешь ещё раз?",
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
        incorrect_score = int(redis_connect.get(f"{event.user_id}_incorrect"))
        redis_connect.set(f"{event.user_id}_incorrect", incorrect_score + 1)


def send_surrender(event, vk, keyboard, redis_connect):
    answer = json.loads(redis_connect.get(f"{event.user_id}_current_question"))
    text = "Эх, решили так быстро сдаться:\nОтвет: " + answer.get("Ответ")
    vk.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )
    current_question = redis_connect.lpop(f"{event.user_id}_question")
    redis_connect.set(f"{event.user_id}_current_question", current_question)
    question = json.loads(current_question)
    new_question = "Новый вопрос: \n" + question.get("Вопрос")
    vk.messages.send(
        user_id=event.user_id,
        message=new_question,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def send_sroce(event, vk, keyboard, redis_connect):
    current_score = redis_connect.get(f"{event.user_id}_score")
    incorrect_score = redis_connect.get(f"{event.user_id}_incorrect")
    vk.messages.send(
        user_id=event.user_id,
        message=f"Ваш счёт: \n-угадано: {current_score}\n-не угадано: {incorrect_score}",
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    env = Env()
    env.read_env()
    redis_host = env.str("REDIS_HOST")
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD")
    vk_token = env.str("VK_GROUP_TOKEN")
    parser = create_parser()
    parsed_args = parser.parse_args()
    filepath = parsed_args.p
    try:
        redis_connect = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            username="default",
            password=redis_password,
        )
        vk_session = vk_api.VkApi(token=vk_token)
        vk = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button("Мой счет", color=VkKeyboardColor.PRIMARY)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == "Стоп":
                    break
                event_handler = {
                    "Старт": partial(send_start, event, vk, keyboard, redis_connect, filepath),
                    "Сдаться": partial(send_surrender, event, vk, keyboard, redis_connect),
                    "Новый вопрос": partial(send_new_question, event, vk, keyboard, redis_connect),
                    "Мой счет": partial(send_sroce, event, vk, keyboard, redis_connect),
                }
                event_handler.get(event.text, partial(send_solution_attempt, event, vk, keyboard, redis_connect))()

    except RedisError as error:
        logger.exception(f"Ошибка Redis: {error}")
    except VkApiError as error:
        logger.exception(f"Ошибка VkApi: {error}")
    except Exception as error:
        logger.exception(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
