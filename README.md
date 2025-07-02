
# Бот викторина

Telegram и VK боты, которые проводят викторину по заранее подготовленным вопросам, учитывают ваши правильные и неправильные ответы. Если вы не знаете ответа, можно нажать на кнопку "Сдаться", и бот покажет правильный ответ.



## Функционал
В боте используется 3 кнопки:
- Новый вопрос — отправляется случайный вопрос из заранее подготовленных файлов.

- Сдаться — показывает правильный ответ и отправляет новый вопрос.

- Мой счёт — показывает количество правильных и неправильных ответов.


## Пример работы
| [TG bot](https://t.me/quize768_bot) | [VK bot](https://vk.com/club230501959) |
|-------------------------------------|---------------------------------------|
| ![](https://private-user-images.githubusercontent.com/147311692/461530034-69908cd8-3ebf-4870-a355-53b01498a162.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0NjExNjIsIm5iZiI6MTc1MTQ2MDg2MiwicGF0aCI6Ii8xNDczMTE2OTIvNDYxNTMwMDM0LTY5OTA4Y2Q4LTNlYmYtNDg3MC1hMzU1LTUzYjAxNDk4YTE2Mi5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQxMjU0MjJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jMjhkMGEyNmM3ZDM1ODZhMzZmYTBhMzU1YTYyM2ZkNzRmNGUwNjNjNzExNTdhYmI1MjE3YWQ5NGE1ODNkODNhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.7lRopevSiIPFMA6PBeJ_zNkPfwb38FowyXxBiOojh3s) | ![](https://private-user-images.githubusercontent.com/147311692/461530104-7fa772ef-7de7-4145-9ded-349adbf8faa1.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0NjExMzgsIm5iZiI6MTc1MTQ2MDgzOCwicGF0aCI6Ii8xNDczMTE2OTIvNDYxNTMwMTA0LTdmYTc3MmVmLTdkZTctNDE0NS05ZGVkLTM0OWFkYmY4ZmFhMS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQxMjUzNThaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iYmM5ZDM0Y2QxNzczZWJiNzIwMDZlYjg2NTM5MzNmODRmN2IzODUxZjY5NjgwNDIyZDA0NTdjNDJiZjEwZWI4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.UzKH8q9yDzO5WI7LX2J6Q0DEZiG93noyNiuOTCbBvHE) |

## Настройка ботов
1. Клонируйте репозиторий:

    ```python
    git clone <URL репозитория>
    ```
2. Установите зависимости:
    ```python
    pip install -r requeriments.txt
    ```
3. Создайте файл .env в корне проекта и добавьте ваш Telegram токен:
    ```python
    TG_TOKEN=<токен Telegram-бота>
    VK_GROUP_TOKEN=<токен вашей группы VK>

    REDIS_HOST=<полученный_адрес>
    REDIS_PORT=<полученный_порт>
    REDIS_PASSWORD=<полученный_пароль>
    ```

Зарегистрируйтесь в [Redis](https://redis.io/). Получите адрес базы данных вида: `redis-12153.f18.us-east-4-9.wc1.cloud.redislabs.com`, его порт вида: `17895` и его `пароль`.


## Запуск ботов

1. Запуск Телеграмм и Вконтакте ботов.
```python
python tg_bot.py

python vk_bot.py
```

## Примечание

Вопросы и ответы хранятся в папке `quiz-questions`. При каждом запуске бот случайным образом выбирает файлы с вопросами для викторины.