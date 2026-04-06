"""
Text preprocessing module for Aspect-Level Sentiment Analysis.
Handles text cleaning, tokenization, and lemmatization.
"""

import re
import string
from collections import OrderedDict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Try to import spaCy, but gracefully fall back if unavailable
nlp = None
try:
    import spacy
    try:
        nlp = spacy.load('en_core_web_sm')
    except (OSError, ImportError):
        pass  # spaCy not available, will use NLTK fallback
except (ImportError, OSError):
    pass  # spaCy not importable

# Download required NLTK data using package names (not lookup paths)
NLTK_PACKAGES = [
    'punkt',
    'punkt_tab',
    'stopwords',
    'wordnet',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng'
]

NLTK_RESOURCE_PATHS = {
    'punkt': 'tokenizers/punkt',
    'punkt_tab': 'tokenizers/punkt_tab',
    'stopwords': 'corpora/stopwords',
    'wordnet': 'corpora/wordnet',
    'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng': 'taggers/averaged_perceptron_tagger_eng',
}

_NLTK_READY = False


def _ensure_nltk_data():
    """Download missing NLTK resources once per process."""
    global _NLTK_READY
    if _NLTK_READY:
        return

    for package in NLTK_PACKAGES:
        resource = NLTK_RESOURCE_PATHS.get(package, package)
        try:
            nltk.data.find(resource)
            continue
        except LookupError:
            pass

        try:
            nltk.download(package, quiet=True)
        except Exception:
            # Keep runtime resilient in restricted environments.
            pass

    _NLTK_READY = True


class TextPreprocessor:
    """Handles all text preprocessing operations."""

    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    SPECIAL_CHAR_PATTERN = re.compile(r'[^a-zA-Z0-9\s!?.,-]')
    NUMBER_PATTERN = re.compile(r'\d+')
    WHITESPACE_PATTERN = re.compile(r'\s+')
    _CACHE_SIZE = 4096
    NEGATION_TERMS = {
        "not", "no", "nor", "never", "none", "nothing", "nowhere", "neither",
        "hardly", "scarcely", "barely", "without"
    }
    NEGATION_FLIPS = {
        "bad": "good",
        "poor": "good",
        "terrible": "good",
        "awful": "good",
        "horrible": "good",
        "worst": "good",
        "slow": "fast",
        "ugly": "good",
        "broken": "working",
        "useless": "useful",
        "expensive": "cheap",
        "excellent": "bad",
        "great": "bad",
        "good": "bad",
        "amazing": "bad",
        "perfect": "bad",
        "love": "hate",
        "liked": "disliked",
        "like": "dislike",
        "helpful": "unhelpful",
        "responsive": "unresponsive",
        "reliable": "unreliable",
        "comfortable": "uncomfortable",
    }
    
    def __init__(self, use_lemmatization=True, use_stopword_removal=True):
        """
        Initialize the preprocessor.
        
        Args:
            use_lemmatization (bool): Whether to apply lemmatization
            use_stopword_removal (bool): Whether to remove stopwords
        """
        _ensure_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.use_lemmatization = use_lemmatization
        self.use_stopword_removal = use_stopword_removal
        self.nlp = nlp  # Use global nlp variable (which gracefully handles unavailability)
        self._preprocess_cache = OrderedDict()
    
    def lowercase(self, text):
        """Convert text to lowercase."""
        return text.lower()
    
    def remove_urls(self, text):
        """Remove URLs from text."""
        return self.URL_PATTERN.sub('', text)
    
    def remove_emails(self, text):
        """Remove email addresses."""
        return self.EMAIL_PATTERN.sub('', text)
    
    def remove_special_characters(self, text):
        """Remove special characters but keep basic punctuation."""
        # Keep periods, commas, exclamation, question marks for context
        text = self.SPECIAL_CHAR_PATTERN.sub('', text)
        return text
    
    def remove_numbers(self, text):
        """Remove numeric digits."""
        return self.NUMBER_PATTERN.sub('', text)
    
    def remove_extra_whitespace(self, text):
        """Remove extra whitespace and normalize spaces."""
        text = self.WHITESPACE_PATTERN.sub(' ', text)
        return text.strip()
    
    def remove_punctuation(self, text):
        """Remove all punctuation."""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    def tokenize(self, text):
        """Tokenize text into words."""
        try:
            return word_tokenize(text)
        except LookupError:
            # Fallback when punkt resources are unavailable.
            return text.split()
    
    def remove_stopwords(self, tokens):
        """Remove stopwords from token list."""
        if self.use_stopword_removal:
            filtered = []
            for token in tokens:
                lower = token.lower()
                # Preserve negation markers so we keep polarity in phrases like "not good".
                if lower in self.NEGATION_TERMS or lower.endswith("n't"):
                    filtered.append(token)
                    continue
                if lower not in self.stop_words:
                    filtered.append(token)
            return filtered
        return tokens

    def apply_negation_flips(self, tokens):
        """Flip common sentiment-bearing words after negation markers.

        This keeps phrases like 'not bad' and 'not great' from being treated
        like their literal surface form only.
        """
        if not tokens:
            return tokens

        flipped = []
        negate_next = False
        for token in tokens:
            lower = token.lower()
            if lower in self.NEGATION_TERMS or lower.endswith("n't"):
                negate_next = True
                continue

            if negate_next:
                replacement = self.NEGATION_FLIPS.get(lower)
                if replacement:
                    flipped.append(replacement)
                    negate_next = False
                    continue

                flipped.append(f"not_{lower}")
                negate_next = False
                continue

            flipped.append(token)

        return flipped
    
    def lemmatize(self, tokens):
        """Apply lemmatization to tokens."""
        if self.use_lemmatization:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        return tokens
    
    def extract_pos_tags(self, text):
        """
        Extract POS tags for aspect extraction (nouns).
        Uses spaCy if available, falls back to NLTK.
        
        Returns:
            dict: Mapping of words to POS tags
        """
        if self.nlp is not None:
            doc = self.nlp(text)
            pos_dict = {token.text: token.pos_ for token in doc}
        else:
            tokens = self.tokenize(text)
            try:
                pos_tags = nltk.pos_tag(tokens)
            except LookupError:
                pos_tags = [(token, 'NN') for token in tokens]
            pos_dict = {word: tag for word, tag in pos_tags}
        
        return pos_dict
    
    def extract_nouns(self, text):
        """
        Extract nouns from text as potential aspects.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of noun tokens
        """
        if self.nlp is not None:
            doc = self.nlp(text)
            nouns = [token.text for token in doc if token.pos_ == 'NOUN']
        else:
            tokens = self.tokenize(text)
            try:
                pos_tags = nltk.pos_tag(tokens)
            except LookupError:
                pos_tags = [(token, 'NN') for token in tokens]
            nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
        
        return nouns
    
    def preprocess(self, text, remove_punct=True, remove_nums=True):
        """
        Complete preprocessing pipeline.
        
        Args:
            text (str): Input text to preprocess
            remove_punct (bool): Remove punctuation
            remove_nums (bool): Remove numbers
            
        Returns:
            str: Preprocessed text (joined tokens)
        """
        # 1. Remove URLs and emails
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        
        # 2. Lowercase
        text = self.lowercase(text)
        
        # 3. Remove special characters (but not punctuation yet)
        text = self.remove_special_characters(text)
        
        # 4. Remove numbers if specified
        if remove_nums:
            text = self.remove_numbers(text)
        
        # 5. Normalize whitespace
        text = self.remove_extra_whitespace(text)
        
        # 6. Tokenize
        tokens = self.tokenize(text)
        
        # 7. Remove punctuation if specified
        if remove_punct:
            tokens = [token for token in tokens if token not in string.punctuation]
        
        # 8. Remove stopwords
        tokens = self.remove_stopwords(tokens)

        # 8.5 Flip common sentiment words after negation
        tokens = self.apply_negation_flips(tokens)
        
        # 9. Lemmatization
        tokens = self.lemmatize(tokens)
        
        # 10. Remove empty tokens
        tokens = [token for token in tokens if token.strip()]
        
        return ' '.join(tokens)

    def _cache_key(self, text, remove_punct, remove_nums):
        return (str(text), bool(remove_punct), bool(remove_nums))

    def preprocess_cached(self, text, remove_punct=True, remove_nums=True):
        """Memoized preprocessing for repeated reviews/aspects in batch calls."""
        key = self._cache_key(text, remove_punct, remove_nums)
        if key in self._preprocess_cache:
            self._preprocess_cache.move_to_end(key)
            return self._preprocess_cache[key]

        processed = self.preprocess(text, remove_punct, remove_nums)
        self._preprocess_cache[key] = processed

        if len(self._preprocess_cache) > self._CACHE_SIZE:
            self._preprocess_cache.popitem(last=False)

        return processed
    
    def preprocess_batch(self, texts, remove_punct=True, remove_nums=True):
        """
        Preprocess multiple texts.
        
        Args:
            texts (list): List of text strings
            remove_punct (bool): Remove punctuation
            remove_nums (bool): Remove numbers
            
        Returns:
            list: List of preprocessed texts
        """
        return [self.preprocess_cached(text, remove_punct, remove_nums) for text in texts]


# Helper function for quick preprocessing
def quick_preprocess(text):
    """Quick preprocessing without optional removals."""
    preprocessor = TextPreprocessor()
    return preprocessor.preprocess(text)


if __name__ == "__main__":
    # Test preprocessing
    preprocessor = TextPreprocessor()
    
    test_texts = [
        "The battery is bad but the camera is excellent! Price: $999",
        "AMAZING product!!! Check it out at www.example.com",
        "The build quality is great, but too expensive."
    ]
    
    print("=== Preprocessing Test ===\n")
    for text in test_texts:
        print(f"Original: {text}")
        print(f"Preprocessed: {preprocessor.preprocess(text)}")
        print(f"Nouns (aspects): {preprocessor.extract_nouns(text)}\n")
