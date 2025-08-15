# app_openai_pfc_simple.py
import os
from dotenv import load_dotenv
import openai
import streamlit as st
import pandas as pd
import json

# --------------------------
# .env 読み込み
# --------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API Key が .env から取得できませんでした。")
    st.stop()

# --------------------------
# GPT計算関数（キャッシュあり）
# --------------------------
@st.cache_data(show_spinner=True)
def get_gpt_full_pfc(food_names, total_kcal, p_ratio, f_ratio, c_ratio):
    prompt = f"""
    あなたは栄養士です。
    以下の条件を満たすように、食材ごとの推奨グラム数と各食材ごとのカロリーを計算してください。
    合計カロリーとPFC比率も出してください。

    条件:
    - 食材: {', '.join(food_names)}
    - 目標総カロリー: {total_kcal} kcal
    - PFC比率: P {p_ratio}%, F {f_ratio}%, C {c_ratio}%

    出力はJSONのみ、解説なし。例:
    {{
      "食材": {{"ご飯": {{"グラム": 150, "カロリー": 252}}}},
      "合計カロリー": 550,
      "合計PFC": {{"P": 30, "F": 20, "C": 50}}
    }}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        return result
    except Exception as e:
        st.warning(f"計算に失敗: {e}")
        return None

# --------------------------
# メイン関数
# --------------------------
def main():
    st.set_page_config(page_title="PFCグラム計算（シンプル版）", layout="wide")
    st.title("PFCグラム計算アプリ（OpenAIシンプル版）🍱")
    st.caption("GPTに食材ごとの推奨グラム数とカロリー、合計PFCを計算させます。")

    # session_state初期化
    defaults = {
        "food_input": "ご飯, 鶏むね肉",
        "total_kcal": 600.0,
        "p_ratio": 30.0,
        "f_ratio": 20.0,
        "c_ratio": 50.0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --------------------------
    # 入力フォーム
    # --------------------------
    st.subheader("1) 食材名をカンマ区切りで入力")
    st.session_state.food_input = st.text_input(
        "例）ご飯, 鶏むね肉, 納豆",
        value=st.session_state.food_input
    )

    st.subheader("2) 目標設定")
    col_a, col_b = st.columns([1,2])
    with col_a:
        st.session_state.total_kcal = st.number_input(
            "目標総カロリー (kcal)",
            min_value=0.0, value=st.session_state.total_kcal, step=10.0
        )
    with col_b:
        st.session_state.p_ratio = st.number_input(
            "P(%)", min_value=0.0, max_value=100.0, value=st.session_state.p_ratio, step=1.0
        )
        st.session_state.f_ratio = st.number_input(
            "F(%)", min_value=0.0, max_value=100.0, value=st.session_state.f_ratio, step=1.0
        )
        st.session_state.c_ratio = st.number_input(
            "C(%)", min_value=0.0, max_value=100.0, value=st.session_state.c_ratio, step=1.0
        )
        if abs((st.session_state.p_ratio + st.session_state.f_ratio + st.session_state.c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")

    # --------------------------
    # 計算ボタン
    # --------------------------
    st.subheader("3) GPTに計算してもらう")
    if st.button("おすすめグラム数を取得"):
        names = [s.strip() for s in st.session_state.food_input.split(",") if s.strip()]
        if not names:
            st.error("食材名を入力してください。")
            st.stop()
        if abs((st.session_state.p_ratio + st.session_state.f_ratio + st.session_state.c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")
            st.stop()

        # GPT計算実行
        result = get_gpt_full_pfc(
            names,
            st.session_state.total_kcal,
            st.session_state.p_ratio,
            st.session_state.f_ratio,
            st.session_state.c_ratio
        )

        if result:
            st.success("計算完了！")

            st.subheader("食材ごとの推奨グラム数とカロリー")
            grams_cal_df = pd.DataFrame([
                {"食材名": name, "推奨グラム(g)": data["グラム"], "カロリー(kcal)": data["カロリー"]}
                for name, data in result["食材"].items()
            ])
            st.dataframe(grams_cal_df, use_container_width=True)

            st.subheader("合計カロリーとPFC比率")
            st.write(f"総カロリー: {result['合計カロリー']} kcal（目標: {st.session_state.total_kcal} kcal）")
            st.write(f"PFC比率: P {result['合計PFC']['P']}% / F {result['合計PFC']['F']}% / C {result['合計PFC']['C']}%")
