import openai
from elevenlabs import ElevenLabs, Voice, VoiceSettings
import os
from dotenv import load_dotenv
import requests
import streamlit as st
from pydub import AudioSegment
from io import BytesIO

# 참고한 API docs
# https://www.postman.com/winter-capsule-627402/luma-api/documentation/n6uwn9m/suno?entity=request-3856400-846e4240-057f-4141-a7d6-639770d4a387

# 환경 변수 로드
load_dotenv()

# ElevenLabs API 키 설정
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
openai.api_key = os.getenv("OPENAI_API_KEY")
# Suno API 키 설정
suno_api_key = os.getenv('SUNO_API_KEY')

# ElevenLabs 클라이언트 초기화
client = ElevenLabs(api_key=elevenlabs_api_key)

def list_available_voices():
    """
    사용 가능한 음성을 나열하고, 사용자가 선택할 수 있도록 반환합니다.
    """
    available_voices = client.voices.get_all()
    print("\nAvailable Voices:")
    for idx, voice in enumerate(available_voices.voices):
        print(f"{idx + 1}. {voice.name} (ID: {voice.voice_id})")
    return available_voices

def get_voice_id_by_gender(gender):
    """
    성별에 따라 적절한 음성 ID를 반환합니다.
    """
    # 성별별 음성 ID 매핑
    voice_mapping = {
        "여성": "Xb7hH8MSUJpSbSDYk0k2",  # 실제 여성 음성 ID로 교체
        "남성": "JBFqnCBsd6RMkjVDRZzb",  # 실제 남성 음성 ID로 교체
    }
    return voice_mapping.get(gender, "voice_id_for_default")  # 기본 음성 ID

def text_to_speech1(text, gender, output_file='output.mp3'):
    """
    텍스트를 성별에 따라 지정된 음성으로 변환하여 오디오 파일로 저장합니다.

    :param text: 변환할 텍스트
    :param gender: 성별 ("남성" 또는 "여성")
    :param output_file: 저장할 오디오 파일명 (기본값: 'output.mp3')
    :return: 생성된 오디오 파일 경로 또는 None
    """
    voice_id = get_voice_id_by_gender(gender)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # 다국어 지원 모델 사용
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"음성 파일이 '{output_file}'로 저장되었습니다.")
        return output_file
    except requests.exceptions.RequestException as e:
        print(f"음성 변환 중 오류 발생: {e}\n응답 내용: {response.text}")
        return None




def upload_user_voice(file_path):
    """
    사용자 목소리를 업로드하고 ElevenLabs에서 사용자 스타일을 등록합니다.
    :param file_path: 사용자의 음성 파일 경로 (예: .wav 형식)
    :return: 등록된 음성 프로필 ID 또는 None
    """
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "xi-api-key": elevenlabs_api_key
    }
    files = {
        "voice": open(file_path, "rb")
    }
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        voice_id = response.json().get("voice_id")
        return voice_id
    except requests.exceptions.RequestException as e:
        print(f"사용자 목소리 업로드 중 오류 발생: {e}")
        return None

def text_to_speech_with_user_voice(text, voice_id, output_file='output_user_voice.mp3'):
    """
    사용자의 목소리 스타일을 적용하여 텍스트를 음성으로 변환합니다.
    :param text: 변환할 텍스트
    :param voice_id: 등록된 사용자 목소리 프로필 ID
    :param output_file: 저장할 오디오 파일명 (기본값: 'output_user_voice.mp3')
    :return: 생성된 오디오 파일 경로 또는 None
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
    except requests.exceptions.RequestException as e:
        print(f"사용자 목소리 스타일 변환 중 오류 발생: {e}")
        return None

def generate_letter(recipient, appreciation, min_wc):
    """
    사용자 입력을 기반으로 진심 어린 감사 편지를 생성합니다.
    """
    prompt = (
        f"'{recipient}'에게 드릴 감사 편지를 작성해주세요. "
        f"감사의 이유는 다음과 같습니다: '{appreciation}'. "
        "편지는 기승전결 구조로 작성되며, 감정적이고 따뜻한 언어를 사용해주세요. 다음 요소를 포함해주세요:\n"
        f"1. (기)'{recipient}'에게 감사드리는 이유와 구체적인 상황.\n"
        f"2. (승) '{recipient}'과의 소중한 추억이나 특별한 순간.\n"
        f"3. (전) '{recipient}'의 사랑과 조언이 삶에 미친 영향.\n"
        f"4. (결) '{recipient}'에게 사랑과 소망을 담아 마무리.\n"
        f"편지는 최소 {min_wc}자에서 {min_wc+10}자 사이로 구성되며, 자연스럽고 감동적인 언어로 작성해주세요."
        
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 감동적인 편지를 작성하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # 충분한 길이를 보장
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"편지 생성 중 오류 발생: {e}")
        return "오류가 발생했습니다. 다시 시도해주세요."

def generate_lyrics(recipient, appreciation, letter, genre):
    """
    사용자 입력과 생성된 편지를 기반으로 노래 가사를 생성합니다.
    :param recipient: 감사의 대상
    :param appreciation: 감사 내용
    :param genre: 노래 장르
    """
    prompt = (
        f"'{recipient}'에게 전하는 감사의 마음과 '{appreciation}'을(를) 주제로 한 한국 노래 가사를 작성해주세요.\n"
        f"다음의 편지 내용을 참고하세요. 편지 내용: '{letter}'"
        f"가사는 아래 형식을 따르며, 끊김 없이 자연스럽게 작성해주세요:\n\n"
        f"- Verse 1: '{recipient}'와의 관계를 소개하고 감사의 마음을 시작으로 표현 (30~40 단어).\n"
        f"- Chorus: '{recipient}'의 사랑과 조언이 삶에 미친 영향을 강조하며 반복적이고 감동적인 메시지 (20~30 단어).\n"
        f"- Verse 2: '{recipient}'와의 구체적인 추억을 기반으로 더 깊은 감정과 스토리를 전개 (30~40 단어).\n"
        f"- Bridge: 감정을 최고조로 끌어올리며, '{recipient}'께 드리는 소망과 사랑의 메시지 (20~30 단어).\n"
        f"- Chorus 반복: 동일한 후렴 반복.\n\n"
        f"입력된 감사 내용: '{appreciation}'\n\n"
        f"'{genre}' 스타일로 가사를 자연스럽고 세련되게 작성해주세요. 자연스럽게 영단어를 중간에 넣어도 좋습니다."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 전문적인 노래 가사를 작성하는 도우미입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,  # 충분한 길이 확보
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"가사 생성 중 오류 발생: {e}")
        return "오류가 발생했습니다. 다시 시도해주세요."
    
def generate_lyrics_and_title(recipient, appreciation, letter, genre):
    """
    사용자 입력과 생성된 편지를 기반으로 노래 제목과 가사를 생성합니다.
    :param recipient: 감사의 대상
    :param appreciation: 감사 내용
    :param letter: 사용자 편지 내용
    :param genre: 노래 장르
    :return: 생성된 노래 제목과 가사
    """
    prompt = (
        f"'{recipient}'에게 전하는 감사의 마음과 '{appreciation}'을(를) 주제로 한 한국 노래 제목과 가사를 작성해주세요.\n"
        f"다음의 편지 내용을 참고하세요:\n\n"
        f"편지 내용: '{letter}'\n\n"
        f"가사는 아래 형식을 따르며, 끊김 없이 자연스럽게 작성해주세요:\n\n"
        f"- Verse 1: '{recipient}'와의 관계를 소개하고 감사의 마음을 표현 (30~40 단어).\n"
        f"- Chorus: '{recipient}'의 사랑과 조언이 삶에 미친 영향을 강조하며, 반복적이고 감동적인 메시지 (20~30 단어).\n"
        f"- Verse 2: '{recipient}'와의 구체적인 추억을 기반으로 더 깊은 감정과 스토리를 전개 (30~40 단어).\n"
        f"- Bridge: 감정을 최고조로 끌어올리며, '{recipient}'께 드리는 소망과 사랑의 메시지 (20~30 단어).\n"
        f"- Chorus 반복: 동일한 후렴 반복.\n\n"
        f"'{genre}' 스타일로 가사를 자연스럽고 세련되게 작성해주세요. 자연스럽게 영단어를 중간에 넣어도 좋습니다.\n\n"
        f"출력 형식은 다음과 같이 해주세요:\n\n"
        f"title: -\n"
        f"lyrics: -\n\n"
        f"예를 들어:\n\n"
        f"title: 당신에게 바치는 노래\n"
        f"lyrics: [Verse 1]\n"
        f"당신과 함께한 시간들...\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 전문적인 노래 가사를 작성하는 도우미입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,  # 충분한 길이 확보
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        
        # 'title: '과 'lyrics: '로 시작하는 부분을 추출
        title = None
        lyrics = None
        if content.startswith('title:'):
            parts = content.split('lyrics:', 1)
            if len(parts) == 2:
                title = parts[0].replace('title:', '').strip()
                lyrics = parts[1].strip()
        
        if title is None or lyrics is None:
            raise ValueError("응답에서 제목 또는 가사를 추출하지 못했습니다.")
        
        return title, lyrics

    except Exception as e:
        print(f"가사 및 제목 생성 중 오류 발생: {e}")
        return "오류가 발생했습니다. 다시 시도해주세요.", ""
    




def generate_and_save_song(lyrics, title, genre, output_file, api_key):
    url = "https://api.suno.ai/generate"  # Suno API의 엔드포인트 URL입니다.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "lyrics": lyrics,
        "title": title,
        "genre": genre,
        "model": "chirp-v3.5"  # 사용할 모델 버전입니다.
    }

    try:
        # 노래 생성 요청
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        data = response.json()
        song_url = data.get("audio_url")
        if not song_url:
            st.error("생성된 노래의 URL을 가져올 수 없습니다.")
            return None

        # 오디오 파일 다운로드
        audio_response = requests.get(song_url)
        audio_response.raise_for_status()

        # 오디오 파일 저장
        audio = AudioSegment.from_file(BytesIO(audio_response.content))
        audio.export(output_file, format="mp3")
        st.success(f"노래가 성공적으로 생성되어 '{output_file}'로 저장되었습니다.")
        return output_file

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP 오류 발생: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"요청 중 오류 발생: {req_err}")
    except Exception as e:
        st.error(f"예기치 않은 오류 발생: {e}")

    return None
