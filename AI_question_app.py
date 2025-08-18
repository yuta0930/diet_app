import streamlit as st
import openai
from dotenv import load_dotenv
import os
import re

def main(container=None):
    if container is None:
        container = st  # デフォルトは st

    container.title("💬 トレーニング・栄養AI質問アプリ")

    # --------------------------
    # .env読み込み
    # --------------------------
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        container.error("OpenAI API Key が取得できません。")
        return
    openai.api_key = api_key

    # --------------------------
    # セッションステート初期化
    # --------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "あなたはトレーニングと栄養の専門家です！"
                    "回答はフレンドリーで明るく、相手に優しく寄り添って安心感を与えてください！"
                    "文章の語尾には「！」「～」を使ってください！"
                    "回答は見出し・太字・区切り線を使って見やすくしてください！"
                    "最後に「次に○○についても知りたい？」のように提案してください！"
                )
            }
        ]

    # --------------------------
    # チャット表示用コンテナ
    # --------------------------
    chat_placeholder = container.empty()

    # --------------------------
    # 簡易Markdown→HTML変換
    # --------------------------
    def simple_markdown_to_html(text):
        # 見出し
        text = re.sub(r'^###\s*(.+)$', r'<h4 style="margin:4px 0;">\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s*(.+)$', r'<h3 style="margin:6px 0;">\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^#\s*(.+)$', r'<h2 style="margin:8px 0;">\1</h2>', text, flags=re.MULTILINE)
        # 太字
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # 改行
        text = text.replace('\n', '<br>')
        return text

    # --------------------------
    # チャット表示関数
    # --------------------------
    def display_chat():
        with chat_placeholder.container():
            for msg in st.session_state.messages:
                content_html = simple_markdown_to_html(msg["content"])
                if msg["role"] == "user":
                    container.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-end; margin:6px 0;">
                            <div style="background-color:#1f2937; color:white; padding:12px 16px; 
                                        border-radius:16px 16px 0 16px; max-width:70%; font-size:16px;">
                                👤 <strong>あなた:</strong><br>{content_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif msg["role"] == "assistant":
                    container.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-start; margin:6px 0;">
                            <div style="background-color:#1f2937; color:#a5d8ff; padding:12px 16px; 
                                        border-radius:16px 16px 16px 0; max-width:70%; font-size:16px;">
                                🤖 <strong>AI:</strong><br>{content_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            container.markdown("<div style='height:1px;'>&nbsp;</div>", unsafe_allow_html=True)

    # --------------------------
    # 送信前にまずチャット表示
    # --------------------------
    display_chat()

    # --------------------------
    # チャット入力フォーム（改行対応）
    # --------------------------
    with container.form("chat_form", clear_on_submit=True):
        user_input = container.text_area("質問を入力してください", key="user_input", height=100)
        submitted = container.form_submit_button("送信")

        if submitted and user_input:
            # ユーザーメッセージ追加
            st.session_state.messages.append({"role": "user", "content": user_input})

            # 送信後すぐに過去チャットを表示
            display_chat()

            # AI応答中のスピナー
            with container.spinner("AIが考えています..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-5-mini",
                        messages=st.session_state.messages
                    )
                    assistant_message = response.choices[0].message.content

                    # AIメッセージ追加
                    st.session_state.messages.append({"role": "assistant", "content": assistant_message})

                    # AI応答後に再表示
                    display_chat()

                except Exception as e:
                    container.error(f"API呼び出しエラー: {e}")

# --------------------------
# 直接実行用
# --------------------------
if __name__ == "__main__":
    main()
