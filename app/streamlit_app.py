import streamlit as st
import sys
import os

# src klasörünü Python path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.summarizer import (
    summarize_text,
    split_sentences,
    select_top_sentence_indices,
    extract_keywords,
    preprocess_text,
)

st.set_page_config(page_title="Metin Özetleme", layout="wide")

# CSS
st.markdown(
    """
    <style>
    .app-title {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight:700;}
    .badge{display:inline-block;background:#e8f5e9;padding:6px 10px;border-radius:14px;margin:4px;font-weight:600;color:#155724}
    .highlight{background:#fff59d;padding:4px;border-radius:6px}
    .summary-box{background:#fafafa;padding:16px;border-radius:8px;border:1px solid #eee}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# Metin Özetleme Projesi")
st.write("Gelişmiş özetleme: model seçimi, ön işlem, vurgulama ve anahtar kelime çıkarımı.")

with st.sidebar:
    st.header("Ayarlar")
    st.subheader("Ön İşleme")
    remove_punct = st.checkbox("Noktalama işaretlerini kaldır", value=True)
    remove_numbers = st.checkbox("Sayıları kaldır", value=True)
    strip_suffixes = st.checkbox("Kısaltma eklerini temizle (TDK'nın, NLP'de)", value=True)
    to_lower = st.checkbox("Küçük harfe çevir", value=True)
    remove_stopwords = st.checkbox("Stopword'leri temizle", value=False)

    st.subheader("Özet Ayarları")
    method_label = st.radio("Yöntem", ("Frekans Tabanlı Özetleme", "Konum Destekli Özetleme"))
    method = "frequency" if method_label.startswith("Frekans") else "location"
    sentence_count = st.slider("Özet uzunluğu (cümle)", min_value=1, max_value=10, value=3)
    location_weight = 0.75
    if method == "location":
        location_weight = st.slider("Konum ağırlığı", min_value=0.0, max_value=2.0, value=0.75, step=0.05)

    st.subheader("Anahtar Kelimeler")
    keyword_count = st.slider("Kaç anahtar kelime gösterilsin?", min_value=1, max_value=30, value=10)

    st.markdown("---")
    if st.button("Ön İşlem Önizle"):
        st.session_state["preview"] = True
    if st.button("Ön İşlemi Metne Uygula"):
        st.session_state["apply_preprocess"] = True

text_input = st.session_state.get("text_input", "")
text_input = st.text_area("Metni buraya girin:", value=text_input, height=300, key="text_input")

# Preview
if st.session_state.get("preview"):
    proc = preprocess_text(text_input, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    st.subheader("Ön İşlem Önizleme")
    st.code(proc)
    st.session_state["preview"] = False

if st.session_state.get("apply_preprocess"):
    proc = preprocess_text(text_input, remove_punct=remove_punct, remove_numbers=remove_numbers, strip_suffixes=strip_suffixes, to_lower=to_lower)
    st.session_state["text_input"] = proc
    st.experimental_rerun()

if st.button("Özetle"):
    if not text_input.strip():
        st.warning("Lütfen bir metin girin.")
    else:
        # compute
        method_key = "frequency" if method == "frequency" else "location"
        summary = summarize_text(
            text_input,
            sentence_count=sentence_count,
            remove_stopwords=remove_stopwords,
            method=method_key,
            location_weight=location_weight,
            remove_punct=remove_punct,
            remove_numbers=remove_numbers,
            strip_suffixes=strip_suffixes,
            to_lower=to_lower,
        )

        kws = extract_keywords(
            text_input,
            top_k=keyword_count,
            remove_stopwords=remove_stopwords,
            remove_punct=remove_punct,
            remove_numbers=remove_numbers,
            strip_suffixes=strip_suffixes,
            to_lower=to_lower,
        )

        left, right = st.columns([2, 1])
        with left:
            st.subheader("Özet")
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
            if kws:
                st.subheader("Anahtar Kelimeler")
                kw_html = "".join([f"<span class='badge'>{k}</span>" for k in kws])
                st.markdown(kw_html, unsafe_allow_html=True)

        with right:
            indices = select_top_sentence_indices(
                text_input,
                sentence_count=sentence_count,
                remove_stopwords=remove_stopwords,
                method=method_key,
                location_weight=location_weight,
                remove_punct=remove_punct,
                remove_numbers=remove_numbers,
                strip_suffixes=strip_suffixes,
                to_lower=to_lower,
            )
            sentences = split_sentences(text_input)
            highlighted = []
            for i, s in enumerate(sentences):
                safe_s = s.replace("<", "&lt;").replace(">", "&gt;")
                if i in indices:
                    highlighted.append(f"<span class='highlight'>{safe_s}</span>")
                else:
                    highlighted.append(safe_s)
            st.subheader("Orijinal Metin (Vurgulanan Cümleler)")
            st.markdown("<div style='line-height:1.6'>" + " ".join(highlighted) + "</div>", unsafe_allow_html=True)
