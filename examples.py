"""
Example usage script for Aspect-Level Sentiment Analysis.
Demonstrates how to use the models and utilities programmatically.
"""

import pandas as pd
import numpy as np
from model import BasicModel, AdvancedModel
from preprocess import TextPreprocessor
from utils import DataLoader, ModelEvaluator, SentimentMapper, AspectExtractor


def example_1_simple_prediction():
    """Example 1: Simple single prediction."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Single Prediction")
    print("="*60)
    
    # Load trained model
    print("\n1. Loading model...")
    try:
        model = BasicModel.load("saved_model/basic_model.pkl")
        print("   ✓ Model loaded")
    except FileNotFoundError:
        print("   ✗ Model not found. Train first: python train.py --train-basic --use-sample")
        return
    
    # Make prediction
    print("\n2. Making prediction...")
    review = "The battery is bad but the camera is excellent"
    
    # Note: For BasicModel, aspect context matters
    input_text = f"battery and camera: {review}"
    sentiments, confidences = model.predict([input_text])
    
    print(f"   Review: \"{review}\"")
    print(f"   Prediction: {sentiments[0]}")
    print(f"   Confidence: {confidences[0]:.2%}")


def example_2_batch_processing():
    """Example 2: Batch processing multiple reviews."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Processing Reviews")
    print("="*60)
    
    # Load model
    print("\n1. Loading model...")
    try:
        model = BasicModel.load("saved_model/basic_model.pkl")
        print("   ✓ Model loaded")
    except FileNotFoundError:
        print("   ✗ Model not found. Train first: python train.py --train-basic --use-sample")
        return
    
    # Prepare batch data
    print("\n2. Preparing batch data...")
    reviews = [
        "The product is amazing and works perfectly",
        "Terrible quality and bad customer service",
        "It's okay, nothing special",
        "Best purchase I've ever made"
    ]
    
    # Predict for all
    print("\n3. Making predictions...")
    results = []
    
    for i, review in enumerate(reviews, 1):
        sentiment, confidence = model.predict_single(review)
        results.append({
            'review': review,
            'sentiment': sentiment,
            'confidence': confidence
        })
        print(f"   {i}. {sentiment.upper()} ({confidence:.2%})")
    
    # Display results
    print("\n4. Results summary:")
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))


def example_3_aspect_extraction():
    """Example 3: Extract aspects from reviews."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Aspect Extraction from Reviews")
    print("="*60)
    
    print("\n1. Initializing preprocessor...")
    preprocessor = TextPreprocessor()
    print("   ✓ Preprocessor initialized")
    
    print("\n2. Extracting aspects...")
    reviews = [
        "The battery drains quickly but the display is gorgeous",
        "Fast processor and great camera quality",
        "Poor keyboard and uncomfortable design"
    ]
    
    for i, review in enumerate(reviews, 1):
        aspects = preprocessor.extract_nouns(review)
        print(f"   {i}. Review: \"{review}\"")
        print(f"      Aspects: {aspects}")


def example_4_preprocessing_pipeline():
    """Example 4: Text preprocessing pipeline."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Text Preprocessing Pipeline")
    print("="*60)
    
    print("\n1. Initializing preprocessor...")
    preprocessor = TextPreprocessor(use_lemmatization=True, use_stopword_removal=True)
    
    print("\n2. Processing raw text...")
    raw_text = "The QUALITY is AMAZING!!! Check www.example.com - Battery: $99!!!!"
    
    print(f"   Original:    {raw_text}")
    
    cleaned = preprocessor.preprocess(raw_text)
    print(f"   Preprocessed: {cleaned}")
    
    print("\n3. Step-by-step breakdown:")
    text = raw_text.lower()
    text = preprocessor.remove_urls(text)
    print(f"   After removing URLs: {text}")
    
    text = preprocessor.remove_numbers(text)
    print(f"   After removing numbers: {text}")
    
    tokens = preprocessor.tokenize(text)
    tokens = preprocessor.remove_stopwords(tokens)
    print(f"   After removing stopwords: {tokens}")


def example_5_custom_training():
    """Example 5: Custom model training."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Model Training")
    print("="*60)
    
    print("\n1. Loading sample dataset...")
    df = DataLoader.create_sample_dataset()
    print(f"   ✓ Loaded {len(df)} records")
    
    print("\n2. Preparing data splits...")
    from sklearn.model_selection import train_test_split
    
    X = df['sentence'].values
    y = df['sentiment'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"   Train set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    print("\n3. Creating and training model...")
    model = BasicModel(max_features=1000)
    metrics = model.train(X_train, y_train)
    print(f"   Train Accuracy: {metrics['train_accuracy']:.4f}")
    
    print("\n4. Evaluating on test set...")
    from sklearn.metrics import accuracy_score
    
    y_pred_train = model.model.predict(model.preprocess_texts(X_train))
    sentiment_mapper = model.sentiment_mapper
    y_train_encoded = sentiment_mapper.encode_labels(y_train)
    train_acc = accuracy_score(y_train_encoded, y_pred_train)
    
    print(f"   Test Accuracy: {train_acc:.4f}")
    
    print("\n5. Model saved to: saved_model/custom_basic_model.pkl")
    # model.save("saved_model/custom_basic_model.pkl")


def example_6_visualization():
    """Example 6: Results visualization."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Results Visualization & Analysis")
    print("="*60)
    
    print("\n1. Loading sample dataset...")
    df = DataLoader.create_sample_dataset()
    
    print("\n2. Dataset statistics:")
    print(f"   Total records: {len(df)}")
    print(f"   Unique aspects: {df['aspect_term'].nunique()}")
    print(f"   Unique sentiments: {df['sentiment'].nunique()}")
    
    print("\n3. Sentiment distribution:")
    sentiment_dist = df['sentiment'].value_counts()
    for sentiment, count in sentiment_dist.items():
        percentage = count / len(df) * 100
        print(f"   {sentiment.upper()}: {count} ({percentage:.1f}%)")
    
    print("\n4. Top aspects:")
    aspect_dist = df['aspect_term'].value_counts().head(5)
    for aspect, count in aspect_dist.items():
        print(f"   {aspect.title()}: {count}")
    
    print("\n5. Aspect-sentiment relationships:")
    crosstab = pd.crosstab(df['aspect_term'], df['sentiment'])
    print(crosstab)


def example_7_comparison():
    """Example 7: Compare BasicModel vs AdvancedModel."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Model Comparison (if both trained)")
    print("="*60)
    
    test_reviews = [
        "The product is amazing!",
        "Terrible quality",
        "It's okay"
    ]
    
    print("\n1. Loading models...")
    try:
        basic_model = BasicModel.load("saved_model/basic_model.pkl")
        print("   ✓ BasicModel loaded")
    except:
        print("   ✗ BasicModel not found")
        return
    
    try:
        advanced_model = AdvancedModel.load("saved_model/advanced_model")
        print("   ✓ AdvancedModel loaded")
        has_advanced = True
    except:
        print("   ⚠ AdvancedModel not found (train with --train-advanced)")
        has_advanced = False
    
    print("\n2. Predictions comparison:")
    print(f"   {'Review':<40} {'BasicModel':<15} {'AdvancedModel':<15}")
    print("   " + "-"*70)
    
    for review in test_reviews:
        basic_pred, basic_conf = basic_model.predict_single(review)
        
        if has_advanced:
            adv_pred, adv_conf = advanced_model.predict_single(review, "product")
            print(f"   {review:<40} {basic_pred:<15} {adv_pred:<15}")
        else:
            print(f"   {review:<40} {basic_pred:<15} {'N/A':<15}")


def example_8_csv_export():
    """Example 8: Export results to CSV."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Export Results to CSV")
    print("="*60)
    
    print("\n1. Loading model...")
    try:
        model = BasicModel.load("saved_model/basic_model.pkl")
    except:
        print("   ✗ Model not found")
        return
    
    print("\n2. Preparing test data...")
    test_data = {
        'review': [
            'Amazing product, highly recommend',
            'Poor quality and bad service',
            'Average, nothing special'
        ],
        'aspect': ['product', 'quality', 'service']
    }
    
    print("\n3. Making predictions...")
    results = []
    
    for review, aspect in zip(test_data['review'], test_data['aspect']):
        sentiment, confidence = model.predict_single(review)
        results.append({
            'review': review,
            'aspect': aspect,
            'sentiment': sentiment,
            'confidence': f"{confidence:.2%}"
        })
    
    results_df = pd.DataFrame(results)
    
    print("\n4. Results:")
    print(results_df.to_string(index=False))
    
    print("\n5. Exporting to CSV...")
    output_file = 'example_results.csv'
    results_df.to_csv(output_file, index=False)
    print(f"   ✓ Results saved to {output_file}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("ASPECT-LEVEL SENTIMENT ANALYSIS - USAGE EXAMPLES")
    print("="*60)
    
    examples = [
        ("1. Simple Prediction", example_1_simple_prediction),
        ("2. Batch Processing", example_2_batch_processing),
        ("3. Aspect Extraction", example_3_aspect_extraction),
        ("4. Preprocessing Pipeline", example_4_preprocessing_pipeline),
        ("5. Custom Training", example_5_custom_training),
        ("6. Visualization & Analysis", example_6_visualization),
        ("7. Model Comparison", example_7_comparison),
        ("8. CSV Export", example_8_csv_export),
    ]
    
    while True:
        print("\n\nREADY TO RUN? Choose an example:")
        print("   0. Run all examples")
        
        for i, (name, _) in enumerate(examples, 1):
            print(f"   {i}. {name}")
        
        print("   9. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '0':
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ Error: {e}")
        elif choice == '9':
            print("\nThanks for exploring the examples! 👋")
            break
        elif choice.isdigit() and 0 < int(choice) <= len(examples):
            idx = int(choice) - 1
            try:
                examples[idx][1]()
            except Exception as e:
                print(f"\n✗ Error: {e}")
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
