import streamlit as st
from knowledge_dict import build_knowledge_dict

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

# 카드 스타일
st.markdown("""
<style>
.topic-card {
    background-color: #1b5b84;
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    font-size: 17px;
    font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
    height: 220px;
    border: 2px solid transparent;
}
.topic-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    background-color: #2474ab;
}
.topic-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# 단계 상태 초기화
if "step" not in st.session_state:
    st.session_state["step"] = "start"

# 단계 1: ID 입력 및 주제 선택
if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("설문 초반에 입력하신 ID를 동일하게 기입해 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요:)")
    st.markdown("<br>", unsafe_allow_html=True)

    user_name = st.text_input("")

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
                col1, col2 = st.columns(2)

                with col1:
                    if st.markdown(f"""
                        <div class="topic-card" onclick="window.location.href='?topic=mental_health'">
                            <div class="topic-title">정신건강</div>
                            이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  
                            최근에 겪고 있는 스트레스나 감정적으로 힘든 일들에 대해 대화하게 됩니다.
                        </div>
                    """, unsafe_allow_html=True):
                        pass

                with col2:
                    if st.markdown(f"""
                        <div class="topic-card" onclick="window.location.href='?topic=relationship_conflict'">
                            <div class="topic-title">관계갈등</div>
                            이 주제를 선택하면 당신은 당신의 <b>AITwinBot</b>과  
                            최근에 있었던 인간관계 문제나 마음이 불편했던 상황들에 대해 대화하게 됩니다.
                        </div>
                    """, unsafe_allow_html=True):
                        pass

                # URL 파라미터 통해 선택 확인
                query_params = st.query_params
                if "topic" in query_params:
                    topic = query_params["topic"]
                    if isinstance(topic, list):  # 리스트일 수 있음
                        topic = topic[0]
                    st.session_state["topic"] = topic

                    label = '정신 건강' if topic == 'mental_health' else '관계 갈등'
                    st.success(f"선택된 주제: {label}")

                    if st.button("➡️ NEXT"):
                        st.session_state["step"] = "instructions"
                        st.rerun()

        except Exception as e:
            st.error(f"❌ 데이터를 불러오는 데 실패했습니다: {e}")

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
