# streamlit run /Users/seohyeon/Desktop/코드모음/project/MelodyGram/main.py
import streamlit as st
from func import generate_letter, text_to_speech1, generate_lyrics, generate_song

def main():
    st.title("감사 편지 및 노래 생성기")

    recipient = st.text_input("감사의 마음을 표현하고 싶은 대상을 입력하세요:", "")
    appreciation = st.text_input("어떤 점이 감사한가요?:", "")
    gender = st.selectbox("당신의 성별을 선택하세요:", ["여성", "남성"])

    if st.button("생성하기"):
        if recipient and appreciation:
            with st.spinner("편지를 생성하고 있습니다..."):
                letter = generate_letter(recipient, appreciation)
                st.success("편지 생성 완료!")
                st.text_area("생성된 편지:", letter, height=200)

            with st.spinner("편지를 음성으로 변환하고 있습니다..."):
                letter_audio_path = text_to_speech1(letter, gender)
                if letter_audio_path:
                    st.success("편지 오디오 생성 완료!")
                    with open(letter_audio_path, 'rb') as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/mp3')
                else:
                    st.error("편지 오디오 생성에 실패했습니다.")

            with st.spinner("노래 가사를 생성하고 있습니다..."):
                lyrics = generate_lyrics(recipient, appreciation)
                st.success("노래 가사 생성 완료!")
                st.text_area("생성된 노래 가사:", lyrics, height=200)

            with st.spinner("노래를 생성하고 있습니다..."):
                song_path = generate_song(lyrics)
                if song_path:
                    st.success("노래 생성 완료!")
                    with open(song_path, 'rb') as song_file:
                        song_bytes = song_file.read()
                        st.audio(song_bytes, format='audio/mp3')
                else:
                    st.error("노래 생성에 실패했습니다.")
        else:
            st.warning("모든 입력 필드를 채워주세요.")

if __name__ == "__main__":
    main()