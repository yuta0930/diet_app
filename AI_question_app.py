# AI_question_app_simple_calorie.py
import streamlit as st
import openai
from dotenv import load_dotenv
import os

def main():
    st.title("💬 トレーニング・栄養AI質問アプリ（簡易カロリー推定）")

    # .env読み込み
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API Key が取得できません。")
        return
    openai.api_key = api_key

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "あなたはトレーニングと栄養の専門家です！"
                    "回答はフレンドリーで明るく、文章の語尾には「～」「！！」などを使ってください！"
                    "回答の最後には「次に○○についても知りたい？」のように提案してください！"
                )
            }
        ]

    chat_placeholder = st.empty()

    def format_message(content):
        return content.replace("\n", "<br>")

    def display_chat():
        with chat_placeholder.container():
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-end; margin:6px 0;">
                            <div style="background-color:#1f2937; color:white; padding:12px 16px; 
                                        border-radius:16px 16px 0 16px; max-width:70%; font-size:16px;">
                                👤 <strong>あなた:</strong><br>{format_message(msg['content'])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                elif msg["role"] == "assistant":
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-start; margin:6px 0;">
                            <div style="background-color:#1f2937; color:#a5d8ff; padding:12px 16px; 
                                        border-radius:16px 16px 16px 0; max-width:70%; font-size:16px;">
                                🤖 <strong>AI:</strong><br>{format_message(msg['content'])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            st.markdown("<div style='height:1px;'>&nbsp;</div>", unsafe_allow_html=True)

    # チャット入力
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("質問を入力してください", key="user_input", height=100)
        submitted = st.form_submit_button("送信")
        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            display_chat()
            with st.spinner("AIが考えています..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-5-mini",
                        messages=st.session_state.messages
                    )
                    assistant_message = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                    display_chat()
                except Exception as e:
                    st.error(f"API呼び出しエラー: {e}")

    st.markdown("---")
    st.subheader("🍱 簡易カロリー推定（画像説明入力方式）")
    uploaded_file = st.file_uploader("弁当の写真をアップロード（表示用）", type=["jpg", "jpeg", "png"])
    food_description = st.text_input("写真に写っている食材を入力（例: ご飯、唐揚げ、卵焼き）")

    if uploaded_file:
        st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)

    if st.button("カロリーを推定する"):
        if not food_description:
            st.warning("食材情報を入力してください！")
        else:
            st.session_state.messages.append({"role": "user", "content": f"この食材からカロリーを推定してください: {food_description}"})
            with st.spinner("AIがカロリーを計算中..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-5-mini",
                        messages=st.session_state.messages
                    )
                    assistant_message = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": f"📊 推定カロリー:\n{assistant_message}"})
                    display_chat()
                except Exception as e:
                    st.error(f"API呼び出しエラー: {e}")

if __name__ == "__main__":
    main()
