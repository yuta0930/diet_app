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
        st.error("OpenAI API Key が取得できません。")
        return
    openai.api_key = api_key

    st.title("💬 トレーニング・栄養AI質問アプリ")

    # --------------------------
    # セッションステート初期化
    # --------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # これまでの会話を表示
    for msg in st.session_state.messages:
        role = "**あなた:**" if msg["role"] == "user" else "**AI:**"
        st.markdown(f"{role} {msg['content']}")

    # --------------------------
    # フォーム入力
    # --------------------------
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("質問を入力してください")
        submitted = st.form_submit_button("送信")

    if submitted and user_input:
        # ユーザーの質問を保存
        st.session_state.messages.append({"role":"user","content":user_input})

        try:
            # ChatCompletion 呼び出し
            response = openai.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:personal::C4ttwgEk",
                messages=st.session_state.messages
            )

            # 修正: オブジェクト属性としてアクセス
            assistant_message = response.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":assistant_message})

        except Exception as e:
            st.error(f"API呼び出しエラー: {e}")

        # 最新の 2 件の会話を表示
        for msg in st.session_state.messages[-2:]:
            role = "**あなた:**" if msg["role"] == "user" else "**AI:**"
            st.markdown(f"{role} {msg['content']}")

if __name__ == "__main__":
    main()


