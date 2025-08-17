import streamlit as st

# --------------------------
# ページ設定（最初に1回だけ）
# --------------------------
st.set_page_config(
    page_title="トレーニング・栄養アプリ",
    page_icon="💪",
    layout="wide"
)

# --------------------------
# タイトル表示（画面最上部固定）
# --------------------------


# --------------------------
# サブアプリのインポート
# --------------------------
from tdee_app import main as tdee_main
from PFC_app import main as pfc_main
from AI_question_app import main as ai_question_main

# --------------------------
# サイドバーでアプリ選択
# --------------------------
st.sidebar.title("アプリ選択")
app_choice = st.sidebar.selectbox(
    "使用するアプリを選んでください",
    ("TDEE計算アプリ", "PFC計算アプリ", "AI質問アプリ")
)

# --------------------------
# 選択に応じてサブアプリを呼び出す
# --------------------------
if app_choice == "TDEE計算アプリ":
    tdee_main()
elif app_choice == "PFC計算アプリ":
    pfc_main()
elif app_choice == "AI質問アプリ":
    ai_question_main()
