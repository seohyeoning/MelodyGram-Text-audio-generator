# streamlit run C:\Users\user\Desktop\psh\project\MelodyGram\new_main.py
import streamlit as st
from new_func import *

import os
from dotenv import load_dotenv

def main():
    suno_api_key = os.getenv('SUNO_API_KEY')
    
    st.set_page_config(page_title="MelodyGram", page_icon="🎶", layout="centered")
    
    # 단계 상태를 session_state로 관리
    if "stage" not in st.session_state:
        st.session_state["stage"] = "입력 단계"

    if "min_wc" not in st.session_state:  # 최소 글자 수 기본값 설정
        st.session_state["min_wc"] = 30

    if "letter" not in st.session_state:  # 편지 초기화
        st.session_state["letter"] = None

    if "genre" not in st.session_state:  # 장르 초기화
        st.session_state["genre"] = "발라드"

    if "lyrics" not in st.session_state:  # 가사 초기화
        st.session_state["lyrics"] = None

    if "song_path" not in st.session_state:  # 노래 초기화
        st.session_state["song_path"] = None

    # 단계 옵션과 현재 단계 설정
    stage_options = ["입력 단계", "목소리 등록", "결과 확인"]
    stage_icons = ["🖊️", "🎤", "🎶"]
    current_stage = st.session_state["stage"]
    
    # 사이드바에 단계 표시
    stage_with_icons = [f"{icon} {stage}" for icon, stage in zip(stage_icons, stage_options)]
    selected_stage_with_icon = st.sidebar.radio("진행 상태", stage_with_icons, index=stage_options.index(current_stage))

    # 선택된 단계에서 아이콘 제거
    st.session_state["stage"] = selected_stage_with_icon.split(" ", 1)[1]

    # 진행 바 표시
    stage_index = stage_options.index(st.session_state["stage"])
    st.progress((stage_index + 1) / len(stage_options))
    st.metric(label="현재 진행 단계", value=f"{stage_index + 1} / {len(stage_options)}")

    # 현재 단계 로직
    if st.session_state["stage"] == "입력 단계":
        st.header("🖊️ 1. 감사 내용을 입력해주세요")

        with st.expander("1. 감사 대상"):
            recipient = st.text_input("감사 대상 (예: 부모님, 친구 등):")

        with st.expander("2. 감사 내용 작성"):
            appreciation = st.text_area(
                "전달하고 싶은 감사함을 표현해주세요.\n"
                "감사드리는 이유, 함께 한 소중한 추억, 삶에 미친 긍정적인 영향 \n"
            )
        with st.expander("3. 편지 분량 설정"):
            min_wc = st.text_input("최소 글자 수 (기본: 30)", value=str(st.session_state["min_wc"]))
        
        # 최소 글자 수 업데이트
        if min_wc and min_wc.isdigit():  # 숫자인 경우만 업데이트
            st.session_state["min_wc"] = int(min_wc)
            
        st.info("입력한 내용을 바탕으로 진심 어린 편지와 노래를 생성합니다. 예시를 참고하세요.")

        if st.button("다음 단계로 이동"):
            if recipient and appreciation:
                st.session_state["inputs"] = {
                    "recipient": recipient,
                    "appreciation": appreciation
                }
                # 편지 생성
                with st.spinner("편지를 생성하고 있습니다..."):
                    st.session_state["letter"] = generate_letter(recipient, appreciation, st.session_state["min_wc"])
                st.session_state["stage"] = "목소리 등록"
            else:
                st.warning("모든 입력 필드를 채워주세요.")

    elif st.session_state["stage"] == "목소리 등록":
        st.header("🎤 2. 사용자 목소리 등록")

        uploaded_file = st.file_uploader("30초 정도의 음성 파일을 업로드하세요:", type=["wav", "mp3"])
        gender = st.selectbox("사용자 성별을 선택하세요 (목소리 미등록 시 사용):", ["여성", "남성"])

        if st.button("목소리 등록"):
            if uploaded_file:
                with st.spinner("사용자 목소리를 등록하고 있습니다..."):
                    voice_id = upload_user_voice(uploaded_file.name)
                    if voice_id:
                        st.session_state["voice_id"] = voice_id
                        st.success("목소리 등록 완료!")
                        st.session_state["stage"] = "결과 확인"
                    else:
                        st.error("목소리 등록에 실패했습니다. 다시 시도해주세요.")
            else:
                st.session_state["voice_id"] = None
                st.session_state["gender"] = gender
                st.success("사용자 목소리가 없으므로 선택한 성별 목소리가 사용됩니다.")
                st.session_state["stage"] = "결과 확인"

    elif st.session_state["stage"] == "결과 확인":
        st.header("🎶 3. 생성 결과 확인")

        inputs = st.session_state.get("inputs", {})
        voice_id = st.session_state.get("voice_id")
        gender = st.session_state.get("gender", "여성")  # 기본값: 여성

        if not inputs:
            st.error("이전 단계를 완료해주세요.")
            return

        recipient = inputs.get("recipient")
        appreciation = inputs.get("appreciation")

        # 노래 장르 선택
        st.subheader("🎶 노래 장르 선택")         
        genre = st.selectbox("노래 장르를 선택하세요:", ["Ballad", "Dance", "Hip-Hop/Rap", "R&B/Soul", "Trot", "Indie", "Jazz"])

        # 장르 변경 시 가사 및 노래만 다시 생성
        if genre != st.session_state["genre"]:
            st.session_state["genre"] = genre
            st.session_state["lyrics"] = None
            st.session_state["title"] = None
            st.session_state["song_path"] = None

        # 편지 표시
        st.subheader("🖊️ 생성된 편지")
        st.text_area("생성된 편지:", st.session_state["letter"], height=200)

        # 가사 생성
        if st.session_state["lyrics"] is None:
            with st.spinner("노래 가사를 생성하고 있습니다..."):
                st.session_state["title"], st.session_state["lyrics"] = generate_lyrics_and_title(recipient, appreciation, st.session_state["letter"], genre)
        st.subheader("🎶 생성된 노래 가사")
        st.text_area("생성된 노래 가사:", st.session_state["lyrics"], height=200)
        

        # 생성된 노래 표시
        st.subheader("🎵 생성된 노래")
        # 노래 생성 버튼 
        if st.button("노래 생성하기"):
            with st.spinner("노래를 생성하고 있습니다..."):
            
                st.session_state["song_path"] = generate_and_save_song(st.session_state["lyrics"], st.session_state["title"] ,st.session_state["genre"], 'C:/Users/user/Desktop/psh/project/MelodyGram/gift_song.mp3', suno_api_key)

        if st.session_state["song_path"]:
            st.audio(st.session_state["song_path"], format='audio/mp3')

if __name__ == "__main__":
    main()
