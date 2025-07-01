import json
import logging

import redis
import vk_api
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from questions import get_questions

logger = logging.getLogger("Logger")


def send_start(event, vk, keyboard):
    vk.messages.send(
        user_id=event.user_id,
        message="Привет! Я бот для викторин!",
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),

    )


# Новый вопрос
def send_new_question(event, vk, keyboard, redis_connect):
    if redis_connect.llen(f"{event.user_id}_question") == 0:
        questions = get_questions()
        for question in questions:
            redis_connect.rpush(f"{event.user_id}_question", json.dumps(question))

    current_question = redis_connect.lpop(f"{event.user_id}_question")
    redis_connect.set(f"{event.user_id}_current_question", current_question)
    new_question = json.loads(current_question)
    print(f"[send_new_question]{new_question}")
    text = "Новый вопрос: \n" + new_question.get("Вопрос")

    vk.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


# Подсчет ответов
def send_solution_attempt(event, vk, keyboard, redis_connect):
    answer = json.loads(redis_connect.get(f"{event.user_id}_current_question"))
    user_answer = event.text
    correct_answer = answer.get("Ответ")
    print(f"[send_solution_attempt]{correct_answer}")
    if user_answer == correct_answer:
        vk.messages.send(
            user_id=event.user_id,
            message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
        current_score = int(redis_connect.get(f"{event.user_id}_score_vk") or 0)
        redis_connect.set(f"{event.user_id}_score_vk", current_score + 1)
    else:
        vk.messages.send(
            user_id=event.user_id,
            message="Неправильно… Попробуешь ещё раз?",
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
        incorrect_score = int(redis_connect.get(f"{event.user_id}_incorrect_vk") or 0)
        redis_connect.set(f"{event.user_id}_incorrect_vk", incorrect_score + 1)


# Сдаться
def send_surrender(event, vk, keyboard, redis_connect):
    answer = json.loads(redis_connect.get(f"{event.user_id}_current_question"))
    text = "Эх, решили так быстро сдаться:\nОтвет: " + answer.get("Ответ")
    vk.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )

    if redis_connect.llen(f"{event.user_id}_question") == 0:
        questions = get_questions()
        for question in questions:
            redis_connect.rpush(f"{event.user_id}_question", json.dumps(question))

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


# Мой счет
def send_sroce(event, vk, keyboard, redis_connect):
    current_score = redis_connect.get(f"{event.user_id}_score_vk")
    incorrect_score = redis_connect.get(f"{event.user_id}_incorrect_vk")
    vk.messages.send(
        user_id=event.user_id,
        message=f"Ваш счёт: \n-угадано: {current_score}\n-не угадано: {incorrect_score}",
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


# def load_questions_redis(event, redis_connect):
#     redis_connect.delete(f"{event.user_id}_question")
#     redis_connect.set(f"{event.user_id}_score", 0)
#     redis_connect.set(f"{event.user_id}_incorrect", 0)


def main():
    env = Env()
    env.read_env()
    redis_host = env.str("REDIS_HOST")
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD")
    vk_token = env.str("VK_GROUP_TOKEN")
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

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == "Стоп":
                    break
                elif event.text == "Старт":
                    send_start(event, vk, keyboard)
                elif event.text == "Сдаться":
                    send_surrender(event, vk, keyboard, redis_connect)
                elif event.text == "Новый вопрос":
                    send_new_question(event, vk, keyboard, redis_connect)
                elif event.text == "Мой счет":
                    send_sroce(event, vk, keyboard, redis_connect)
                else:
                    send_solution_attempt(event, vk, keyboard, redis_connect)

    except Exception as error:
        logger.exception(f"VK бот упал с ошибкой:{error}")


if __name__ == "__main__":
    main()