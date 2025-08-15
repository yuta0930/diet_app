# PFC_app.py
import streamlit as st

def main():
    st.title("🍽 PFC計算アプリ（手動）")
    st.caption("目標カロリーとPFC比率から必要量を計算します。")

    with st.form("pfc_form"):
        total_kcal = st.number_input("総カロリー(kcal)", min_value=0, value=2000)
        p_ratio = st.number_input("P(%)", min_value=0, max_value=100, value=30)
        f_ratio = st.number_input("F(%)", min_value=0, max_value=100, value=20)
        c_ratio = st.number_input("C(%)", min_value=0, max_value=100, value=50)
        submitted = st.form_submit_button("計算 ▶")

    if submitted:
        if abs(p_ratio + f_ratio + c_ratio - 100) > 1e-6:
            st.error("P+F+Cの合計は100%にしてください。")
            return
        p_kcal = total_kcal * p_ratio / 100
        f_kcal = total_kcal * f_ratio / 100
        c_kcal = total_kcal * c_ratio / 100
        st.success(f"P: {p_kcal/4:.1f} g, F: {f_kcal/9:.1f} g, C: {c_kcal/4:.1f} g")
