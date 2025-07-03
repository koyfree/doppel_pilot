import streamlit as st
import time
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# 단계 상태 초기화
if "step" not in st.session_state:
    st.session_state["step"] = "start"

# 단계 1: ID 입력 및 주제 선택
if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("<br>", unsafe_allow_html=True)
    # 1. 사용자 ID 입력
    user_name = st.text_input("설문 초반에 입력하신 ID를 동일하게 기입해 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요:)")

    # 2. 주제 선택
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 대화 주제를 선택해 주세요.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧘 정신 건강"):
            st.session_state["topic"] = "mental_health"
    with col2:
        if st.button("🤝 관계 갈등"):
            st.session_state["topic"] = "relationship_conflict"
