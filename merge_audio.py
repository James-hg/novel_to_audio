import re
from pathlib import Path
from pydub import AudioSegment
from tqdm import tqdm

# Matches: Chuong_201_part3.mp3, chuong-201-Part-03.mp3, "Chuong 201 part 3.mp3", etc.
NUM_KEY = re.compile(r".*?chuong[ _-]*([0-9]+).*?part[ _-]*([0-9]+)", re.IGNORECASE)

def chap_part_key(p: Path):
    m = NUM_KEY.match(p.stem)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    # fallback: put non-matching files at the end, by name
    return (10**9, 10**9, p.name.lower())

def merge_audio(input_folder):
    input_folder = Path(input_folder)
    output_file = input_folder / "merged_output.mp3"

    mp3_files = sorted(input_folder.glob("*.mp3"), key=chap_part_key)

    merged = AudioSegment.empty()
    for mp3_file in tqdm(mp3_files, desc= "Merging progress: "):
        audio = AudioSegment.from_mp3(mp3_file)
        merged += audio
        print(f"✅ Merged: {mp3_file.name}")

    print(f"Merging {len(mp3_files)} files:")
    merged.export(output_file, format="mp3")
    print(f"\n🎉 All files merged into: {output_file}")

