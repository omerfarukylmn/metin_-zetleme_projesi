import sys
import os
sys.path.append(os.path.abspath('.'))

from src.summarizer import clean_words, split_sentences, summarize_text


def test_clean_words_basic():
    text = "Bu bir örnek metindir."
    words = clean_words(text)
    assert isinstance(words, list)
    assert "bu" in words or "örnek" in words


def test_split_sentences_basic():
    text = "İlk cümle. İkinci cümle! Üçüncü?"
    sents = split_sentences(text)
    assert len(sents) == 3


def test_summarize_returns_text():
    text = "Birinci cümle önemli. İkinci cümle daha az önemli. Üçüncü cümle yine önemli."
    summary = summarize_text(text, sentence_count=2)
    assert isinstance(summary, str)
    assert len(summary) > 0
