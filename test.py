# test.py (리팩터링 버전)
import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL


def run():
    st.title("🧠 AITwinBot 대화 세션")

    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    profile = st.session_state["profile"]
    system_prompt = SYSTEM_PROMPT_MTL.replace("{knowledge}", profile)

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.phase = "intro"
        st.session_state.intro_index = 0
        st.session_state.awaiting_user = False
        st.session_state.user_inputs = []

    # 메시지 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
            # 근황 묻기 (GPT가 생성)
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                    {"role": "user", "content": "지금 첫 질문을 해줘."}
                ],
                temperature=0.7,
            )
            prompt = response.choices[0].message.content.strip()
            st.chat_message("assistant").markdown(prompt)
            st.session_state.messages.append({"role": "assistant", "content": prompt})
            st.session_state.phase = "prompt1"
            st.session_state.awaiting_user = True

    # 입력창 항상 노출
    user_input = st.chat_input("메시지를 입력해 주세요.")

    if st.session_state.awaiting_user and not user_input:
        st.stop()

    if user_input and st.session_state.awaiting_user:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_inputs.append(user_input)
        st.session_state.awaiting_user = False

        phase = st.session_state.phase

        if phase in ["prompt1", "followup1", "followup2"]:
            # 꼬리 질문도 GPT가 생성
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
            )
            q = response.choices[0].message.content.strip()
            st.session_state.phase = "followup1" if phase == "prompt1" else ("followup2" if phase == "followup1" else "reflection")

        elif phase == "reflection":
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
            )
            q = response.choices[0].message.content.strip()
            st.session_state.phase = "insight_button"

        elif phase == "insight_button":
            if user_input.lower() in ["yes", "응", "말해줘", "좋아"]:
                st.session_state.phase = "insight"
                st.rerun()
            else:
                q = "혹시 더 듣고 싶으면 'YES'라고 해줘!"
                st.session_state.awaiting_user = True
                st.chat_message("assistant").markdown(q)
                st.session_state.messages.append({"role": "assistant", "content": q})
                st.stop()

        elif phase == "insight":
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
            )
            q = response.choices[0].message.content.strip()
            st.session_state.phase = "suggestion_button"

        elif phase == "suggestion_button":
            if user_input.lower() in ["yes", "응", "말해줘", "좋아"]:
                st.session_state.phase = "suggestion"
                st.rerun()
            else:
                q = "그럼, 듣고 싶어지면 알려줘!"
                st.session_state.awaiting_user = True
                st.chat_message("assistant").markdown(q)
                st.session_state.messages.append({"role": "assistant", "content": q})
                st.stop()

        elif phase == "suggestion":
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            q = reply + "\n\n📋 설문은 아래 링크에서 진행해 주세요! 👉 [설문 링크](https://example.com)"
            st.session_state.phase = "done"

        # 공통 메시지 출력
        if st.session_state.phase != "done":
            st.session_state.awaiting_user = True

        st.chat_message("assistant").markdown(q)
        st.session_state.messages.append({"role": "assistant", "content": q})
