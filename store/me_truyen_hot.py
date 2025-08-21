import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
# https://metruyenhot.me/mo-mat-thay-than-tai/chuong-2/
BASE_URL = "https://metruyenhot.me"
NOVEL_PATH = "/mo-mat-thay-than-tai/chuong-2/"
FULL_URL = BASE_URL + NOVEL_PATH

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_chapter_links():
    print("📖 Fetching chapter list...")
    res = requests.get(FULL_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    chapter_list = soup.select(".list-chapter li a")
    # chapter_links = [BASE_URL + a["href"] for a in chapter_list]
    chapter_links = [a["href"] for a in chapter_list]
    # chapter_links.reverse()  # Make sure chapters are in order
    return chapter_links

# def clean_ads(text):
#     ad_keywords = [
#         "truyen88", "Truyen88.vip", "google search", "đọc full",
#         "group facebook", "truyện hot", "trang web sao chép", "xin cảm ơn",
#         "xem thêm truyện", "chế tạo hào môn", "này bác sĩ", "manh thê", "Hướng dẫn:", "Truyen88", "truyen88.vip",
#         "Chương này có nội dung ảnh", "truyện 88", "admin"
#     ]

#     # Split text into lines and remove any line containing ad keywords
#     cleaned_lines = [
#         line for line in text.splitlines()
#         if not any(keyword.lower() in line.lower() for keyword in ad_keywords)
#         and len(line.strip()) > 0  # optional: skip empty lines
#     ]

#     return "\n".join(cleaned_lines)

def clean_ads(text):
    ad_keywords = ["quảng cáo", "metruyenhot", "duy trì website", "tiền duy trì"]
    lines = [ln for ln in text.splitlines()
             if not any(kw.lower() in ln.lower() for kw in ad_keywords)]
    return "\n".join(lines)

def get_chapter_content(url):
    for _ in range(3):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.select_one("h2").get_text(strip=True)
            raw_content = soup.select_one(".chapter-c").get_text(separator="\n", strip=True)
            cleaned_content = clean_ads(raw_content)
            return f"{title}\n\n{cleaned_content}\n\n"
        except Exception:
            time.sleep(1)
    print(f"❌ Failed to fetch {url}")
    return ""


# def get_chapter_content(url):
#     for _ in range(3):  # Retry up to 3 times
#         try:
#             res = requests.get(url, headers=HEADERS, timeout=10)
#             res.raise_for_status()
#             soup = BeautifulSoup(res.text, 'html.parser')
#             title = soup.select_one("h2").get_text(strip=True)
#             content = soup.select_one(".chapter-c").get_text(separator="\n", strip=True)
#             return f"{title}\n\n{content}\n\n"
#         except Exception as e:
#             time.sleep(1)
#     print(f"❌ Failed to fetch {url}")
#     return ""

def main():
    chapter_links = get_chapter_links()
    print(f"🔗 Total chapters found: {len(chapter_links)}")

    with open("mo_mat_thay_than_tai.txt", "w", encoding="utf-8") as f:
        for url in tqdm(chapter_links, desc="📥 Downloading"):
            chapter = get_chapter_content(url)
            f.write(chapter)
            time.sleep(0.5)  # Be nice to the server

    print("✅ Done! Saved as 'mo_mat_thay_than_tai.txt'.")

if __name__ == "__main__":
    main()

"""
Hướng dẫn: Để tìm đọc các bộ truyện hot khác, các bạn lên Google Search gõ tên truyện + truyen88 và chọn kết quả đầu tiên . Xin cảm ơn
**********
Hiện tại có nhiều website sao chép đăng lại truyện từ truyen88 trái phép, gây thiệt hại về kinh tế và ảnh hưởng tới tốc độ ra chương mới. Chúng tôi rất mong quý độc giả ủng hộ, đẩy lùi nạn sao chép trái phép bằng cách chỉ đọc truyện trên Truyen88.vip. Xin cảm ơn!
**********
Các bạn vào group facebook để yêu cầu truyện, báo lỗi chương và trao đổi giao lưu với nhau nhé!
**********
Truyện được đăng độc quyền trên Truyen88.vip!
Xem thêm truyện hay tại truyen88.vip nhé
Đọc full Chế Chế Tạo Hào Môn trên truyen88.vip
Sau cái đêm hôm đó, cô nghĩ rằng cả đời này cô sẽ không có được tình yêu
Đọc full Này Bác Sĩ Hư Hỏng Em Yêu Anh trên truyen88.vip
Đọc full Nhà có manh thê cưng chiều trên truyen88.vip

"""