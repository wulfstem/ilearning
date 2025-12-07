import streamlit as st
import pandas as pd
import pickle
from pathlib import Path
import matplotlib.pyplot as plt

output_path = Path("ex4/processed_data/datasets.pkl")
enums = "DATA1", "DATA2", "DATA3"
datasets = {}
with open(output_path, "rb") as f:
        datasets = pickle.load(f)

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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(revenue.index, revenue.values)
    ax.set_title('Daily Revenue Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

tab1, tab2, tab3 = st.tabs(["DATA1", "DATA2", "DATA3"])
tabs = [tab1, tab2, tab3]

for i, name in enumerate(enums):
    with tabs[i]:
        st.header(name)
        with st.container():
            st.subheader("Top 5 days by revenue")
            st.table(daily_revenue(datasets[name]).sort_values(ascending=False).head(5))
        with st.container():
            st.subheader("Number of unique users")
            st.write(unique_users(datasets[name]))
        with st.container():
            st.subheader("Number of unique sets of authors")
            st.write(count_unique_authors(datasets[name]))
        with st.container():
            st.subheader("The name of most popular author(s)")
            authors, count = most_popular_author_set(datasets[name])
            st.write(f"Most popular author(s): {', '.join(authors)} with {count} sales")
        with st.container():
            st.subheader("Best buyer")
            top_sig, top_amount, user_ids = top_spender(datasets[name], build_user_sigs(datasets[name]))
            n, phone, address = top_sig.split("||")
            st.write(f"Best buyer: {n}")
            st.write(f"Phone: {phone}")
            st.write(f"Address: {address}")
            st.write(f"Total spent: ${top_amount:.2f}")
            st.write(f"User IDs: {', '.join(map(str, user_ids))}")
        with st.container():
            st.subheader("Daily Revenue Plot")
            plot_daily_revenue(datasets[name], name)