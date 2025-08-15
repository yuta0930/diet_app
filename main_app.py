import streamlit as st
from AI_question_app import main as ai_question_main
from PFC_app import main as pfc_main
from tdee_app import main as tdee_main

st.sidebar.title("アプリ選択")

# 初期選択を TDEE に設定
default_index = 0  # TDEE計算アプリがリストの先頭なので index=0

app_choice = st.sidebar.selectbox(
    "使用するアプリを選んでください",
    ("TDEE計算アプリ", "PFC計算アプリ", "AI質問アプリ"),
    index=default_index
)

# 選択されたアプリを表示
if app_choice == "AI質問アプリ":
    ai_question_main()
elif app_choice == "PFC計算アプリ":
    pfc_main()
elif app_choice == "TDEE計算アプリ":
    tdee_main()