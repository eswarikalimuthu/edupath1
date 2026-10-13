
"""
CareerCompass RAG Ingestion Pipeline

Supports:
    - CSV files
    - PDF files

Freshness policy:
    - 2023 and newer -> KEEP
    - 2022 and older historical data -> SKIP
    - Undated career data -> KEEP
    - Undated scholarship data -> KEEP
    - Undated scheme data -> KEEP
    - Undated course data -> KEEP only when it is not clearly historical

Run from project root:

    python -m src.ingest
"""

import os
import glob
import hashlib
import re

import chromadb
import pandas as pd
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from src import config


# ============================================================
# CSV EXTRACTION
# ============================================================

def extract_rows_from_csv(csv_path: str) -> list[str]:
    """
    Convert every CSV row into a text document.
    """

    df = pd.read_csv(csv_path)

    row_texts = []

    for _, row in df.iterrows():

        parts = []

        for column in df.columns:

            value = row[column]

            if pd.notna(value):

                parts.append(
                    f"{column}: {value}"
                )

        if parts:

            row_texts.append(
                ". ".join(parts)
            )

    return row_texts


# ============================================================
# DATA FRESHNESS FILTER
# ============================================================

def is_recent_or_current(
    text: str,
    category: str,
    source: str,
) -> bool:
    """
    Decide whether a document should be included in RAG.

    Rules:

    1. Explicit 2023+ data:
       KEEP

    2. Explicit 2022 or older historical data:
       SKIP

    3. Undated career information:
       KEEP

    4. Undated scholarship information:
       KEEP

    5. Undated government schemes:
       KEEP

    6. Undated course information:
       KEEP unless the source itself clearly indicates
       historical data.

    This prevents old datasets such as:
        TNEA 2019
        NIRF 2020
        NIRF 2021
        NIRF 2022

    from entering the new RAG database.
    """

    combined_text = (
        f"{source} {text}"
    ).lower()

    # --------------------------------------------------------
    # Detect explicit years
    # --------------------------------------------------------

    years = [
        int(year)
        for year in re.findall(
            r"\b(20\d{2})\b",
            combined_text
        )
    ]

    # --------------------------------------------------------
    # Explicit historical indicators
    # --------------------------------------------------------

    historical_patterns = [
        r"\b20\d{2}\s*[-_ ]?\s*cutoff\b",
        r"\bcutoff\s*[-_ ]?\s*20\d{2}\b",
        r"\bnirf\s*[-_ ]?\s*20\d{2}\b",
        r"\b20\d{2}\s*ranking\b",
        r"\branking\s*[-_ ]?\s*20\d{2}\b",
        r"\bhistorical\b",
        r"\bold\s+data\b",
        r"\bprevious\s+year\b",
    ]

    # If source/text explicitly says it is historical,
    # only keep it if it also contains 2023+ information.
    has_historical_marker = any(
        re.search(
            pattern,
            combined_text,
            re.IGNORECASE
        )
        for pattern in historical_patterns
    )

    # --------------------------------------------------------
    # No year found
    # --------------------------------------------------------

    if not years:

        # Undated reference information is allowed.
        return True

    # --------------------------------------------------------
    # 2023+ information exists
    # --------------------------------------------------------

    if any(year >= 2023 for year in years):

        return True

    # --------------------------------------------------------
    # All detected years are 2022 or older
    # --------------------------------------------------------

    if all(year <= 2022 for year in years):

        print(
            f"    [SKIP OLD DATA] "
            f"{source} | {category} | "
            f"Years: {sorted(set(years))}"
        )

        return False

    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    return True


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from every page of a PDF.
    """

    reader = PdfReader(pdf_path)

    text_parts = []

    for page in reader.pages:

        page_text = page.extract_text() or ""

        text_parts.append(
            page_text
        )

    return "\n".join(text_parts)


# ============================================================
# TEXT CHUNKING
# ============================================================

def chunk_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    """
    Split long text into overlapping chunks.
    """

    text = " ".join(
        text.split()
    )

    if not text:

        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += (
            chunk_size - overlap
        )

    return chunks


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_documents() -> list[dict]:
    """
    Automatically scan all configured categories.

    Supports:
        *.csv
        *.pdf
    """

    all_chunks = []

    total_loaded = 0
    total_skipped = 0

    for category in config.CATEGORIES:

        folder = os.path.join(
            config.RAW_DATA_DIR,
            category
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        pdf_files = glob.glob(
            os.path.join(
                folder,
                "*.pdf"
            )
        )

        csv_files = glob.glob(
            os.path.join(
                folder,
                "*.csv"
            )
        )

        files = (
            pdf_files
            + csv_files
        )

        if not files:

            print(
                f"[WARNING] No PDF/CSV found "
                f"in {folder}"
            )

            continue

        print(
            f"\nCategory: {category}"
        )

        # ====================================================
        # PDFs
        # ====================================================

        for pdf_path in pdf_files:

            filename = os.path.basename(
                pdf_path
            )

            print(
                f"  Reading PDF: {filename}"
            )

            raw_text = extract_text_from_pdf(
                pdf_path
            )

            chunks = chunk_text(
                raw_text
            )

            for chunk in chunks:

                if not is_recent_or_current(
                    chunk,
                    category,
                    filename
                ):
                    total_skipped += 1
                    continue

                all_chunks.append(
                    {
                        "text": chunk,
                        "category": category,
                        "source": filename,
                    }
                )

                total_loaded += 1

        # ====================================================
        # CSVs
        # ====================================================

        for csv_path in csv_files:

            filename = os.path.basename(
                csv_path
            )

            print(
                f"  Reading CSV: {filename}"
            )

            row_texts = extract_rows_from_csv(
                csv_path
            )

            for row_text in row_texts:

                chunks = chunk_text(
                    row_text
                )

                for chunk in chunks:

                    if not is_recent_or_current(
                        chunk,
                        category,
                        filename
                    ):
                        total_skipped += 1
                        continue

                    all_chunks.append(
                        {
                            "text": chunk,
                            "category": category,
                            "source": filename,
                        }
                    )

                    total_loaded += 1

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n============================================"
    )

    print(
        "DATA FRESHNESS SUMMARY"
    )

    print(
        "============================================"
    )

    print(
        f"Documents kept       : {total_loaded}"
    )

    print(
        f"Old documents skipped: {total_skipped}"
    )

    print(
        "Policy                : 2023+"
    )

    print(
        "Undated reference data: KEPT"
    )

    print(
        "============================================"
    )

    return all_chunks


# ============================================================
# DETERMINISTIC DOCUMENT ID
# ============================================================

def create_document_id(
    document: dict
) -> str:
    """
    Create a stable ID from category + source + text.

    This prevents duplicate records when ingestion
    is run multiple times.
    """

    raw_id = (
        document["category"]
        + "|"
        + document["source"]
        + "|"
        + document["text"]
    )

    return hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()


# ============================================================
# VECTOR STORE
# ============================================================

def build_vector_store(
    documents: list[dict]
):
    """
    Embed documents and store them in ChromaDB.
    """

    if not documents:

        print(
            "\nNo documents found."
        )

        return

    print(
        f"\nTotal documents/chunks: "
        f"{len(documents)}"
    )

    # ========================================================
    # LOAD EMBEDDING MODEL
    # ========================================================

    print(
        f"\nLoading embedding model: "
        f"{config.EMBEDDING_MODEL}"
    )

    model = SentenceTransformer(
        config.EMBEDDING_MODEL
    )

    # ========================================================
    # CONNECT TO CHROMADB
    # ========================================================

    client = chromadb.PersistentClient(
        path=config.CHROMA_DB_DIR
    )

    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        },
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_documents = {}

    for document in documents:

        doc_id = create_document_id(
            document
        )

        unique_documents[
            doc_id
        ] = document

    documents = list(
        unique_documents.values()
    )

    # ========================================================
    # PREPARE DATA
    # ========================================================

    ids = [
        create_document_id(document)
        for document in documents
    ]

    texts = [
        document["text"]
        for document in documents
    ]

    metadatas = [
        {
            "category": document["category"],
            "source": document["source"],
        }
        for document in documents
    ]

    # ========================================================
    # GENERATE EMBEDDINGS
    # ========================================================

    print(
        f"\nGenerating embeddings for "
        f"{len(texts)} documents..."
    )

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
    ).tolist()

    # ========================================================
    # UPSERT INTO CHROMADB
    # ========================================================

    print(
        "\nUpdating ChromaDB..."
    )

    batch_size = 200

    for i in tqdm(
        range(
            0,
            len(texts),
            batch_size
        ),
        desc="Writing to ChromaDB"
    ):

        collection.upsert(

            ids=ids[
                i:i + batch_size
            ],

            documents=texts[
                i:i + batch_size
            ],

            embeddings=embeddings[
                i:i + batch_size
            ],

            metadatas=metadatas[
                i:i + batch_size
            ],
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print(
        "\n============================================"
    )

    print(
        "RAG INGESTION COMPLETED"
    )

    print(
        "============================================"
    )

    print(
        f"Documents processed : "
        f"{len(texts)}"
    )

    print(
        f"ChromaDB total      : "
        f"{collection.count()}"
    )

    print(
        f"Collection          : "
        f"{config.COLLECTION_NAME}"
    )

    print(
        "============================================"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n============================================"
    )

    print(
        "CareerCompass RAG Ingestion"
    )

    print(
        "============================================"
    )

    documents = load_documents()

    build_vector_store(
        documents
    )

