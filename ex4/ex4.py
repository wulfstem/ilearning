import pandas as pd
import numpy as np
import yaml
from pathlib import Path

data_folder = Path("data")

with open(data_folder / "DATA1/books.yaml", "r", encoding="utf-8") as f:
    books_data = yaml.safe_Load(f)

books = pd.DataFrame(books_data)

books = books.dropna(how="all")
books.columns = (books.columns.str.strip().str.lower().str.replace(" ", "_"))

books = books.drop_duplicates()

for col in books.columns:
    if "date" in col:
        books[col] = pd.to_datetime(books[col], errors="coerce")
    if books[col].dtype in [np.float64, np.int64]:
        books[col] = books[col].fillna(books[col].mean())
    else:
        books[col] = books[col].fillna("Unknown")
