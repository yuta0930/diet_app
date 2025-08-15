# AI_question_app.py
import streamlit as st
import openai
from dotenv import load_dotenv
import os

def main():
    # --------------------------
    # .env読み込み
    # --------------------------
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("⚠️ OPENAI_API_KEY が .env から取得できませんでした。")
        return
    else:
        openai.api_key = api_key

    # --------------------------
    # Streamlit UI
    # --------------------------
    st.set_page_config(page_title="トレーニング・栄養AI", layout="wide")
    st.title("💪 トレーニング・栄養AI（チャット）")

    # セッションステートにチャット履歴を保持
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # チャット履歴表示
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**あなた:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**AI:** {msg['content']}")

    # ユーザー入力フォーム
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("質問を入力してください", "")
        submitted = st.form_submit_button("送信")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        try:
            # OpenAI API呼び出し
            response = openai.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:personal::C4ttwgEk",  # ファインチューニング済みモデル
                messages=st.session_state.messages
            )
            assistant_message = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            st.markdown(f"**AI:** {assistant_message}")
        except Exception as e:
            st.error(f"API呼び出しでエラーが発生しました: {e}")
