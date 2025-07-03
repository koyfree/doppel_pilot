import streamlit as st
from knowledge_dict import build_knowledge_dict
import time

st.set_page_config(page_title="AITwinBot 실험 연구", page_icon="🤖")

st.markdown(
    """
    <style>
    .card {
        background-color: #0f4c75;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        transition: background-color 0.3s ease;
        cursor: pointer;
        height: 250px;
    }
    .card:hover {
        background-color: #3282b8;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-desc {
        font-size: 16px;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 단계 1: ID 입력 및 주제 선택
if "step" not in st.session_state:
    st.session_state["step"] = "start"

if st.session_state["step"] == "start":
    st.title("🧠 AITwinBot 실험 연구")
    st.markdown("설문 초반에 입력하신 ID를 동일하게 기입해 주세요. 잊어 버리신 경우 관리자에게 문의해 주세요:)")

    user_name = st.text_input("", key="user_input_name")

    st.markdown("#### 대화 주제를 선택해 주세요.")
    # 카드 선택 시 query param으로 이동
query_params = st.experimental_get_query_params()

if "topic" in query_params:
    st.session_state["topic"] = query_params["topic"][0]
    st.success(f"선택된 주제: {st.session_state['topic']}")
    # 다음 단계로 이동하도록 조건 설정 가능

st.markdown(
    """
    <div class="card-container">
        <a href="?topic=mental_health" class="card">
            <div class="card-title">정신건강</div>
            <div class="card-desc">
                이 주제를 선택하면 당신은 당신의 AITwinBot과 최근에 겪고 있는 스트레스나 감정적으로 힘든 일들에 대해 대화하게 됩니다.
            </div>
        </a>
        <a href="?topic=relationship_conflict" class="card">
            <div class="card-title">관계갈등</div>
            <div class="card-desc">
                이 주제를 선택하면 당신은 당신의 AITwinBot과 최근에 있었던 인간관계 문제나 마음이 불편했던 상황들에 대해 대화하게 됩니다.
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

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

# ✅ 새로운 중간 단계: 화면 비우고 자연 전환
elif st.session_state["step"] == "chat_loading":
    # 화면 비우기
    placeholder = st.empty()
    placeholder.empty()

    # 약간의 지연 후 다음 단계로
    time.sleep(0.5)
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
