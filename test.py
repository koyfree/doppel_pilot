
import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL
import time

def run():
    st.title("🧠 AITwinBot 대화 세션")

    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.phase = "intro"
        st.session_state.intro_index = 0
        st.session_state.user_inputs = []
        st.session_state.awaiting_user = False
        st.session_state.awaiting_response = False
        st.session_state.pending_user_input = None
        st.session_state.profile = st.session_state.get("profile", "")

    # 메시지 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # system prompt 준비
    system_prompt = SYSTEM_PROMPT_MTL.replace("{knowledge}", st.session_state.profile)

    # 인트로 메시지 출력
    intro_messages = [
        "Hi! I'm your doppelgänger chatbot created based on your data. Nice to meet you!",
        "Before we officially begin, let me explain how our conversation will go.",
        "I'm going to ask you a few questions on a certain topic. Based on your answers, I'll show you 'my thoughts on your answers' in three parts. You can read each part and evaluate it right away.",
        "Okay, let's get started!"
    ]

    if st.session_state.phase == "intro":
        if st.session_state.intro_index < len(intro_messages):
            msg = intro_messages[st.session_state.intro_index]
            st.chat_message("assistant").markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.intro_index += 1
            st.rerun()
        else:
            st.session_state.phase = "prompt1"
            st.session_state.awaiting_response = True
            st.rerun()

    # YES 버튼 처리
    if st.session_state.phase in ["insight_button", "suggestion_button"]:
        if st.button("✅ YES"):
            st.session_state.messages.append({"role": "user", "content": "YES"})
            st.chat_message("user").markdown("YES")
            st.session_state.user_inputs.append("YES")
            st.session_state.awaiting_user = False
            st.session_state.awaiting_response = True

            if st.session_state.phase == "insight_button":
                st.session_state.phase = "insight"
            elif st.session_state.phase == "suggestion_button":
                st.session_state.phase = "suggestion"
            st.rerun()

    # 사용자 입력 가능 단계
    allow_input = st.session_state.phase in [
        "prompt1", "followup1", "followup2", "followup3"
    ]
    user_input = None
    if allow_input and not st.session_state.awaiting_response:
        user_input = st.chat_input("메시지를 입력해 주세요.")

    if user_input and not st.session_state.awaiting_response:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_inputs.append(user_input)
        st.session_state.pending_user_input = user_input
        st.session_state.awaiting_response = True
        st.session_state.awaiting_user = False
        st.rerun()

    # GPT 응답 생성
    if st.session_state.awaiting_response:
        with st.spinner("🤖 챗봇이 입력 중이에요..."):
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            st.chat_message("assistant").markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        # phase 전환
        if st.session_state.phase == "prompt1":
            st.session_state.phase = "followup1"
            st.session_state.awaiting_user = True
        elif st.session_state.phase == "followup1":
            st.session_state.phase = "followup2"
            st.session_state.awaiting_user = True
        elif st.session_state.phase == "followup2":
            st.session_state.phase = "followup3"
            st.session_state.awaiting_user = True
        elif st.session_state.phase == "followup3":
            st.session_state.phase = "reflection"
            st.session_state.awaiting_user = True
        elif st.session_state.phase == "reflection":
            st.session_state.phase = "insight_button"
            st.session_state.awaiting_user = False
        elif st.session_state.phase == "insight":
            st.session_state.phase = "suggestion_button"
            st.session_state.awaiting_user = False
        elif st.session_state.phase == "suggestion":
            st.chat_message("assistant").markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # 설문 안내 메시지도 같이 출력
            final_msg = "📋 설문은 아래 링크에서 진행해 주세요!\n👉 [설문 링크](https://example.com)"
            st.chat_message("assistant").markdown(final_msg)
            st.session_state.messages.append({"role": "assistant", "content": final_msg})

            st.session_state.phase = "done"

        st.session_state.awaiting_response = False
        st.session_state.pending_user_input = None
        st.rerun()
