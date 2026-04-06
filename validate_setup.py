"""
Installation validator and setup helper script.
Checks that all dependencies and models are properly installed.
"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...", end=" ")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (requires 3.8+)")
        return False


def check_package(package_name, import_name=None):
    """Check if package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"  ✓ {package_name}")
        return True
    except ImportError:
        print(f"  ✗ {package_name} (not found)")
        return False


def check_core_packages():
    """Check all core packages."""
    print("\n✓ Checking core packages...")
    
    packages = [
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('scikit-learn', 'sklearn'),
        ('nltk', 'nltk'),
        ('spacy', 'spacy'),
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
    ]
    
    all_installed = True
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_installed = False
    
    return all_installed


def check_language_models():
    """Check language models."""
    print("\n✓ Checking language models...")
    
    # Check spaCy model
    try:
        import spacy
        spacy.load('en_core_web_sm')
        print("  ✓ spaCy en_core_web_sm model")
    except:
        print("  ✗ spaCy en_core_web_sm model (run: python -m spacy download en_core_web_sm)")
        return False
    
    # Check NLTK data
    import nltk
    from nltk.data import find
    
    required_nltk = ['tokenizers/punkt', 'corpora/stopwords', 'corpora/wordnet', 'corpora/averaged_perceptron_tagger']
    all_found = True
    
    for resource in required_nltk:
        try:
            find(resource)
            print(f"  ✓ NLTK {resource}")
        except LookupError:
            print(f"  ✗ NLTK {resource}")
            all_found = False
    
    return all_found


def check_directories():
    """Check required directories exist."""
    print("\n✓ Checking directories...")
    
    dirs = ['data', 'saved_model', 'logs']
    
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ✗ {dir_name}/ missing (creating...)")
            Path(dir_name).mkdir(exist_ok=True)
    
    return True


def check_models():
    """Check trained models."""
    print("\n✓ Checking trained models...")
    
    if Path('saved_model/basic_model.pkl').exists():
        print("  ✓ BasicModel found (saved_model/basic_model.pkl)")
    else:
        print("  ⚠ BasicModel not found (run: python train.py --train-basic --use-sample)")
    
    if Path('saved_model/advanced_model/pytorch_model.bin').exists():
        print("  ✓ AdvancedModel found")
    else:
        print("  ⚠ AdvancedModel not found (run: python train.py --train-advanced --use-sample)")


def check_gpu():
    """Check GPU availability."""
    print("\n✓ Checking GPU...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ NVIDIA GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"    CUDA Version: {torch.version.cuda}")
        else:
            print("  ⚠ No GPU detected (CPU will be used)")
    except:
        print("  ⚠ Could not check GPU (PyTorch issue)")


def install_missing_packages():
    """Install missing packages."""
    print("\n" + "="*60)
    response = input("Install missing packages? (y/n): ").lower()
    
    if response == 'y':
        print("Installing from requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Installation complete!")
        
        # Try downloading language models
        print("\nDownloading language models...")
        try:
            import spacy
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
        except:
            pass
        
        try:
            import nltk
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')
        except:
            pass
        
        return True
    
    return False


def validate_installation():
    """Main validation function."""
    print("\n" + "="*60)
    print("ASPECT-LEVEL SENTIMENT ANALYSIS - INSTALLATION CHECK")
    print("="*60)
    
    # Run checks
    python_ok = check_python_version()
    packages_ok = check_core_packages()
    models_ok = check_language_models()
    dirs_ok = check_directories()
    check_gpu()
    check_models()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if python_ok and packages_ok and models_ok and dirs_ok:
        print("✓ Installation is valid!")
        print("\nNext steps:")
        print("1. Train models: python train.py --train-basic --use-sample")
        print("2. Run app: streamlit run app.py")
        return True
    else:
        print("✗ Installation has issues!")
        print("\nTrying to fix...")
        if not packages_ok or not models_ok:
            install_missing_packages()
        return False


def quick_test():
    """Quick functionality test."""
    print("\n" + "="*60)
    print("QUICK FUNCTIONALITY TEST")
    print("="*60)
    
    try:
        print("\nTesting preprocessing...")
        from preprocess import TextPreprocessor
        preprocessor = TextPreprocessor()
        text = "The product is amazing!"
        cleaned = preprocessor.preprocess(text)
        print(f"  ✓ '{text}' -> '{cleaned}'")
        
        print("\nTesting data loading...")
        from utils import DataLoader
        df = DataLoader.create_sample_dataset()
        print(f"  ✓ Loaded {len(df)} sample records")
        
        print("\nTesting sentiment mapper...")
        from utils import SentimentMapper
        mapper = SentimentMapper()
        print(f"  ✓ Sentiment classes: {mapper.labels}")
        
        print("\nTesting model initialization...")
        from model import BasicModel
        model = BasicModel()
        print(f"  ✓ BasicModel initialized")
        
        print("\n✓ All functionality tests passed!")
        return True
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


def show_next_steps():
    """Show next steps."""
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
    print("""
1. TRAINING:
   python train.py --train-basic --use-sample        # Fast
   python train.py --train-advanced --use-sample     # Slow but accurate

2. RUN APPLICATION:
   streamlit run app.py

3. OPEN BROWSER:
   http://localhost:8501

4. ANALYZE REVIEWS:
   - Go to "Single Review" tab
   - Enter review: "Battery is bad but camera is great"
   - Click "Analyze"
   - View aspect-level sentiments!

5. BATCH PROCESSING:
   - Prepare CSV with 'sentence' and 'aspect_term' columns
   - Upload to "Batch Analysis" tab
   - Download results

For detailed help, see QUICK_START.md or README.md
    """)


if __name__ == "__main__":
    # Run validation
    success = validate_installation()
    
    # Quick test
    test_ok = quick_test()
    
    # Show next steps
    show_next_steps()
    
    # Exit code
    sys.exit(0 if (success and test_ok) else 1)
