# PFC_app.py
import os
from dotenv import load_dotenv
import openai
import streamlit as st
import pandas as pd
import json

def main():
    # --------------------------
    # .env読み込み
    # --------------------------
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        st.error("OpenAI API Key が .env から取得できませんでした。")
        return

    st.title("🍱 PFCグラム計算アプリ（OpenAIシンプル版）")
    st.caption("GPTに食材ごとの推奨グラム数と合計PFCを計算させます。")

    # --------------------------
    # GPT計算関数
    # --------------------------
    @st.cache_data(show_spinner=True)
    def get_gpt_full_pfc(food_names, total_kcal, p_ratio, f_ratio, c_ratio):
        prompt = f"""
        あなたは栄養士です。
        以下の条件を満たすように、食材ごとの推奨グラム数を計算してください。
        合計カロリーとPFC比率も出してください。

        条件:
        - 食材: {', '.join(food_names)}
        - 目標総カロリー: {total_kcal} kcal
        - PFC比率: P {p_ratio}%, F {f_ratio}%, C {c_ratio}%

        出力はJSONのみ、解説なし。例:
        {{
          "食材グラム": {{
            "ご飯": 150,
            "鶏むね肉": 120,
            "納豆": 50
          }},
          "合計カロリー": 610,
          "合計PFC": {{
            "P": 30,
            "F": 20,
            "C": 50
          }}
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
    # 入力
    # --------------------------
    st.subheader("1) 食材名をカンマ区切りで入力")
    food_input = st.text_input("例）ご飯, 鶏むね肉, 納豆", value="ご飯, 鶏むね肉")

    st.subheader("2) 目標設定")
    col_a, col_b = st.columns([1,2])
    with col_a:
        total_kcal = st.number_input("目標総カロリー (kcal)", min_value=0.0, value=600.0, step=10.0)
    with col_b:
        p_ratio = st.number_input("P(%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
        f_ratio = st.number_input("F(%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        c_ratio = st.number_input("C(%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
        if abs((p_ratio + f_ratio + c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")

    # --------------------------
    # 計算ボタン
    # --------------------------
    st.subheader("3) GPTに計算してもらう")
    if st.button("おすすめグラム数を取得"):
        names = [s.strip() for s in food_input.split(",") if s.strip()]
        if not names:
            st.error("食材名を入力してください。")
            return
        if abs((p_ratio + f_ratio + c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")
            return

        # 計算実行
        result = get_gpt_full_pfc(names, total_kcal, p_ratio, f_ratio, c_ratio)

        if result:
            # 必要キーのチェック
            if "食材グラム" in result and "合計カロリー" in result and "合計PFC" in result:
                st.success("計算完了！")

                st.subheader("食材ごとの推奨グラム数")
                grams_df = pd.DataFrame(list(result["食材グラム"].items()), columns=["食材名", "推奨グラム(g)"])
                st.dataframe(grams_df, use_container_width=True)

                st.subheader("合計カロリーとPFC比率")
                pfc = result["合計PFC"]
                st.write(f"総カロリー: {result.get('合計カロリー', 0)} kcal（目標: {total_kcal} kcal）")
                st.write(f"PFC比率: P {pfc.get('P',0)}% / F {pfc.get('F',0)}% / C {pfc.get('C',0)}%")
            else:
                st.warning("返却されたデータに必要なキーが含まれていません。JSON形式を確認してください。")
        else:
            st.error("計算結果を取得できませんでした。")
