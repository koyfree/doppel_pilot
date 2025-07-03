import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# CSS for radio button styling
st.markdown("""
<style>
div[data-baseweb="radio"] > div {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}
div[data-baseweb="radio"] label {
    background-color: #1b5b84;
    padding: 20px;
    border-radius: 12px;
    color: white;
    width: 320px;
    height: 200px;
    font-size: 16px;
    font-weight: 400;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
div[data-baseweb="radio"] input:checked + div {
    border: 2px solid #ffd54f;
}
</style>
""", unsafe_allow_html=True)

if "step" not in st.session_state:
    st.session_state["step"] = "start"

if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("설문 초반에 입력하신 ID를 동일하게 기입해 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요 :)")
    user_name = st.text_input("")

    if user_name:
        sheet_url = "https://docs.google.com/spreadsheets/d/1pQ9Wps-6sJH3EWgEgb4QdJJ_MItBBnSbTPbTKCWQhLI/edit?gid=1798623846#gid=1798623846"
        openai_api_key = st.secrets["openai"]["api_key"]

        try:
            knowledge = build_knowledge_dict(sheet_url, openai_api_key)

            if user_name not in knowledge:
                st.error("⚠️ ID를 정확하게 기입해 주세요.")
            else:
                st.success("✅ 확인 되었습니다!")
                st.session_state["user_name"] = user_name
                st.session_state["profile"] = knowledge[user_name]

                st.markdown("### 대화 주제를 선택해 주세요.")

                choice = st.radio(
                    label="",
                    options=["정신 건강", "관계 갈등"],
                    format_func=lambda x: "🧘 정신 건강" if x == "정신 건강" else "🤝 관계 갈등"
                )

                # 주제 설명
                if choice == "정신 건강":
                    st.markdown("""
                    **정신 건강**  
                    이 주제를 선택하면 당신은 AITwinBot과 최근에 겪고 있는 스트레스나 감정적으로 힘든 일들에 대해 대화하게 됩니다.
                    """)
                    st.session_state["topic"] = "mental_health"
                elif choice == "관계 갈등":
                    st.markdown("""
                    **관계 갈등**  
                    이 주제를 선택하면 당신은 AITwinBot과 최근에 있었던 인간관계 문제나 마음이 불편했던 상황들에 대해 대화하게 됩니다.
                    """)
                    st.session_state["topic"] = "relationship_conflict"

                # NEXT 버튼
                if st.button("➡️ NEXT"):
                    st.session_state["step"] = "instructions"
                    st.rerun()

        except Exception as e:
            st.error(f"❌ 데이터를 불러오는 데 실패했습니다: {e}")

elif st.session_state["step"] == "instructions":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("### 📝 연구 안내")
    st.write("""
        이제부터 당신은 당신의 AITwinBot과 얘기하게 됩니다.  
        이 챗봇은 당신이 사전에 제공한 정보를 바탕으로 설계되었으며, 대화를 통해 당신에 대해 더 잘 알게 됩니다.

        대화를 시작하시려면 아래 '시작하기' 버튼을 눌러 주세요.
    """)
    if st.button("👉 시작하기"):
        st.session_state["step"] = "chat"
        st.rerun()

elif st.session_state["step"] == "chat":
    topic = st.session_state["topic"]
    if topic == "mental_health":
        import test as app
    elif topic == "relationship_conflict":
        import dpl_rel_new as app
    app.run()
