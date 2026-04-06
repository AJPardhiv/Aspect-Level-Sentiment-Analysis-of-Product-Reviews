#!/usr/bin/env python3
"""
Advanced Streamlit app for Aspect-Level Sentiment Analysis.
Works with BasicModel artifacts and degrades gracefully when advanced dependencies are absent.
"""

import os
import pickle
import hashlib
import re
import sys
import subprocess
from typing import List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st


SENTIMENT_ORDER = ["positive", "negative", "neutral"]
MAX_TEXT_CHARS = int(os.getenv("ABSA_MAX_TEXT_CHARS", "5000"))
MAX_BATCH_ROWS = int(os.getenv("ABSA_MAX_BATCH_ROWS", "1000"))
MAX_UPLOAD_MB = float(os.getenv("ABSA_MAX_UPLOAD_MB", "5"))
MIN_CONFIDENCE_GOOD = float(os.getenv("ABSA_MIN_CONFIDENCE_GOOD", "0.75"))

CLAUSE_SPLIT_PATTERN = re.compile(r"\b(?:but|however|although|though|while|yet)\b|[;,.]", re.IGNORECASE)
LIGHT_STOPWORDS = {
    "the", "and", "with", "this", "that", "from", "have", "has", "been", "were", "was", "are", "is",
    "for", "but", "not", "very", "just", "only", "into", "onto", "when", "where", "what", "which"
}


st.set_page_config(
    page_title="ABSA Studio",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Source+Sans+3:wght@400;600;700&display=swap');
            .stApp {background: radial-gradient(circle at 8% 12%, #f5fff7 0%, #f7fbff 38%, #fff7f1 100%);}
            .block-container {padding-top: 1.0rem; max-width: 1200px;}
            .hero {
                padding: 1.2rem 1.3rem;
                border: 1px solid #d7e3f1;
                border-radius: 16px;
                background: linear-gradient(145deg,#f8fff8,#f4f9ff 55%,#fff6ed);
                box-shadow: 0 8px 25px rgba(25, 48, 79, 0.08);
            }
            .hero h2 {font-family: 'Manrope', sans-serif; letter-spacing: 0.1px; color: #123049;}
            .hero p {font-family: 'Source Sans 3', sans-serif; color: #334f66; margin: 0.2rem 0 0;}
            .kpi-card {
                border: 1px solid #dae6f4;
                border-radius: 12px;
                padding: 0.7rem 0.85rem;
                background: #ffffffb8;
            }
            .chip {padding: 0.2rem 0.5rem; border-radius: 999px; font-size: 0.85rem; font-weight: 700;}
            .chip-pos {background:#dff5e8; color:#0f6a37;}
            .chip-neg {background:#fde4e4; color:#8f1e1e;}
            .chip-neu {background:#efeef6; color:#4b4a64;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _load_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sanitize_text(text: str) -> str:
    return str(text).strip()[:MAX_TEXT_CHARS]


@st.cache_data
def _load_aspect_lexicon() -> List[str]:
    lexicon: set[str] = set()
    candidate_paths = ["data/semeval_2014_absa.csv", "data/sample_reviews.csv"]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if "aspect_term" in df.columns:
                    for term in df["aspect_term"].dropna().astype(str):
                        cleaned = term.strip().lower()
                        if cleaned and len(cleaned) >= 2:
                            lexicon.add(cleaned)
            except Exception:
                continue
    return sorted(lexicon)


@st.cache_data
def _get_dataset_status() -> dict:
    semeval_path = "data/semeval_2014_absa.csv"
    sample_path = "data/sample_reviews.csv"
    semeval_exists = os.path.exists(semeval_path)
    sample_exists = os.path.exists(sample_path)
    semeval_rows = 0
    sample_rows = 0

    if semeval_exists:
        try:
            semeval_rows = len(pd.read_csv(semeval_path))
        except Exception:
            semeval_rows = 0
    if sample_exists:
        try:
            sample_rows = len(pd.read_csv(sample_path))
        except Exception:
            sample_rows = 0

    return {
        "semeval_exists": semeval_exists,
        "sample_exists": sample_exists,
        "semeval_rows": semeval_rows,
        "sample_rows": sample_rows,
    }


def _split_into_clauses(text: str) -> List[str]:
    chunks = [part.strip() for part in CLAUSE_SPLIT_PATTERN.split(text) if part and part.strip()]
    if not chunks:
        return [text.strip()]
    return chunks


def _detect_aspects_for_clause(clause: str, lexicon: List[str]) -> List[str]:
    lower_clause = clause.lower()
    matched = [aspect for aspect in lexicon if re.search(rf"\\b{re.escape(aspect)}\\b", lower_clause)]
    if matched:
        return matched[:3]

    fallback_tokens = [
        tok for tok in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", lower_clause)
        if tok not in LIGHT_STOPWORDS
    ]
    if fallback_tokens:
        return fallback_tokens[:2]
    return ["general"]


def _analyze_clause_level(text: str, artifact, lexicon: List[str]) -> pd.DataFrame:
    clauses = _split_into_clauses(text)
    labels, conf, _ = _predict_detailed(clauses, artifact)
    rows = []
    for clause, label, confidence in zip(clauses, labels, conf):
        aspects = _detect_aspects_for_clause(clause, lexicon)
        for aspect in aspects:
            rows.append(
                {
                    "clause": clause,
                    "aspect": aspect,
                    "sentiment": label,
                    "confidence": round(float(confidence), 4),
                }
            )
    return pd.DataFrame(rows)


def _run_command(command: List[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3600)
        output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        return result.returncode, output[-6000:]
    except Exception as exc:
        return 1, str(exc)


@st.cache_resource
def load_model_artifact():
    candidates = ["saved_model/basic_model.pkl", "saved_model/basic_model_lite.pkl"]
    expected_hash = os.getenv("ABSA_MODEL_SHA256", "").strip().lower()
    for path in candidates:
        if os.path.exists(path):
            try:
                if expected_hash:
                    actual_hash = _sha256_file(path)
                    if actual_hash != expected_hash:
                        raise ValueError("Model artifact hash mismatch.")
                artifact = _load_pickle(path)
                return path, artifact
            except Exception:
                continue
    return None, None


def _standardize_probabilities(prob_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure sentiment probability columns are always present and ordered."""
    for sentiment in SENTIMENT_ORDER:
        if sentiment not in prob_df.columns:
            prob_df[sentiment] = 0.0
    other_cols = [c for c in prob_df.columns if c not in SENTIMENT_ORDER]
    return prob_df[SENTIMENT_ORDER + other_cols]


def _predict_detailed(texts: List[str], artifact) -> Tuple[List[str], List[float], pd.DataFrame]:
    # Format A: BasicModel.save state dict
    if isinstance(artifact, dict) and "model" in artifact and "sentiment_mapper" in artifact:
        pipeline = artifact["model"]
        mapper = artifact["sentiment_mapper"]

        X = pipeline.named_steps["tfidf"].transform(texts)
        classifier = pipeline.named_steps["classifier"]
        preds = classifier.predict(X)
        probs = classifier.predict_proba(X)
        class_labels = mapper.decode_labels(classifier.classes_)

        labels = mapper.decode_labels(preds)
        conf = probs.max(axis=1).tolist()
        prob_df = _standardize_probabilities(pd.DataFrame(probs, columns=class_labels))
        return labels, conf, prob_df

    # Format B: lite dict with vectorizer/model + mapping
    if isinstance(artifact, dict) and "vectorizer" in artifact and "model" in artifact:
        vectorizer = artifact["vectorizer"]
        model = artifact["model"]
        inv = artifact.get("inverse_mapping")
        if inv is None:
            lm = artifact.get("label_mapping", {"positive": 0, "negative": 1, "neutral": 2})
            inv = {v: k for k, v in lm.items()}

        X = vectorizer.transform(texts)
        preds = model.predict(X)
        probs = model.predict_proba(X)
        classes = getattr(model, "classes_", list(range(probs.shape[1])))
        class_labels = [inv.get(int(cls_id), str(cls_id)) for cls_id in classes]

        labels = [inv.get(int(p), "unknown") for p in preds]
        conf = probs.max(axis=1).tolist()
        prob_df = _standardize_probabilities(pd.DataFrame(probs, columns=class_labels))
        return labels, conf, prob_df

    # Format C: loaded class instance with predict
    if hasattr(artifact, "predict"):
        labels, conf = artifact.predict(texts)
        labels = list(labels)
        conf = list(conf)

        prob_df = pd.DataFrame(0.0, index=range(len(labels)), columns=SENTIMENT_ORDER)
        for idx, (label, confidence) in enumerate(zip(labels, conf)):
            lbl = str(label).lower()
            if lbl not in prob_df.columns:
                prob_df[lbl] = 0.0
            prob_df.loc[idx, lbl] = float(confidence)
            remainder = max(0.0, 1.0 - float(confidence))
            others = [c for c in SENTIMENT_ORDER if c != lbl]
            if others:
                share = remainder / len(others)
                for col in others:
                    prob_df.loc[idx, col] = share

        return labels, conf, _standardize_probabilities(prob_df)

    raise ValueError("Unsupported model artifact format.")


def _predict_with_artifact(texts: List[str], artifact) -> Tuple[List[str], List[float]]:
    labels, conf, _ = _predict_detailed(texts, artifact)
    return labels, conf


def predict_one(text: str, artifact):
    labels, conf, prob_df = _predict_detailed([text], artifact)
    return labels[0], float(conf[0]), prob_df.iloc[0]


def badge(sentiment: str) -> str:
    s = sentiment.lower()
    if s == "positive":
        return "positive"
    if s == "negative":
        return "negative"
    return "neutral"


def main():
    st.markdown("<div class='hero'><h2>ABSA Studio</h2><p>Production-focused sentiment analysis with safer batch handling, confidence explainability, and deployment-ready workflows.</p></div>", unsafe_allow_html=True)

    model_path, artifact = load_model_artifact()
    if artifact is None:
        st.error("No trained model found in saved_model.")
        st.info("Run: python train.py --use-sample --train-basic")
        st.stop()

    dataset_status = _get_dataset_status()
    st.sidebar.success(f"Loaded model: {model_path}")
    st.sidebar.caption(f"Limits: {MAX_TEXT_CHARS} chars/text, {MAX_BATCH_ROWS} rows/batch, {MAX_UPLOAD_MB:.1f} MB/upload")
    if dataset_status["semeval_exists"] and dataset_status["semeval_rows"] > 0:
        st.sidebar.info(f"Data mode: SemEval/Kaggle ({dataset_status['semeval_rows']} rows)")
    else:
        st.sidebar.warning("Data mode: Sample-only. Add SemEval dataset for production analysis.")
    st.sidebar.markdown("### Confidence Guide")
    conf_guide = pd.DataFrame(
        {
            "band": ["Very High", "High", "Medium", "Low"],
            "threshold": [0.90, 0.75, 0.60, 0.00],
            "meaning": [
                "Prediction is strongly reliable",
                "Likely correct",
                "Borderline, verify context",
                "Uncertain, treat as weak signal",
            ],
        }
    )
    conf_fig = px.bar(
        conf_guide,
        x="threshold",
        y="band",
        orientation="h",
        color="band",
        text=conf_guide["threshold"].map(lambda x: f">= {int(x * 100)}%"),
        title="What Confidence % Means",
        color_discrete_sequence=["#1f8f4e", "#4caf50", "#f6c85f", "#f44336"],
    )
    conf_fig.update_layout(showlegend=False, xaxis_title="Confidence", yaxis_title="")
    st.sidebar.plotly_chart(conf_fig, width="stretch")
    st.sidebar.caption("If confidence is below 60%, check multiple reviews before deciding.")

    tabs = st.tabs(["Single", "Compare", "Batch", "Insights", "Data Ops"])

    with tabs[0]:
        st.subheader("Single Review Analysis")
        text = st.text_area("Review text", height=140, placeholder="The battery is poor but the camera is amazing.")
        if st.button("Analyze Review", width="stretch"):
            if not text.strip():
                st.warning("Please enter a review.")
            else:
                cleaned_text = _sanitize_text(text)
                aspect_lexicon = _load_aspect_lexicon()
                sentiment, confidence, prob_row = predict_one(cleaned_text, artifact)
                c1, c2 = st.columns(2)
                c1.metric("Sentiment", sentiment.upper())
                c2.metric("Confidence", f"{confidence:.1%}")
                st.markdown(f"Result class: <span class='{badge(sentiment)}'>{sentiment.upper()}</span>", unsafe_allow_html=True)

                quality_band = "Strong" if confidence >= MIN_CONFIDENCE_GOOD else "Needs Review"
                st.markdown(
                    f"<div class='kpi-card'><b>Executive Signal:</b> {quality_band} decision confidence for this review.</div>",
                    unsafe_allow_html=True,
                )

                sorted_probs = prob_row.sort_values(ascending=False)
                top_two = sorted_probs.head(2)
                st.caption(
                    f"Top classes: {top_two.index[0]} ({top_two.iloc[0]:.1%}), "
                    f"{top_two.index[1]} ({top_two.iloc[1]:.1%})"
                )

                prob_plot = pd.DataFrame(
                    {
                        "sentiment": prob_row.index,
                        "probability": prob_row.values,
                    }
                )
                fig = px.bar(
                    prob_plot,
                    x="sentiment",
                    y="probability",
                    color="sentiment",
                    text=prob_plot["probability"].map(lambda x: f"{x:.1%}"),
                    title="Class Probability Breakdown (Positive/Negative/Neutral)",
                    color_discrete_map={
                        "positive": "#2ca02c",
                        "negative": "#d62728",
                        "neutral": "#7f7f7f",
                    },
                )
                fig.update_layout(yaxis_title="Probability", xaxis_title="Sentiment")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, width="stretch")

                st.markdown("#### Aspect-by-Clause Sentiment Breakdown")
                clause_df = _analyze_clause_level(cleaned_text, artifact, aspect_lexicon)
                st.dataframe(clause_df, width="stretch")

                for _, row in clause_df.iterrows():
                    sentiment_class = str(row["sentiment"]).lower()
                    chip_class = "chip-neu"
                    if sentiment_class == "positive":
                        chip_class = "chip-pos"
                    elif sentiment_class == "negative":
                        chip_class = "chip-neg"
                    st.markdown(
                        f"<div style='margin-bottom:0.35rem;'><span class='chip {chip_class}'>{sentiment_class.upper()}</span> "
                        f"<b>{row['aspect']}</b>: {row['clause']}</div>",
                        unsafe_allow_html=True,
                    )

    with tabs[1]:
        st.subheader("Compare Two Reviews")
        c1, c2 = st.columns(2)
        t1 = c1.text_area("Review A", height=130)
        t2 = c2.text_area("Review B", height=130)
        if st.button("Compare", width="stretch"):
            rows = []
            active_reviews = [("A", t1), ("B", t2)]
            valid = [(name, _sanitize_text(text)) for name, text in active_reviews if text.strip()]

            if valid:
                review_names = [x[0] for x in valid]
                review_texts = [x[1] for x in valid]
                labels, conf, prob_df = _predict_detailed(review_texts, artifact)
                for idx, name in enumerate(review_names):
                    rows.append({"review": name, "sentiment": labels[idx], "confidence": conf[idx]})

            if not rows:
                st.warning("Enter at least one review.")
            else:
                df = pd.DataFrame(rows)
                st.dataframe(df, width="stretch")
                fig = px.bar(df, x="review", y="confidence", color="sentiment", title="Confidence Comparison")
                st.plotly_chart(fig, width="stretch")

                prob_df = prob_df.copy()
                prob_df["review"] = review_names
                melt_df = prob_df.melt(id_vars=["review"], var_name="sentiment", value_name="probability")
                prob_comp = px.bar(
                    melt_df,
                    x="sentiment",
                    y="probability",
                    color="review",
                    barmode="group",
                    title="Per-Class Probability Comparison",
                )
                st.plotly_chart(prob_comp, width="stretch")

    with tabs[2]:
        st.subheader("Batch Processing")
        method = st.radio("Input method", ["Upload CSV", "Paste lines"], horizontal=True)
        confidence_threshold = st.slider("Minimum confidence to display", 0.0, 1.0, 0.0, 0.05)
        sentiment_filter = st.multiselect(
            "Sentiments to display",
            options=SENTIMENT_ORDER,
            default=SENTIMENT_ORDER,
        )

        batch_df = None
        text_col = None

        if method == "Upload CSV":
            up = st.file_uploader("Upload CSV", type=["csv"])
            if up is not None:
                upload_size_mb = up.size / (1024 * 1024)
                if upload_size_mb > MAX_UPLOAD_MB:
                    st.error(f"File is too large ({upload_size_mb:.2f} MB). Max allowed: {MAX_UPLOAD_MB:.1f} MB")
                else:
                    try:
                        batch_df = pd.read_csv(up)
                    except Exception as exc:
                        st.error(f"Could not read CSV: {exc}")
                for col in ["sentence", "text", "review", "content", "comment", "body"]:
                    if batch_df is not None and col in batch_df.columns:
                        text_col = col
                        break
                if batch_df is not None and text_col is None:
                    st.error(f"No text column found. Available columns: {batch_df.columns.tolist()}")
                elif batch_df is not None:
                    if len(batch_df) > MAX_BATCH_ROWS:
                        batch_df = batch_df.head(MAX_BATCH_ROWS).copy()
                        st.warning(f"Input had more than {MAX_BATCH_ROWS} rows. Only first {MAX_BATCH_ROWS} were kept.")
                    st.success(f"Using text column: {text_col} ({len(batch_df)} rows)")

        else:
            raw = st.text_area("One review per line", height=180)
            lines = [_sanitize_text(x) for x in raw.splitlines() if x.strip()]
            if lines:
                if len(lines) > MAX_BATCH_ROWS:
                    lines = lines[:MAX_BATCH_ROWS]
                    st.warning(f"Only first {MAX_BATCH_ROWS} lines were kept.")
                batch_df = pd.DataFrame({"review": lines})
                text_col = "review"
                st.success(f"Captured {len(lines)} reviews")

        if batch_df is not None and text_col is not None and st.button("Run Batch", width="stretch"):
            texts = [_sanitize_text(x) for x in batch_df[text_col].fillna("").astype(str).tolist()]
            labels, conf, prob_df = _predict_detailed(texts, artifact)
            out = batch_df.copy()
            out["predicted_sentiment"] = labels
            out["confidence"] = [round(float(x), 4) for x in conf]

            # Add probability columns for transparency (helps explain positive vs negative visibility).
            for sentiment in SENTIMENT_ORDER:
                out[f"prob_{sentiment}"] = prob_df[sentiment].round(4)

            filtered = out[
                (out["confidence"] >= confidence_threshold)
                & (out["predicted_sentiment"].isin(sentiment_filter if sentiment_filter else SENTIMENT_ORDER))
            ].copy()

            st.dataframe(filtered, width="stretch", height=420)

            summary = filtered["predicted_sentiment"].value_counts().reindex(SENTIMENT_ORDER, fill_value=0).reset_index()
            summary.columns = ["sentiment", "count"]
            fig = px.pie(summary, names="sentiment", values="count", title="Sentiment Distribution")
            st.plotly_chart(fig, width="stretch")

            uncertain = out.sort_values("confidence", ascending=True).head(5)
            st.markdown("#### Most Uncertain Predictions")
            st.dataframe(
                uncertain[[text_col, "predicted_sentiment", "confidence", "prob_positive", "prob_negative", "prob_neutral"]],
                width="stretch",
            )

            st.download_button(
                label="Download Batch Results",
                data=out.to_csv(index=False),
                file_name="absa_batch_results.csv",
                mime="text/csv",
                width="stretch",
            )

    with tabs[3]:
        st.subheader("Model Insights")
        st.write("Use this section to quickly sanity-check predictions.")
        probes = [
            "The battery is excellent and lasts long.",
            "Terrible camera quality and laggy performance.",
            "The build is okay for the price.",
        ]
        labels, conf = _predict_with_artifact(probes, artifact)
        probe_df = pd.DataFrame({"probe_text": probes, "predicted_sentiment": labels, "confidence": conf})
        st.dataframe(probe_df, width="stretch")

    with tabs[4]:
        st.subheader("Kaggle Dataset + Deployment Readiness")
        st.write("Prepare a production-grade dataset and train on SemEval instead of sample reviews.")

        status = _get_dataset_status()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("SemEval Rows", status["semeval_rows"])
            st.metric("Sample Rows", status["sample_rows"])
        with c2:
            st.caption("Recommended production flow")
            st.code("python download_semeval_dataset.py\npython train.py --data-path data/semeval_2014_absa.csv --train-basic")

        if st.button("Run Kaggle/SemEval Download", width="stretch"):
            with st.spinner("Downloading and preparing SemEval dataset..."):
                code, out = _run_command([sys.executable, "download_semeval_dataset.py"])
            if code == 0:
                st.success("SemEval dataset prepared.")
                _get_dataset_status.clear()
            else:
                st.error("Dataset step failed. Check Kaggle credentials.")
            st.text_area("Command Output", value=out, height=220)

        if st.button("Train Basic Model on SemEval", width="stretch"):
            with st.spinner("Training model on Kaggle/SemEval dataset..."):
                code, out = _run_command([
                    sys.executable,
                    "train.py",
                    "--data-path",
                    "data/semeval_2014_absa.csv",
                    "--train-basic",
                ])
            if code == 0:
                st.success("Training completed on SemEval dataset.")
                load_model_artifact.clear()
            else:
                st.error("Training failed. Review output.")
            st.text_area("Training Output", value=out, height=220)


if __name__ == "__main__":
    main()
