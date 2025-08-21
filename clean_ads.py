import google.generativeai as genai
import os, re, time, typing as t
from tqdm import tqdm

PROMPT = (
    "Bạn là bộ lọc làm sạch văn bản tiểu thuyết tiếng Việt.\n"
    "YÊU CẦU NGHIÊM NGẶT:\n"
    "1) GIỮ nguyên nội dung truyện (xuống dòng, dấu câu, khoảng trắng).\n"
    "2) LOẠI BỎ toàn bộ quảng cáo/link/kêu gọi theo dõi/website/app/telegram/watermark/chữ ký nhóm dịch/"
    "   các câu lặp vô nghĩa.\n"
    "3) KHÔNG thêm/chỉnh sửa/tóm tắt/chú thích.\n"
    "4) Nếu câu có cả nội dung truyện lẫn quảng cáo, chỉ xóa phần quảng cáo.\n"
    "5) ĐẦU RA: CHỈ văn bản sạch, KHÔNG tiêu đề, KHÔNG nhãn, KHÔNG trích dẫn.\n"
    "-----\n"
)

# --- Simple regex cleaner (before LLM call) ---
AD_REGEX = re.compile("|".join([
    r"https?://\S+", r"www\.\S+",
    r"\b(đọc|xem thêm)(?: truyện)? tại\b",
    r"\bquảng cáo\b", r"\btelegram\b", r"\bzalo\b",
    r"like(?:\s+và)?\s*share", r"theo dõi (?:kênh|page)",
    r"©\s*\w+", r"chap(?:ter)? \d+ ?(?:reup|raw)",
    r"Truyện\s*\d+\s+chúc\s+các\s+bạn\s+đọc\s+truyện\s+vui\s+vẻ",
]), flags=re.IGNORECASE)


def configure_gemini(api_key: t.Optional[str] = None) -> None:
    """
    Configure the google.generativeai client.
    - If api_key is None, reads GOOGLE_API_KEY from env.
    """
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY not set. Pass api_key or export env var. Run (export GOOGLE_API_KEY=\"key\")")
    genai.configure(api_key=key)

def pre_regex_clean(s: str) -> str:
    return AD_REGEX.sub("", s)

CHAP_HEADER = re.compile(r"^\s*(?:Chương|Chuong|Chapter)\s+\d+\b", re.MULTILINE)

def split_by_chapter(text: str) -> t.List[str]:
    parts = re.split(r"(?=^\s*(?:Chương|Chuong|Chapter)\s+\d+\b)", text, flags=re.MULTILINE)
    parts = [p for p in parts if p.strip()]

    if not parts:
        return [text]

    # If the first chunk is not a chapter header, treat it as preface and merge with the next
    if not CHAP_HEADER.match(parts[0]) and len(parts) >= 2 and CHAP_HEADER.match(parts[1]):
        parts[1] = parts[0].rstrip() + "\n" + parts[1]
        parts = parts[1:]

    return parts


def clean_chunk(chunk: str, model_name: str = "gemini-2.5-flash", retries: int = 3) -> tuple[str, int]:
    """
    Cleans a single chapter chunk via Gemini with deterministic settings.
    """
    payload = PROMPT + chunk
    model = genai.GenerativeModel(model_name)
    total_tokens_used = 0

    last_err: t.Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            resp = model.generate_content(payload, generation_config={"temperature": 0})
            total_tokens_used = resp.usage_metadata.total_token_count
            return (resp.text or "").strip(), total_tokens_used
        except Exception as e:
            last_err = e
            print(f"[clean_chunk] Attempt {attempt}/{retries} failed: {e}")
            time.sleep(2)
    raise RuntimeError(f"Gemini call failed after {retries} retries: {last_err}")

def clean_ads(raw_novel: str, start: int) -> list[str]:
    """
    INPUT: raw novel as string
    OUTPUT: cleaned novel as list of strings (chapters)
    """
    # Optional storing cleaned chapters
    # clean = open("cleaned_chapters.txt", "w")
    # clean.truncate(0)
    raw_novel = raw_novel.replace("†", "t")
    try:
        cleaned_chapters = []
        configure_gemini()
        raw_novel = pre_regex_clean(raw_novel)
        chapters = split_by_chapter(raw_novel)
        total_token_count = 0
        """
        Current Gemini Api (hard) limit:
        Tokens/min: 250,000
        Requests/min: 10 (negligible)
        Requests/day: 250 (https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas?invt=Ab6Amw&project=cleanads&pageState=(%22allQuotasTable%22:(%22s%22:%5B(%22i%22:%22currentPercent%22,%22s%22:%221%22),(%22i%22:%22currentUsage%22,%22s%22:%220%22),(%22i%22:%22displayName%22,%22s%22:%220%22),(%22i%22:%22displayDimensions%22,%22s%22:%220%22)%5D,%22f%22:%22%255B%257B_22k_22_3A_22Name_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22GenerateContent%2520free%2520tier%2520input%2520token%2520count%2520limit%2520per%2520model%2520per%2520minute_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22displayName_22%257D_2C%257B_22k_22_3A_22Dimensions%2520%2528e.g.%2520location%2529_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22model_3Agemini-2.5-flash_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22displayDimensions_22%257D_2C%257B_22k_22_3A_22_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22OR_5C_22_22_2C_22o_22_3Atrue_2C_22s_22_3Atrue%257D_2C%257B_22k_22_3A_22Name_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22Request%2520limit%2520per%2520model%2520per%2520day%2520for%2520a%2520project%2520in%2520the%2520free%2520tier_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22displayName_22%257D_2C%257B_22k_22_3A_22Dimensions%2520%2528e.g.%2520location%2529_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22model_3Agemini-2.5-flash_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22displayDimensions_22%257D%255D%22,%22c%22:%5B%22monitoredResource%22%5D)))
        """
        TOKEN_LIMIT_PER_MINUTE = 240000
        for idx, chap in enumerate(tqdm(chapters, desc="Cleaning progress: "), start=start):
            print(f"Cleaning chapter {idx}\n")
            # print(f"chapter content: {chap}")

            # estimate chapter token
            estimate_chap_token = int((len(PROMPT) + len(chap)) * 1.5)

            if int(total_token_count) + estimate_chap_token > TOKEN_LIMIT_PER_MINUTE:
                waiting_time = 60
                print(f"Used {total_token_count} tokens, wait {waiting_time}s to reset")
                for _ in tqdm(range(waiting_time), desc="Waiting progress: "):
                    time.sleep(1)
                print("Token/min reseted")
                total_token_count = 0

            # clean chunks
            cleaned_text, tokens_used_in_call = clean_chunk(chap)
            tokens_used_in_call = int(tokens_used_in_call)

            # # debugging
            # clean.write(cleaned_text + "\n") # store cleaned chapters
            # print(f"estimated chap token: {chap_token}")
            # print(f"actual chap token: {tokens_used_in_call}")
            # print(f"cleaned_text sample: {cleaned_text}\n")
            # print(f"cleaned_text sample: {cleaned_text[:100]}\n")
            # clean.close()

            # update tokens used
            total_token_count += tokens_used_in_call
            cleaned_chapters.append(cleaned_text)
            print(f"Done cleaning chapter {idx}\n")

        return cleaned_chapters

    except RuntimeError as e:
        print(f"An error occurred: {e}")
        return []