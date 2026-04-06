# Project Document

## Dataset Details

- Dataset-1
   - Name: Sample Aspect-Based Sentiment Dataset
   - Source File: data/sample_reviews.csv
   - Total no of Samples: 91
   - Training Samples: 64
   - Validation Samples: 8
   - Testing Samples: 19

## Labels Format

- Task Type: Aspect-Level Sentiment Classification
- Input Fields:
   - sentence: Full review sentence
   - aspect_term: Target aspect in the sentence
- Output Field:
   - sentiment: Sentiment class for the given aspect

- Sentiment Labels Used:
   - positive (49 samples)
   - negative (41 samples)
   - neutral (1 sample)

## Few Samples of Dataset

| sentence | aspect_term | sentiment |
|---|---|---|
| The battery is bad but the camera is excellent | battery | negative |
| The battery is bad but the camera is excellent | camera | positive |
| Great food and friendly staff | food | positive |
| Service was decent, nothing special | service | neutral |
| Battery lasts all day easily | battery | positive |

## Methodology Architecture

- Approach: Aspect-Level Sentiment Classification
- Model Variants:
   - Basic Pipeline (executed): TF-IDF (1-2 grams) + Logistic Regression
   - Advanced Pipeline (implemented option): Fine-tuned BERT (bert-base-uncased)

- End-to-End Methodology:
   1. Data Loading:
      - Load dataset from CSV/JSON (default: sample dataset)
      - Required fields: sentence, aspect_term, sentiment
   2. Data Splitting:
      - Train/Test split using test_size=0.2
      - Train/Validation split from train set using val_size=0.1
      - Stratified split when class counts allow
   3. Text Preprocessing (Basic Pipeline):
      - Lowercasing
      - URL/email cleanup
      - Special character normalization
      - Tokenization + stopword removal + lemmatization
   4. Feature & Model Training:
      - Basic: TF-IDF vectorization -> Logistic Regression training
      - Advanced: Input as "aspect [SEP] sentence" -> BERT fine-tuning
   5. Evaluation:
      - Validation during training
      - Test-set predictions, confidence scores, and classification metrics
   6. Artifacts:
      - Trained models saved in saved_model/
      - Predictions/reports saved in logs/

- Architecture Flow:

```text
Input Data (sentence, aspect_term, sentiment)
        |
        v
Data Split (train / val / test)
        |
        +------------------------------+
        |                              |
        v                              v
Basic Pipeline                     Advanced Pipeline
(Preprocess -> TF-IDF -> LR)      (aspect [SEP] sentence -> BERT)
        |                              |
        +---------------+--------------+
                        |
                        v
                 Sentiment Prediction
            (positive / negative / neutral)
                        |
                        v
            Metrics + Confidence + Logs
```

## Notes

- Data split is based on training settings in this project (test_size=0.2, val_size=0.1 from remaining train split).
- The dataset is in CSV format with one aspect-sentiment pair per row.
- Technical run note: logged training/evaluation runs in logs/training.log used the built-in sample dataset (20 rows), producing Train/Val/Test = 14/2/4.
- SemEval dataset file data/semeval_2014_absa.csv was not present during logged runs, so fallback-to-sample behavior was triggered.

## Tasks and Results

- Task-1: Dataset Preparation and Label Validation
   - Work done:
      - Loaded Dataset-1 from data/sample_reviews.csv
      - Verified required columns: sentence, aspect_term, sentiment
      - Computed split counts for the configured split setup
   - Results:
      - Total samples: 91
      - Train/Validation/Test: 64 / 8 / 19
      - Label distribution: positive=49, negative=41, neutral=1

- Task-2: Model Training and Test Evaluation (Basic Pipeline)
   - Work done:
      - Trained TF-IDF (1-2 grams) + Logistic Regression model
      - Saved model artifact to saved_model/basic_model.pkl
      - Evaluated on test set and exported predictions
   - Results (from logs/training.log):
      - Executed on built-in sample dataset (20 rows), not on data/sample_reviews.csv
      - Train/Validation/Test used in logged run: 14 / 2 / 4
      - Test accuracy: 0.50
      - Weighted F1-score: 0.33
      - Class-wise performance:
         - Positive: precision=0.50, recall=1.00, f1=0.67
         - Negative: precision=0.00, recall=0.00, f1=0.00
      - Predictions file generated: logs/basic_model_predictions.csv

- Task-2A: Visualization Artifacts (Generated from project outputs)
   - Work done:
      - Generated report images for dataset/task/model interpretation
   - Results:
      - Task-1 visuals: logs/visualizations/task1_label_distribution.png, logs/visualizations/task1_split_counts.png
      - Task-2 visuals: logs/visualizations/task2_accuracy.png, logs/visualizations/task2_confusion_matrix.png, logs/visualizations/task2_confidence_distribution.png
      - Task-3 visual: logs/visualizations/task3_workflow_coverage.png

- Task-3: Application-Level Inference Workflows
   - Work done:
      - Implemented and tested Streamlit workflows in app.py:
         - Single Review Analysis
         - Compare Two Reviews
         - Batch Processing with CSV export
   - Results:
      - All three task flows are available and executable through the UI
      - Batch output supports downloadable CSV with:
         - predicted_sentiment
         - confidence
         - prob_positive / prob_negative / prob_neutral

## Conclusion

- The project successfully implements an end-to-end Aspect-Based Sentiment Analysis workflow from dataset preparation to deployment-ready inference.
- Dataset validation, label checks, and split creation were completed with reproducible counts (91 total, 64/8/19 for train/val/test).
- The baseline TF-IDF + Logistic Regression model was trained and evaluated on the built-in sample run split (14/2/4), producing measurable results (accuracy: 0.50, weighted F1: 0.33).
- Streamlit-based inference workflows are functional for single review analysis, review comparison, and batch processing with exportable outputs.
- Visualization artifacts are available for dataset distribution and model evaluation, improving interpretability of results.
- Current performance indicates scope for improvement, especially for minority/underperforming classes; next iterations should focus on class balancing, running training on the full target dataset, and advanced model fine-tuning once PyTorch/BERT training is enabled.