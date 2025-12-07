import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import yaml, re
from ydata_profiling import ProfileReport
from pathlib import Path

data_folder = Path("ex4/data")
output_path = Path("ex4/processed_data")
datasets = {}

def parse_price(raw):
    if pd.isna(raw):
        return np.nan
    text = str(raw).strip()
    text = text.replace(" ", "")
    if "€" in text or "EUR" in text:
        currency = "EUR"
    else:
        currency = "USD"
    cents_pattern = r"(\d+)[¢](\d+)"
    m = re.search(cents_pattern, text)
    if m:
        number = float(f"{m.group(1)}.{m.group(2)}")
    else:
        numbers = re.findall(r"\d+\.?\d*", text)
        if not numbers:
            return np.nan
        number = float(numbers[0])
    if currency == "EUR":
        number *= 1.2
    return number

def clean_phone_number(phone):
    if pd.isna(phone):
        return np.nan
    return re.sub(r"\D", "", str(phone))

def daily_revenue(dataset):
    return dataset["orders"].groupby(dataset["orders"]["timestamp"].dt.date)["paid_price"].sum()

def count_unique_authors(dataset):
    unique_sets = set()
    for author in dataset["books"]["author"]:
        parts = [a.strip() for a in author.split(",") if a.strip()]
        author_set = frozenset(parts)
        unique_sets.add(author_set)
    return len(unique_sets)

def unique_users(dataset):
    users = dataset["users"].copy()
    id_fields = ["name", "email", "phone", "address"]
    signatures = []
    for ignore in id_fields:
        keep = [c for c in id_fields if c != ignore]
        sig = users[keep].astype(str).agg("||".join, axis=1)
        signatures.append(sig)
    all_signatures = pd.concat(signatures, axis=1)
    users["master_signature"] = all_signatures.min(axis=1)
    return users["master_signature"].nunique()

def most_popular_author_set(dataset):
    author_map = {}
    for _, row in dataset["books"].iterrows():
        raw = str(row["author"])
        parts = [a.strip() for a in raw.split(",") if a.strip()]
        author_map[row["id"]] = frozenset(parts)

    sales = {}

    for _, row in dataset["orders"].iterrows():
        book_id = row["book_id"]
        quantity = row["quantity"]
        author_set = author_map[book_id]
        if author_set not in sales:
            sales[author_set] = 0
        sales[author_set] += quantity
    
    ranked = sorted(sales.items(), key=lambda x: x[1], reverse=True)

    return ranked[0]

def build_user_sigs(dataset):
    users = dataset["users"].copy()
    id_fields = ["name", "email", "phone", "address"]
    signatures = []
    for ignore in id_fields:
        keep = [c for c in id_fields if c != ignore]
        sig = users[keep].astype(str).agg("||".join, axis=1)
        signatures.append(sig)
    all_signatures = pd.concat(signatures, axis=1)
    users["master_signature"] = all_signatures.min(axis=1)

    return users[["id", "master_signature"]]

def top_spender(dataset, users_sig):
    merged = dataset["orders"].merge(users_sig, left_on="user_id", right_on="id", how="left")
    spending = merged.groupby("master_signature")["paid_price"].sum()
    top_sig = spending.idxmax()
    top_amount = spending.max()
    user_ids = users_sig[users_sig["master_signature"] == top_sig]["id"].tolist()
    return top_sig, top_amount, user_ids

def plot_daily_revenue(dataset, dataset_name):
    revenue = daily_revenue(dataset)
    ax = plt.subplots(figsize=(12, 6))
    ax.plot(revenue.index, revenue.values)
    ax.set_title('Daily Revenue Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path / dataset_name / f"daily_revenue_{dataset_name}.png")
    plt.close()

for folder in data_folder.iterdir():
    dataset = {}
    for file in folder.iterdir():
        if file.suffix == ".yaml":
            with open(file, "r", encoding="utf-8") as f:
                df = pd.DataFrame(yaml.safe_load(f))
        elif file.suffix == ".parquet":
            df = pd.read_parquet(file)
        elif file.suffix == ".csv":
            df = pd.read_csv(file)
        else:
            print(f"Skipping unsupported file: {file.name}")
            continue

        df = df.dropna(how="all")
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(":", "", regex=False)
        df = df.drop_duplicates()

        for col in df.columns:
            if "year" in col:
                df[col] = df[col].astype(str).str.strip().str.upper()
                df[col] = df[col].replace({"NULL": None, "NONE": None, "-": None, "0": None, "": None})
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].astype('Int64')
                continue

            if "unit_price" in col:
                df[col] = df[col].apply(parse_price)
                continue

            if "timestamp" in col:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("A.M.", "AM", regex=False)
                    .str.replace("P.M.", "PM", regex=False)
                    .str.replace("a.m.", "AM", regex=False)
                    .str.replace("p.m.", "PM", regex=False)
                    .str.replace(",", " ", regex=False)
                    .str.replace(";", " ", regex=False)
                    .str.strip()
                )
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df["date"] = df[col].dt.date
                continue
            
            if "phone" in col:
                df[col] = df[col].apply(clean_phone_number)
                continue

        if "quantity" in df.columns and "unit_price" in df.columns:
            df["paid_price"] = df["quantity"] * df["unit_price"]

        dataset[file.stem] = df
        report = ProfileReport(df, title=f"Profiling Report for {file.stem} in {folder.name}", explorative=True)
        report.to_file(output_path / folder.name / f"report_{file.stem}.html")    
    datasets[folder.name] = dataset
with open(output_path / "datasets.pkl", "wb") as f:
    pickle.dump(datasets, f)