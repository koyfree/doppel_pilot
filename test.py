import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT_MTL
import time

st.markdown("""
<style>
/* assistant 말풍선 간 간격 줄이기 */
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
        "본격적으로 시작하기 전에, 우리 대화가 어떻게 진행될지 간단히 설명할게.",
        "내가 특정 주제에 대해 몇 가지 물어볼게. 그걸 바탕으로, 이 주제에 대한 내 생각을 세 부분으로 나누어 얘기할거야. 마지막엔 대화가 어땠는지 평가할 수 있는 설문 링크를 알려 줄게. 꼭 참여해 줘!",
        "좋아, 그럼 시작할게!"
    ]

    # 인트로 단계 처리
    if st.session_state.phase == "intro":
        if st.session_state.intro_index < len(intro_messages):
            current_msg = intro_messages[st.session_state.intro_index]

            # 이미 추가된 메시지인지 확인
            if len(st.session_state.messages) == st.session_state.intro_index:
                with st.chat_message("assistant"):
                    st.markdown(current_msg)
                st.session_state.messages.append({"role": "assistant", "content": current_msg})
                time.sleep(0.5)
                st.session_state.intro_index += 1
                st.rerun()
        else:
            st.session_state.phase = "prompt1"
            st.session_state.awaiting_response = True
            st.rerun()

    # YES(응) 버튼 처리
    if st.session_state.phase in ["insight_button", "suggestion_button"]:
        if st.button("응👌"):
            st.session_state.messages.append({"role": "user", "content": "응"})
            st.chat_message("user").markdown("응")
            st.session_state.user_inputs.append("응")
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
        
        # 아래로 스크롤
        st.markdown("""
        <script>
        window.scrollTo(0, document.body.scrollHeight);
        </script>
        """, unsafe_allow_html=True)
        
        # 단계 전환: 사용자 입력 이후 다음 단계는 이미 위에서 처리됨
        if st.session_state.phase == "reflection":
            st.session_state.phase = "insight_button"
            st.session_state.awaiting_user = False
            st.markdown("""
            <script>
            setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
            }, 500);
            </script>
            """, unsafe_allow_html=True)

            time.sleep(0.5)
        
        elif st.session_state.phase == "insight":
            st.session_state.phase = "suggestion_button"
            st.session_state.awaiting_user = False
        elif st.session_state.phase == "suggestion":
            time.sleep(1)
            final_msg1 = "우리 대화는 여기까지야! 얘기 나눠줘서 고마워😊"
            final_msg2 = "📋대화가 어땠는지에 대한 평가는 여기 링크에서 알려줘!\n👉 [설문 링크](https://docs.google.com/forms/d/e/1FAIpQLScVEoXWLJiS5QN8X3HuFs_dyKnio-Nt759OazvofRQO84dbvw/viewform?usp=dialog)"
            st.chat_message("assistant").markdown(final_msg1)
            st.session_state.messages.append({"role": "assistant", "content": final_msg1})
            time.sleep(1)
            st.chat_message("assistant").markdown(final_msg2)
            st.session_state.messages.append({"role": "assistant", "content": final_msg2})
            st.session_state.phase = "done"

        st.session_state.awaiting_response = False
        st.session_state.pending_user_input = None
        st.rerun()
