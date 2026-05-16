import sys
import os
sys.path.append(os.path.abspath('.'))

from src.summarizer import clean_words


def test_clean_words_lowercase_and_tokens():
    text = "TDK'nın NLP'de TÜBİTAK’a örnek metin: 12345!"
    words = clean_words(text, remove_stopwords=False)
    assert any(w.islower() for w in words)
    assert all(isinstance(w, str) for w in words)


def test_clean_words_removes_non_alpha():
    text = "abc 123 #$% öçğ"
    words = clean_words(text)
    # sayılar temizlenmiş olmalı (regex hedefi harfleri alır)
    assert not any(char.isdigit() for char in "".join(words))
