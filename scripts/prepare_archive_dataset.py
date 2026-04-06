from pathlib import Path

import pandas as pd


SEMEVAL_2014_FILES = {
    "Restaurants_Train_v2.csv",
    "Laptop_Train_v2.csv",
    "restaurants-trial.csv",
    "laptops-trial.csv",
}

SEMEVAL_2016_FILES = {
    "Restaurants_Test_Data_PhaseA.csv",
    "Laptops_Test_Data_PhaseA.csv",
    "Restaurants_Test_Data_PhaseB.csv",
    "Laptops_Test_Data_PhaseB.csv",
}


def normalize_frame(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if not {"sentence", "aspect_term", "polarity"}.issubset(df.columns):
        return pd.DataFrame(columns=["sentence", "aspect_term", "sentiment", "source_file"])

    keep = df[["sentence", "aspect_term", "polarity"]].copy()
    keep = keep.rename(columns={"polarity": "sentiment"})
    keep["sentiment"] = keep["sentiment"].astype(str).str.lower().str.strip()
    keep["source_file"] = source_name
    keep = keep.dropna(subset=["sentence", "aspect_term", "sentiment"])
    keep = keep[keep["sentiment"].isin(["positive", "negative", "neutral", "conflict"])]
    return keep


def save_dataset(df: pd.DataFrame, output_path: Path, label: str) -> bool:
    if df.empty:
        print(f"Warning: No rows found for {label}. File was not overwritten: {output_path}")
        return False

    df.to_csv(output_path, index=False)
    print(f"Saved {label}: {output_path}")
    print(f"Rows ({label}): {len(df)}")
    print(f"Sentiment distribution ({label}):")
    print(df["sentiment"].value_counts().to_string())
    print()
    return True


def main() -> None:
    base = Path("data/semeval_raw")
    files = sorted(SEMEVAL_2014_FILES | SEMEVAL_2016_FILES)

    frames = []
    for name in files:
        path = base / name
        if not path.exists():
            continue

        keep = normalize_frame(pd.read_csv(path), source_name=name)
        if not keep.empty:
            frames.append(keep)

    if not frames:
        raise RuntimeError("No compatible CSV files found in data/semeval_raw")

    out = pd.concat(frames, ignore_index=True)

    out_2014 = out[out["source_file"].isin(SEMEVAL_2014_FILES)].copy()
    out_2016 = out[out["source_file"].isin(SEMEVAL_2016_FILES)].copy()

    output_path_2016 = Path("data/semeval_2016_absa.csv")
    output_path_2014 = Path("data/semeval_2014_absa.csv")
    saved_2014 = save_dataset(out_2014, output_path_2014, label="SemEval 2014")
    saved_2016 = save_dataset(out_2016, output_path_2016, label="SemEval 2016")

    print(f"Combined rows: {len(out)}")
    print("Sentiment distribution:")
    print(out["sentiment"].value_counts().to_string())
    if not saved_2016:
        print("Note: SemEval 2016 split is empty because current CSV sources do not include polarity labels for that split.")
    if not saved_2014:
        print("Note: SemEval 2014 split is empty. Verify source file mapping and raw CSV schemas.")


if __name__ == "__main__":
    main()
