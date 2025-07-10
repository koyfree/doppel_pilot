import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# 스타일 정의
st.markdown("""
<style>
.topic-card {
    background-color: #ffffff;
    color: black;
    padding: 25px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 400;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    height: 190px;
    box-sizing: border-box;
    transition: border 0.2s ease;
    margin-bottom: 10px;
}
.topic-card.selected {
    border: 4px solid #f63366;
}
.topic-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
}
.radio-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

if "step" not in st.session_state:
    st.session_state["step"] = "start"

if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("설문 초반에 입력하신 ID를 동일하게 기입한 뒤 Enter키를 눌러 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요 😊")

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

                st.markdown("")
                st.markdown("")
                st.markdown("### 대화 주제를 선택해 주세요.")

                topic_options = {
                    "정신건강": {
                        "key": "mental_health",
                        "description": "이 주제를 선택하면 당신은 TwinBot과\n 최근에 겪고 있는 스트레스나 감정적으로 힘든 일들에 대해 대화하게 됩니다."
                    },
                    "관계갈등": {
                        "key": "relationship_conflict",
                        "description": "이 주제를 선택하면 당신은 TwinBot과\n 최근에 있었던 인간관계 문제나 마음이 불편했던 상황들에 대해 대화하게 됩니다."
                    }
                }

                selected_label = st.session_state.get("radio_topic")

                col1, col2 = st.columns(2)

                with col1:
                    selected = "selected" if selected_label == "정신건강" else ""
                    st.markdown(f"""
                        <div class="topic-card {selected}">
                            <div class="topic-title">정신건강</div>
                            <div>{topic_options['정신건강']['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.container():
                        if st.radio(
                            label="",
                            options=["정신건강"],
                            key="radio_mh",
                            index=None,
                            label_visibility="collapsed"
                        ) == "정신건강":
                            st.session_state["radio_topic"] = "정신건강"

                with col2:
                    selected = "selected" if selected_label == "관계갈등" else ""
                    st.markdown(f"""
                        <div class="topic-card {selected}">
                            <div class="topic-title">관계갈등</div>
                            <div>{topic_options['관계갈등']['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.container():
                        if st.radio(
                            label="",
                            options=["관계갈등"],
                            key="radio_rel",
                            index=None,
                            label_visibility="collapsed"
                        ) == "관계갈등":
                            st.session_state["radio_topic"] = "관계갈등"

                selected_label = st.session_state.get("radio_topic")
                if selected_label:
                    selected_key = topic_options[selected_label]["key"]
                    st.session_state["selected_label"] = selected_label
                    st.session_state["topic"] = selected_key
                    st.success(f"{selected_label} 주제를 선택하셨습니다. 아래 '다음' 버튼을 눌러 진행해 주세요.")
                    st.markdown("")
                    if st.button("➡️ 다음"):
                        st.session_state["step"] = "instructions"
                        st.rerun()

        except Exception as e:
            st.error(f"❌ 데이터를 불러오는 데 실패했습니다: {e}")

elif st.session_state["step"] == "instructions":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("### 📝 연구 안내")
    st.write("""
        이제부터 당신은 AITwinBot과 얘기하게 됩니다.  
        이 TwinBot은 당신이 사전에 제공한 정보를 바탕으로 설계되었으며, 대화를 통해 당신에 대해 더 잘 알게 됩니다.

        대화를 시작하시려면 아래 '시작하기' 버튼을 눌러 주세요.
    """)
    
    print(knowledge)

    if st.button("➡️ 시작하기"):
        st.session_state["step"] = "chat"
        st.rerun()

elif st.session_state["step"] == "chat":
    topic = st.session_state["topic"]
    if topic == "mental_health":
        import dpl_mtl as app
    elif topic == "relationship_conflict":
        import dpl_rel as app
    app.run()
