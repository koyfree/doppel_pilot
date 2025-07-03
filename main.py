import streamlit as st

# 스타일 정의 (카드 + 선택 시 하이라이트 + 중앙 정렬 라디오 버튼)
st.markdown("""
<style>
.topic-container {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 20px;
}
.topic-card {
    width: 300px;
    background-color: #1b5b84;
    color: white;
    padding: 25px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 400;
    height: 240px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border 0.2s ease;
    border: 4px solid transparent;
}
.topic-card.selected {
    border: 4px solid #f63366;
}
.topic-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
}
.center-radio {
    display: flex;
    justify-content: center;
    gap: 50px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 AITwinBot 실험 연구")
st.markdown("### 대화 주제를 선택해 주세요.")

# 옵션
topic_options = {
    "정신건강": "mental_health",
    "관계갈등": "relationship_conflict"
}

# 라디오 버튼 선택
selected = st.radio(
    "원하는 주제를 선택해 주세요.",
    list(topic_options.keys()),
    horizontal=True,
    index=None,
    label_visibility="collapsed",
    key="radio_selection"
)

# 세션에 topic 저장
if selected:
    st.session_state["topic"] = topic_options[selected]

# 카드 출력 (선택에 따라 하이라이트)
selected_topic = st.session_state.get("topic", "")

st.markdown('<div class="topic-container">', unsafe_allow_html=True)

# 카드: 정신건강
mental_selected = "selected" if selected_topic == "mental_health" else ""
st.markdown(f"""
<div class="topic-card {mental_selected}">
    <div>
        <div class="topic-title">정신건강</div>
        이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  
        최근에 겪고 있는 스트레스나 감정적으로  
        힘든 일들에 대해 대화하게 됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 카드: 관계갈등
rel_selected = "selected" if selected_topic == "relationship_conflict" else ""
st.markdown(f"""
<div class="topic-card {rel_selected}">
    <div>
        <div class="topic-title">관계갈등</div>
        이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  
        최근에 있었던 인간관계 문제나  
        마음이 불편했던 상황들에 대해 대화하게 됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # topic-container 끝

# NEXT 버튼 노출
if selected:
    st.success(f"선택된 주제: {selected}")
    if st.button("➡️ NEXT"):
        st.session_state["step"] = "instructions"
        st.rerun()
