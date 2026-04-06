"""
Dataset utility module for loading sample and SemEval datasets.
Provides unified interface for both datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DatasetManager:
    """Unified dataset manager for sample and SemEval data."""
    
    @staticmethod
    def get_available_datasets() -> dict:
        """Get list of available datasets."""
        datasets = {
            'sample': {
                'path': None,  # Generated on-the-fly
                'size': 20,
                'domains': ['electronics', 'food', 'service'],
                'description': 'Built-in sample dataset (20 records)'
            }
        }
        
        # Check if SemEval dataset exists
        semeval_path = Path('data/semeval_2016_absa.csv')
        legacy_path = Path('data/semeval_2014_absa.csv')
        if semeval_path.exists():
            size = len(pd.read_csv(semeval_path))
            datasets['semeval'] = {
                'path': str(semeval_path),
                'size': size,
                'domains': ['restaurants', 'laptops'],
                'description': f'SemEval-2016 ABSA dataset ({size} records)'
            }
        elif legacy_path.exists():
            size = len(pd.read_csv(legacy_path))
            datasets['semeval'] = {
                'path': str(legacy_path),
                'size': size,
                'domains': ['restaurants', 'laptops'],
                'description': f'Legacy SemEval ABSA dataset ({size} records)'
            }
        else:
            datasets['semeval'] = {
                'path': None,
                'size': None,
                'domains': ['restaurants', 'laptops'],
                'description': 'SemEval-2016 ABSA dataset (not prepared yet)'
            }
        
        return datasets
    
    @staticmethod
    def load_dataset(dataset_name: str = 'sample') -> pd.DataFrame:
        """
        Load a dataset by name.
        
        Args:
            dataset_name: 'sample' or 'semeval'
            
        Returns:
            pd.DataFrame: Loaded dataset
        """
        if dataset_name == 'sample':
            logger.info("Loading sample dataset...")
            from utils import DataLoader
            return DataLoader.create_sample_dataset()
        
        elif dataset_name == 'semeval':
            semeval_path = Path('data/semeval_2016_absa.csv')
            if not semeval_path.exists():
                semeval_path = Path('data/semeval_2014_absa.csv')
            
            if not semeval_path.exists():
                raise FileNotFoundError(
                    f"SemEval dataset not found at {semeval_path}\n"
                    f"Download it using: python download_semeval_dataset.py"
                )
            
            logger.info(f"Loading SemEval dataset from {semeval_path}...")
            df = pd.read_csv(semeval_path)
            logger.info(f"Loaded {len(df)} records")
            return df
        
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
    
    @staticmethod
    def print_dataset_info(df: pd.DataFrame, name: str = "Dataset"):
        """Print dataset information."""
        print(f"\n{'='*60}")
        print(f"{name.upper()}")
        print(f"{'='*60}")
        
        print(f"Total records: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        
        if 'sentence' in df.columns:
            print(f"Unique sentences: {df['sentence'].nunique()}")
        
        if 'aspect_term' in df.columns:
            print(f"Unique aspects: {df['aspect_term'].nunique()}")
        
        if 'sentiment' in df.columns:
            print(f"\nSentiment distribution:")
            print(df['sentiment'].value_counts().to_string())
        
        print(f"{'='*60}\n")
    
    @staticmethod
    def create_comparison_split(
        dataset_name: str = 'sample',
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Create train/val/test splits for comparison.
        
        Args:
            dataset_name: Dataset to use
            test_size: Test set fraction
            val_size: Validation set fraction
            random_state: Random seed
            
        Returns:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        from sklearn.model_selection import train_test_split
        
        df = DatasetManager.load_dataset(dataset_name)
        
        X = df['sentence'].values
        y = df['sentiment'].values
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        # Split train/val
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train,
            test_size=val_size / (1 - test_size),
            random_state=random_state,
            stratify=y_train
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test


def print_available_datasets():
    """Print all available datasets."""
    datasets = DatasetManager.get_available_datasets()
    
    print("\n" + "="*60)
    print("AVAILABLE DATASETS")
    print("="*60 + "\n")
    
    for name, info in datasets.items():
        status = "✓" if info['path'] else "✗"
        print(f"{status} {name.upper()}")
        print(f"  Description: {info['description']}")
        print(f"  Domains: {', '.join(info['domains'])}")
        
        if info['size']:
            print(f"  Records: {info['size']}")
        
        if not info['path']:
            print(f"  Setup: Run 'python download_semeval_dataset.py'")
        
        print()
    
    print("="*60 + "\n")


def compare_models_on_datasets():
    """Compare models on different datasets."""
    from model import BasicModel
    from sklearn.metrics import accuracy_score
    from utils import SentimentMapper
    
    print("\n" + "="*60)
    print("COMPARING MODELS ON DATASETS")
    print("="*60 + "\n")
    
    datasets_to_test = ['sample']
    
    # Check if SemEval exists
    if Path('data/semeval_2016_absa.csv').exists():
        datasets_to_test.append('semeval')
    elif Path('data/semeval_2014_absa.csv').exists():
        datasets_to_test.append('semeval')
    
    # Load model
    try:
        model = BasicModel.load('saved_model/basic_model.pkl')
    except FileNotFoundError:
        print("✗ Model not found. Train first: python train.py --train-basic --use-sample")
        return
    
    results = []
    
    for dataset_name in datasets_to_test:
        print(f"Testing on {dataset_name} dataset...")
        
        # Load data
        df = DatasetManager.load_dataset(dataset_name)
        X = df['sentence'].values
        y = df['sentiment'].values
        
        # Predict
        predictions, confidences = model.predict(X)
        
        # Calculate accuracy
        sentiment_mapper = model.sentiment_mapper
        y_encoded = sentiment_mapper.encode_labels(y)
        y_pred_encoded = sentiment_mapper.encode_labels(predictions)
        accuracy = accuracy_score(y_encoded, y_pred_encoded)
        
        results.append({
            'Dataset': dataset_name.upper(),
            'Records': len(df),
            'Accuracy': f"{accuracy:.2%}",
            'Avg Confidence': f"{confidences.mean():.2%}"
        })
        
        print(f"  ✓ Accuracy: {accuracy:.2%}")
        print(f"  ✓ Avg Confidence: {confidences.mean():.2%}\n")
    
    # Display results
    print("="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    print()


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("DATASET MANAGER UTILITY")
    print("="*60)
    
    # Show available datasets
    print_available_datasets()
    
    # Try loading sample
    print("Loading sample dataset...")
    df_sample = DatasetManager.load_dataset('sample')
    DatasetManager.print_dataset_info(df_sample, "Sample Dataset")
    
    # Try loading SemEval
    print("Checking for SemEval dataset...")
    try:
        df_semeval = DatasetManager.load_dataset('semeval')
        DatasetManager.print_dataset_info(df_semeval, "SemEval Dataset")
    except FileNotFoundError as e:
        print(f"⚠️  {e}\n")
    
    # Compare models if available
    try:
        compare_models_on_datasets()
    except Exception as e:
        print(f"Model comparison skipped: {e}\n")
