import json


def load_questions_in_redis(user_id, redis_connect, filepath):
    questions = load_questions_from_file(filepath)
    for question in questions:
        redis_connect.rpush(f"{user_id}_question", json.dumps(question))


def load_questions_from_file(filepath):
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
