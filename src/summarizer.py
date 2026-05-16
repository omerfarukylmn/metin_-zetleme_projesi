import re
from collections import Counter
import unicodedata

TURKISH_STOPWORDS = set([
    "acaba", "ama", "ancak", "artık", "asla", "aslında", "az", "bana", "bazen", "bazı",
    "bazıları", "belki", "ben", "beni", "benim", "beri", "bile", "bir", "biraz", "biri",
    "birkaç", "birkez", "birçok", "birşey", "biz", "bize", "bizi", "bizim", "böyle",
    "böylece", "bu", "buna", "bunda", "bundan", "bunu", "bunun", "burada", "bütün",
    "çoğu", "çok", "çünkü", "da", "daha", "dahi", "de", "defa", "değil", "diğer", "diğeri",
    "diğerleri", "diye", "dolayı", "eğer", "en", "gibi", "göre", "hala", "hangi", "hangisi",
    "hani", "hatta", "hem", "henüz", "hep", "hepsi", "her", "herhangi", "herkes", "hiç",
    "hiçbir", "hiçbiri", "için", "ile", "ilgili", "ise", "işte", "itibaren", "kadar",
    "karşın", "kendi", "kendilerine", "kendini", "kendisi", "kendisine", "kendisini",
    "kez", "ki", "kim", "kime", "kimi", "kimin", "kimisi", "mı", "mi", "mu", "mü", "nasıl",
    "ne", "neden", "nedenle", "nerde", "nerede", "nereye", "niçin", "niye", "o", "olan",
    "olarak", "oldu", "olduğu", "olduğunu", "olmak", "olmayan", "olmaz", "olsa", "olsun",
    "olup", "olur", "olursa", "oluyor", "on", "ona", "ondan", "onlar", "onlardan", "onları",
    "onların", "onu", "onun", "orada", "öte", "ötürü", "öyle", "rağmen", "sana", "sanki",
    "sen", "senden", "seni", "senin", "siz", "sizden", "size", "sizi", "sizin", "sonra",
    "şayet", "şey", "şeyden", "şeye", "şeyi", "şeyler", "şimdi", "şöyle", "şu", "şuna",
    "şunda", "şundan", "şunu", "şunun", "tabi", "tamam", "tüm", "tümü", "üzere", "var",
    "vardı", "ve", "veya", "veyahut", "ya", "yahut", "yalnız", "yani", "yerine", "yine",
    "yoksa", "zaten"
])


def split_sentences(text):
    """Basit cümle bölücü."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def preprocess_text(text, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    if text is None:
        return ""
    out = str(text)
    # Normalize unicode to avoid combined characters (helps Turkish İ/ı issues)
    out = unicodedata.normalize('NFKC', out)
    if strip_suffixes:
        out = re.sub(r"([A-Za-zÇĞİÖŞÜçğıöşü0-9]+)[’']\S+", r"\1", out)
    # Normalize capital dotted İ before lowercasing to avoid 'i\u0307' artifacts
    out = out.replace('\u0130', 'I')
    if to_lower:
        out = out.lower()
        # replace possible combining dotted-i sequences produced by lower()
        out = out.replace('i\u0307', 'i')
    if remove_numbers:
        out = re.sub(r"\d+", " ", out)
    if remove_punct:
        out = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def clean_words(text, remove_stopwords=False, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    proc = preprocess_text(text, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    words = re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]+\b", proc)
    if remove_stopwords:
        words = [w for w in words if w not in TURKISH_STOPWORDS]
    return words


def _compute_sentence_scores(text, remove_stopwords=False, method="frequency", location_weight=0.75, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    sentences = split_sentences(text)
    words_all = clean_words(text, remove_stopwords=remove_stopwords, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    freqs = Counter(words_all)
    sentence_scores = []
    n = len(sentences)
    for i, s in enumerate(sentences):
        words = clean_words(s, remove_stopwords=remove_stopwords, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
        if not words:
            continue
        score = sum(freqs.get(w, 0) for w in words)
        score = score / len(words)
        if method == "location" and n > 0:
            pos = i / (n - 1) if n > 1 else 0
            distance = abs(pos - 0.5)
            position_factor = 1 + location_weight * (1 - 2 * distance)
            score = score * position_factor
            if i == 0 or i == n - 1:
                max_freq = max(freqs.values()) if freqs else 0
                score += location_weight * max_freq
        sentence_scores.append((i, s, score))
    return sentence_scores


def select_top_sentence_indices(text, sentence_count=3, remove_stopwords=False, method="frequency", location_weight=0.75, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    scores = _compute_sentence_scores(text, remove_stopwords=remove_stopwords, method=method, location_weight=location_weight, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    top = sorted(scores, key=lambda x: x[2], reverse=True)[:sentence_count]
    indices = [i for i, _, _ in top]
    return indices


def extract_keywords(text, top_k=10, remove_stopwords=False, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    words = clean_words(text, remove_stopwords=remove_stopwords, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    if not words:
        return []
    freqs = Counter(words)
    return [w for w, _ in freqs.most_common(top_k)]


def summarize_text(text, sentence_count=3, remove_stopwords=False, method="frequency", location_weight=0.75, remove_punct=True, remove_numbers=True, strip_suffixes=True, to_lower=True):
    indices = select_top_sentence_indices(text, sentence_count=sentence_count, remove_stopwords=remove_stopwords, method=method, location_weight=location_weight, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    sentences = split_sentences(text)
    selected = [sentences[i] for i in sorted(indices) if i < len(sentences)]
    return " ".join(selected)
