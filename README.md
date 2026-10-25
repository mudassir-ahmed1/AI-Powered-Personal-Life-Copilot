# JARVIS — AI Desktop Assistant

A Python desktop assistant with a PyQt5 interface, voice input/output, local Ollama-powered chat, browser controls, WhatsApp Web launching, system information, and productivity utilities.

## Features visible in the current `main.py`

- PyQt5 desktop interface and animated JARVIS-style HUD
- Speech recognition and text-to-speech
- Local language-model requests through Ollama (`phi3` by default)
- Browser navigation and web searches
- WhatsApp Web message-link launching
- System, battery, storage, and uptime information
- Screenshot, clipboard, password-generation, and file-search utilities
- Optional webcam photo/video capture with OpenCV
- Weather and news requests using external APIs

Some features require an internet connection or third-party services; the project is **not fully offline**. Speech recognition uses Google's online recognition service, and weather/news use web APIs.

## Requirements

- Windows is recommended; some functions use Windows-specific APIs and applications.
- Python 3.10 or a compatible version supported by the dependencies.
- Ollama installed and running, with the `phi3` model downloaded, for local AI responses.
- A microphone for voice input.
- The additional `skills` package used by `main.py` (see below).

Install Python packages:

```bash
python -m pip install -r requirements.txt
```

`SpeechRecognition` microphone input may require PyAudio. If installation fails on Windows, install a compatible PyAudio wheel for your Python version.

## Project files required

The current `main.py` imports these project modules:

- `skills/youtube_skill.py`
- `skills/spotify_skill.py`
- `skills/search_skill.py`
- `skills/apps_skill.py`
- `skills/calculator_skill.py`

Those files must be present in a `skills` folder beside `main.py`. They are not included in this repository snapshot yet, so the project may not run until they are added.

The application also creates `contacts.json` locally when needed. Keep personal contact numbers out of public commits.

## Run

After adding the required `skills` modules and configuring dependencies:

```bash
python main.py
```

Start Ollama and ensure the configured model is available before using AI chat.

## API keys and privacy

Do not commit API keys, tokens, phone numbers, or other secrets. Store API credentials in environment variables or a local `.env` file excluded from Git. If a key has already been committed to a public repository, revoke or rotate it and remove it from the repository history where practical.

## Author

Mudassir Ahmed
