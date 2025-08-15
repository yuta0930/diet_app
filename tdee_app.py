# tdee_app.py
import math
import streamlit as st

ACTIVITY_FACTORS = {
    "ほぼ動かない（デスクワーク中心・運動なし）": 1.2,
    "軽い運動（週1〜3回の軽い運動）": 1.375,
    "中程度の運動（週3〜5回の中強度運動）": 1.55,
    "激しい運動（ほぼ毎日運動・肉体労働）": 1.725,
    "非常に激しい運動（アスリート並み）": 1.9,
}

def mifflin_st_jeor_bmr(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if sex=="男性" else -161)

def katch_mcardle_bmr(weight_kg: float, body_fat_percent: float) -> float:
    lbm = weight_kg * (1 - body_fat_percent / 100.0)
    return 370 + 21.6 * lbm

def validate_positive(name: str, value: float):
    if not math.isfinite(value) or value <= 0:
        st.error(f"{name} は正の数を入力してください。")
        st.stop()

def round_int(x: float) -> int:
    return int(round(x))

def main():
    st.title("⚖️ 体重維持カロリー計算（TDEE）")
    st.caption("Mifflin-St Jeor または Katch-McArdle でTDEEを計算します。")

    # サイドバー説明
    with st.sidebar:
        st.header("使い方")
        st.markdown(
            """
            1. 単位を選択  
            2. 必要項目を入力して「計算 ▶」  
            3. 維持・減量・増量のカロリー目安が表示
            """
        )

    # セッションステート初期化
    defaults = {
        "unit": "メートル法（kg, cm）",
        "sex": "男性",
        "age": 30,
        "activity_label": "中程度の運動（週3〜5回の中強度運動）",
        "weight": 65.0,
        "height": 170.0,
        "body_fat": 0.0,
        "formula": "Mifflin-St Jeor",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.form("tdee_form"):
        unit = st.radio("単位", ["メートル法（kg, cm）", "ヤード・ポンド法（lb, in）"], index=0 if st.session_state["unit"].startswith("メートル") else 1, horizontal=True)
        col1, col2 = st.columns(2)
        with col1:
            sex = st.selectbox("性別", ["男性", "女性"], index=0 if st.session_state["sex"]=="男性" else 1)
            age = st.number_input("年齢（歳）", min_value=10, max_value=100, value=st.session_state["age"], step=1)
            activity_label = st.selectbox("活動レベル", list(ACTIVITY_FACTORS.keys()), index=list(ACTIVITY_FACTORS.keys()).index(st.session_state["activity_label"]))
        with col2:
            if unit.startswith("メートル法"):
                weight = st.number_input("体重（kg）", min_value=20.0, max_value=300.0, value=st.session_state["weight"], step=0.1)
                height = st.number_input("身長（cm）", min_value=120.0, max_value=250.0, value=st.session_state["height"], step=0.1)
            else:
                weight = st.number_input("体重（lb）", min_value=44.0, max_value=660.0, value=st.session_state["weight"], step=0.1)
                height = st.number_input("身長（in）", min_value=47.0, max_value=98.0, value=st.session_state["height"], step=0.1)
            body_fat = st.number_input("体脂肪率（%）※任意", min_value=0.0, max_value=70.0, value=st.session_state["body_fat"], step=0.1)

        formula = st.radio("BMR式", ["Mifflin-St Jeor", "Katch-McArdle"], index=0 if st.session_state["formula"].startswith("Mifflin") else 1)
        submitted = st.form_submit_button("計算 ▶")

    if submitted:
        # 入力値をセッションに保存
        st.session_state.update({
            "unit": unit,
            "sex": sex,
            "age": age,
            "activity_label": activity_label,
            "weight": weight,
            "height": height,
            "body_fat": body_fat,
            "formula": formula
        })

        validate_positive("年齢", float(age))
        validate_positive("体重", float(weight))
        validate_positive("身長", float(height))

        weight_kg = weight if unit.startswith("メートル法") else weight*0.45359237
        height_cm = height if unit.startswith("メートル法") else height*2.54

        if formula.startswith("Katch") and body_fat <= 0.0:
            st.error("Katch-McArdle を選ぶ場合は体脂肪率を入力してください。")
            st.stop()

        bmr = katch_mcardle_bmr(weight_kg, body_fat) if formula.startswith("Katch") else mifflin_st_jeor_bmr(sex, weight_kg, height_cm, int(age))
        tdee = bmr * ACTIVITY_FACTORS[activity_label]
        cut_10 = tdee * 0.9
        bulk_10 = tdee * 1.1

        # 計算結果をセッションに保存
        st.session_state['bmr'] = round_int(bmr)
        st.session_state['tdee'] = round_int(tdee)
        st.session_state['cut_10'] = round_int(cut_10)
        st.session_state['bulk_10'] = round_int(bulk_10)

    # 計算結果を表示
    if 'bmr' in st.session_state:
        st.success(f"BMR: {st.session_state['bmr']} kcal, TDEE: {st.session_state['tdee']} kcal")
        st.markdown(
            f"- 維持: **{st.session_state['tdee']} kcal**\n"
            f"- 減量(-10%): **{st.session_state['cut_10']} kcal**\n"
            f"- 増量(+10%): **{st.session_state['bulk_10']} kcal**"
        )

if __name__ == "__main__":
    main()
