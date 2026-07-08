# Wiki-Parser & Search ETL PIPELINE

This application processes massive, raw Wikipedia dumps, cleans the text extracted from them, and stores the structured data into an optimized database for instantaneous article lookups.

---

### Key Workflow

1. **Extraction (`extract_dump.py`):** Streams and reads large Wikipedia dump files in chunks to prevent memory overflows.
2. **Transformation (`transform_data.py`):** Extracts article content, strips code, links, and tags, leaving only clean text. To maximize performance, text processing is distributed across multiple CPU cores.
3. **Loading & Search (`load_data.py`):** Performs ultra-fast, optimized search queries for keywords across millions of processed articles.

---

### Project Structure & Modules

* **`load_data.py`** — The main entry point of the application. It prompts the user for a specific category to search articles.
* **`extract_dump.py`** — The extraction script responsible for parsing and initializing the project from a raw `xml.bz2` archive.
* **`transform_data.py`** — The text-cleaning module. It triggers distributed text processing, strips media tags, and updates the `clean_content` column in the database.
* **`database/utils/db_connector.py`** — Context managers ensuring secure and safe database session management.
* **`database/utils/models.py`** — Handles data type validation for records retrieved from the database.
* **`utils/create_index.py`** — Builds database indices to speed up search queries.
* **`utils/hash_utils.py`** — Implements salted hashing utilities.
* **`utils/other_utils.py`** — A utility module handling word-counting logic.
