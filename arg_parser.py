import argparse


def create_parser() -> 'argparse.ArgumentParser':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Скрипт для загрузки вопросов викторы бота
        """)
    parser.add_argument(
        "-p",
        default="quiz-questions/1vs1200.txt",
        help="Путь до файла с вопросами",
    )
    return parser
