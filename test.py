import streamlit as st
import openai
from prompts import SYSTEM_PROMPT_MTL
from knowledge_dict import build_knowledge_dict

# GPT 호출 함수
def call_gpt(messages, system_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}] + messages
    )
    return response.choices[0].message.content.strip()

def run():
    st.set_page_config(page_title="Doppelgänger Chatbot", layout="centered")

    # ✅ 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False
    if "first_question_done" not in st.session_state:
        st.session_state.first_question_done = False
    if "followup_count" not in st.session_state:
        st.session_state.followup_count = 0
    if "reflection_done" not in st.session_state:
        st.session_state.reflection_done = False
    if "suggestion_done" not in st.session_state:
        st.session_state.suggestion_done = False
    if "knowledge_dict" not in st.session_state:
        sheet_url = "https://docs.google.com/spreadsheets/d/1hXYw7YIAHufbIoCgjkH-UVoERWu8hh5LA_jc0O0sCd4/edit?usp=sharing"
        st.session_state.knowledge_dict = build_knowledge_dict(sheet_url)
    if "name" not in st.session_state:
        st.session_state.name = list(st.session_state.knowledge_dict.keys())[0]  # 기본값

    name = st.session_state.name
    knowledge = st.session_state.knowledge_dict[name]
    system_prompt = SYSTEM_PROMPT_MTL.format(knowledge=knowledge)

    # ✅ 인트로 메시지 출력
    intro_messages = [
        f"안녕 {name}! 나는 너의 데이터를 기반으로 만들어진 AITwinBot이야.",
        "만나서 반가워!",
        "본격적으로 시작하기 전에, 우리 대화가 어떻게 이루어질지 알려줄게.",
        "내가 너한테 어떤 주제에 대한 몇 가지 질문을 할 거야. 그리고 나서 내 생각을 3번에 걸쳐 얘기해줄게. 그럼 시작할게!"
    ]

    if not st.session_state.intro_done:
        for msg in intro_messages:
            with st.chat_message("assistant"):
                st.markdown(f"<div style='color: gray;'>{msg}</div>", unsafe_allow_html=True)
        st.session_state.intro_done = True

    # ✅ 첫 질문 출력
    if st.session_state.intro_done and not st.session_state.first_question_done:
        first_question = call_gpt(st.session_state.messages, system_prompt)
        st.session_state.messages.append({"role": "assistant", "content": first_question})
        with st.chat_message("assistant"):
            st.markdown(first_question)
        st.session_state.first_question_done = True

    # ✅ 사용자 입력창 항상 표시
    user_input = st.chat_input("메시지를 입력해주세요")

    if user_input:
        # 사용자 발화 저장 및 출력
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # follow-up 질문 3개 → 공감 → 성찰 → 제안
        if st.session_state.followup_count < 3:
            reply = call_gpt(st.session_state.messages, system_prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.followup_count += 1

        elif not st.session_state.reflection_done:
            with st.chat_message("assistant"):
                st.markdown("당신 이야기를 듣고 나니까 이런 감정이 느껴졌어. 고마워.")
            st.session_state.messages.append({"role": "assistant", "content": "당신 이야기를 듣고 나니까 이런 감정이 느껴졌어. 고마워."})
            st.session_state.reflection_done = True

        elif not st.session_state.suggestion_done:
            with st.chat_message("assistant"):
                st.markdown("혹시 내가 생각하는 방향을 한 번 들어볼래?")
            st.session_state.messages.append({"role": "assistant", "content": "혹시 내가 생각하는 방향을 한 번 들어볼래?"})
            st.session_state.suggestion_done = True

        else:
            with st.chat_message("assistant"):
                st.markdown("고마워. 여기서 대화를 마무리할게. 아래 설문에 참여해줘!")
