import sqlite3
import os

DB_PATH = os.path.join("DB'S", "ruwiki_2021.db")

conn = sqlite3.connect(DB_PATH)
print("Создание индекса")
conn.execute(
    """
    CREATE INDEX IF NOT EXISTS idx_clean_content 
    ON articles(clean_content) 
    WHERE clean_content IS NULL;
    """)
conn.commit()
conn.close()
print("Индекc создан")