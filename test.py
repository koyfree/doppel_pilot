import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL
import time

st.markdown("""
<style>
/* 말풍선 간 간격 줄이기 */
div.stChatMessage {
    margin-bottom: 0.1rem !important;
}
</style>
""", unsafe_allow_html=True)

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

    # 시스템 프롬프트
    system_prompt = SYSTEM_PROMPT_MTL.replace("{knowledge}", st.session_state.profile)

    # 인트로 메시지
    intro_messages = [
        "안녕! 나는 너의 데이터를 기반으로 만들어진 너의 AITwinBot이야. 만나서 반가워!",
        "본격적으로 시작하기 전에, 우리 대화가 어떻게 진행될지 간단히 설명할.",
        "내가 특정 주제에 대해 몇 가지 물어볼게. 그걸 바탕으로, 이 주제에 대한 내 생각을 세 부분으로 나누어 얘기할거야. 마지막엔 대화가 어땠는지 평가할 수 있는 설문 링크를 알려 줄게. 꼭 참여해 줘!",
        "좋아, 그럼 시작할게!"
    ]

    # 인트로 단계 처리
    if st.session_state.phase == "intro":
        if st.session_state.intro_index == 0:
            full_intro = "\n\n".join(intro_messages)
            st.chat_message("assistant").markdown(full_intro)
            st.session_state.messages.append({"role": "assistant", "content": full_intro})
            st.session_state.intro_index = len(intro_messages)  # 전부 출력 완료 처리
            time.sleep(0.5)
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

    # 사용자 입력 허용 여부
    allow_input = st.session_state.phase in ["prompt1", "followup1", "followup2", "followup3"]
    user_input = None
    if allow_input and not st.session_state.awaiting_response:
        user_input = st.chat_input("메시지를 입력해 주세요.")

    # 사용자 입력 처리 및 phase 전환
    if user_input and not st.session_state.awaiting_response:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_inputs.append(user_input)
        st.session_state.pending_user_input = user_input

        # 🔽 사용자 입력 시 phase 전환
        if st.session_state.phase == "prompt1":
            st.session_state.phase = "followup1"
        elif st.session_state.phase == "followup1":
            st.session_state.phase = "followup2"
        elif st.session_state.phase == "followup2":
            st.session_state.phase = "followup3"
        elif st.session_state.phase == "followup3":
            st.session_state.phase = "reflection"

        st.session_state.awaiting_response = True
        st.session_state.awaiting_user = False
        st.rerun()

    # GPT 응답 처리
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

        # 단계 전환: 사용자 입력 이후 다음 단계는 이미 위에서 처리됨
        if st.session_state.phase == "reflection":
            st.session_state.phase = "insight_button"
            st.session_state.awaiting_user = False
            time.sleep(0.1)
        elif st.session_state.phase == "insight":
            st.session_state.phase = "suggestion_button"
            st.session_state.awaiting_user = False
        elif st.session_state.phase == "suggestion":
            final_msg = "이것으로 대화가 완료되었습니다! \n📋 설문은 아래 링크에서 진행해 주세요!\n👉 [설문 링크](https://example.com)"
            st.chat_message("assistant").markdown(final_msg)
            st.session_state.messages.append({"role": "assistant", "content": final_msg})
            st.session_state.phase = "done"

        st.session_state.awaiting_response = False
        st.session_state.pending_user_input = None
        st.rerun()
