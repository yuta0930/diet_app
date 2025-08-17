# AI_question_app.py
import streamlit as st
import openai
from dotenv import load_dotenv
import os

def main():
    st.title("💬 トレーニング・栄養AI質問アプリ")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API Key が取得できません。")
        return
    openai.api_key = api_key

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_placeholder = st.empty()

    def display_chat():
        """AIを左、質問者を右にした吹き出し表示"""
        with chat_placeholder.container():
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                        <div style="
                            display:flex;
                            justify-content:flex-end;  /* 右寄せ */
                            margin:6px 0;
                        ">
                            <div style="
                                background-color:#1f2937;
                                color:white;
                                padding:12px 16px;
                                border-radius:16px 16px 0 16px;  /* 右側吹き出し */
                                max-width:70%;
                                font-size:16px;
                            ">
                                👤 <strong>あなた:</strong><br>{msg['content']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="
                            display:flex;
                            justify-content:flex-start;  /* 左寄せ */
                            margin:6px 0;
                        ">
                            <div style="
                                background-color:#1f2937;
                                color:#a5d8ff;
                                padding:12px 16px;
                                border-radius:16px 16px 16px 0;  /* 左側吹き出し */
                                max-width:70%;
                                font-size:16px;
                            ">
                                🤖 <strong>AI:</strong><br>{msg['content']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.markdown("<div style='height:1px;'>&nbsp;</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("質問を入力してください", key="user_input")
        submitted = st.form_submit_button("送信")

        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            try:
                response = openai.chat.completions.create(
                    model="ft:gpt-3.5-turbo-0125:personal::C5XqVe0t",
                    messages=st.session_state.messages
                )
                assistant_message = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            except Exception as e:
                st.error(f"API呼び出しエラー: {e}")

    display_chat()

if __name__ == "__main__":
    main()
