import streamlit as st

# --------------------------
# ページ設定
# --------------------------
st.set_page_config(
    page_title="トレーニング・栄養アプリ",
    page_icon="💪",
    layout="wide"
)

# --------------------------
# カスタムCSS（スマホ対応）
# --------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1000px;
        margin: auto;
    }
    @media (max-width: 768px) {
        h1 {font-size: 1.5rem;}
        h2 {font-size: 1.2rem;}
        h3 {font-size: 1rem;}
        p, label, div {font-size: 0.9rem;}
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# サブアプリのインポート
# --------------------------
from tdee_app import main as tdee_main
from PFC_app import main as pfc_main
from AI_question_app import main as ai_question_main
from calorie_app import main as calorie_main

# --------------------------
# ボタンでアプリ切替
# --------------------------
app_choice = st.radio(
    "使用するアプリを選んでください",
    ("TDEE計算アプリ", "グラム計算アプリ", "カロリー予測アプリ", "AI質問アプリ"),
    horizontal=True
)

if app_choice == "TDEE計算アプリ":
    tdee_main()
elif app_choice == "グラム計算アプリ":
    pfc_main()
elif app_choice == "カロリー予測アプリ":
    calorie_main()
elif app_choice == "AI質問アプリ":
    ai_question_main()
