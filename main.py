import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# 카드 스타일 정의
st.markdown("""
<style>
.card-container {
    display: flex;
    justify-content: center;
    gap: 30px;
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
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    position: relative;
    box-sizing: border-box;
}
.topic-card input[type="radio"] {
    position: absolute;
    bottom: 20px;
    right: 20px;
    transform: scale(1.4);
}
.topic-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 상태 초기화
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

                # 주제 정의
                topic_options = {
                    "정신건강": {
                        "key": "mental_health",
                        "description": "이 주제를 선택하면 당신은 당신의 AITwinBot과 최근에 겪고 있는 스트레스나 감정적으로 힘든 일들에 대해 대화하게 됩니다."
                    },
                    "관계갈등": {
                        "key": "relationship_conflict",
                        "description": "이 주제를 선택하면 당신은 당신의 AITwinBot과 최근에 있었던 인간관계 문제나 마음이 불편했던 상황들에 대해 대화하게 됩니다."
                    }
                }

                # 라디오 버튼만으로 선택 (UI는 카드)
                selected_label = st.radio(
                    "주제를 아래 카드에서 선택하세요:",
                    options=list(topic_options.keys()),
                    index=None,
                    label_visibility="collapsed"
                )

                # 카드 렌더링
                cards_html = '<div class="card-container">'
                for label, content in topic_options.items():
                    checked = "checked" if selected_label == label else ""
                    cards_html += (
                        f'<label>'
                        f'<div class="topic-card">'
                        f'<div class="topic-title">{label}</div>'
                        f'<div>{content["description"]}</div>'
                        f'<input type="radio" name="topic_fake" {checked} disabled />'
                        f'</div>'
                        f'</label>'
                    )
                cards_html += '</div>'
                st.markdown(cards_html, unsafe_allow_html=True)

                # 선택되었을 경우 저장 및 NEXT 표시
                if selected_label:
                    selected_key = topic_options[selected_label]["key"]
                    st.session_state["topic"] = selected_key
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
