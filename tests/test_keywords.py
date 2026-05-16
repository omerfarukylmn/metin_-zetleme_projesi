import sys
import os
from collections import Counter
sys.path.append(os.path.abspath('.'))

# Bu test dosyası, basit anahtar kelime çıkarımı davranışını kontrol eder
from src.summarizer import clean_words


def extract_top_keywords(text, top_k=5, remove_stopwords=False):
    words = clean_words(text, remove_stopwords=remove_stopwords)
    counts = Counter(words)
    return [w for w, _ in counts.most_common(top_k)]


def test_extract_top_keywords_basic():
    text = "elma armut elma muz elma armut"
    kws = extract_top_keywords(text, top_k=2)
    assert "elma" in kws
    assert len(kws) == 2
