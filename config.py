"""
Config file for Aspect-Level Sentiment Analysis Application.
Centralized configuration for models, preprocessing, and UI settings.
"""

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Basic Model Settings
BASIC_MODEL_CONFIG = {
    'model_type': 'tfidf_logistic',
    'max_features': 5000,
    'ngram_range': (1, 2),
    'classifier_max_iter': 1000,
    'random_state': 42,
    'model_path': 'saved_model/basic_model.pkl'
}

# Advanced Model Settings
ADVANCED_MODEL_CONFIG = {
    'model_type': 'bert_fine_tuned',
    'bert_model': 'bert-base-uncased',
    'num_classes': 3,
    'hidden_dropout_prob': 0.1,
    'learning_rate': 2e-5,
    'max_sequence_length': 128,
    'random_state': 42,
    'model_path': 'saved_model/advanced_model'
}

# Research / experimental ABSA model families
RESEARCH_MODEL_FAMILIES = {
    'spanbert_span_extraction': {
        'display_name': 'SpanBERT for span-level aspect extraction',
        'task': 'span_extraction',
        'backbone': 'SpanBERT/spanbert-base-cased',
        'description': 'Extracts aspect spans first, then routes them into sentiment scoring.',
        'status': 'experimental',
    },
    'bert_e2e_absa': {
        'display_name': 'BERT-E2E-ABSA for joint modeling',
        'task': 'joint_extraction_classification',
        'backbone': 'bert-base-uncased',
        'description': 'Learns aspect extraction and sentiment classification together.',
        'status': 'experimental',
    },
    't5_structured_absa': {
        'display_name': 'Generative T5 with structured output',
        'task': 'generation',
        'backbone': 't5-base',
        'description': 'Generates structured ABSA output such as JSON or tagged tuples.',
        'status': 'experimental',
    },
}

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================

TRAINING_CONFIG = {
    'basic_model': {
        'use_preprocessing': True,
        'test_size': 0.2,
        'val_size': 0.1,
    },
    'advanced_model': {
        'epochs': 3,
        'batch_size': 16,
        'learning_rate': 2e-5,
        'warmup_steps': 0,
        'weight_decay': 0.01,
        'gradient_accumulation_steps': 1,
        'max_grad_norm': 1.0,
    }
}

# ============================================================================
# PREPROCESSING CONFIGURATION
# ============================================================================

PREPROCESSING_CONFIG = {
    'use_lemmatization': True,
    'use_stopword_removal': True,
    'remove_urls': True,
    'remove_emails': True,
    'remove_special_characters': True,
    'remove_numbers': False,  # Keep numbers sometimes useful for price context
    'remove_punctuation': True,
    'lowercase': True,
}

# ============================================================================
# ASPECT EXTRACTION CONFIGURATION
# ============================================================================

ASPECT_EXTRACTION_CONFIG = {
    'method': 'nouns',  # 'nouns' or 'capitalized_words'
    'min_aspect_length': 2,  # Minimum characters for aspect
    'max_aspects_per_review': 10,  # Maximum aspects to extract
    'use_pos_tagging': True,  # Use spaCy POS tagging
}

# ============================================================================
# STREAMLIT UI CONFIGURATION
# ============================================================================

STREAMLIT_CONFIG = {
    'page_title': 'Aspect-Level Sentiment Analyzer',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    
    # Model selection defaults
    'default_model': 'basic',  # 'basic' or 'advanced'
    'show_confidence': True,
    'show_debug_info': False,
    
    # Visualization settings
    'plot_height': 400,
    'plot_width': None,  # Auto
    'color_scheme': {
        'positive': '#28a745',
        'negative': '#dc3545',
        'neutral': '#ffc107'
    },
    
    # Batch processing
    'max_batch_size': 1000,
    'batch_chunk_size': 100,
}

# ============================================================================
# DATA CONFIGURATION
# ============================================================================

DATA_CONFIG = {
    'data_directory': 'data/',
    'sample_dataset_size': 20,
    'sentiment_labels': ['positive', 'negative', 'neutral'],
    'random_seed': 42,
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'log_directory': 'logs/',
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'save_predictions': True,
    'save_metrics': True,
}

# ============================================================================
# SENTIMENT MAPPER
# ============================================================================

SENTIMENT_LABELS = {
    'positive': 0,
    'negative': 1,
    'neutral': 2,
}

SENTIMENT_COLORS = {
    'positive': '🟢',
    'negative': '🔴',
    'neutral': '🟡',
}

# ============================================================================
# DEVICE CONFIGURATION
# ============================================================================

DEVICE_CONFIG = {
    'use_cuda': True,  # Automatically detect and use GPU if available
    'cuda_device_id': 0,  # GPU device ID to use
}

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE_CONFIG = {
    'enable_model_caching': True,  # Cache loaded models in memory
    'cache_max_size': 3,  # Maximum models to cache
    'enable_prediction_caching': False,  # Cache predictions
    'prediction_cache_ttl': 3600,  # Cache TTL in seconds
}

# ============================================================================
# EXPORT & DOWNLOAD CONFIGURATION
# ============================================================================

EXPORT_CONFIG = {
    'supported_formats': ['csv', 'json', 'excel'],
    'default_format': 'csv',
    'include_confidence': True,
    'include_timestamp': True,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_config(model_type='basic'):
    """Get configuration for specific model type."""
    if model_type.lower() == 'basic':
        return BASIC_MODEL_CONFIG
    elif model_type.lower() == 'advanced':
        return ADVANCED_MODEL_CONFIG
    elif model_type.lower() in RESEARCH_MODEL_FAMILIES:
        return RESEARCH_MODEL_FAMILIES[model_type.lower()]
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def list_research_model_families():
    """Return the experimental model families supported by the project."""
    return RESEARCH_MODEL_FAMILIES.copy()


def get_sentiment_label(sentiment_str):
    """Convert sentiment string to label index."""
    return SENTIMENT_LABELS.get(sentiment_str.lower(), 0)


def get_sentiment_color(sentiment_str):
    """Get emoji for sentiment."""
    return SENTIMENT_COLORS.get(sentiment_str.lower(), '⚪')


def print_config(config_dict=None, indent=0):
    """Pretty print configuration."""
    if config_dict is None:
        config_dict = {
            'Basic Model': BASIC_MODEL_CONFIG,
            'Advanced Model': ADVANCED_MODEL_CONFIG,
            'Preprocessing': PREPROCESSING_CONFIG,
            'Training': TRAINING_CONFIG,
            'Streamlit': STREAMLIT_CONFIG,
        }
    
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(' ' * indent + f"{key}:")
            print_config(value, indent + 2)
        else:
            print(' ' * indent + f"{key}: {value}")


if __name__ == "__main__":
    print("="*60)
    print("ASPECT-LEVEL SENTIMENT ANALYSIS - CONFIGURATION")
    print("="*60)
    print_config()
