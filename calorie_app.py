# calorie_app.py
import streamlit as st
import openai
from dotenv import load_dotenv
import os

def main():
    # --------------------------
    # APIキー読み込み
    # --------------------------
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API Key が取得できません。")
        st.stop()
    openai.api_key = api_key

    # --------------------------
    # セッションステート初期化
    # --------------------------
    if "dishes" not in st.session_state:
        st.session_state.dishes = []

    if "calorie_result" not in st.session_state:
        st.session_state.calorie_result = ""

    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None

    # --------------------------
    # メインUI
    # --------------------------
    st.title("🍴 カロリー予測アプリ")
    st.markdown("""
    - 複数の料理を登録可能（ご飯・からあげ・サラダなど）
    - 量が分からない場合は標準量や目安量でカロリー推定
    - 量が分かる場合はテキストでグラム数を入力
    """)

    # --------------------------
    # 新しい料理追加フォーム
    # --------------------------
    st.subheader("新しい料理を追加")
    dish_name = st.text_input("料理名（例：カレーライス）", key="dish_name_input")
    amount_known = st.radio(
        "量はわかりますか？",
        options=["はい、わかる", "いいえ、わからない"],
        key="amount_known_input"
    )

    dish_info = {}
    if amount_known == "はい、わかる":
        dish_info["amount_text"] = st.text_input(
            "量を入力してください（例：150g）",
            key="amount_text_input"
        )
    else:
        portion = st.selectbox(
            "目安量を選んでください",
            options=["少なめ", "普通", "大盛り"],
            key="portion_input"
        )
        dish_info["portion"] = portion

    if st.button("料理を追加", key="add_dish_button"):
        if dish_name.strip() != "":
            st.session_state.dishes.append({
                "name": dish_name,
                "info": dish_info,
                "amount_known": amount_known
            })
            st.session_state.calorie_result = ""  # 結果リセット

    # --------------------------
    # 削除処理（描画前に行う）
    # --------------------------
    if st.session_state.delete_index is not None:
        st.session_state.dishes.pop(st.session_state.delete_index)
        st.session_state.delete_index = None
        st.session_state.calorie_result = ""  # 結果リセット

    # --------------------------
    # 登録済み料理リスト（削除ボタン付き）
    # --------------------------
    st.subheader("登録済みの料理")
    for i, d in enumerate(st.session_state.dishes):
        info_text = d["info"].get("amount_text") if d["amount_known"] == "はい、わかる" else f"目安量: {d['info']['portion']}"
        cols = st.columns([4,1])
        cols[0].text(f"{i+1}. {d['name']} ({info_text})")
        if cols[1].button("削除", key=f"delete_{i}_{d['name']}"):
            st.session_state.delete_index = i  # フラグセット

    # --------------------------
    # カロリー計算
    # --------------------------
    if st.button("合計カロリー計算", key="calc_calorie_button"):
        if len(st.session_state.dishes) == 0:
            st.warning("少なくとも1つの料理を追加してください。")
        else:
            dish_lines = []
            for d in st.session_state.dishes:
                if d["amount_known"] == "はい、わかる":
                    line = f"{d['name']}: {d['info']['amount_text']}"
                else:
                    line = f"{d['name']}: 量不明（{d['info']['portion']}）"
                dish_lines.append(line)
            dish_text = "\n".join(dish_lines)

            prompt = f"""
あなたは料理のカロリー計算の専門家です。
以下の複数の料理と量から、それぞれの概算カロリー・PFC（たんぱく質・脂質・炭水化物）と
合計カロリー・合計PFCを計算してください。
- 量が不明な場合は、標準量または「少なめ」「普通」「大盛り」を想定して計算してください

料理一覧:
{dish_text}

出力形式は以下のようにしてください:
料理名: xxx kcal, たんぱく質 xx g, 脂質 xx g, 炭水化物 xx g
...
合計: xxx kcal, たんぱく質 xx g, 脂質 xx g, 炭水化物 xx g
"""
            with st.spinner("AIが計算しています..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "あなたは料理の栄養専門家です。"},
                            {"role": "user", "content": prompt}
                        ],
                    )
                    st.session_state.calorie_result = response.choices[0].message.content
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    # --------------------------
    # 計算結果表示
    # --------------------------
    if st.session_state.calorie_result:
        st.subheader("推定結果")
        st.text(st.session_state.calorie_result)


if __name__ == "__main__":
    main()
