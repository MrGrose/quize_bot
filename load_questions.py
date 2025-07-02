import os
import random

directory = "D:/quize_bot/quiz-questions"


def get_random_file():
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    random_file = random.choice(files)
    return os.path.join(directory, random_file)


def get_questions(directory=None):
    random_file = directory if directory else get_random_file()
    questions = []
    current_question = {}
    with open(random_file, 'r', encoding='KOI8-R') as file:
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
                current_question['Ответ'] = section[len('Ответ:'):].strip().replace('\n', '')

    return questions[:random.randint(5, len(questions))]
