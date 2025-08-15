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

    st.title("🍱 PFCグラム計算アプリ（改善版＋食材カロリー表示）")
    st.caption("GPTに食材ごとの推奨グラム数と合計PFCを計算させます。")

    # --------------------------
    # GPT計算関数
    # --------------------------
    @st.cache_data(show_spinner=True)
    def get_gpt_full_pfc(food_names, total_kcal, p_ratio, f_ratio, c_ratio, min_gram=50):
        priority = {}
        for i, food in enumerate(food_names):
            if i == 0:
                priority[food] = "主食"
            elif i == 1:
                priority[food] = "主菜"
            else:
                priority[food] = "副菜"

        prompt = f"""
        あなたは栄養士です。
        以下の条件を満たすように、食材ごとの推奨グラム数を計算してください。

        条件:
        - 食材: {', '.join(food_names)}
        - 各食材の最低量: {min_gram}g
        - 食材優先度: {priority}
        - 目標総カロリー: {total_kcal} kcal
        - PFC比率: P {p_ratio}%, F {f_ratio}%, C {c_ratio}%
        - 出力は現実的な食材量にしてください。0gや極端に少ないグラムは避けてください。
        - JSONのみで出力。解説なし。
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            for food, gram in result.get("食材グラム", {}).items():
                if gram < min_gram:
                    result["食材グラム"][food] = min_gram
            return result
        except Exception as e:
            st.warning(f"計算に失敗: {e}")
            return None

    # --------------------------
    # 入力
    # --------------------------
    st.subheader("1) 食材名をカンマ区切りで入力")
    if "food_input" not in st.session_state:
        st.session_state.food_input = "ご飯, 鶏むね肉"
    food_input = st.text_input("例）ご飯, 鶏むね肉, 納豆", value=st.session_state.food_input)
    st.session_state.food_input = food_input

    st.subheader("2) 目標設定")
    col_a, col_b = st.columns([1,2])
    with col_a:
        if "total_kcal" not in st.session_state:
            st.session_state.total_kcal = 600.0
        total_kcal = st.number_input("目標総カロリー (kcal)", min_value=0.0, value=st.session_state.total_kcal, step=10.0)
        st.session_state.total_kcal = total_kcal
    with col_b:
        if "p_ratio" not in st.session_state:
            st.session_state.p_ratio = 30.0
            st.session_state.f_ratio = 20.0
            st.session_state.c_ratio = 50.0
        p_ratio = st.number_input("P(%)", min_value=0.0, max_value=100.0, value=st.session_state.p_ratio, step=1.0)
        f_ratio = st.number_input("F(%)", min_value=0.0, max_value=100.0, value=st.session_state.f_ratio, step=1.0)
        c_ratio = st.number_input("C(%)", min_value=0.0, max_value=100.0, value=st.session_state.c_ratio, step=1.0)
        st.session_state.p_ratio = p_ratio
        st.session_state.f_ratio = f_ratio
        st.session_state.c_ratio = c_ratio

        if abs((p_ratio + f_ratio + c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")

    # --------------------------
    # 計算ボタン
    # --------------------------
    st.subheader("3) GPTに計算してもらう")
    if "pfc_result" not in st.session_state:
        st.session_state.pfc_result = None

    names = [s.strip() for s in food_input.split(",") if s.strip()]

    if st.button("おすすめグラム数を取得"):
        if not names:
            st.error("食材名を入力してください。")
        elif abs((p_ratio + f_ratio + c_ratio) - 100.0) > 1e-6:
            st.error("P+F+C の合計を 100% にしてください。")
        else:
            st.session_state.pfc_result = get_gpt_full_pfc(names, total_kcal, p_ratio, f_ratio, c_ratio, min_gram=50)

    # --------------------------
    # 結果表示関数
    # --------------------------
    def display_result(result):
        if "食材グラム" in result and "合計カロリー" in result and "合計PFC" in result:
            st.success("計算完了！")

            st.subheader("食材ごとの推奨グラム数とカロリー")
            grams = result["食材グラム"]
            total_cal = result["合計カロリー"]

            total_grams = sum(grams.values())
            data = []
            for food, gram in grams.items():
                kcal = total_cal * (gram / total_grams)
                data.append({"食材名": food, "推奨グラム(g)": gram, "カロリー(kcal)": round(kcal,1)})
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            st.subheader("合計カロリーとPFC比率")
            pfc = result["合計PFC"]
            st.write(f"総カロリー: {total_cal} kcal（目標: {total_kcal} kcal）")
            st.write(f"PFC比率: P {pfc.get('P',0)}% / F {pfc.get('F',0)}% / C {pfc.get('C',0)}%")
        else:
            st.warning("返却されたデータに必要なキーが含まれていません。JSON形式を確認してください。")

    # ページロード時も自動で表示
    if st.session_state.pfc_result:
        display_result(st.session_state.pfc_result)

if __name__ == "__main__":
    main()
