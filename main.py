import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# CSS 스타일 설정
st.markdown("""
<style>
.card-container {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 20px;
    flex-wrap: wrap;
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
    box-sizing: border-box;
}
.topic-card.selected {
    border: 4px solid #f63366;
}
.topic-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
    color: white;
}
.center-radio {
    display: flex;
    justify-content: center;
    margin-top: 30px;
}
button {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# 상태 초기화
if "step" not in st.session_state:
    st.session_state["step"] = "start"

# STEP 1: ID 입력 + 주제 선택
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

                selected_label = st.radio(
                    "원하는 주제를 선택해 주세요.",
                    list(topic_options.keys()),
                    horizontal=True,
                    index=None,
                    label_visibility="collapsed",
                    key="radio_selection"
                )

                if selected_label:
                    st.session_state["topic"] = topic_options[selected_label]

                selected_topic = st.session_state.get("topic", "")

                st.markdown('<div class="card-container">', unsafe_allow_html=True)

                for label, key in topic_options.items():
                    selected = "selected" if selected_topic == key else ""
                    card_text = {
                        "정신건강": "이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  최근에 겪고 있는 스트레스나 감정적으로  힘든 일들에 대해 대화하게 됩니다.",
                        "관계갈등": "이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  최근에 있었던 인간관계 문제나  마음이 불편했던 상황들에 대해 대화하게 됩니다."
                    }[label]
                    st.markdown(f"""
                    <div class="topic-card {selected}">
                        <div>
                            <div class="topic-title">{label}</div>
                            {card_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

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
