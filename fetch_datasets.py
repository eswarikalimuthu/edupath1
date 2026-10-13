"""
Module 1 - Automated dataset fetcher.
Downloads career, scholarship, and course datasets directly into
data/raw/<category>/ so you don't have to click through web pages.

Setup (one-time):
    pip install kagglehub datasets
    # Kaggle API key must exist at ~/.kaggle/kaggle.json (see README)

Usage:
    python src/fetch_datasets.py
"""
import os
import shutil

import kagglehub
from datasets import load_dataset

import config


def fetch_career_dataset():
    """Downloads the Job Descriptions 2025 dataset (Kaggle) into data/raw/career/"""
    print("Fetching career dataset from Kaggle...")
    path = kagglehub.dataset_download("adityarajsrv/job-descriptions-2025-tech-and-non-tech-roles")

    dest_dir = os.path.join(config.RAW_DATA_DIR, "career")
    for fname in os.listdir(path):
        if fname.endswith(".csv"):
            shutil.copy(os.path.join(path, fname), os.path.join(dest_dir, fname))
            print(f"  Saved {fname} -> data/raw/career/")


def fetch_course_dataset():
    """Downloads the NIRF Top 100 Indian Universities dataset (Kaggle) into data/raw/course/"""
    print("Fetching course dataset from Kaggle...")
    path = kagglehub.dataset_download("vishardmehta/top-100-indian-universities-dataset")

    dest_dir = os.path.join(config.RAW_DATA_DIR, "course")
    for fname in os.listdir(path):
        if fname.endswith(".csv"):
            shutil.copy(os.path.join(path, fname), os.path.join(dest_dir, fname))
            print(f"  Saved {fname} -> data/raw/course/")


def fetch_tnea_cutoff_dataset():
    """
    Downloads real TNEA (Tamil Nadu Engineering Admissions) cutoff data
    into data/raw/course/ - college, branch, and community-wise cutoff
    marks. This is the granular course-level detail NIRF rankings don't
    have (NIRF only gives aggregate institute scores).
    """
    print("Fetching TNEA cutoff dataset from Kaggle...")
    path = kagglehub.dataset_download("naveen201105/tnea-2019-cutoff")

    dest_dir = os.path.join(config.RAW_DATA_DIR, "course")
    for fname in os.listdir(path):
        if fname.endswith(".csv"):
            shutil.copy(os.path.join(path, fname), os.path.join(dest_dir, f"TNEA_{fname}"))
            print(f"  Saved TNEA_{fname} -> data/raw/course/")


def fetch_scholarship_dataset():
    """
    Downloads the indian-govt-scholarships dataset (Hugging Face) and
    writes it as a plain CSV with 'label' and 'text' columns into
    data/raw/scholarship/ - no PDF binary needed, just the extracted text.
    """
    print("Fetching scholarship dataset from Hugging Face...")
    ds = load_dataset("NetraVerse/indian-govt-scholarships", split="train")

    dest_path = os.path.join(config.RAW_DATA_DIR, "scholarship", "indian_govt_scholarships.csv")
    df = ds.to_pandas()[["label", "text"]]
    df.to_csv(dest_path, index=False)
    print(f"  Saved {len(df)} scholarship records -> data/raw/scholarship/indian_govt_scholarships.csv")


if __name__ == "__main__":
    try:
        fetch_career_dataset()
    except Exception as e:
        print(f"[FAILED] Career dataset: {e}\n")

    try:
        fetch_course_dataset()
    except Exception as e:
        print(f"[FAILED] Course dataset: {e}\n")

    try:
        fetch_tnea_cutoff_dataset()
    except Exception as e:
        print(f"[FAILED] TNEA cutoff dataset: {e}\n")

    try:
        fetch_scholarship_dataset()
    except Exception as e:
        print(f"[FAILED] Scholarship dataset: {e}\n")

    print("\nDone. Check messages above for any [FAILED] datasets - rerun the script to retry those.")
    print("Then run: python src/ingest.py")