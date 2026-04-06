#!/usr/bin/env python3
"""
Lite training script - works without PyTorch/spaCy dependencies
Uses only NLTK for preprocessing
"""

import argparse
import os
import pickle
import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from preprocess import TextPreprocessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BasicModelLite:
    """Simplified TF-IDF + Logistic Regression model"""
    
    def __init__(self, max_features=5000):
        self.preprocessor = TextPreprocessor()
        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.label_mapping = {'positive': 0, 'negative': 1, 'neutral': 2}
        self.inverse_mapping = {v: k for k, v in self.label_mapping.items()}
    
    def train(self, texts, sentiments):
        """Train the model"""
        logger.info(f"Training on {len(texts)} samples")
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        y = np.array([self.label_mapping[s.lower()] for s in sentiments])
        
        # Train model
        self.model.fit(X, y)
        logger.info("✓ Model trained successfully")
    
    def predict(self, texts):
        """Predict on texts"""
        if isinstance(texts, str):
            texts = [texts]
        
        texts = self.preprocessor.preprocess_batch([str(text) for text in texts])
        X = self.vectorizer.transform(texts)
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Convert to labels and confidences
        labels = [self.inverse_mapping[p] for p in predictions]
        confidences = np.max(probabilities, axis=1).tolist()
        
        return labels, confidences
    
    def save(self, path):
        """Save model"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'model': self.model,
                'label_mapping': self.label_mapping,
                'inverse_mapping': self.inverse_mapping
            }, f)
        logger.info(f"✓ Model saved to {path}")
    
    def load(self, path):
        """Load model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.vectorizer = data['vectorizer']
        self.model = data['model']
        self.label_mapping = data['label_mapping']
        self.inverse_mapping = data['inverse_mapping']
        logger.info(f"✓ Model loaded from {path}")


def load_sample_data():
    """Load sample dataset"""
    csv_path = 'data/sample_reviews.csv'
    if not os.path.exists(csv_path):
        logger.error(f"Sample data not found at {csv_path}")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} samples from {csv_path}")
    return df


def train_model_lite(use_sample=True, data_path=None):
    """Train lite model"""
    
    logger.info("=" * 60)
    logger.info("ASPECT-LEVEL SENTIMENT ANALYSIS - LITE TRAINING")
    logger.info("=" * 60)
    
    # Load data
    if use_sample:
        df = load_sample_data()
    elif data_path:
        if not os.path.exists(data_path):
            logger.error(f"Data file not found: {data_path}")
            sys.exit(1)
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} samples from {data_path}")
    else:
        logger.error("Must specify either --use-sample or --data-path")
        sys.exit(1)
    
    # Preprocess with the same negation-aware pipeline used at inference.
    text_col = None
    for col in ['sentence', 'text', 'review', 'content']:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        logger.error(f"No text column found. Available columns: {df.columns.tolist()}")
        sys.exit(1)
    
    preprocessor = TextPreprocessor()
    texts = preprocessor.preprocess_batch([str(t) for t in df[text_col]])
    sentiments = df['sentiment'].tolist() if 'sentiment' in df.columns else df[df.columns[-1]].tolist()
    
    # Split data (don't stratify for small datasets)
    stratify = None if len(set(sentiments)) < 3 or min([sentiments.count(s) for s in set(sentiments)]) < 2 else sentiments
    
    texts_train, texts_test, sentiments_train, sentiments_test = train_test_split(
        texts, sentiments, test_size=0.2, random_state=42, stratify=stratify
    )
    
    logger.info(f"Train set: {len(texts_train)} samples")
    logger.info(f"Test set: {len(texts_test)} samples")
    
    # Train
    logger.info("\nTraining BasicModel (TF-IDF + Logistic Regression)...")
    model = BasicModelLite()
    model.train(texts_train, sentiments_train)
    
    # Evaluate
    logger.info("\nEvaluating on test set...")
    predictions, confidences = model.predict(texts_test)
    
    accuracy = accuracy_score(sentiments_test, predictions)
    precision = precision_score(sentiments_test, predictions, average='weighted', zero_division=0)
    recall = recall_score(sentiments_test, predictions, average='weighted', zero_division=0)
    f1 = f1_score(sentiments_test, predictions, average='weighted', zero_division=0)
    
    logger.info(f"\n{'Metric':<20} {'Score':<10}")
    logger.info(f"{'-'*30}")
    logger.info(f"{'Accuracy':<20} {accuracy:<10.4f}")
    logger.info(f"{'Precision':<20} {precision:<10.4f}")
    logger.info(f"{'Recall':<20} {recall:<10.4f}")
    logger.info(f"{'F1-Score':<20} {f1:<10.4f}")
    
    logger.info(f"\nClassification Report:\n")
    logger.info(classification_report(sentiments_test, predictions))
    
    # Save
    save_path = 'saved_model/basic_model_lite.pkl'
    model.save(save_path)
    
    logger.info("=" * 60)
    logger.info("✓ TRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nNext steps:")
    logger.info(f"1. Run: python predict_lite.py")
    logger.info(f"2. Or: streamlit run app_lite.py")
    
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train BasicModel (Lite Version)')
    parser.add_argument('--use-sample', action='store_true', help='Use sample dataset')
    parser.add_argument('--data-path', type=str, help='Path to CSV dataset')
    parser.add_argument('--epochs', type=int, default=1, help='Number of epochs (ignored for lite model)')
    
    args = parser.parse_args()
    
    if not args.use_sample and not args.data_path:
        args.use_sample = True
    
    train_model_lite(use_sample=args.use_sample, data_path=args.data_path)
