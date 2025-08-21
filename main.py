from get_novel import get_novel
from clean_ads import clean_ads
from check_char import check_char
from tts import tts
from merge_audio import merge_audio
import os
from dotenv import load_dotenv
"""
Order:
- get_novel.py -> get chapters, output: str
- clean_ads.py -> run gemini api clean ads, output: list of str (chapters)
- check_char.py -> get list of chaps, check available and remaining char, output: t/f
- tts.py -> if check_char = true: run tts, split into chunks (5000 bytes), output: folder of .mp3
- merge_audio.py -> merge output .mp3 into 1 .mp3 file
"""
# CHAPTERS
START = 201
END = 300
BASE = "https://truyenfull.vision"
PREFIX = "/mo-mat-thay-than-tai/chuong-"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_USAGE = 4000000
FOLDER_NAME = f"tran_hao_{START}_{END}"

def proceed():
    user = input("proceed? (y/n): ").lower()
    return True if user == 'y' else False

def get_keys():
    # load from .env if running locally
    load_dotenv()

    # Gemini
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

    # Google service account JSON
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set")


def main():
    get_keys()
    # get full raw novel from web
    raw_novel = get_novel(base=BASE, prefix=PREFIX, header=HEADERS, start=START, end=END)
    print(f"get_novel() done\n")
    # print(f"First 500 chars: \n{raw_novel}")
    # print(f"First 500 chars: \n{raw_novel[:500]}")
    if not proceed():
        return

    # clean chunks and ads
    cleaned_chapters = clean_ads(raw_novel, START)


    print(f"clean_ads() done")
    # print(f"First chap 500 chars:\n{cleaned_chapters[0][:500]}")
    # print(f"Last chap 500 chars:\n{cleaned_chapters[-1][:500]}")
    if not proceed():
        return

    # check remaining char
    current_usage_path = "/Users/jameshoang/Desktop/cmpt/tts/tts_usage.txt"
    if not check_char(cleaned_chapters, current_usage_path, MAX_USAGE, START):
        return

    # convert to speech
    tts(cleaned_chapters, FOLDER_NAME, START)
    if not proceed():
        return

    # merge
    merge_audio(FOLDER_NAME)

if __name__ == "__main__":
    main()


