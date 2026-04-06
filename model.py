"""
Machine Learning models for Aspect-Level Sentiment Analysis.
Implements:
- BasicModel: TF-IDF + Logistic Regression
- AdvancedModel: Fine-tuned BERT
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Union
from pathlib import Path
import warnings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Conditionally import PyTorch (only needed for AdvancedModel)
torch = None
nn = None
Dataset = None
DataLoader = None
AutoTokenizer = None
AutoModel = None
AdamW = None
get_linear_schedule_with_warmup = None

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoTokenizer, AutoModel, AdamW, get_linear_schedule_with_warmup
except (ImportError, OSError):
    pass  # PyTorch/transformers not available, BasicModel will still work

TORCH_AVAILABLE = (
    torch is not None and nn is not None and Dataset is not None and
    DataLoader is not None and AutoTokenizer is not None and AutoModel is not None
)

from preprocess import TextPreprocessor
from utils import ModelSerializer, SentimentMapper

warnings.filterwarnings('ignore')


class BasicModel:
    """TF-IDF + Logistic Regression model for aspect sentiment classification."""
    
    def __init__(self, max_features: int = 5000, use_preprocessing: bool = True):
        """
        Initialize BasicModel.
        
        Args:
            max_features: Maximum features for TF-IDF
            use_preprocessing: Whether to preprocess text
        """
        self.max_features = max_features
        self.use_preprocessing = use_preprocessing
        self.preprocessor = TextPreprocessor() if use_preprocessing else None
        self.sentiment_mapper = None
        
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'))
        ])
        
        self.is_trained = False
    
    def preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts if enabled."""
        if self.use_preprocessing and self.preprocessor:
            return self.preprocessor.preprocess_batch(texts)
        return texts
    
    def train(self, X_train: List[str], y_train: List[str], 
              X_val: List[str] = None, y_val: List[str] = None) -> Dict:
        """
        Train the model.
        
        Args:
            X_train: Training texts
            y_train: Training labels
            X_val: Validation texts
            y_val: Validation labels
            
        Returns:
            dict: Training metrics
        """
        # Initialize sentiment mapper
        self.sentiment_mapper = SentimentMapper(list(set(y_train)))
        
        # Preprocess
        X_train_processed = self.preprocess_texts(X_train)
        
        # Encode labels
        y_train_encoded = self.sentiment_mapper.encode_labels(y_train)
        
        # Train
        self.model.fit(X_train_processed, y_train_encoded)
        self.is_trained = True
        
        # Compute training metrics
        y_train_pred = self.model.predict(X_train_processed)
        train_accuracy = np.mean(y_train_pred == y_train_encoded)
        
        metrics = {'train_accuracy': train_accuracy}
        
        # Validation metrics if provided
        if X_val is not None and y_val is not None:
            X_val_processed = self.preprocess_texts(X_val)
            y_val_encoded = self.sentiment_mapper.encode_labels(y_val)
            y_val_pred = self.model.predict(X_val_processed)
            val_accuracy = np.mean(y_val_pred == y_val_encoded)
            metrics['val_accuracy'] = val_accuracy
        
        return metrics
    
    def predict(self, texts: List[str]) -> Tuple[List[str], np.ndarray]:
        """
        Predict sentiments.
        
        Args:
            texts: Input texts
            
        Returns:
            tuple: (predicted_labels, confidence_scores)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        X_processed = self.preprocess_texts(texts)
        
        # Get predictions and probabilities
        predictions = self.model.predict(X_processed)
        probabilities = self.model.named_steps['classifier'].predict_proba(
            self.model.named_steps['tfidf'].transform(X_processed)
        )
        confidence = np.max(probabilities, axis=1)
        
        # Decode labels
        predicted_labels = self.sentiment_mapper.decode_labels(predictions)
        
        return predicted_labels, confidence
    
    def predict_single(self, text: str) -> Tuple[str, float]:
        """
        Predict sentiment for a single text.
        
        Args:
            text: Input text
            
        Returns:
            tuple: (predicted_label, confidence_score)
        """
        labels, confidences = self.predict([text])
        return labels[0], confidences[0]
    
    def save(self, filepath: str):
        """Save model."""
        state = {
            'model': self.model,
            'sentiment_mapper': self.sentiment_mapper,
            'max_features': self.max_features,
            'use_preprocessing': self.use_preprocessing
        }
        ModelSerializer.save_model_pickle(state, filepath)
    
    @classmethod
    def load(cls, filepath: str):
        """Load model."""
        state = ModelSerializer.load_model_pickle(filepath)
        
        instance = cls(max_features=state['max_features'],
                      use_preprocessing=state['use_preprocessing'])
        instance.model = state['model']
        instance.sentiment_mapper = state['sentiment_mapper']
        instance.is_trained = True
        
        return instance


# Only define PyTorch-dependent classes if PyTorch is available
if TORCH_AVAILABLE:
    class ABSADataset(Dataset):
        """PyTorch Dataset for ABSA tasks."""
        
        def __init__(self, texts: List[str], aspects: List[str], sentiments: List[str],
                     tokenizer, max_length: int = 128):
            """
            Initialize dataset.
            
            Args:
                texts: Review texts
                aspects: Aspect terms
                sentiments: Sentiment labels
                tokenizer: HuggingFace tokenizer
                max_length: Maximum sequence length
            """
            self.texts = texts
            self.aspects = aspects
            self.sentiments = sentiments
            self.tokenizer = tokenizer
            self.max_length = max_length
            
            # Create sentiment mapper
            self.sentiment_mapper = SentimentMapper(list(set(sentiments)))
            
            # Encode sentiments
            self.sentiment_ids = self.sentiment_mapper.encode_labels(sentiments)
        
        def __len__(self):
            return len(self.texts)
        
        def __getitem__(self, idx):
            """Get item and encode using tokenizer."""
            text = self.texts[idx]
            aspect = self.aspects[idx]
            sentiment_id = self.sentiment_ids[idx]
            
            # Combine text and aspect for better context
            input_text = f"{aspect} [SEP] {text}"
            
            # Tokenize
            encoding = self.tokenizer(
                input_text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            return {
                'input_ids': encoding['input_ids'].squeeze(0),
                'attention_mask': encoding['attention_mask'].squeeze(0),
                'sentiment_id': torch.tensor(sentiment_id, dtype=torch.long)
            }
else:
    # Dummy class when PyTorch not available
    class ABSADataset:
        """Dummy ABSADataset (PyTorch not available)."""
        pass


# Only define PyTorch-dependent classes if PyTorch is available
if TORCH_AVAILABLE:
    class BERTClassifier(nn.Module):
        """BERT-based classifier for aspect sentiment analysis."""
        
        def __init__(self, model_name: str = 'bert-base-uncased', num_classes: int = 3, hidden_dim: int = 768):
            """
            Initialize BERT classifier.
            
            Args:
                model_name: HuggingFace model identifier
                num_classes: Number of sentiment classes
                hidden_dim: Hidden dimension size
            """
            super(BERTClassifier, self).__init__()
            
            self.bert = AutoModel.from_pretrained(model_name)
            self.dropout = nn.Dropout(0.1)
            self.linear = nn.Linear(self.bert.config.hidden_size, num_classes)
        
        def forward(self, input_ids, attention_mask):
            """Forward pass."""
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            pooled_output = outputs.pooler_output
            dropped = self.dropout(pooled_output)
            logits = self.linear(dropped)
            return logits
    
    
    class AdvancedModel:
        """Fine-tuned BERT model for aspect sentiment classification."""
        
        def __init__(self, model_name: str = 'bert-base-uncased', num_classes: int = 3,
                     learning_rate: float = 2e-5, device: str = None):
            """
            Initialize AdvancedModel.
            
            Args:
                model_name: HuggingFace model identifier
                num_classes: Number of sentiment classes
                learning_rate: Learning rate for training
                device: Device to use ('cuda' or 'cpu')
            """
            self.model_name = model_name
            self.num_classes = num_classes
            self.learning_rate = learning_rate
            
            # Device
            if device is None:
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            else:
                self.device = device
            
            # Tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.classifier = BERTClassifier(model_name, num_classes).to(self.device)
            
            self.sentiment_mapper = None
            self.is_trained = False
        
        def train_epoch(self, train_loader, optimizer, scheduler) -> float:
            """Train for one epoch."""
            self.classifier.train()
            total_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                sentiment_ids = batch['sentiment_id'].to(self.device)
                
                optimizer.zero_grad()
                
                logits = self.classifier(input_ids, attention_mask)
                loss = nn.CrossEntropyLoss()(logits, sentiment_ids)
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.classifier.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                
                total_loss += loss.item()
            
            return total_loss / len(train_loader)
        
        @torch.no_grad()
        def evaluate(self, val_loader) -> float:
            """Evaluate on validation set."""
            self.classifier.eval()
            correct = 0
            total = 0
            
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                sentiment_ids = batch['sentiment_id'].to(self.device)
                
                logits = self.classifier(input_ids, attention_mask)
                predictions = torch.argmax(logits, dim=1)
                
                correct += (predictions == sentiment_ids).sum().item()
                total += sentiment_ids.size(0)
            
            return correct / total if total > 0 else 0.0
        
        def train(self, X_train: List[str], aspects_train: List[str], y_train: List[str],
                  X_val: List[str] = None, aspects_val: List[str] = None, y_val: List[str] = None,
                  epochs: int = 3, batch_size: int = 32) -> Dict:
            """
            Train the model.
            
            Args:
                X_train: Training texts
                aspects_train: Training aspects
                y_train: Training labels
                X_val: Validation texts
                aspects_val: Validation aspects
                y_val: Validation labels
                epochs: Number of epochs
                batch_size: Batch size
                
            Returns:
                dict: Training metrics
            """
            # Initialize sentiment mapper
            self.sentiment_mapper = SentimentMapper(list(set(y_train)))
            
            # Create datasets
            train_dataset = ABSADataset(X_train, aspects_train, y_train, self.tokenizer)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            
            # Optimizer and scheduler
            optimizer = AdamW(self.classifier.parameters(), lr=self.learning_rate)
            total_steps = len(train_loader) * epochs
            scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=0,
                num_training_steps=total_steps
            )
            
            # Training loop
            train_losses = []
            val_accuracies = []
            
            for epoch in range(epochs):
                # Train
                train_loss = self.train_epoch(train_loader, optimizer, scheduler)
                train_losses.append(train_loss)
                
                # Validate
                if X_val is not None and y_val is not None:
                    val_dataset = ABSADataset(X_val, aspects_val, y_val, self.tokenizer)
                    val_loader = DataLoader(val_dataset, batch_size=batch_size)
                    val_accuracy = self.evaluate(val_loader)
                    val_accuracies.append(val_accuracy)
                    print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Val Accuracy: {val_accuracy:.4f}")
                else:
                    print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f}")
            
            self.is_trained = True
            
            # Return metrics
            metrics = {'train_losses': train_losses}
            if val_accuracies:
                metrics['val_accuracies'] = val_accuracies
                metrics['best_val_accuracy'] = max(val_accuracies)
            
            return metrics
        
        @torch.no_grad()
        def predict(self, texts: List[str], aspects: List[str]) -> Tuple[List[str], np.ndarray]:
            """
            Predict sentiments.
            
            Args:
                texts: Input texts
                aspects: Aspect terms
                
            Returns:
                tuple: (predicted_labels, confidence_scores)
            """
            if not self.is_trained:
                raise ValueError("Model not trained. Call train() first.")
            
            self.classifier.eval()
            
            # Create dataset (without true labels)
            input_texts = [f"{aspect} [SEP] {text}" for text, aspect in zip(texts, aspects)]
            
            predictions_list = []
            confidences_list = []
            
            for input_text in input_texts:
                encoding = self.tokenizer(
                    input_text,
                    max_length=128,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                
                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                
                logits = self.classifier(input_ids, attention_mask)
                probabilities = torch.softmax(logits, dim=1)
                
                prediction = torch.argmax(logits, dim=1).item()
                confidence = probabilities.max().item()
                
                predictions_list.append(prediction)
                confidences_list.append(confidence)
            
            # Decode labels
            predicted_labels = self.sentiment_mapper.decode_labels(np.array(predictions_list))
            confidences = np.array(confidences_list)
            
            return predicted_labels, confidences
        
        def predict_single(self, text: str, aspect: str) -> Tuple[str, float]:
            """Predict for single text-aspect pair."""
            labels, confidences = self.predict([text], [aspect])
            return labels[0], confidences[0]
        
        def save(self, filepath: str):
            """Save model."""
            Path(filepath).mkdir(parents=True, exist_ok=True)
            self.classifier.save_pretrained(filepath)
            self.tokenizer.save_pretrained(filepath)
            
            # Save metadata
            metadata = {
                'model_name': self.model_name,
                'num_classes': self.num_classes,
                'sentiment_mapper': self.sentiment_mapper,
            }
            ModelSerializer.save_model_pickle(metadata, f"{filepath}/metadata.pkl")
        
        @classmethod
        def load(cls, filepath: str, device: str = None):
            """Load model."""
            instance = cls(model_name='bert-base-uncased', device=device)
            instance.classifier = BERTClassifier('bert-base-uncased').to(instance.device)
            instance.classifier.load_state_dict(torch.load(f"{filepath}/pytorch_model.bin", map_location=instance.device))
            instance.tokenizer = AutoTokenizer.from_pretrained(filepath)
            
            metadata = ModelSerializer.load_model_pickle(f"{filepath}/metadata.pkl")
            instance.sentiment_mapper = metadata['sentiment_mapper']
            instance.is_trained = True
            
            return instance
else:
    # Dummy classes when PyTorch not available
    class BERTClassifier:
        """Dummy BERTClassifier (PyTorch not available)."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch/Transformers unavailable. Install dependencies for AdvancedModel.")
    
    class AdvancedModel:
        """Dummy AdvancedModel (PyTorch not available)."""
        def __init__(self, *args, **kwargs):
            raise ImportError("AdvancedModel unavailable because PyTorch could not be loaded.")


if __name__ == "__main__":
    # Test BasicModel
    print("Testing BasicModel...\n")
    
    texts = [
        "The battery is bad but the camera is excellent",
        "Great food and friendly staff",
        "The display is beautiful but battery life is poor"
    ]
    aspects = ["battery", "camera", "food"]
    sentiments = ["negative", "positive", "positive"]
    
    basic_model = BasicModel()
    metrics = basic_model.train(texts, sentiments)
    print(f"Training metrics: {metrics}\n")
    
    predicted, confidence = basic_model.predict_single("The battery is amazing")
    print(f"Prediction: {predicted}, Confidence: {confidence:.4f}\n")
    
    # Model info
    print(f"BasicModel created successfully!")
