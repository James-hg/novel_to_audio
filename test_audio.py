from google.cloud import texttospeech

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jameshoang/Desktop/cmpt/tts/ttstruyenngontinh-5e12e9bda03d.json"

# Initialize client
client = texttospeech.TextToSpeechClient()

file_path = "/Users/jameshoang/Desktop/cmpt/tts/mo_mat_thay_than_tai_1_100.txt"
file_name = os.path.splitext(os.path.basename(file_path))[0]

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()
    text = text.replace("\n"," ")
    text = " ".join(text.split())

# split text if needed
byte_length = len(text.encode("utf-8"))
print(f"Characters: {len(text)}, Bytes: {byte_length}")


# Set the text
synthesis_input = texttospeech.SynthesisInput(text=text)


user = input("Continue (y)")
if user == "y":

    # # Select voice
    # voice = texttospeech.VoiceSelectionParams(
    #     language_code="en-US",
    # name="vi-VN-Standard-A",
    #     name="en-US-Wavenet-D"
    # )

    # Configure voice: Vietnamese - Standard female
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Set audio format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.3,
        pitch=-2.0
    )
    """
    1: 2.0
    2: 1.5
    3: 1.0
    4: -0.5
    5: -1.0
    6: -2.0
    """

    # Perform request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    file_name += ".mp3"
    # Save the audio
    with open(file_name, "wb") as out:
        out.write(response.audio_content)
        print(f"✅ Audio saved to {file_name}")

