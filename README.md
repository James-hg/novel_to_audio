# Novel to Audio

This project automates the process of converting online novels into audio files using text-to-speech (TTS) technology. It includes tools for scraping novel content, cleaning and processing text, generating audio, and managing output files.

## Features

- **Novel Scraping**: Download and extract text from online novel sources.
- **Text Cleaning**: Remove ads and unwanted characters from the extracted text.
- **Text-to-Speech**: Convert cleaned text into audio files using TTS APIs.
- **Audio Merging**: Combine multiple audio segments into a single file.
- **Quiz Generation**: Create quizzes based on novel content (experimental).

## Directory Structure

- `main.py` — Main entry point for the workflow.
- `get_novel.py` — Script for scraping and extracting novel text.
- `clean_ads.py` — Cleans ads and extraneous content from text files.
- `tts.py` — Handles text-to-speech conversion.
- `merge_audio.py` — Merges generated audio files.
- `check_char.py` — Utility for character validation in text.
- `quizziz.py` — Quiz generation from novel content.
- `test_audio.py` — Test script for audio output.
- `store/` — Contains modules for text extraction and storage.
- `test_voice/` — Directory for testing voice outputs.
- `requirements.txt` — Python dependencies.

## Requirements

- Python 3.8+
- See `requirements.txt` for required packages.

## Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the main workflow:

   ```bash
   python main.py
   ```

3. Follow prompts or edit scripts for custom workflows (e.g., scraping, cleaning, TTS).

## Notes

- TTS API usage may require API keys or credentials (see `tts.py`).
- Some scripts are experimental or for testing purposes.

## License

MIT License
