# test.py
import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL

def run():
    st.title("🧠 AITwinBot 대화 세션")

    # OpenAI API 준비
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.phase = "intro"
        st.session_state.awaiting_user = False
        st.session_state.intro_index = 0
        st.session_state.user_inputs = []

    # 프로필 정보 불러오기
    profile = st.session_state["profile"]
    system_prompt = SYSTEM_PROMPT_MTL.replace("{knowledge}", profile)

    # 메시지 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 인트로 메시지 4개 순차 출력
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
            # GPT로 근황 묻기
            prompt = "요즘 마음이 조금 힘들었던 적 있어?"  # Step 1에 해당
            st.chat_message("assistant").markdown(prompt)
            st.session_state.messages.append({"role": "assistant", "content": prompt})
            st.session_state.phase = "prompt1"
            st.session_state.awaiting_user = True
            st.stop()

    # 사용자 입력 처리
    user_input = st.chat_input("메시지를 입력해 주세요.")
    if user_input and st.session_state.awaiting_user:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_inputs.append(user_input)
        st.session_state.awaiting_user = False

        # 다음 단계 로직
        phase = st.session_state.phase

        if phase == "prompt1":
            next_question = "Could you tell me a bit more about what happened? Was there a specific event that triggered these feelings, or has it just been more of a general mood?"
            st.session_state.messages.append({"role": "assistant", "content": next_question})
            st.chat_message("assistant").markdown(next_question)
            st.session_state.phase = "followup1"
            st.session_state.awaiting_user = True
            st.stop()

        elif phase == "followup1":
            next_question = "Have you felt this way before, at any other point in your life?"
            st.session_state.messages.append({"role": "assistant", "content": next_question})
            st.chat_message("assistant").markdown(next_question)
            st.session_state.phase = "followup2"
            st.session_state.awaiting_user = True
            st.stop()

        elif phase == "followup2":
            next_question = "Around the time these feelings started, do you remember anything in your daily life that changed, even slightly?"
            st.session_state.messages.append({"role": "assistant", "content": next_question})
            st.chat_message("assistant").markdown(next_question)
            st.session_state.phase = "reflection"
            st.session_state.awaiting_user = True
            st.stop()

        elif phase == "reflection":
            # GPT 응답: 공감
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").markdown(reply)
            st.session_state.phase = "insight_button"
            st.stop()

        elif phase == "insight_button":
            if user_input.lower() in ["yes", "응", "말해줘", "좋아"]:
                st.session_state.phase = "insight"
                st.rerun()
            else:
                st.chat_message("assistant").markdown("혹시 더 듣고 싶으면 'YES'라고 해줘!")
                st.stop()

        elif phase == "insight":
            # GPT 응답: 성찰
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").markdown(reply)
            st.session_state.phase = "suggestion_button"
            st.stop()

        elif phase == "suggestion_button":
            if user_input.lower() in ["yes", "응", "말해줘", "좋아"]:
                st.session_state.phase = "suggestion"
                st.rerun()
            else:
                st.chat_message("assistant").markdown("그럼, 듣고 싶어지면 알려줘!")
                st.stop()

        elif phase == "suggestion":
            # GPT 응답: 제안
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").markdown(reply)

            # 마지막 안내
            st.chat_message("assistant").markdown("📋 설문은 아래 링크에서 진행해 주세요!\n👉 [설문 링크](https://example.com)")
            st.session_state.phase = "done"
            st.stop()

