"""
Prepare SemEval-2016 ABSA dataset from the local archive files.

The workspace already contains the English SemEval ABSA source files under
data/semeval_raw, so this script standardizes them into a single CSV that the
app and training pipeline can consume.
"""

import os
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET


def find_source_directory() -> Path:
    candidates = [Path("data/semeval_raw"), Path("Downloads/archive (1)"), Path.home() / "Downloads" / "archive (1)"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find SemEval raw files in data/semeval_raw or Downloads/archive (1)")


def explore_dataset(dataset_path):
    """Explore downloaded dataset structure."""
    print("\n" + "="*60)
    print("EXPLORING DATASET STRUCTURE")
    print("="*60)
    
    dataset_path = Path(dataset_path)
    
    print(f"\nDataset location: {dataset_path}")
    print(f"Dataset exists: {dataset_path.exists()}\n")
    
    if not dataset_path.exists():
        return
    
    print("Files in downloaded dataset:")
    print("-" * 60)
    
    for item in dataset_path.rglob('*'):
        if item.is_file():
            size = item.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024**2:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size/(1024**2):.1f}MB"
            
            rel_path = item.relative_to(dataset_path)
            print(f"  {rel_path} ({size_str})")
    
    print("-" * 60)


def process_xml_files(dataset_path):
    """
    Process XML files and convert to CSV format.
    """
    print("\n" + "="*60)
    print("PROCESSING DATASET")
    print("="*60)
    
    dataset_path = Path(dataset_path)
    xml_files = list(dataset_path.glob('**/*.xml'))
    
    if not xml_files:
        print("\n⚠️  No XML files found in dataset")
        print("The dataset might be in a different format")
        return None
    
    print(f"\nFound {len(xml_files)} XML files")
    
    all_records = []

    for xml_file in xml_files:
        print(f"\nProcessing: {xml_file.name}")

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            file_records = 0
            for sentence in root.findall('.//sentence'):
                sentence_text = sentence.findtext('text', '')
                aspects_elem = sentence.find('aspectTerms')
                if aspects_elem is None:
                    continue

                for aspect in aspects_elem.findall('aspectTerm'):
                    term = aspect.get('term')
                    sentiment = aspect.get('polarity')
                    if term and sentiment:
                        all_records.append({
                            'sentence': sentence_text,
                            'aspect_term': term,
                            'sentiment': sentiment.lower(),
                            'file': xml_file.name,
                        })
                        file_records += 1

            print(f"  ✓ Extracted {file_records} records")
        except Exception as e:
            print(f"  ✗ Error processing {xml_file.name}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        print(f"\n✓ Total records extracted: {len(df)}")
        print(f"\nDataset statistics:")
        print(f"  Unique sentences: {df['sentence'].nunique()}")
        print(f"  Unique aspects: {df['aspect_term'].nunique()}")
        print(f"  Sentiment distribution:")
        print(df['sentiment'].value_counts().to_string())
        return df

    print("✗ No records extracted")
    return None


def save_processed_dataset(df, output_path='data/semeval_2016_absa.csv'):
    """Save processed dataset to CSV."""
    if df is None:
        return None
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Dataset saved to: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f}KB")
    
    return output_path


def main():
    """Main function."""
    
    print("\n" + "="*70)
    print("SEMEVAL-2016 ABSA DATASET DOWNLOADER & PROCESSOR")
    print("="*70)
    
    try:
        dataset_path = find_source_directory()
    except FileNotFoundError as exc:
        print(f"\n✗ {exc}")
        return
    
    # Explore structure
    explore_dataset(dataset_path)
    
    # Process XML files
    df = process_xml_files(dataset_path)
    
    if df is not None:
        # Save as CSV
        csv_path = save_processed_dataset(df, 'data/semeval_2016_absa.csv')
        save_processed_dataset(df, 'data/semeval_2014_absa.csv')
        
        # Show sample
        print("\n" + "="*60)
        print("SAMPLE DATA")
        print("="*60)
        print(df.head(10).to_string(index=False))
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print(f"""
Now you can train models with the real SemEval-2016 dataset:

python train.py --data-path {csv_path} --train-basic
python train.py --data-path {csv_path} --train-advanced --epochs 5

Or use it with the web app!
        """)
    else:
        print("\n⚠️  Could not process dataset")
        print("The dataset might be in a different format")
        print("Try exploring the dataset manually at:", dataset_path)


if __name__ == "__main__":
    main()
