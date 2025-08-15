import math
import streamlit as st

ACTIVITY_FACTORS = {
    "ほぼ動かない（デスクワーク中心・運動なし）": 1.2,
    "軽い運動（週1〜3回の軽い運動）": 1.375,
    "中程度の運動（週3〜5回の中強度運動）": 1.55,
    "激しい運動（ほぼ毎日運動・肉体労働）": 1.725,
    "非常に激しい運動（アスリート並み）": 1.9,
}

def mifflin_st_jeor_bmr(sex, weight_kg, height_cm, age):
    return 10*weight_kg + 6.25*height_cm - 5*age + (5 if sex=="男性" else -161)

def katch_mcardle_bmr(weight_kg, body_fat):
    lbm = weight_kg * (1 - body_fat/100.0)
    return 370 + 21.6*lbm

def validate_positive(name, value):
    if not math.isfinite(value) or value <= 0:
        st.error(f"{name} は正の数を入力してください。")
        st.stop()

def round_int(x):
    return int(round(x))

def main():
    st.set_page_config(page_title="体重維持カロリー計算（TDEE）", page_icon="⚖️", layout="centered")
    st.title("⚖️ 体重維持カロリー計算（TDEE）")

    # session_state初期化
    defaults = {
        "unit": "メートル法（kg, cm）",
        "sex": "男性",
        "age": 30,
        "activity_label": "中程度の運動（週3〜5回の中強度運動）",
        "weight": 65.0,
        "height": 170.0,
        "body_fat": 0.0,
        "formula": "Mifflin-St Jeor（標準）"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.form("tdee_form"):
        st.session_state.unit = st.radio("単位の選択", ["メートル法（kg, cm）", "ヤード・ポンド法（lb, in）"], horizontal=True, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.sex = st.selectbox("性別", ["男性", "女性"], index=0)
            st.session_state.age = st.number_input("年齢（歳）", min_value=10, max_value=100, value=st.session_state.age, step=1)
            st.session_state.activity_label = st.selectbox("活動レベル", list(ACTIVITY_FACTORS.keys()), index=2)
        with col2:
            if st.session_state.unit.startswith("メートル法"):
                st.session_state.weight = st.number_input("体重（kg）", min_value=20.0, max_value=300.0, value=st.session_state.weight, step=0.1)
                st.session_state.height = st.number_input("身長（cm）", min_value=120.0, max_value=250.0, value=st.session_state.height, step=0.1)
            else:
                st.session_state.weight = st.number_input("体重（lb）", min_value=44.0, max_value=660.0, value=st.session_state.weight, step=0.1)
                st.session_state.height = st.number_input("身長（in）", min_value=47.0, max_value=98.0, value=st.session_state.height, step=0.1)
            st.session_state.body_fat = st.number_input("体脂肪率（%）※任意", min_value=0.0, max_value=70.0, value=st.session_state.body_fat, step=0.1)

        st.session_state.formula = st.radio("BMRの計算式", ["Mifflin-St Jeor（標準）", "Katch-McArdle（体脂肪率が必要）"], index=0)
        submitted = st.form_submit_button("計算 ▶")

    if submitted:
        validate_positive("年齢", float(st.session_state.age))
        validate_positive("体重", float(st.session_state.weight))
        validate_positive("身長", float(st.session_state.height))

        # 単位変換
        if st.session_state.unit.startswith("メートル法"):
            weight_kg = st.session_state.weight
            height_cm = st.session_state.height
        else:
            weight_kg = st.session_state.weight * 0.45359237
            height_cm = st.session_state.height * 2.54

        # BMR計算
        if st.session_state.formula.startswith("Katch"):
            if st.session_state.body_fat <= 0.0:
                st.error("Katch-McArdle を選ぶ場合は体脂肪率を入力してください。")
                st.stop()
            bmr = katch_mcardle_bmr(weight_kg, st.session_state.body_fat)
            formula_used = "Katch-McArdle"
        else:
            bmr = mifflin_st_jeor_bmr(st.session_state.sex, weight_kg, height_cm, int(st.session_state.age))
            formula_used = "Mifflin-St Jeor"

        activity_factor = ACTIVITY_FACTORS[st.session_state.activity_label]
        tdee = bmr * activity_factor

        cut_10 = tdee * 0.90
        bulk_10 = tdee * 1.10

        st.success(f"計算結果（式：{formula_used}、活動係数：{activity_factor}）")
        c1, c2, c3 = st.columns(3)
        c1.metric("BMR（基礎代謝）", f"{round_int(bmr)} kcal/日")
        c2.metric("TDEE（維持カロリー）", f"{round_int(tdee)} kcal/日")
        c3.metric("活動係数", f"{activity_factor}")

        st.divider()
        st.subheader("目安の摂取カロリー")
        st.markdown(
            f"""
            - 維持: **{round_int(tdee)} kcal/日**  
            - 減量（-10%）: **{round_int(cut_10)} kcal/日**  
            - 増量（+10%）: **{round_int(bulk_10)} kcal/日**
            """
        )

        prot_low = weight_kg * 1.6
        prot_high = weight_kg * 2.2
        st.caption(f"タンパク質摂取目安: {prot_low:.0f}〜{prot_high:.0f} g/日")
