import bz2
import xml.etree.ElementTree as ET
import os
from database.utils.db_connector import create_connection, create_transaction

DUMP_DIR = os.path.join("database", "dumps")
DUMP_FILE = "ruwiki-20210720-pages-articles-multistream.xml.bz2"
DUMP_PATH = os.path.join(DUMP_DIR, DUMP_FILE)

DB_DIR = os.path.join("database", "db's")
DB_FILE = "ruwiki_2021.db"
DB_PATH = os.path.join(DB_DIR, DB_FILE)

def init_database() -> None:
    with create_transaction(DB_PATH) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                title TEXT,
                raw_content TEXT,
                clean_content TEXT
            )
        """)

def parse_and_import() -> None:
    if not os.path.exists(DUMP_PATH):
        print(f"Файл дампа {DUMP_FILE} не найден")
        return
    
    with create_connection(DB_PATH, tuning=True) as conn:
        cursor = conn.cursor()
        print(f"Начало чтения {DUMP_FILE}...")
        
        with bz2.open(DUMP_PATH, "rt", encoding="utf-8") as f:
            context = ET.iterparse(f, events=("start","end"))
            
            event, root = next(context)

            batch = []
            count = 0
            
            for event, elem in context:
                if elem.tag.endswith("page"):
                    title_elem = elem.find(".//{*}title")
                    ns_elem = elem.find(".//{*}ns")
                    id_elem = elem.find(".//{*}id")
                    text_elem = elem.find(".//{*}text")
                    
                    if title_elem is not None and ns_elem is not None and ns_elem.text == "0":
                        article_id = id_elem.text if id_elem is not None else str(count)
                        title = title_elem.text
                        text = text_elem.text if text_elem is not None else ""

                        batch.append((article_id, title, text, None))
                    
                    if len(batch) >= 10000:
                        with conn:
                            cursor.executemany("INSERT OR IGNORE INTO ARTICLES VALUES (?, ?, ?, ?)", batch)
                        count += len(batch)
                        print(f"Импортировано статей: {count}...")
                        batch = []
                    
                    elem.clear()
                    root.clear()
            
            if batch:
                with conn:
                    cursor.executemany("INSERT OR IGNORE INTO ARTICLES VALUES (?, ?, ?, ?)", batch)
                count += len(batch)
            
    print(f"Всего импортировано статей: {count}")

if __name__ == "__main__":
    print("Инициализация базы данных...")
    init_database()
    parse_and_import()