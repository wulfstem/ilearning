import json, sqlite3
from pathlib import Path

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

try:
    file_path = Path(__file__).parent/'task1_d.json'
    with file_path.open('r', encoding='utf-8') as file:
        text = file.read()
    text = text.replace(":", '"')
    text = text.replace("=>", '":')
    data = json.loads(text)
except FileNotFoundError:
    print(f"File not found: {file_path}")
except json.JSONDecodeError:
    print("Error decoding JSON from the file.")

cursor.execute("DROP TABLE IF EXISTS books;")

cursor.execute("""
    CREATE TABLE books (
        id TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        genre TEXT,
        publisher TEXT,
        year INTEGER,
        price TEXT)
""")

for entry in data:
    entry["id"] = str(entry["id"])

    cursor.execute("""
        INSERT INTO books (id, title, author, genre, publisher, year, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (entry["id"], entry["title"], entry["author"], entry["genre"], entry["publisher"], entry["year"], entry["price"]))

cursor.execute("DROP TABLE IF EXISTS summary;")

cursor.execute("""
    CREATE TABLE summary AS
    SELECT year as publication_year,
    COUNT(*) as book_count,
    ROUND(SUM(CASE
        WHEN price LIKE "€%" THEN CAST(SUBSTR(price, 2) * 1.2 AS REAL)
        ELSE CAST(SUBSTR(price, 2) AS REAL)
    END) / COUNT(*), 2) as average_price
    FROM books
    GROUP BY year
""")

conn.commit()