import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

BASE = "https://metruyenhot.me"
PREFIX = "/mo-mat-thay-than-tai/chuong-"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_ads(text):
    ad_keywords = ["quảng cáo", "duy trì website", "tiếp tục ủng hộ"]
    return "\n".join(line for line in text.splitlines()
                     if not any(kw in line.lower() for kw in ad_keywords))

# def get_chapter_content(url):
#     for _ in range(3):
#         try:
#             r = requests.get(url, headers=HEADERS, timeout=10)
#             r.raise_for_status()
#             soup = BeautifulSoup(r.text, 'html.parser')
#             title = soup.select_one('h1, h2').get_text(strip=True)
#             content_div = soup.find('div', class_='chapter-c') or soup.select_one('.chuong-noi-dung')
#             content = content_div.get_text(separator='\n', strip=True) if content_div else ""
#             return f"{title}\n\n{clean_ads(content)}\n\n"
#         except Exception:
#             time.sleep(1)
#     print(f"Failed: {url}")
#     return ""

def extract_full_text(soup):
    # Get all text within chapter-c including bold, span, etc.
    content_div = soup.find('div', class_='chapter-c') or soup.select_one('.chuong-noi-dung')
    if not content_div:
        return ""

    # Join all direct and nested text
    lines = []
    for element in content_div.descendants:
        if element.name in ['br', 'p']:
            lines.append("\n")
        elif isinstance(element, str):
            lines.append(element.strip())
    return " ".join([line for line in lines if line]).replace("  ", " ")


# def get_chapter_content(url):
#     chapter_text = ""
#     part = 1
#     max_parts = 10  # avoid infinite loop on malformed pagination

#     while part <= max_parts:
#         part_url = url if part == 1 else url.rstrip('/') + f"-trang-{part}/"

#         try:
#             r = requests.get(part_url, headers=HEADERS, timeout=10)
#             r.raise_for_status()
#             soup = BeautifulSoup(r.text, 'html.parser')

#             if part == 1:
#                 title_tag = soup.select_one('h1, h2')
#                 title = title_tag.get_text(strip=True) if title_tag else f"Chương từ {url}"
#                 chapter_text += f"{title}\n\n"

#             # content_div = soup.find('div', class_='chapter-c') or soup.select_one('.chuong-noi-dung')
#             content = extract_full_text(soup)

#             # Clean and append
#             cleaned = clean_ads(content)
#             if cleaned.strip():
#                 chapter_text += cleaned + "\n\n"
#             else:
#                 break  # No content? Probably last page

#             # Check if there is a "next" button — if not, break
#             next_link = soup.select_one('a.page-link[rel="next"]')
#             if not next_link or 'trang' not in next_link.get('href', ''):
#                 break  # No further part

#             part += 1
#             time.sleep(0.3)

#         except Exception:
#             print(f"⚠️ Failed to fetch part {part_url}")
#             break

#     return chapter_text.strip() + "\n\n"

def get_chapter_content(url):
    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            title_tag = soup.select_one('h1, h2')
            title = title_tag.get_text(strip=True) if title_tag else f"Chương từ {url}"

            # 1. Get main content
            content_div = soup.find('div', class_='chapter-c')
            content = content_div.get_text(separator='\n', strip=True) if content_div else ""

            # 2. Get all <p> after content_div
            extra_parts = []
            next_node = content_div.find_next_sibling()
            while next_node:
                if next_node.name == 'p':
                    text = next_node.get_text(strip=True)
                    if text:
                        extra_parts.append(text)
                elif next_node.name in ['h2', 'footer']:
                    break  # stop if next chapter or footer
                next_node = next_node.find_next_sibling()

            # 3. Merge all parts
            full_content = content + "\n\n" + "\n".join(extra_parts)
            return f"{title}\n\n{clean_ads(full_content)}\n\n"

        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            time.sleep(1)
            continue

    return ""


def main():
    START, END = 34, 34
    chapter_links = [f"{BASE}{PREFIX}{i}/" for i in range(START, END+1)]
    with open(f"mo_mat_thay_than_tai_{START}_{END}.txt", 'w', encoding='utf-8') as f:
        for url in tqdm(chapter_links, desc="Downloading"):
            chap = get_chapter_content(url)
            f.write(chap)
            time.sleep(0.5)
    print(f"Finished saving chapters {START} to {END}.")

if __name__ == "__main__":
    main()
