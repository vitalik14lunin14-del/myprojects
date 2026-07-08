import logging
import sys
import os
from database.utils.db_connector import create_connection
from database.utils.models import Article
from utils.other_utils import count_words
from typing import Generator

DB_DIR = "database/db's"
DB_NAME = "ruwiki_2021.db"
LOGS_DIR = "logs"
OUTPUT_FILE = os.path.join(LOGS_DIR, "wiki_out.txt")
LOG_FILE = os.path.join(LOGS_DIR, "log.txt")
DB_PATH = os.path.join(DB_DIR, DB_NAME)

BATCH_SIZE = 1000

def logging_setup() -> None:
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
        )
    
def db_category_parser(category: str) -> Generator[tuple, None, None]:
    with create_connection(DB_PATH, tuning=True) as conn:
        cursor = conn.cursor()
        query = """
                SELECT id, title, clean_content
                FROM articles
                WHERE title LIKE ? AND clean_content IS NOT NULL
                """
        cursor.execute(query,(f"%{category}%", ))

        for raw in cursor:
            yield raw

def run_pipeline() -> None:
    with open(OUTPUT_FILE ,"w", encoding="utf-8") as f:
        f.write("")
    logging_setup()

    category = input("Введите категорию: ")

    if not category:
        logging.warning("Категория не может быть пустой")
        return
    logging.info(f"Начало парсинга по запросу {category}...")
    try:
        articles_stream = db_category_parser(category)

        batch_buffer = []
        total_processed = 0
        with open(OUTPUT_FILE ,"a", encoding="utf-8") as f:
            for row in articles_stream:
                article = Article(id=row[0], title=row[1], content=row[2])
                
                words_count = count_words(article.content)

                masked_data = article.get_masked_data()

                formatted_row = f"{masked_data["id"]}: {article.title}| {words_count} | {masked_data["content"]}\n"
                batch_buffer.append(formatted_row)
                total_processed += 1

                if(len(batch_buffer) == BATCH_SIZE):
                    f.writelines(batch_buffer)
                    batch_buffer.clear()

            if(batch_buffer):
                f.writelines(batch_buffer)
                logging.info(f"Остатки батчинга: {len(batch_buffer)}")
                batch_buffer.clear()

        if(total_processed == 0): logging.warning("Статьи по запросу не найдены")
        else: logging.info(f"Всего обработанных статей по запросу: {total_processed}")
    except Exception as e:
        logging.critical(f"Произошла ошибка программы: {e}")

if(__name__ == "__main__"):
    run_pipeline()
