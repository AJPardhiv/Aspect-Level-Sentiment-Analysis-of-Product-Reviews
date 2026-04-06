"""
Training script for Aspect-Level Sentiment Analysis models.
Trains both BasicModel and AdvancedModel.
"""

import sys
import argparse
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

from preprocess import TextPreprocessor
from model import BasicModel
from model import AdvancedModel, TORCH_AVAILABLE

ADVANCED_MODEL_AVAILABLE = TORCH_AVAILABLE

from utils import DataLoader, ModelEvaluator, SentimentMapper, print_metrics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_data(data_path: str = None, use_sample: bool = True) -> pd.DataFrame:
    """
    Load training data.
    
    Args:
        data_path: Path to dataset (CSV or JSON)
        use_sample: Use sample dataset if available
        
    Returns:
        pd.DataFrame: Dataset
    """
    if use_sample:
        logger.info("Loading sample dataset...")
        return DataLoader.create_sample_dataset()

    # If no explicit path is provided, prefer SemEval if present.
    if data_path is None:
        semeval_path = "data/semeval_2014_absa.csv"
        if os.path.exists(semeval_path):
            logger.info(f"No data path provided. Using SemEval dataset: {semeval_path}")
            return DataLoader.load_csv(semeval_path)
        logger.warning("No SemEval dataset found. Falling back to sample dataset.")
        return DataLoader.create_sample_dataset()

    if not os.path.exists(data_path):
        logger.warning(f"Dataset not found at {data_path}. Falling back to sample dataset.")
        return DataLoader.create_sample_dataset()

    logger.info(f"Loading data from {data_path}...")
    if data_path.endswith('.csv'):
        return DataLoader.load_csv(data_path)
    elif data_path.endswith('.json'):
        return DataLoader.load_json(data_path)
    else:
        raise ValueError("Unsupported file format")


def prepare_data(df: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.1):
    """
    Prepare train/val/test splits.
    
    Args:
        df: Input dataframe
        test_size: Test set fraction
        val_size: Validation set fraction (from train)
        
    Returns:
        tuple: (X_train, X_val, X_test, y_train, y_val, y_test, aspects_train, aspects_val, aspects_test)
    """
    # Separate features and labels
    X = df['sentence'].values
    y = df['sentiment'].values
    aspects = df['aspect_term'].values
    
    # Check if stratification is possible
    min_class_count = pd.Series(y).value_counts().min()
    stratify_split = y if min_class_count >= 2 else None
    
    # Split train/test
    X_train, X_test, y_train, y_test, aspects_train, aspects_test = train_test_split(
        X, y, aspects,
        test_size=test_size,
        random_state=42,
        stratify=stratify_split
    )
    
    # Check if stratification is possible for val split
    min_train_class_count = pd.Series(y_train).value_counts().min()
    stratify_split_train = y_train if min_train_class_count >= 2 else None
    
    # Split train/val
    X_train, X_val, y_train, y_val, aspects_train, aspects_val = train_test_split(
        X_train, y_train, aspects_train,
        test_size=val_size,
        random_state=42,
        stratify=stratify_split_train
    )
    
    logger.info(f"Train set: {len(X_train)} samples")
    logger.info(f"Val set: {len(X_val)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    logger.info(f"Class distribution in train: {pd.Series(y_train).value_counts().to_dict()}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test, aspects_train, aspects_val, aspects_test


def train_basic_model(X_train, X_val, y_train, y_val, save_path: str = "saved_model/basic_model.pkl"):
    """
    Train basic model.
    
    Args:
        X_train: Training texts
        X_val: Validation texts
        y_train: Training labels
        y_val: Validation labels
        save_path: Path to save model
        
    Returns:
        BasicModel: Trained model
    """
    logger.info("\n" + "="*60)
    logger.info("TRAINING BASIC MODEL (TF-IDF + Logistic Regression)")
    logger.info("="*60)
    
    model = BasicModel(max_features=5000, use_preprocessing=True)
    
    metrics = model.train(X_train, y_train, X_val, y_val)
    print_metrics(metrics, "Basic Model Training Metrics")
    
    # Save
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    model.save(save_path)
    logger.info(f"Model saved to {save_path}")
    
    return model


def train_advanced_model(X_train, X_val, y_train, y_val,
                        aspects_train, aspects_val,
                        save_path: str = "saved_model/advanced_model",
                        epochs: int = 3, batch_size: int = 16):
    """
    Train advanced BERT model.
    
    Args:
        X_train: Training texts
        X_val: Validation texts
        y_train: Training labels
        y_val: Validation labels
        aspects_train: Training aspects
        aspects_val: Validation aspects
        save_path: Path to save model
        epochs: Number of training epochs
        batch_size: Batch size
        
    Returns:
        AdvancedModel: Trained model
    """
    logger.info("\n" + "="*60)
    logger.info("TRAINING ADVANCED MODEL (Fine-tuned BERT)")
    logger.info("="*60)
    
    model = AdvancedModel(model_name='bert-base-uncased')
    
    metrics = model.train(
        X_train, aspects_train, y_train,
        X_val, aspects_val, y_val,
        epochs=epochs,
        batch_size=batch_size
    )
    
    print_metrics(metrics, "Advanced Model Training Metrics")
    
    # Save
    model.save(save_path)
    logger.info(f"Model saved to {save_path}")
    
    return model


def evaluate_on_test_set(model, X_test, y_test, aspects_test, model_type: str = "basic"):
    """
    Evaluate model on test set.
    
    Args:
        model: Trained model
        X_test: Test texts
        y_test: True labels
        aspects_test: Test aspects
        model_type: 'basic' or 'advanced'
    """
    logger.info(f"\nEvaluating {model_type.upper()} model on test set...")
    
    if model_type == "basic":
        predictions, confidences = model.predict(X_test)
    else:  # advanced
        predictions, confidences = model.predict(X_test, aspects_test)
    
    # Compute metrics
    evaluator = ModelEvaluator()
    
    # Map labels to indices for evaluation
    sentiment_mapper = SentimentMapper(list(set(y_test)))
    y_test_encoded = sentiment_mapper.encode_labels(y_test)
    y_pred_encoded = sentiment_mapper.encode_labels(predictions)
    
    metrics = evaluator.compute_metrics(y_test_encoded, y_pred_encoded)
    print_metrics(metrics, f"{model_type.upper()} Model Test Metrics")
    
    # Print detailed report
    logger.info(evaluator.classification_report(y_test_encoded, y_pred_encoded,
                                               labels=sentiment_mapper.labels))
    
    # Save predictions
    results_df = pd.DataFrame({
        'text': X_test,
        'aspect': aspects_test,
        'true_sentiment': y_test,
        'predicted_sentiment': predictions,
        'confidence': confidences
    })
    
    results_df.to_csv(f"logs/{model_type}_model_predictions.csv", index=False)
    logger.info(f"Predictions saved to logs/{model_type}_model_predictions.csv")
    
    return results_df


def main(args):
    """Main training pipeline."""
    
    logger.info("="*60)
    logger.info("ASPECT-LEVEL SENTIMENT ANALYSIS - TRAINING PIPELINE")
    logger.info("="*60)
    
    # If user provided explicit data path, do not force sample.
    if args.data_path:
        args.use_sample = False

    # Check if AdvancedModel is available
    if args.train_advanced and not ADVANCED_MODEL_AVAILABLE:
        logger.warning("AdvancedModel (BERT) requires PyTorch, which is not available.")
        logger.warning("Falling back to BasicModel (TF-IDF + Logistic Regression)")
        args.train_advanced = False
        args.train_basic = True
    
    # Load data
    df = load_data(args.data_path, args.use_sample)
    
    # Prepare splits
    X_train, X_val, X_test, y_train, y_val, y_test, aspects_train, aspects_val, aspects_test = prepare_data(
        df,
        test_size=args.test_size,
        val_size=args.val_size
    )
    
    # Train basic model
    if args.train_basic:
        try:
            basic_model = train_basic_model(X_train, X_val, y_train, y_val)
            evaluate_on_test_set(basic_model, X_test, y_test, aspects_test, "basic")
        except Exception as e:
            logger.error(f"Error training basic model: {e}")
            if not args.train_advanced:
                raise
    
    # Train advanced model
    if args.train_advanced:
        try:
            advanced_model = train_advanced_model(
                X_train, X_val, y_train, y_val,
                aspects_train, aspects_val,
                epochs=args.epochs,
                batch_size=args.batch_size
            )
            evaluate_on_test_set(advanced_model, X_test, y_test, aspects_test, "advanced")
        except Exception as e:
            logger.error(f"Error training advanced model: {e}")
            if not args.train_basic:
                raise
    
    logger.info("\n" + "="*60)
    logger.info("TRAINING COMPLETED!")
    logger.info("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ABSA models")
    
    parser.add_argument('--data-path', type=str, default=None,
                       help='Path to dataset (CSV or JSON)')
    parser.add_argument('--use-sample', action='store_true', default=False,
                       help='Use sample dataset')
    parser.add_argument('--train-basic', action='store_true', default=False,
                       help='Train basic model')
    parser.add_argument('--train-advanced', action='store_true', default=False,
                       help='Train advanced model (requires GPU)')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set fraction')
    parser.add_argument('--val-size', type=float, default=0.1,
                       help='Validation set fraction')
    parser.add_argument('--epochs', type=int, default=3,
                       help='Number of training epochs for advanced model')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size for advanced model')
    
    args = parser.parse_args()

    # Default behavior when no explicit train flags are provided.
    if not args.train_basic and not args.train_advanced:
        args.train_basic = True

    # If no data source supplied, prefer SemEval if available inside load_data().
    
    main(args)
