import sqlite3
import os
import re
from concurrent.futures import ProcessPoolExecutor
from mwparserfromhell import parse
from database.utils.db_connector import create_connection

DB_DIR = os.path.join("database", "db's")
DB_FILE = "ruwiki_2021.db"
DB_PATH = os.path.join(DB_DIR, DB_FILE)

def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    raw_text = re.sub(r"\{\{(?:число|рост|увеличение|снижение|падение)\|([^}]+)\}\}", r"\1", raw_text)
    
    wikicode = parse(raw_text)
    clean_text: str = wikicode.strip_code()
    
    clean_text = re.sub(r"\s*//\s*[^,\.\n]+(?:,\s*\d{4}|\s*-\d{2}-\d{2})?\.?", "", clean_text)
    
    clean_text = re.sub(r"([а-яё\.\)])([А-ЯЁ])", r"\1 \2", clean_text)
    
    clean_text = re.sub(r"\s*\(\s*\)", "", clean_text)
    clean_text = re.sub(r"[ \t\xa0]+", " ", clean_text)
    
    lines: list[str] = []
    garbage_prefixes = (
        "Файл:", "Категория:", "Image:", "Category:", 
        "thumb|", "мини|", "200px|", "300px|", "100px|"
    )
    
    for line in clean_text.split("\n"):
        line = line.strip()
        
        if not line or line.upper().startswith(("#REDIRECT", "#ПЕРЕНАПРАВЛЕНИЕ")) or line.startswith(garbage_prefixes):
            continue
            
        line = re.sub(r"\s*\(\s*см\.\s+фиг\s*\.?\s*\d+\s*\)\s*\.?", "", line, flags=re.IGNORECASE)
        
        line = re.compile(r"^[,\.\-\s]+").sub("", line)
        
        if line:
            lines.append(line)
            
    return "\n".join(lines)

def process_single_row(row: tuple) -> tuple[str,int]:
    a_id, raw_content = row
    return clean_text(raw_content), a_id

def main() -> None:
    num_workers: int = os.cpu_count() or 4

    with create_connection(DB_PATH, tuning=True) as conn:
        batch_size: int = 5000
        total_processed: int = 0
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            while True:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, raw_content 
                    FROM articles
                    WHERE raw_content IS NOT NULL AND clean_content IS NULL
                    LIMIT ?
                    """, (batch_size, ))
                rows = cursor.fetchall()

                if not rows: 
                    print("статьи обработаны")
                    break

                batch = list(executor.map(process_single_row, rows, chunksize=100))

                try:
                    with conn:
                        write_cursor = conn.cursor()
                        write_cursor.executemany(
                            """
                            UPDATE articles
                            SET clean_content = ?
                            WHERE id = ?
                            """,  batch)
                    
                    total_processed += len(batch)
                    print(f"Успешно обработана пачка из {total_processed} статей")
                    
                except sqlite3.Error as e:
                    print(f"Критическая ошибка базы данных при фиксации батча: {e}")
                    break

if __name__ == "__main__": main()
