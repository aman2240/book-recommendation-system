from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pickle
import re
import pandas as pd

app = FastAPI(title="Book Recommendation API")

# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load Models & Data
# --------------------------------------------------
knn = pickle.load(open("knn.pkl", "rb"))
tfidf = pickle.load(open("tfidf.pkl", "rb"))
tfidf_matrix = pickle.load(open("tfidf_matrix.pkl", "rb"))
df = pickle.load(open("df.pkl", "rb"))

# Ensure thumbnail & preview_link exist
if "thumbnail" not in df.columns:
    df["thumbnail"] = ""

if "preview_link" not in df.columns:
    df["preview_link"] = ""

# --------------------------------------------------
# Utility: Clean Text
# --------------------------------------------------
def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


# --------------------------------------------------
# Utility: Fix Thumbnail URL
# --------------------------------------------------
def fix_thumbnail(url):
    if isinstance(url, str) and url.startswith("http://"):
        return url.replace("http://", "https://")
    return url


# --------------------------------------------------
# Helper: Similar Books
# --------------------------------------------------
def get_similar_books_by_index(idx: int, n: int = 10):

    distances, indices = knn.kneighbors(
        tfidf_matrix[idx],
        n_neighbors=n + 1
    )

    recommendations = []

    for i in range(1, len(indices[0])):  # Skip itself
        book_index = indices[0][i]

        recommendations.append({
            "title": df.iloc[book_index]["title"],
            "authors": df.iloc[book_index]["authors"],
            "thumbnail": fix_thumbnail(df.iloc[book_index]["thumbnail"]),
            "preview_link": df.iloc[book_index]["preview_link"],
            "similarity": float(1 - distances[0][i])
        })

    return recommendations


# --------------------------------------------------
# Root
# --------------------------------------------------
@app.get("/")
def home():
    return {"message": "Book Recommendation API Running 🚀"}


# --------------------------------------------------
# Title Recommendation (KNN)
# --------------------------------------------------
@app.get("/recommend")
def recommend_books(title: str, n: int = 10):

    title_clean = clean_text(title)

    if title_clean not in df["title_clean"].values:
        return {"error": "Book not found"}

    idx = df[df["title_clean"] == title_clean].index[0]

    return get_similar_books_by_index(idx, n)


# --------------------------------------------------
# Author Recommendation
# --------------------------------------------------
@app.get("/author")
def recommend_by_author(name: str, n: int = 10):

    name_clean = clean_text(name)

    matches = df[df["authors_clean"].str.contains(name_clean, na=False)]

    if matches.empty:
        return {"error": "No books found"}

    results = []

    for _, row in matches.head(n).iterrows():
        results.append({
            "title": row["title"],
            "authors": row["authors"],
            "thumbnail": fix_thumbnail(row["thumbnail"]),
            "preview_link": row["preview_link"]
        })

    return results


# --------------------------------------------------
# Category Recommendation
# --------------------------------------------------
@app.get("/category")
def recommend_by_category(name: str, n: int = 10):

    name_clean = clean_text(name)

    matches = df[df["categories_clean"].str.contains(name_clean, na=False)]

    if matches.empty:
        return {"error": "No books found"}

    results = []

    for _, row in matches.head(n).iterrows():
        results.append({
            "title": row["title"],
            "authors": row["authors"],
            "categories": row.get("categories"),
            "thumbnail": fix_thumbnail(row["thumbnail"]),
            "preview_link": row["preview_link"]
        })

    return results


# --------------------------------------------------
# Get All Books (for dropdown)
# --------------------------------------------------
@app.get("/books")
def get_all_books():
    return df[["title"]].drop_duplicates().sort_values("title").to_dict(orient="records")


# --------------------------------------------------
# Smart Unified Search
# --------------------------------------------------
@app.get("/search")
def search_books(query: str = Query(...), n: int = 10):

    query_clean = clean_text(query)

    # 1️⃣ Try Title Match
    title_matches = df[df["title_clean"].str.contains(query_clean, na=False)]

    if not title_matches.empty:
        idx = title_matches.index[0]
        return get_similar_books_by_index(idx, n)

    # 2️⃣ Try Author Match
    author_matches = df[df["authors_clean"].str.contains(query_clean, na=False)]

    if not author_matches.empty:
        results = []
        for _, row in author_matches.head(n).iterrows():
            results.append({
                "title": row["title"],
                "authors": row["authors"],
                "thumbnail": fix_thumbnail(row["thumbnail"]),
                "preview_link": row["preview_link"]
            })
        return results

    # 3️⃣ Try Category Match
    category_matches = df[df["categories_clean"].str.contains(query_clean, na=False)]

    if not category_matches.empty:
        results = []
        for _, row in category_matches.head(n).iterrows():
            results.append({
                "title": row["title"],
                "authors": row["authors"],
                "thumbnail": fix_thumbnail(row["thumbnail"]),
                "preview_link": row["preview_link"]
            })
        return results

    return {"message": "No books found"}
