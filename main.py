import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# 단계 상태 초기화
if "step" not in st.session_state:
    st.session_state["step"] = "start"

# 단계 1: ID 입력 및 주제 선택
if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")

    # 1. 사용자 ID 입력
    user_name = st.text_input("""설문 초반에 입력하신 ID를 동일하게 기입해 주세요. ID는 대소문자를 구별합니다. 
    잊어 버리신 경우 관리자에게 문의해 주세요:)""")

    # 2. 주제 선택
    st.markdown("#### 대화 주제를 선택해 주세요.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧘 정신 건강"):
            st.session_state["topic"] = "mental_health"
    with col2:
        if st.button("🤝 관계 갈등"):
            st.session_state["topic"] = "relationship_conflict"

    # 3. ID 확인 및 NEXT 버튼
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

                if "topic" in st.session_state:
                    label = '정신 건강' if st.session_state['topic'] == 'mental_health' else '관계 갈등'
                    st.success(f"선택된 주제: {label}")

                    if st.button("➡️ NEXT"):
                        st.session_state["step"] = "instructions"
                        st.rerun()
                else:
                    st.info("👆 위에서 먼저 주제를 선택해 주세요.")

        except Exception as e:
            st.error(f"Failed to load knowledge: {e}")

# 단계 2: 안내문
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

# 단계 3: 챗봇 대화 시작
elif st.session_state["step"] == "chat":
    topic = st.session_state["topic"]
    if topic == "mental_health":
        import test as app
    elif topic == "relationship_conflict":
        import dpl_rel_new as app
    app.run()
