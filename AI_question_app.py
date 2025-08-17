import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API Key が取得できません。")
        return

    client = OpenAI(api_key=api_key)

    st.title("💬 トレーニング・栄養AI質問アプリ")

    # 初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "あなたは親切で専門的なトレーニング・栄養アドバイザーです。"}
        ]

    # これまでの会話を表示（systemは除外）
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        role = "**あなた:**" if msg["role"] == "user" else "**AI:**"
        st.markdown(f"{role} {msg['content']}")

    # 入力フォーム
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("質問を入力してください")
        submitted = st.form_submit_button("送信")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:personal::C4ttwgEk",
                messages=st.session_state.messages,
            )
            assistant_message = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            st.error(f"API呼び出しエラー: {e}")

        # 最新のやりとりを表示
        for msg in st.session_state.messages[-2:]:
            if msg["role"] == "system":
                continue
            role = "**あなた:**" if msg["role"] == "user" else "**AI:**"
            st.markdown(f"{role} {msg['content']}")

if __name__ == "__main__":
    main()


