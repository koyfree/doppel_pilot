import streamlit as st
import time
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL  # 반드시 {knowledge} 포함되어 있어야 함

def run():
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    name = st.session_state["user_name"]
    knowledge = st.session_state["profile"]

    # 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "phase" not in st.session_state:
        st.session_state.phase = "intro"
    if "intro_step" not in st.session_state:
        st.session_state.intro_step = 0
    if "followup_count" not in st.session_state:
        st.session_state.followup_count = 0
    if "awaiting_button" not in st.session_state:
        st.session_state.awaiting_button = False

    st.title("🧠 AITwinBot – 맞춤형 심리 대화")

    # 인트로 메시지 리스트
    intro_messages = [
        f"안녕 {name}! 나는 너의 데이터를 기반으로 만들어진 AITwinBot이야.",
        "만나서 반가워!",
        "본격적으로 시작하기 전에, 우리 대화가 어떻게 이루어질지 알려줄게.",
        "내가 너한테 어떤 주제에 대한 몇 가지 질문을 할 거야. 그리고 나서 내 생각을 3번에 걸쳐 얘기해줄게. 그럼 시작할게!"
    ]

    # -------------------
    # 1. 인트로 단계: 자동 출력
    # -------------------
    if st.session_state.phase == "intro":
        step = st.session_state.get("intro_step", 0)

        for i in range(min(step + 1, len(intro_messages))):
            with st.chat_message("assistant"):
                st.markdown(intro_messages[i])

        if step < len(intro_messages):
            time.sleep(0.6)
            st.session_state.intro_step += 1
            st.rerun()
        else:
            # 인트로 끝 → 시스템 프롬프트 삽입 + GPT 첫 질문 유도
            system_prompt = SYSTEM_PROMPT_MTL.format(knowledge=knowledge)
            st.session_state.messages.append({"role": "system", "content": system_prompt})
            st.session_state.phase = "kickoff"
            st.rerun()
        st.stop()

    # -------------------
    # 2. 이전 대화 출력
    # -------------------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -------------------
    # 3. 버튼 기반 단계 (공감/성찰)
    # -------------------
    if st.session_state.awaiting_button:
        label = "네, 더 들어볼게요." if st.session_state.phase == "empathy" else "응, 계속 들어볼래."
        if st.button(label):
            with st.chat_message("user"):
                st.markdown("네")
            st.session_state.messages.append({"role": "user", "content": "네"})
            st.session_state.awaiting_button = False
            if st.session_state.phase == "empathy":
                st.session_state.phase = "reflection"
            elif st.session_state.phase == "reflection":
                st.session_state.phase = "suggestion"
            st.rerun()
        st.stop()

    # -------------------
    # 4. GPT 응답 생성 조건
    # -------------------
    generate_response = (
        st.session_state.phase in ["kickoff", "followup_1", "followup_2", "followup_3", "empathy", "reflection", "suggestion"]
        and (len(st.session_state.messages) > 0)
        and (st.session_state.messages[-1]["role"] != "user")
    )

    if generate_response:
        with st.chat_message("assistant"):
            with st.spinner("🤖 챗봇이 입력 중이에요..."):
                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=st.session_state.messages,
                    temperature=1,
                    max_tokens=2048
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        # 단계 전환
        if st.session_state.phase == "kickoff":
            st.session_state.phase = "followup_1"
        elif st.session_state.phase.startswith("followup_"):
            st.session_state.followup_count += 1
            if st.session_state.followup_count == 1:
                st.session_state.phase = "followup_2"
            elif st.session_state.followup_count == 2:
                st.session_state.phase = "followup_3"
            elif st.session_state.followup_count == 3:
                st.session_state.phase = "empathy"
                st.session_state.awaiting_button = True
        elif st.session_state.phase == "suggestion":
            st.session_state.phase = "done"
        st.rerun()

    # -------------------
    # 5. 사용자 입력 받기 (꼬리질문 단계에서만)
    # -------------------
    if st.session_state.phase in ["followup_1", "followup_2", "followup_3"]:
        user_input = st.chat_input("메시지를 입력하세요")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

    # -------------------
    # 6. 마지막 안내 메시지
    # -------------------
    if st.session_state.phase == "done":
        with st.chat_message("assistant"):
            st.markdown("지금까지 고마워요. 아래 링크로 가서 설문을 완료해 주세요! 👉 [설문하러 가기](https://your-survey-link.com)")
