import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_DIR = os.path.join(BASE_DIR, "quiz-questions")


def load_questions(user_id, redis_connect):
    questions = get_questions()
    for question in questions:
        redis_connect.rpush(f"{user_id}_question", json.dumps(question))


def get_random_file():
    if not os.path.exists(QUESTIONS_DIR):
        raise FileNotFoundError(f"Папка {QUESTIONS_DIR} не найдена")
    files = [f for f in os.listdir(QUESTIONS_DIR) if f.endswith('.txt')]
    if not files:
        raise FileNotFoundError("Нет .txt файлов в папке quiz-questions")
    random_file = random.choice(files)
    return os.path.join(QUESTIONS_DIR, random_file)


def get_questions():
    filepath = get_random_file()
    questions = []
    current_question = {}
    with open(filepath, 'r', encoding='KOI8-R') as file:
        files = file.read()
        sections = files.strip().split('\n\n')
        for section in sections:
            section = section.strip()
            if section.startswith('Вопрос'):
                if current_question:
                    questions.append(current_question)
                    current_question = {}
                current_question['Вопрос'] = (
                    section[len('Вопрос 1:'):].strip().replace('\n', '') 
                    if section.startswith('Вопрос 1:') 
                    else section.split(':', 1)[1].strip().replace('\n', '')
                )
            elif section.startswith('Ответ'):
                current_question['Ответ'] = section[len('Ответ:'):].strip().replace('\n', '').split('.')[0]

    return questions