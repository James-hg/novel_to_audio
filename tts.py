import os
import re
from tqdm import tqdm
from google.cloud import texttospeech

# 🔐 Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jameshoang/Desktop/cmpt/tts/ttstruyenngontinh-5e12e9bda03d.json"

def clean_text(text) -> str:
    """
    Cleans a chap
    Remove blank lines, asterisks, and facebook links
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("*") or "facebook" in line.lower():
            continue
        cleaned.append(line)
    return " ".join(cleaned)

# ✂️ Byte-safe chunking with sentence boundary handling
def split_into_chunks(text, max_bytes=5000) -> list[str]:
    """
    Split a chap into chunks
    TTS input limit: 5000 bytes
    """
    chunks = []
    current_chunk = ""
    for sentence in re.split(r'(?<=[.!?]) +', text):
        candidate = current_chunk + " " + sentence if current_chunk else sentence
        if len(candidate.encode('utf-8')) <= max_bytes:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(sentence.encode('utf-8')) > max_bytes:
                s = sentence
                while len(s.encode('utf-8')) > max_bytes:
                    for i in range(len(s), 0, -1):
                        if len(s[:i].encode('utf-8')) <= max_bytes:
                            chunks.append(s[:i].strip())
                            s = s[i:].strip()
                            break
                if s:
                    current_chunk = s
                else:
                    current_chunk = ""
            else:
                current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def tts(chapters:  list[str], folder_name: str, start: int):
    # Output folder
    os.makedirs(folder_name, exist_ok=True)

    # Init client
    client = texttospeech.TextToSpeechClient()

    # TTS settings
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    """
    Check test voice:
    id  :   pitch
    1   :    2.0
    2   :    1.5
    3   :    1.0
    4   :   -0.5
    5   :   -1.0
    6   :   -2.0
    """
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.4,
        pitch=-2.0
    )

    print(f"Found {len(chapters)} chapters")
    for id, chap in enumerate(tqdm(chapters, desc="Converting progress: "), start=start):
        # pre api call
        clean_chap = clean_text(chap)
        chunks = split_into_chunks(clean_chap)

        for idx, chunk in enumerate(chunks, start=1):
            synthesis_input = texttospeech.SynthesisInput(text = chunk)
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

            filename = f"Chuong_{id:03d}_part{idx}.mp3"
            filepath = os.path.join(folder_name, filename)

            with open(filepath, "wb") as out:
                out.write(response.audio_content)
                print(f"✅ Saved: {filepath}")
