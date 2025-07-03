import argparse
from pathlib import Path


def create_parser() -> 'argparse.ArgumentParser':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Скрипт для загрузки вопросов викторы бота
        """)
    default_path = Path("quiz-questions") / "1vs1200.txt"
    parser.add_argument(
        "-p",
        default=default_path,
        type=Path,
        help="Путь до файла с вопросами",
    )
    return parser
