import openai
from elevenlabs import ElevenLabs, Voice, VoiceSettings
import os
from dotenv import load_dotenv
import requests

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

def generate_letter(recipient, appreciation):
    """
    수신자와 감사한 내용을 기반으로 진심 어린 감사 편지를 생성합니다.
    """
    prompt = (
        f"다음 정보를 바탕으로 따뜻하고 진심 어린 감사 편지를 작성해주세요:\n\n"
        f"- 받는 사람: {recipient}\n"
        f"- 감사한 내용: {appreciation}\n\n"
        f"편지는 150자 이내로 요약해주세요."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 편지를 작성하는 어시스턴트입니다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7,
    )

    letter = response.choices[0].message.content.strip()
    return letter

def generate_lyrics(recipient, appreciation):
    """
    사용자 입력과 생성된 편지를 기반으로 노래 가사를 생성합니다.
    """
    prompt = f"'{recipient}'에게 전하는 감사의 마음과 '{appreciation}'을(를) 주제로 한 노래 가사를 작성해주세요."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 노래 가사를 작성하는 도우미입니다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

import time

def generate_song(lyrics, style="ballad", retries=3, delay=5):
    """
    생성된 가사를 기반으로 노래를 생성하고 오디오 파일로 저장합니다.
    :param lyrics: 노래 가사
    :param style: 노래 스타일 (기본값: "ballad")
    :param retries: 재시도 횟수 (기본값: 3)
    :param delay: 재시도 간 대기 시간 (초, 기본값: 5)
    :return: 생성된 오디오 파일 경로
    """
    url = "https://api.suno.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {suno_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "lyrics": lyrics,
        "style": style,
        "language": "ko"
    }

    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            audio_url = response.json().get("audio_url")
            audio_response = requests.get(audio_url)
            output_path = "song.mp3"
            with open(output_path, "wb") as f:
                f.write(audio_response.content)
            return output_path
        else:
            print(f"오류 발생: {response.status_code}, {response.text}")
            if response.status_code == 503:
                print(f"{delay}초 후에 재시도합니다...")
                time.sleep(delay)
            else:
                break
    raise Exception(f"최종 오류 발생: {response.status_code}, {response.text}")