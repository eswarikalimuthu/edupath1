"""
Module 1 - Step 5: Sanity-check retrieval before moving to Module 2 (agents).

Usage:
    python src/test_retrieval.py "What scholarships exist for engineering students?"
    python src/test_retrieval.py "eligibility for merit scholarship" --category scholarship
"""
import sys
import argparse

import chromadb
from sentence_transformers import SentenceTransformer

from src import config


def query(query_text: str, category: str = None, top_k: int = 5):
    model = SentenceTransformer(config.EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name=config.COLLECTION_NAME)

    query_embedding = model.encode([query_text]).tolist()

    where_filter = {"category": category} if category else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
    )

    print(f"\nQuery: {query_text}")
    if category:
        print(f"Filtered to category: {category}")
    print("-" * 60)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    if not docs:
        print("No results. Did you run ingest.py first?")
        return

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
        print(f"\n[{i}] score={1 - dist:.3f} | source={meta['source']} | category={meta['category']}")
        print(doc[:300] + ("..." if len(doc) > 300 else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", help="Query to search for")
    parser.add_argument("--category", default=None, choices=config.CATEGORIES)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    query(args.query_text, category=args.category, top_k=args.top_k)
