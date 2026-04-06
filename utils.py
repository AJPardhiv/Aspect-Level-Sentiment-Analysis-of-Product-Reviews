"""
Utility functions for Aspect-Level Sentiment Analysis.
Includes data loading, model evaluation, and visualization helpers.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Any
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns


class DataLoader:
    """Handles loading and processing of ABSA datasets."""
    
    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """Load CSV dataset."""
        return pd.read_csv(filepath)
    
    @staticmethod
    def load_json(filepath: str) -> List[Dict]:
        """Load JSON dataset."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def create_sample_dataset() -> pd.DataFrame:
        """
        Create a sample SemEval ABSA-like dataset for testing.
        
        Returns:
            pd.DataFrame: Sample dataset with columns: sentence, aspect, sentiment
        """
        sample_data = [
            {"sentence": "The battery is bad but the camera is excellent", 
             "aspect_term": "battery", "sentiment": "negative"},
            {"sentence": "The battery is bad but the camera is excellent", 
             "aspect_term": "camera", "sentiment": "positive"},
            {"sentence": "Great food and friendly staff", 
             "aspect_term": "food", "sentiment": "positive"},
            {"sentence": "Great food and friendly staff", 
             "aspect_term": "staff", "sentiment": "positive"},
            {"sentence": "The display is beautiful but battery life is poor", 
             "aspect_term": "display", "sentiment": "positive"},
            {"sentence": "The display is beautiful but battery life is poor", 
             "aspect_term": "battery life", "sentiment": "negative"},
            {"sentence": "Excellent product with good build quality", 
             "aspect_term": "product", "sentiment": "positive"},
            {"sentence": "Excellent product with good build quality", 
             "aspect_term": "build quality", "sentiment": "positive"},
            {"sentence": "The price is too high", 
             "aspect_term": "price", "sentiment": "negative"},
            {"sentence": "Service was decent, nothing special", 
             "aspect_term": "service", "sentiment": "neutral"},
            {"sentence": "Amazing camera quality but mediocre performance", 
             "aspect_term": "camera quality", "sentiment": "positive"},
            {"sentence": "Amazing camera quality but mediocre performance", 
             "aspect_term": "performance", "sentiment": "negative"},
            {"sentence": "Poor customer service and bad warranty", 
             "aspect_term": "customer service", "sentiment": "negative"},
            {"sentence": "Poor customer service and bad warranty", 
             "aspect_term": "warranty", "sentiment": "negative"},
            {"sentence": "The interface is intuitive and responsive", 
             "aspect_term": "interface", "sentiment": "positive"},
            {"sentence": "The interface is intuitive and responsive", 
             "aspect_term": "responsiveness", "sentiment": "positive"},
            {"sentence": "Battery drains quickly", 
             "aspect_term": "battery", "sentiment": "negative"},
            {"sentence": "Screen is scratched easily", 
             "aspect_term": "screen", "sentiment": "negative"},
            {"sentence": "Good value for money", 
             "aspect_term": "value", "sentiment": "positive"},
            {"sentence": "The keyboard is uncomfortable", 
             "aspect_term": "keyboard", "sentiment": "negative"},
        ]
        
        return pd.DataFrame(sample_data)
    
    @staticmethod
    def save_dataset(df: pd.DataFrame, filepath: str):
        """Save dataset to CSV."""
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
    
    @staticmethod
    def download_semeval_data(output_dir: str = "./data"):
        """
        Create a note for downloading SemEval ABSA dataset.
        Users can manually download from official source or use this as reference.
        """
        instructions = """
        To use the full SemEval ABSA dataset:
        
        1. Download from: http://alt.qcri.org/semeval2014/task4/
        2. Place XML files in ./data/ folder
        3. Parse using provided load_xml function
        
        For demonstration, sample_dataset is used.
        """
        print(instructions)


class ModelEvaluator:
    """Handles model evaluation and metrics computation."""
    
    @staticmethod
    def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, average: str = 'weighted') -> Dict[str, float]:
        """
        Compute classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method for multi-class metrics
            
        Returns:
            dict: Dictionary with accuracy, precision, recall, f1-score
        """
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
            'f1': f1_score(y_true, y_pred, average=average, zero_division=0)
        }
    
    @staticmethod
    def classification_report(y_true: np.ndarray, y_pred: np.ndarray, labels: List[str] = None) -> str:
        """Generate detailed classification report."""
        return classification_report(y_true, y_pred, target_names=labels, zero_division=0)
    
    @staticmethod
    def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, labels: List[str] = None,
                             title: str = "Confusion Matrix", save_path: str = None):
        """
        Plot and optionally save confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names
            title: Plot title
            save_path: Path to save plot
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels)
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return plt


class ModelSerializer:
    """Handles model saving and loading."""
    
    @staticmethod
    def save_model_pickle(model: Any, filepath: str):
        """Save model using pickle."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {filepath}")
    
    @staticmethod
    def load_model_pickle(filepath: str) -> Any:
        """Load model from pickle."""
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {filepath}")
        return model
    
    @staticmethod
    def save_model_state(model: Any, filepath: str, framework: str = 'sklearn'):
        """
        Save model state (flexible for sklearn or transformers).
        
        Args:
            model: Model object
            filepath: Save path
            framework: 'sklearn' or 'torch'
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if framework == 'sklearn':
            ModelSerializer.save_model_pickle(model, filepath)
        elif framework == 'torch':
            import torch
            torch.save(model.state_dict(), filepath)
            print(f"Model state saved to {filepath}")
    
    @staticmethod
    def load_model_state(filepath: str, model=None, framework: str = 'sklearn'):
        """Load model state (flexible for sklearn or transformers)."""
        if framework == 'sklearn':
            return ModelSerializer.load_model_pickle(filepath)
        elif framework == 'torch':
            import torch
            if model is None:
                raise ValueError("Model object required for torch loading")
            model.load_state_dict(torch.load(filepath))
            return model


class AspectExtractor:
    """Handles aspect extraction strategies."""
    
    @staticmethod
    def extract_from_labels(aspects: List[str]) -> List[str]:
        """Extract aspects directly from labels."""
        return list(set(aspects))
    
    @staticmethod
    def extract_nouns_as_aspects(text: str, nlp=None) -> List[str]:
        """
        Extract nouns from text as aspects.
        
        Args:
            text: Input text
            nlp: spaCy model
            
        Returns:
            list: Extracted nouns
        """
        if nlp is not None:
            doc = nlp(text)
            nouns = [token.text for token in doc if token.pos_ == 'NOUN']
        else:
            import nltk
            tokens = nltk.word_tokenize(text.lower())
            pos_tags = nltk.pos_tag(tokens)
            nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
        
        return nouns


class SentimentMapper:
    """Maps sentiment labels to indices and vice versa."""
    
    def __init__(self, labels: List[str] = None):
        """
        Initialize sentiment mapper.
        
        Args:
            labels: List of sentiment labels (e.g., ['positive', 'negative', 'neutral'])
        """
        if labels is None:
            labels = ['positive', 'negative', 'neutral']
        
        self.labels = sorted(list(set(labels)))
        self.label_to_id = {label: idx for idx, label in enumerate(self.labels)}
        self.id_to_label = {idx: label for label, idx in self.label_to_id.items()}
    
    def label_to_index(self, label: str) -> int:
        """Convert label to index."""
        return self.label_to_id.get(label, 0)
    
    def index_to_label(self, index: int) -> str:
        """Convert index to label."""
        return self.id_to_label.get(index, self.labels[0])
    
    def encode_labels(self, labels: List[str]) -> np.ndarray:
        """Encode list of labels to indices."""
        return np.array([self.label_to_index(label) for label in labels])
    
    def decode_labels(self, indices: np.ndarray) -> List[str]:
        """Decode list of indices to labels."""
        return [self.index_to_label(int(idx)) for idx in indices]
    
    def get_num_classes(self) -> int:
        """Get number of sentiment classes."""
        return len(self.labels)


def print_metrics(metrics: Dict[str, float], title: str = "Model Metrics"):
    """Pretty print metrics."""
    print(f"\n{'='*50}")
    print(f"{title:^50}")
    print(f"{'='*50}")
    for metric, value in metrics.items():
        print(f"{metric.capitalize():.<30} {value:.4f}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # Test utilities
    print("Testing DataLoader...")
    df = DataLoader.create_sample_dataset()
    print(df.head(10))
    
    print("\nTesting SentimentMapper...")
    mapper = SentimentMapper()
    print(f"Labels: {mapper.labels}")
    print(f"Positive -> {mapper.label_to_index('positive')}")
    print(f"Index 1 -> {mapper.index_to_label(1)}")
