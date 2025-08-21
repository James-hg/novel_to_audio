# Website: truyenfull.vision
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

def get_chapter_content(url, headers) -> str:
    """
    INPUT: link to novel website
    OUTPUT: chapter's content as string
    """
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        title_tag = soup.select_one("h1, h2")
        title = title_tag.get_text(strip=True) if title_tag else f"Chương từ {url}"

        content_div = soup.find('div', class_='chapter-c') or soup.select_one('.chuong-noi-dung')
        content_raw = content_div.get_text(separator="\n", strip=True) if content_div else "[Không tìm thấy nội dung]"

        # Keep only the content after the first line of **********
        lines = content_raw.splitlines()
        try:
            start_index = lines.index("**********") + 1
            content_after_asterisks = "\n".join(lines[start_index:])
        except ValueError:
            content_after_asterisks = content_raw  # fallback if no asterisks found

        return f"{title}\n\n{content_after_asterisks}\n\n"

    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return ""

def get_novel(base, prefix, header, start, end) -> str:
    """
    INPUT: link to novel website
    OUTPUT: full raw novel as string
    """
    raw_novel = ""
    chapter_links = [f"{base}{prefix}{i}/" for i in range(start, end + 1)]

    for url in tqdm(chapter_links, desc="Downloading chapters"):
        chapter = get_chapter_content(url, header)
        if chapter.strip():
            raw_novel += chapter + "\n"
            time.sleep(0.5)

    return raw_novel
