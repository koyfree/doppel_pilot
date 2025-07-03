import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# CSS for 카드처럼 보이는 버튼
st.markdown("""
<style>
div.stButton > button {
    background-color: #1b5b84;
    color: white;
    padding: 25px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 400;
    height: 240px;
    width: 100%;
    text-align: left;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    margin-bottom: 20px;
    border: 4px solid transparent;
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 12px rgba(0,0,0,0.25);
}
div.stButton.selected > button {
    border: 4px solid #f63366;
}
</style>
""", unsafe_allow_html=True)

# 초기 상태 설정
if "step" not in st.session_state:
    st.session_state["step"] = "start"

# STEP 1
if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("설문 초반에 입력하신 ID를 동일하게 기입해 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요 :)")

    user_name = st.text_input("ID")

    if user_name:
        sheet_url = "https://docs.google.com/spreadsheets/d/1pQ9Wps-6sJH3EWgEgb4QdJJ_MItBBnSbTPbTKCWQhLI/edit?gid=1798623846#gid=1798623846"
        openai_api_key = st.secrets["openai"]["api_key"]

        try:
            knowledge = build_knowledge_dict(sheet_url, openai_api_key)

            if user_name not in knowledge:
                st.error("⚠️ ID를 정확하게 기입해 주세요. ID는 대소문자를 구별합니다.")
            else:
                st.success("✅ 확인 되었습니다!")
                st.session_state["user_name"] = user_name
                st.session_state["profile"] = knowledge[user_name]

                st.markdown("### 대화 주제를 선택해 주세요.")

                topic_options = {
                    "정신건강": "mental_health",
                    "관계갈등": "relationship_conflict"
                }

                selected_topic = st.session_state.get("topic", "")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("정신건강"):
                        st.session_state["topic"] = "mental_health"

                with col2:
                    if st.button("관계갈등"):
                        st.session_state["topic"] = "relationship_conflict"

                # 강조 테두리는 CSS로 하기 어려우므로 선택 상태 표시
                selected_label = {
                    "mental_health": "정신건강",
                    "relationship_conflict": "관계갈등"
                }.get(st.session_state.get("topic", ""), None)

                if selected_label:
                    st.success(f"선택된 주제: {selected_label}")
                    if st.button("➡️ NEXT"):
                        st.session_state["step"] = "instructions"
                        st.rerun()

        except Exception as e:
            st.error(f"❌ 데이터를 불러오는 데 실패했습니다: {e}")

# STEP 2: 안내문
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

# STEP 3: 챗봇 실행
elif st.session_state["step"] == "chat":
    topic = st.session_state["topic"]
    if topic == "mental_health":
        import test as app
    elif topic == "relationship_conflict":
        import dpl_rel_new as app
    app.run()
