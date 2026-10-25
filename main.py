"""
JARVIS - Ultimate AI Assistant (Iron Man Edition)
Heavy Deep Voice | 80+ Features | Browser Automation | WhatsApp Integration | Premium UI
"""

import speech_recognition as sr
import pyttsx3
import datetime
import os
import re
import pyjokes
import requests
import psutil
import sys
import threading
import time
import random
import string
import pyperclip
import pyautogui
import qrcode
import subprocess
import platform
import socket
import getpass
import math
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from skills.youtube_skill import play_youtube
from skills.spotify_skill import play_spotify
from skills.search_skill import web_search
from skills.apps_skill import open_application, close_application, force_close_application, close_all_apps
from skills.calculator_skill import calculate

# ─── Configuration ───────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"
USE_GUI = True

WEATHER_API_KEY = "02a033ba6dfb53f1f1f554619766b9e3"
NEWS_API_KEY = "1e636be1aa894740b1e541ed8fd7fdad"

jarvis_ui = None
reminders = []
recognizer = None

# ─── HEAVY DEEP VOICE ENGINE ────────────────────────────────────
import asyncio as _aio, tempfile as _tmp, ctypes as _ct

engine = pyttsx3.init()
engine.setProperty("rate", 170); engine.setProperty("volume", 1.0)
for _v in engine.getProperty("voices"):
    if any(n in _v.name.lower() for n in ["david","mark","george"]):
        engine.setProperty("voice", _v.id); break

_USE_EDGE = False
try:
    import edge_tts as _etts; _USE_EDGE = True
    print("✅ edge-tts Christopher Neural active")
except ImportError:
    print("ℹ  pip install edge-tts  for human voice")

_VOICE, _RATE, _PITCH = "en-US-ChristopherNeural", "-5%", "-8Hz"

def _play_mp3(path):
    try:
        mci = _ct.windll.winmm.mciSendStringW
        mci(f'open "{path}" type mpegvideo alias jsnd', None, 0, None)
        mci("play jsnd wait", None, 0, None)
        mci("close jsnd", None, 0, None)
    except Exception as e: print(f"  MCI: {e}")
    try:
        import os as _o; _o.unlink(path)
    except: pass

# Reuse one event loop — eliminates ~300ms overhead per speak call
_ev_loop = _aio.new_event_loop()

def _edge_speak(text):
    try:
        t = _tmp.NamedTemporaryFile(suffix=".mp3", delete=False)
        p = t.name; t.close()
        _ev_loop.run_until_complete(
            _etts.Communicate(text, _VOICE, rate=_RATE, pitch=_PITCH).save(p)
        )
        _play_mp3(p)
    except Exception as e:
        print(f"  edge err ({e})")
        try: engine.say(text); engine.runAndWait()
        except: pass

def speak(text: str):
    print(f"\n🤖 JARVIS: {text}")
    if jarvis_ui: jarvis_ui.add_message_signal.emit("JARVIS", text, False)
    if _USE_EDGE: _edge_speak(text)
    else: engine.say(text); engine.runAndWait()


# ─── Speech Recognition ─────────────────────────────────────────
def init_recognizer():
    global recognizer
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.energy_threshold = 300
    return recognizer


def listen() -> str:
    global recognizer
    if recognizer is None:
        init_recognizer()
    with sr.Microphone() as source:
        if jarvis_ui:
            jarvis_ui.update_status_signal.emit("LISTENING...", "#00ff00")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            query = recognizer.recognize_google(audio, language="en-US")
            print(f"👤 You said: {query}")
            if jarvis_ui:
                jarvis_ui.update_status_signal.emit("READY", "#00ff00")
                jarvis_ui.add_message_signal.emit("You", query, False)
            return query.lower().strip()
        except:
            if jarvis_ui:
                jarvis_ui.update_status_signal.emit("READY", "#00ff00")
            return ""


# ─── BROWSER AUTOMATION FEATURES ─────────────────────────────────
def open_website(url: str):
    """Open a website in default browser"""
    try:
        # Add https:// if not present
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}"
    except:
        return "Failed to open website"


def open_popular_site(site: str):
    """Open popular websites by name"""
    sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://reddit.com",
        "twitter": "https://twitter.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "linkedin": "https://linkedin.com",
        "amazon": "https://amazon.com",
        "flipkart": "https://flipkart.com",
        "netflix": "https://netflix.com",
        "hotstar": "https://hotstar.com",
        "whatsapp web": "https://web.whatsapp.com",
        "chatgpt": "https://chat.openai.com",
        "gemini": "https://gemini.google.com",
    }

    site_lower = site.lower()
    if site_lower in sites:
        webbrowser.open(sites[site_lower])
        return f"Opening {site}"
    else:
        return open_website(site)


def search_google(query: str):
    """Search Google"""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Searching Google for {query}"


def search_youtube(query: str):
    """Search YouTube"""
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Searching YouTube for {query}"


def close_browser_tab():
    """Close current browser tab (Ctrl+W)"""
    pyautogui.hotkey('ctrl', 'w')
    return "Closed current browser tab"


def new_browser_tab():
    """Open new browser tab (Ctrl+T)"""
    pyautogui.hotkey('ctrl', 't')
    return "Opened new tab"


def close_browser_window():
    """Close browser window (Alt+F4)"""
    pyautogui.hotkey('alt', 'f4')
    return "Closed browser window"


def refresh_page():
    """Refresh current page (Ctrl+R)"""
    pyautogui.hotkey('ctrl', 'r')
    return "Refreshed page"


def go_back():
    """Go back in browser (Alt+Left)"""
    pyautogui.hotkey('alt', 'left')
    return "Went back"


def go_forward():
    """Go forward in browser (Alt+Right)"""
    pyautogui.hotkey('alt', 'right')
    return "Went forward"


def open_incognito():
    """Open incognito/private window"""
    pyautogui.hotkey('ctrl', 'shift', 'n')
    return "Opened incognito window"


def zoom_in():
    """Zoom in (Ctrl+Plus)"""
    pyautogui.hotkey('ctrl', '+')
    return "Zoomed in"


def zoom_out():
    """Zoom out (Ctrl+Minus)"""
    pyautogui.hotkey('ctrl', '-')
    return "Zoomed out"


def fullscreen_browser():
    """Toggle fullscreen (F11)"""
    pyautogui.press('f11')
    return "Toggled fullscreen"


# ─── WHATSAPP AUTOMATION FEATURES ───────────────────────────────
def open_whatsapp_web():
    """Open WhatsApp Web"""
    webbrowser.open("https://web.whatsapp.com")
    return "Opening WhatsApp Web. Please scan QR code if needed."


def send_whatsapp_message(phone_number: str, message: str):
    """Send WhatsApp message using WhatsApp Web URL scheme"""
    # Clean phone number (remove non-digits)
    phone = re.sub(r'\D', '', phone_number)
    # Add India country code if not present
    if not phone.startswith('91') and len(phone) == 10:
        phone = '91' + phone
    elif not phone.startswith('91') and len(phone) > 10:
        phone = '91' + phone[-10:]

    # Encode message for URL
    encoded_msg = message.replace(' ', '%20').replace('\n', '%0A')
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
    webbrowser.open(url)
    return f"Opening WhatsApp to send message to {phone_number}. Press Enter to send."


import json as _jarvis_json

def _contacts_path():
    """Return path to contacts.json in the same folder as main.py."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")


def load_contacts() -> dict:
    """Load contacts from contacts.json. Auto-creates file if missing."""
    path = _contacts_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = _jarvis_json.load(f)
            result = {k.lower().strip(): str(v) for k, v in data.items()}
            print(f"  Contacts loaded: {list(result.keys())}")
            return result
        except Exception as e:
            print(f"  contacts.json error: {e}")
    # Create default template
    default = {
        "mom":    "919999999991",
        "dad":    "919999999992",
        "self":   "919999999993",
        "friend": "919999999994"
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            _jarvis_json.dump(default, f, indent=4)
        print(f"  Created contacts.json at: {path}")
        print(f"  IMPORTANT: Edit it with your real numbers!")
    except Exception as e:
        print(f"  Could not create contacts.json: {e}")
    return default


def save_contact(name: str, number: str) -> str:
    """Save or update a contact in contacts.json."""
    try:
        contacts = load_contacts()
        number = re.sub(r"\D", "", number)
        if len(number) == 10:
            number = "91" + number
        contacts[name.lower().strip()] = number
        with open(_contacts_path(), "w", encoding="utf-8") as f:
            _jarvis_json.dump(contacts, f, indent=4)
        return f"Saved {name} with number {number} in contacts, sir."
    except Exception as e:
        return f"Could not save contact: {e}"


def send_whatsapp_to_contact(contact: str, message: str) -> str:
    """Look up contact by name from contacts.json and send WhatsApp message."""
    contacts = load_contacts()
    key = contact.lower().strip()
    print(f"  WhatsApp lookup: '{key}' in {list(contacts.keys())}")

    # 1. Exact name match
    if key in contacts:
        return send_whatsapp_message(contacts[key], message)

    # 2. Partial match (e.g. "bro" matches "brother")
    for name, number in contacts.items():
        if key in name or name in key:
            return send_whatsapp_message(number, message)

    # 3. Raw phone number
    digits = re.sub(r"\D", "", key)
    if len(digits) >= 10:
        return send_whatsapp_message(digits, message)

    return f"Contact '{contact}' not found. Say: save contact {contact} NUMBER to add them."


# ─── Core Functions ─────────────────────────────────────────────
def take_screenshot():
    try:
        path = os.path.expanduser(f"~/Desktop/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pyautogui.screenshot().save(path)
        return "Screenshot captured"
    except:
        return "Screenshot failed"


def generate_password():
    pwd = ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(14))
    pyperclip.copy(pwd)
    return f"Password generated and copied"


def get_weather(city="London"):
    try:
        data = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric",
            timeout=5).json()
        if data.get('cod') == 200:
            return f"{city}: {data['weather'][0]['description']}, {data['main']['temp']}°C"
        return f"City {city} not found"
    except:
        return "Weather offline"


def get_news():
    try:
        articles = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}",
                                timeout=5).json().get('articles', [])[:2]
        if articles:
            return "Top headlines: " + ". ".join([f"{a['title'][:50]}" for a in articles])
        return "News unavailable"
    except:
        return "News offline"


def get_motivation():
    quotes = [
        "The only way to do great work is to love what you do.",
        "Success is not final, failure is not fatal.",
        "Believe you can and you're halfway there.",
    ]
    return random.choice(quotes)


def get_battery_info() -> str:
    """Get accurate battery status on Windows."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery detected. Running on desktop power."
        percent = battery.percent
        plugged = battery.power_plugged
        secs_left = battery.secsleft
        status = "charging" if plugged else "discharging"
        if plugged and percent >= 99:
            status = "fully charged"
        time_str = ""
        if not plugged and secs_left not in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED):
            hours = secs_left // 3600
            mins = (secs_left % 3600) // 60
            time_str = f", {hours}h {mins}m remaining"
        return f"Battery is at {percent:.0f}%, {status}{time_str}."
    except Exception as e:
        return f"Could not read battery: {str(e)}"


def get_system_info() -> str:
    """Get accurate real-time system info."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage('C:\\')
        except:
            disk = psutil.disk_usage('/')
        battery_str = get_battery_info()
        return (
            f"CPU: {cpu}%. "
            f"RAM: {ram.used // (1024**2)} MB of {ram.total // (1024**2)} MB ({ram.percent}%). "
            f"Disk: {disk.free // (1024**3)} GB free of {disk.total // (1024**3)} GB. "
            f"{battery_str}"
        )
    except Exception as e:
        return f"System info error: {str(e)}"


def system_health():
    health = []
    try:
        requests.get("http://www.google.com", timeout=3)
        health.append("Internet: Connected")
    except:
        health.append("Internet: Disconnected")
    try:
        disk = psutil.disk_usage('C:\\')
    except:
        disk = psutil.disk_usage('/')
    health.append(f"Free: {disk.free // (1024**3)} GB")
    health.append(get_battery_info())
    return " | ".join(health)


def daily_briefing():
    now = datetime.datetime.now()
    greeting = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 17 else "Good evening"
    return f"{greeting}, sir. It's {now.strftime('%I:%M %p')}. {get_weather('London')}"


def get_random_fact():
    facts = [
        "A day on Venus is longer than a year on Venus.",
        "Bananas are berries, but strawberries aren't.",
        "Octopuses have three hearts.",
        "Honey never spoils.",
    ]
    return random.choice(facts)


def get_uptime():
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot
    return f"Uptime: {uptime.days}d, {uptime.seconds // 3600}h, {(uptime.seconds % 3600) // 60}m"


_conv_history = []

# Persistent HTTP session — eliminates TCP handshake per request (~200ms saved)
_ai_session = requests.Session()
_ai_session.headers.update({"Content-Type": "application/json"})
import json as _fastjson

def ask_ollama(user_input: str) -> str:
    """Fastest possible Ollama call: persistent session + minimal prompt + early exit."""
    global _conv_history
    _conv_history.append(f"U:{user_input}")
    if len(_conv_history) > 10: _conv_history = _conv_history[-10:]

    # Ultra-compact prompt — fewer input tokens = faster first token out
    hist = "\n".join(_conv_history[-6:])
    prompt = f"JARVIS AI. 1-2 sentences, witty, direct. Never refuse.\n{hist}\nJ:"

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": 55,     # Hard cap — enough for 1-2 sentences
                "temperature": 0.5,
                "top_k": 15,           # Very tight = fastest token selection
                "top_p": 0.8,
                "repeat_penalty": 1.05,
                "num_ctx": 512,        # Tiny context window = fast processing
            }
        }
        parts = []
        with _ai_session.post(OLLAMA_URL, json=payload, stream=True, timeout=14) as r:
            for raw in r.iter_lines():
                if not raw: continue
                try:
                    c = _fastjson.loads(raw)
                    tok = c.get("response", "")
                    if tok: parts.append(tok)
                    joined = "".join(parts)
                    # Stop the moment we hit sentence end — don't wait for model to finish
                    if len(joined) > 18 and joined.rstrip()[-1] in ".!?": break
                    if c.get("done"): break
                except: continue

        reply = "".join(parts).strip().lstrip("J:").strip()
        if reply:
            _conv_history.append(f"J:{reply}")
            return reply
        return "At your service, sir."
    except Exception as e:
        print(f"  Ollama: {e}")
        return "AI offline. Run: ollama serve"



import json as _jj

# ── Write to Notepad (fast, silent) ──────────────────────────────
def write_to_notepad(text: str, title: str = "JARVIS") -> bool:
    try:
        import tempfile
        f = tempfile.NamedTemporaryFile(mode="w",suffix=".txt",prefix="JARVIS_",delete=False,encoding="utf-8")
        f.write(f"{'='*60}\n  JARVIS — {title}\n  {datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n{'='*60}\n\n")
        f.write(text)
        f.close()
        subprocess.Popen(["notepad.exe", f.name])
        return True
    except Exception as e:
        print(f"Notepad err: {e}"); return False

def generate_and_write(prompt: str, ctype: str):
    if jarvis_ui:
        jarvis_ui.update_status_signal.emit("WRITING...", "#ffaa00")
        jarvis_ui.add_message_signal.emit("JARVIS", f"Writing {ctype}, opening Notepad...", False)
    systems = {
        "code": "Write ONLY working code with comments. No intro/outro.",
        "html": "Write complete HTML+CSS in one file. Code only.",
        "python": "Write clean Python code. Code only.",
        "java": "Write clean Java code. Code only.",
        "javascript": "Write clean JS. Code only.",
        "essay": "Write structured essay: intro, 3 paragraphs, conclusion.",
        "email": "Write professional email: Subject, greeting, body, sign-off.",
        "letter": "Write formal letter: date, subject, body, signature.",
        "story": "Write engaging short story.",
        "article": "Write informative article with title, intro, sections, conclusion.",
        "paragraph": "Write one detailed paragraph.",
        "resume": "Write professional resume with all standard sections.",
        "report": "Write detailed report: summary, findings, conclusion.",
    }
    sys_p = systems.get(ctype, "Write the requested content clearly.")
    try:
        payload = {"model": MODEL_NAME,
                   "prompt": f"{sys_p}\n\nRequest: {prompt}\n\nOutput:\n",
                   "stream": True, "options": {"num_predict":800,"temperature":0.65,"top_p":0.9}}
        parts = []
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
            for line in r.iter_lines():
                if not line: continue
                try:
                    c = __import__("json").loads(line)
                    parts.append(c.get("response",""))
                    if c.get("done"): break
                except: continue
        gen = "".join(parts).strip()
        if gen: write_to_notepad(gen, title=f"{ctype.upper()}: {prompt[:45]}")
        else:
            if jarvis_ui: jarvis_ui.add_message_signal.emit("JARVIS","Could not generate. Is Ollama running?",False)
    except Exception as e: print(f"gen_write err: {e}")
    if jarvis_ui: jarvis_ui.update_status_signal.emit("READY","#00ff00")


# ── Video / Photo ────────────────────────────────────────────────
def take_photo() -> str:
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            os.startfile("microsoft.windows.camera:"); return "Opened Camera app, sir."
        time.sleep(0.8)
        ret, frame = cap.read(); cap.release()
        if ret:
            path = os.path.expanduser(f"~/Desktop/JARVIS_Photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(path, frame)
            return f"Photo saved to Desktop, sir."
        return "Webcam error, sir."
    except ImportError:
        os.startfile("microsoft.windows.camera:"); return "Opened Camera app. Run pip install opencv-python for direct capture."
    except Exception as e: return f"Photo failed: {e}"

def record_video(seconds: int = 10) -> str:
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened(): return "No webcam found, sir."
        path = os.path.expanduser(f"~/Desktop/JARVIS_Video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        fps = 20.0; w = int(cap.get(3)); h = int(cap.get(4))
        out = cv2.VideoWriter(path, fourcc, fps, (w, h))
        speak(f"Recording {seconds} seconds now, sir.")
        end = time.time() + seconds
        while time.time() < end:
            ret, frame = cap.read()
            if ret: out.write(frame)
            else: break
        cap.release(); out.release()
        return f"Video saved to Desktop, sir."
    except ImportError: return "Run: pip install opencv-python"
    except Exception as e: return f"Recording failed: {e}"


# ── File system access ───────────────────────────────────────────
def search_files(query: str, folder: str = None) -> str:
    """Search for files by name on the system."""
    search_dir = folder or os.path.expanduser("~")
    results = []
    try:
        for root, dirs, files in os.walk(search_dir):
            # Skip hidden/system folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                       ["Windows","Program Files","AppData\Local\Temp"]]
            for f in files:
                if query.lower() in f.lower():
                    results.append(os.path.join(root, f))
                    if len(results) >= 5: break
            if len(results) >= 5: break
    except PermissionError: pass
    if results:
        for r in results:
            speak(f"Found: {os.path.basename(r)}")
        subprocess.Popen(f'explorer /select,"{results[0]}"'  )
        return f"Found {len(results)} file(s). Opening location of first result."
    return f"No files matching '{query}' found, sir."

def open_file(path_or_name: str) -> str:
    """Open a file — by full path or search by name."""
    if os.path.exists(path_or_name):
        os.startfile(path_or_name)
        return f"Opened {os.path.basename(path_or_name)}, sir."
    # Try searching
    home = os.path.expanduser("~")
    for root, dirs, files in os.walk(home):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if path_or_name.lower() in f.lower():
                full = os.path.join(root, f)
                os.startfile(full)
                return f"Opened {f}, sir."
    return f"Could not find {path_or_name}, sir."

def list_downloads() -> str:
    """List recent files in Downloads folder."""
    dl = os.path.expanduser("~/Downloads")
    try:
        files = sorted(os.listdir(dl), key=lambda x: os.path.getmtime(os.path.join(dl,x)), reverse=True)[:8]
        names = ", ".join(files)
        speak(f"Recent downloads: {names}")
        os.startfile(dl)
        return f"Opened Downloads. Recent: {names}"
    except Exception as e: return f"Could not list downloads: {e}"

def open_desktop() -> str:
    desktop = os.path.expanduser("~/Desktop")
    os.startfile(desktop)
    return "Opened Desktop folder, sir."

def open_documents() -> str:
    docs = os.path.expanduser("~/Documents")
    os.startfile(docs)
    return "Opened Documents folder, sir."


# ─── COMMAND HANDLER WITH BROWSER & WHATSAPP ─────────────────────
def handle_command(query: str) -> bool:
    q = query.lower().strip()

    # Exit command
    if any(w in q for w in ["exit", "quit", "goodbye", "bye", "shutdown"]):
        speak("Powering down. Goodbye sir.")
        return False

    # Stop listening
    if "stop listening" in q:
        if jarvis_ui:
            jarvis_ui.stop_listening_signal.emit()
        return True

    # ============================================================
    # BROWSER AUTOMATION COMMANDS
    # ============================================================

    # Open website
    if "open website" in q or "go to" in q:
        site = q.replace("open website", "").replace("go to", "").strip()
        if site:
            result = open_popular_site(site)
            speak(result)
        else:
            speak("Which website would you like me to open?")
        return True

    # Search Google
    if "search google for" in q or "google" in q:
        term = q.replace("search google for", "").replace("google", "").strip()
        if term:
            result = search_google(term)
            speak(result)
        else:
            speak("What would you like me to search on Google?")
        return True

    # Search YouTube
    if "search youtube for" in q:
        term = q.replace("search youtube for", "").strip()
        if term:
            result = search_youtube(term)
            speak(result)
        else:
            speak("What would you like me to search on YouTube?")
        return True

    # Browser tab controls
    if "close tab" in q or "close this tab" in q:
        result = close_browser_tab()
        speak(result)
        return True

    if "new tab" in q or "open new tab" in q:
        result = new_browser_tab()
        speak(result)
        return True

    if "close window" in q or "close browser" in q:
        result = close_browser_window()
        speak(result)
        return True

    if "refresh" in q or "reload page" in q:
        result = refresh_page()
        speak(result)
        return True

    if "go back" in q or "back" in q:
        result = go_back()
        speak(result)
        return True

    if "go forward" in q or "forward" in q:
        result = go_forward()
        speak(result)
        return True

    if "incognito" in q or "private window" in q:
        result = open_incognito()
        speak(result)
        return True

    if "zoom in" in q:
        result = zoom_in()
        speak(result)
        return True

    if "zoom out" in q:
        result = zoom_out()
        speak(result)
        return True

    if "fullscreen" in q:
        result = fullscreen_browser()
        speak(result)
        return True

    # ============================================================
    # WHATSAPP COMMANDS
    # ============================================================

    if "open whatsapp" in q:
        result = open_whatsapp_web()
        speak(result)
        return True

    if "send whatsapp message" in q:
        # Parse: send whatsapp message to [number/contact] [message]
        match = re.search(r'to\s+(\S+)\s+(.+)', q)
        if match:
            recipient = match.group(1)
            message = match.group(2)
            result = send_whatsapp_to_contact(recipient, message)
            speak(result)
        else:
            speak("Please specify recipient and message. Example: send whatsapp message to 9876543210 Hello")
        return True

    # ============================================================
    # MEDIA COMMANDS
    # ============================================================

    if "spotify" in q and ("play" in q or "song" in q):
        song = q
        for word in ["play", "on spotify", "spotify", "song", "music", "please"]:
            song = song.replace(word, "")
        song = song.strip()
        if song:
            speak(f"Playing {song} on Spotify, sir.")
            play_spotify(song, auto_play=True)
        else:
            speak("What would you like me to play on Spotify?")
        return True

    if "youtube" in q and ("play" in q or "video" in q):
        video = q
        for word in ["play", "on youtube", "youtube", "video", "watch", "please"]:
            video = video.replace(word, "")
        video = video.strip()
        if video:
            speak(f"Playing {video} on YouTube, sir.")
            play_youtube(video, auto_play=True)
        else:
            speak("What would you like me to play on YouTube?")
        return True

    if q.startswith("play ") and len(q) > 5:
        song = q.replace("play ", "").strip()
        if "spotify" in song:
            song = song.replace("on spotify", "").replace("on Spotify", "").strip()
            speak(f"Playing {song} on Spotify, sir.")
            play_spotify(song, auto_play=True)
        else:
            song = song.replace("on youtube", "").replace("on YouTube", "").strip()
            speak(f"Playing {song} on YouTube, sir.")
            play_youtube(song, auto_play=True)
        return True

    # ============================================================
    # SYSTEM & INFORMATION COMMANDS
    # ============================================================

    if "health" in q:
        speak(system_health())
    elif "battery" in q or "battery status" in q:
        speak(get_battery_info())
    elif "system info" in q or "system information" in q or "pc info" in q:
        speak(get_system_info())
    elif "cpu" in q or "ram" in q or "memory" in q:
        speak(get_system_info())
    elif "briefing" in q or "daily briefing" in q:
        speak(daily_briefing())
    elif "fact" in q or "random fact" in q:
        speak(get_random_fact())
    elif "uptime" in q:
        speak(get_uptime())
    elif "time" in q and "date" not in q:
        speak(f"It's {datetime.datetime.now().strftime('%I:%M %p')}")
    elif "date" in q or "today" in q:
        speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
    elif "weather" in q:
        city_match = re.search(r'weather(?:\s+in)?\s+([a-zA-Z]+)', q)
        city = city_match.group(1) if city_match else "Hyderabad"
        speak(get_weather(city))
    elif "news" in q:
        speak(get_news())
    elif "screenshot" in q:
        speak(take_screenshot())
    elif "password" in q:
        speak(generate_password())
    elif "joke" in q:
        speak(pyjokes.get_joke())
    elif "motivate" in q or "motivation" in q:
        speak(get_motivation())

    # ============================================================
    # VOLUME CONTROL
    # ============================================================

    elif "volume up" in q or "increase volume" in q:
        for _ in range(5):
            pyautogui.press('volumeup')
        speak("Volume increased")
    elif "volume down" in q or "decrease volume" in q:
        for _ in range(5):
            pyautogui.press('volumedown')
        speak("Volume decreased")
    elif "mute" in q:
        pyautogui.press('volumemute')
        speak("Volume muted")

    # ============================================================
    # OPEN APPLICATION
    # ============================================================

    elif any(w in q for w in ["open", "launch", "start"]):
        app = q
        for word in ["open", "launch", "start", "run", "please", "the"]:
            app = app.replace(word, "")
        app = app.strip()

        special_apps = {
            "excel": "excel", "word": "word", "powerpoint": "powerpoint",
            "notepad": "notepad", "calculator": "calculator", "chrome": "chrome",
            "spotify": "spotify", "vs code": "vs code"
        }

        if app in special_apps:
            app = special_apps[app]

        if app and len(app) > 1:
            speak(f"Opening {app}, sir.")
            open_application(app)
        else:
            speak("Which application would you like me to open?")

    # ============================================================
    # CLOSE COMMANDS
    # ============================================================

    elif "close all" in q or "close everything" in q:
        speak(close_all_apps())
    elif "close" in q:
        app = q.replace("close", "").strip()
        if app and len(app) > 1:
            speak(close_application(app))
        else:
            pyautogui.hotkey('alt', 'f4')
            speak("Closed current window")

    # ── IP Address ───────────────────────────────────────────────
    elif "ip address" in q or "my ip" in q or "what is my ip" in q:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                public_ip = requests.get("https://api.ipify.org", timeout=4).text
                speak(f"Your local IP is {local_ip} and your public IP is {public_ip}.")
            except:
                speak(f"Your local IP address is {local_ip}.")
        except:
            speak("Could not retrieve IP address.")

    # ── Disk Space ───────────────────────────────────────────────
    elif "disk space" in q or "storage" in q or "disk usage" in q:
        try:
            try:
                disk = psutil.disk_usage("C:\\")
            except:
                disk = psutil.disk_usage("/")
            used = disk.used // (1024**3)
            free = disk.free // (1024**3)
            total = disk.total // (1024**3)
            speak(f"Disk: {used} GB used, {free} GB free, {total} GB total.")
        except Exception as e:
            speak(f"Could not get disk info: {str(e)}")

    # ── Clipboard ────────────────────────────────────────────────
    elif "read clipboard" in q or "what is in clipboard" in q or "clipboard content" in q:
        try:
            content_clip = pyperclip.paste()
            if content_clip and content_clip.strip():
                speak(f"Clipboard contains: {content_clip[:150]}")
            else:
                speak("Clipboard is empty.")
        except:
            speak("Could not read clipboard.")

    elif "copy" in q and "clipboard" in q:
        text = q.replace("copy", "").replace("to clipboard", "").replace("clipboard", "").strip()
        if text:
            pyperclip.copy(text)
            speak(f"Copied to clipboard.")

    # ── Calculate (voice-triggered) ──────────────────────────────
    elif any(w in q for w in ["calculate", "what is", "how much is", "compute", "solve"]):
        expr = q
        for w in ["calculate", "what is", "how much is", "compute", "solve", "please"]:
            expr = expr.replace(w, "")
        expr = expr.strip()
        if expr:
            result = calculate(expr)
            speak(result)
        else:
            speak("What would you like me to calculate?")

    # ── System shortcuts ─────────────────────────────────────────
    elif "minimize all" in q or "show desktop" in q:
        pyautogui.hotkey('win', 'd')
        speak("Showing desktop.")
    elif "task view" in q or "virtual desktop" in q:
        pyautogui.hotkey('win', 'tab')
        speak("Opening task view.")
    elif "take screenshot" in q or "capture screen" in q:
        speak(take_screenshot())
    elif "empty recycle bin" in q:
        import winreg
        os.system('PowerShell -Command "Clear-RecycleBin -Confirm:$false"')
        speak("Recycle bin emptied.")

    # ============================================================
    # HELP
    # ============================================================

    elif "help" in q or "what can you do" in q:
        help_text = """NEW BROWSER COMMANDS:
🌐 'open website google' - Open any website
🔍 'search google for python' - Google search
▶️ 'search youtube for songs' - YouTube search
📑 'close tab', 'new tab', 'refresh', 'go back'
🔒 'incognito mode', 'zoom in/out', 'fullscreen'

💬 WHATSAPP:
📱 'open whatsapp' - Open WhatsApp Web
💬 'send whatsapp message to 9876543210 Hello'

🎵 MEDIA: 'play Believer on Spotify', 'play song on youtube'
📱 APPS: 'open excel', 'open notepad'
⚡ SYSTEM: 'time', 'weather', 'screenshot', 'joke', 'volume up'"""
        speak(help_text)

    # ── Photo / Video ─────────────────────────────────────────────
    elif any(p in q for p in ["take photo","capture photo","take picture","take a photo"]):
        speak("Taking photo now, sir.")
        threading.Thread(target=lambda: speak(take_photo()), daemon=True).start()

    elif any(p in q for p in ["record video","start recording","record a video"]):
        secs = 10
        m = re.search(r"(\d+)\s*(?:second|sec)", q)
        if m: secs = min(int(m.group(1)), 120)
        threading.Thread(target=lambda: record_video(secs), daemon=True).start()

    # ── File system ───────────────────────────────────────────────
    elif any(p in q for p in ["search file","find file","search for file","look for file"]):
        fname = q
        for w in ["search file","find file","search for file","look for file","called","named","please"]:
            fname = fname.replace(w,"")
        speak(search_files(fname.strip()))

    elif any(p in q for p in ["open file","open document"]):
        fname = q
        for w in ["open file","open document","please"]:
            fname = fname.replace(w,"")
        speak(open_file(fname.strip()))

    elif any(p in q for p in ["open downloads","show downloads","my downloads"]):
        speak(list_downloads())

    elif any(p in q for p in ["open desktop","show desktop files"]):
        speak(open_desktop())

    elif any(p in q for p in ["open documents","my documents"]):
        speak(open_documents())

    # ── Contacts ─────────────────────────────────────────────────
    elif "save contact" in q or "add contact" in q:
        m = re.search(r"(?:save|add) contact\s+(\w+)\s+(\d+)", q)
        if m: speak(save_contact(m.group(1), m.group(2)))
        else: speak("Say: save contact NAME NUMBER")

    elif "show contacts" in q or "list contacts" in q or "my contacts" in q:
        names = ", ".join(load_contacts().keys())
        speak(f"Your contacts: {names}.")

    # ── Write to Notepad ─────────────────────────────────────────
    elif any(q.startswith(w) for w in ["write ","generate ","create ","draft ","make a "]) or          any(p in q for p in ["code for","code in","essay on","essay about","email to",
                               "email about","letter to","story about","article on",
                               "html for","program for","script for"]):
        ctype = "content"
        if any(w in q for w in ["html","webpage","website"]): ctype = "html"
        elif "python" in q or "py " in q: ctype = "python"
        elif "java" in q and "javascript" not in q: ctype = "java"
        elif any(w in q for w in ["javascript"," js "]): ctype = "javascript"
        elif any(w in q for w in ["code","program","script","function","algorithm"]): ctype = "code"
        elif "essay" in q: ctype = "essay"
        elif "email" in q or "mail" in q: ctype = "email"
        elif "letter" in q: ctype = "letter"
        elif "story" in q: ctype = "story"
        elif "article" in q or "blog" in q: ctype = "article"
        elif "paragraph" in q: ctype = "paragraph"
        elif "resume" in q: ctype = "resume"
        elif "report" in q: ctype = "report"
        topic = q
        for w in ["write","generate","create","draft","make","a","an","the","code for","code in",
                  "essay on","essay about","email about","email to","letter to","story about",
                  "html for","program for","script for","please","sir","me"]:
            topic = re.sub(r"\b"+re.escape(w)+r"\b"," ",topic)
        topic = " ".join(topic.split()).strip() or q
        threading.Thread(target=generate_and_write, args=(topic,ctype), daemon=True).start()

    # ── Fun extras ────────────────────────────────────────────────
    elif "flip a coin" in q or "toss coin" in q:
        speak(f"It is {random.choice(['Heads','Tails'])}, sir.")
    elif "roll a dice" in q or "roll dice" in q:
        speak(f"You rolled a {random.randint(1,6)}, sir.")
    elif any(p in q for p in ["how are you","are you ok"]):
        speak("Fully operational and running at peak efficiency, sir.")
    elif "who made you" in q or "who built you" in q:
        speak("You built me, sir. Your personal JARVIS.")
    elif "good morning" in q: speak("Good morning sir. All systems online.")
    elif "good night" in q: speak("Good night sir. Rest well.")
    elif "good afternoon" in q or "good evening" in q: speak("Good to hear from you sir.")
    elif "clear chat" in q:
        if jarvis_ui: jarvis_ui.chat_area.clear()
        speak("Chat cleared, sir.")
    elif "what can you do" in q or "your features" in q:
        speak("I can open apps, play music, search the web, write code and essays to Notepad, control your browser, send WhatsApp messages, take photos, record videos, search your files, answer any question, and much more, sir.")

    # ── Conversational AI fallback ────────────────────────────────
    else:
        if jarvis_ui: jarvis_ui.update_status_signal.emit("THINKING...", "#ffaa00")
        response = ask_ollama(q)
        speak(response)

    return True


# ─── PREMIUM UI CLASS ───────────────────────────────────────────

import math as _M

# ── Color palette ────────────────────────────────────────────────
_C  = "#00d4ff"   # main cyan
_G  = "#00ff88"   # green (active)
_AM = "#ffaa00"   # amber (thinking)
_RD = "#ff3355"   # red (standby/alert)
_PU = "#aa55ff"   # purple (speaking)
_BG = "#03080f"   # deep background
_BG2= "#060f1e"
_P  = "rgba(0,180,255,"


def _btn(color="#00d4ff", h=28):
    c = color
    return f"""
    QPushButton {{
        background: rgba(0,0,0,0);
        color: {c};
        border: 1px solid {c}44;
        border-radius: 5px;
        font-size: 10px;
        font-weight: bold;
        padding: 3px 5px;
        text-align: left;
        min-height: {h}px;
    }}
    QPushButton:hover {{
        background: {c}22;
        border: 1px solid {c};
        color: #ffffff;
    }}
    QPushButton:pressed {{ background: {c}44; }}
"""


# ════════════════════════════════════════════════════════════════
#  IRON MAN HOLOGRAM WIDGET
# ════════════════════════════════════════════════════════════════
class IronManHologram(QWidget):
    """Iron Man HUD hologram — arc reactor + helmet outline + data rings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(260, 260)
        self._a = 0.0       # rotation angle
        self._p = 0.0       # pulse 0-1
        self._pd = 1
        self._state = "standby"
        self._wave = [0.0] * 32   # voice waveform
        self._wave_t = 0
        t = QTimer(self); t.timeout.connect(self._step); t.start(33)  # ~30fps

    def set_state(self, s: str):
        self._state = s; self.update()

    def push_wave(self):
        """Animate waveform when speaking/listening."""
        import random as _r
        self._wave = [_r.random() for _ in range(32)]

    def _step(self):
        self._a = (self._a + (3 if self._state == "thinking" else 1.5)) % 360
        self._p += 0.05 * self._pd
        if self._p >= 1 or self._p <= 0: self._pd *= -1
        if self._state in ("listening", "speaking"):
            self._wave_t += 1
            if self._wave_t % 4 == 0:
                import random as _r
                self._wave = [max(0.05, w * 0.85 + _r.random() * 0.3) for w in self._wave]
        else:
            self._wave = [max(0.05, w * 0.92) for w in self._wave]
        self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx = cy = 130; a = self._a; pv = self._p

        sc = {
            "standby":  QColor(0, 160, 220),
            "listening": QColor(0, 255, 120),
            "thinking": QColor(255, 160, 0),
            "speaking": QColor(160, 80, 255),
            "writing":  QColor(255, 200, 0),
        }.get(self._state, QColor(0, 160, 220))
        r, g, b = sc.red(), sc.green(), sc.blue()

        # ── Background radial glow ─────────────────────────────
        bg = QRadialGradient(cx, cy, 120)
        bg.setColorAt(0, QColor(r,g,b, int(20 + pv*15)))
        bg.setColorAt(0.6, QColor(r,g,b, 5))
        bg.setColorAt(1, QColor(0,0,0,0))
        p.setBrush(bg); p.setPen(Qt.NoPen)
        p.drawEllipse(10, 10, 240, 240)

        # ── Outer dashed data ring ─────────────────────────────
        pen = QPen(QColor(r,g,b, 35), 1, Qt.DashLine)
        pen.setDashPattern([4,6]); p.setPen(pen); p.setBrush(Qt.NoBrush)
        p.drawEllipse(6, 6, 248, 248)

        # ── Tick marks (36 total, major at 90°) ───────────────
        for i in range(36):
            rad = _M.radians(i * 10 + a * 0.2)
            r1 = 118; r2 = 112 if i % 9 == 0 else (115 if i % 3 == 0 else 116)
            al = 80 if i % 9 == 0 else (45 if i % 3 == 0 else 22)
            p.setPen(QPen(QColor(r,g,b,al), 1 if i % 3 == 0 else 1))
            p.drawLine(int(cx+_M.cos(rad)*r1), int(cy+_M.sin(rad)*r1),
                       int(cx+_M.cos(rad)*r2), int(cy+_M.sin(rad)*r2))

        # ── Rotating arc segments ─────────────────────────────
        for i, (al, span, w) in enumerate([(200,100,3),(120,65,2),(55,40,1),(25,22,1)]):
            p.setPen(QPen(QColor(r,g,b,al), w))
            p.setBrush(Qt.NoBrush)
            start = int((a + i*80) % 360 * 16)
            p.drawArc(12, 12, 236, 236, start, span*16)

        # ── Counter-rotating inner ring ────────────────────────
        for i in range(4):
            p.setPen(QPen(QColor(r,g,b,60), 1))
            start = int((-a*1.5 + i*90) % 360 * 16)
            p.drawArc(42, 42, 176, 176, start, 30*16)

        # ── Helmet outline (Iron Man face shape) ──────────────
        helm_col = QColor(r,g,b,45)
        p.setPen(QPen(helm_col, 1))
        p.setBrush(Qt.NoBrush)
        # Helmet silhouette using polygon
        pts = [
            QPoint(cx, cy-72),       # top center
            QPoint(cx+38, cy-58),    # top right
            QPoint(cx+52, cy-20),    # right cheek
            QPoint(cx+48, cy+18),    # right jaw
            QPoint(cx+28, cy+42),    # chin right
            QPoint(cx, cy+52),       # chin center
            QPoint(cx-28, cy+42),    # chin left
            QPoint(cx-48, cy+18),    # left jaw
            QPoint(cx-52, cy-20),    # left cheek
            QPoint(cx-38, cy-58),    # top left
        ]
        p.drawPolygon(*pts)

        # Eye slits (Iron Man eyes)
        eye_col = QColor(r, g, b, int(100 + pv*80))
        p.setPen(Qt.NoPen)
        p.setBrush(eye_col)
        # Left eye
        p.drawRoundedRect(cx-34, cy-18, 24, 8, 3, 3)
        # Right eye
        p.drawRoundedRect(cx+10, cy-18, 24, 8, 3, 3)

        # Nose/faceplate line
        p.setPen(QPen(QColor(r,g,b,30), 1))
        p.drawLine(cx, cy-10, cx, cy+20)
        p.drawLine(cx-15, cy+20, cx+15, cy+20)

        # ── 8 Orbit dots on middle ring ───────────────────────
        for i in range(8):
            ang = _M.radians(a*1.2 + i*45)
            dx = cx + _M.cos(ang)*88; dy = cy + _M.sin(ang)*88
            al = int(70 + pv*130*(1 if i%2==0 else 0.4))
            sz = 5 if i%2==0 else 3
            p.setPen(Qt.NoPen); p.setBrush(QColor(r,g,b,al))
            p.drawEllipse(int(dx)-sz//2, int(dy)-sz//2, sz, sz)

        # ── Sweep line ────────────────────────────────────────
        sw = _M.radians(a*0.9)
        p.setPen(QPen(QColor(r,g,b,50), 1))
        p.drawLine(cx, cy, int(cx+_M.cos(sw)*100), int(cy+_M.sin(sw)*100))

        # ── Voice waveform ring ───────────────────────────────
        if self._state in ("listening","speaking"):
            for i, amp in enumerate(self._wave):
                ang = _M.radians(i * (360/32))
                r_in = 62; r_out = r_in + amp * 16
                al = int(60 + amp*120)
                p.setPen(QPen(QColor(r,g,b,al), 1.5))
                p.drawLine(
                    int(cx+_M.cos(ang)*r_in), int(cy+_M.sin(ang)*r_in),
                    int(cx+_M.cos(ang)*r_out), int(cy+_M.sin(ang)*r_out)
                )

        # ── Arc reactor core ─────────────────────────────────
        cs = int(28 + pv*8)
        cg = QRadialGradient(cx, cy, cs)
        cg.setColorAt(0, QColor(230,250,255, int(235+pv*20)))
        cg.setColorAt(0.4, QColor(r,g,b, int(170+pv*50)))
        cg.setColorAt(0.85, QColor(r,g,b,30))
        cg.setColorAt(1, QColor(0,0,0,0))
        p.setPen(Qt.NoPen); p.setBrush(cg)
        p.drawEllipse(cx-cs, cy-cs, cs*2, cs*2)
        # Hard center dot
        p.setBrush(QColor(240,255,255,255))
        p.drawEllipse(cx-5, cy-5, 10, 10)

        # ── JARVIS text ───────────────────────────────────────
        f = QFont("Courier New", 9, QFont.Bold); p.setFont(f)
        al = int(130 + pv*80)
        p.setPen(QColor(r,g,b,50)); p.drawText(107, 152, "JARVIS")
        p.setPen(QColor(230,250,255,al)); p.drawText(106, 151, "JARVIS")
        # State label
        f2 = QFont("Courier New", 7); p.setFont(f2)
        state_txt = self._state.upper()
        p.setPen(QColor(r,g,b,int(80+pv*60)))
        p.drawText(cx - len(state_txt)*3, cy+68, state_txt)

        p.end()


# ════════════════════════════════════════════════════════════════
#  MAIN UI
# ════════════════════════════════════════════════════════════════
class JarvisUI(QMainWindow):
    update_status_signal   = pyqtSignal(str, str)
    add_message_signal     = pyqtSignal(str, str, bool)
    process_command_signal = pyqtSignal(str)
    stop_listening_signal  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_listening    = False
        self.continuous_mode = False
        self._drag_pos       = None
        self.setup_signals()
        self.init_ui()
        init_recognizer()

    def setup_signals(self):
        self.update_status_signal.connect(self.update_status)
        self.add_message_signal.connect(self.add_message)
        self.process_command_signal.connect(self.process_command)
        self.stop_listening_signal.connect(self.stop_listening)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(e.globalPos() - self._drag_pos)

    def init_ui(self):
        self.setWindowTitle("JARVIS")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        scr = QApplication.primaryScreen().geometry()
        W, H = 1480, 880
        self.setGeometry((scr.width()-W)//2, (scr.height()-H)//2, W, H)

        root = QFrame(); root.setObjectName("R")
        root.setStyleSheet(f"""
            #R {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {_BG}, stop:0.5 {_BG2}, stop:1 {_BG});
                 border-radius:16px; border:1px solid {_P}35); }}
        """)
        self.setCentralWidget(root)
        vl = QVBoxLayout(root); vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        vl.addWidget(self._titlebar())
        body = QHBoxLayout(); body.setContentsMargins(10,8,10,8); body.setSpacing(8)
        body.addWidget(self._left_panel(),   0)
        body.addWidget(self._center_panel(), 1)
        body.addWidget(self._right_panel(),  0)
        vl.addLayout(body)
        vl.addWidget(self._statusbar())

        QTimer(self).singleShot(0, lambda: (
            setattr(self, '_time_timer', QTimer(self)),
            self._time_timer.timeout.connect(self._tick_time),
            self._time_timer.start(1000),
            self._tick_time(),
            QTimer.singleShot(500, self._tick_metrics)
        ))
        self.add_message_signal.emit("JARVIS",
            "Systems online. Iron Man edition active. How can I assist you, sir?", False)

    # ─── TITLE BAR ──────────────────────────────────────────────
    def _titlebar(self):
        bar = QFrame(); bar.setFixedHeight(50)
        bar.setStyleSheet(f"""QFrame{{background:rgba(0,10,30,210);
            border-bottom:1px solid {_P}28);
            border-top-left-radius:16px;border-top-right-radius:16px;}}""")
        lay = QHBoxLayout(bar); lay.setContentsMargins(18,0,14,0)

        logo = QLabel("⚡ J.A.R.V.I.S")
        logo.setStyleSheet(f"color:{_C};font-size:18px;font-weight:bold;font-family:'Courier New';letter-spacing:4px;")
        lay.addWidget(logo)

        sub = QLabel("  Iron Man Edition  v3.0  •  Phi-3 Neural AI")
        sub.setStyleSheet(f"color:{_P}50);font-size:9px;letter-spacing:2px;")
        lay.addWidget(sub)
        lay.addStretch()

        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color:{_C};font-size:15px;font-family:'Courier New';margin-right:18px;")
        lay.addWidget(self.time_label)

        self.ai_dot = QLabel("● AI ONLINE")
        self.ai_dot.setStyleSheet(f"color:{_G};font-size:10px;font-weight:bold;margin-right:16px;")
        lay.addWidget(self.ai_dot)

        for txt, fn, col in [("─", self.showMinimized, _C), ("□", self._tog_max, _C), ("✕", self.close_app, _RD)]:
            b = QPushButton(txt); b.setFixedSize(30,30)
            b.clicked.connect(fn)
            b.setStyleSheet(f"""QPushButton{{background:transparent;color:{col};
                border:1px solid {col};border-radius:15px;font-size:13px;font-weight:bold;}}
                QPushButton:hover{{background:{col};color:#000;}}""")
            lay.addWidget(b)
        return bar

    # ─── LEFT PANEL ─────────────────────────────────────────────
    def _left_panel(self):
        panel = QFrame(); panel.setFixedWidth(280)
        panel.setStyleSheet(f"""QFrame{{background:rgba(3,10,25,190);
            border:1px solid {_P}22);border-radius:12px;}}""")
        lay = QVBoxLayout(panel); lay.setContentsMargins(12,14,12,14); lay.setSpacing(10)

        self.hologram = IronManHologram()
        lay.addWidget(self.hologram, alignment=Qt.AlignCenter)

        self.state_lbl = QLabel("● STANDBY")
        self.state_lbl.setAlignment(Qt.AlignCenter)
        self.state_lbl.setStyleSheet(f"color:{_RD};font-size:12px;font-weight:bold;letter-spacing:4px;")
        lay.addWidget(self.state_lbl)

        self.mic_btn = QPushButton("🎤   ACTIVATE JARVIS")
        self.mic_btn.setFixedHeight(42)
        self.mic_btn.clicked.connect(self.toggle_listening)
        self.mic_btn.setStyleSheet(f"""QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(0,130,220,200),stop:1 rgba(0,70,180,200));
            color:white;border-radius:21px;font-size:12px;font-weight:bold;border:none;}}
            QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(0,210,100,200),stop:1 rgba(0,140,60,200));}}""")
        lay.addWidget(self.mic_btn)

        # Metrics
        mf = QFrame()
        mf.setStyleSheet(f"QFrame{{background:rgba(0,0,0,70);border:1px solid {_P}18);border-radius:8px;}}")
        ml = QVBoxLayout(mf); ml.setContentsMargins(10,8,10,8); ml.setSpacing(3)
        hdr = QLabel("◈  SYSTEM MONITOR")
        hdr.setStyleSheet(f"color:{_C};font-size:8px;font-weight:bold;letter-spacing:3px;")
        ml.addWidget(hdr)
        for attr, txt, col in [
            ("cpu_lbl",  "⚡ CPU: --",     _C),
            ("ram_lbl",  "🧠 RAM: --",     "#00bbff"),
            ("bat_lbl",  "🔋 Battery: --", _G),
            ("disk_lbl", "💾 Disk: --",    _AM),
            ("net_lbl",  "🌐 Net: --",     "#cc88ff"),
        ]:
            lb = QLabel(txt); lb.setStyleSheet(f"color:{col};font-size:10px;padding:1px 0;")
            ml.addWidget(lb); setattr(self, attr, lb)
        lay.addWidget(mf)
        QTimer.singleShot(600, self._tick_metrics)
        lay.addStretch()
        return panel

    # ─── CENTER PANEL ────────────────────────────────────────────
    def _center_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"""QFrame{{background:rgba(3,10,25,190);
            border:1px solid {_P}22);border-radius:12px;}}""")
        lay = QVBoxLayout(panel); lay.setContentsMargins(10,12,10,10); lay.setSpacing(6)

        hdr = QLabel("⚡  COMMAND MATRIX")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setStyleSheet(f"""color:{_C};font-size:11px;font-weight:bold;letter-spacing:4px;
            background:{_P}12);border-radius:7px;padding:5px;border:1px solid {_P}22);""")
        lay.addWidget(hdr)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""QScrollArea{background:transparent;border:none;}
            QScrollBar:vertical{background:rgba(0,0,0,0);width:4px;}
            QScrollBar::handle:vertical{background:rgba(0,180,255,55);border-radius:2px;}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}""")
        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        grid = QVBoxLayout(inner); grid.setSpacing(7); grid.setContentsMargins(2,2,2,2)

        cats = [
            ("🖥️  SYSTEM", _AM, [
                ("⏰ Time","time"),("📅 Date","date"),("🔋 Battery","battery status"),
                ("💻 System Info","system info"),("📸 Screenshot","screenshot"),
                ("💾 Disk Space","disk space"),("🌐 My IP","what is my ip"),
                ("⏱ Uptime","uptime"),("📋 Clipboard","read clipboard"),
                ("🔒 Lock Screen","lock screen"),("🔁 Restart","restart computer"),
                ("💡 Random Fact","fact"),("📋 Briefing","briefing"),
                ("🔐 Password","generate password"),
            ]),
            ("🔊  VOLUME & DISPLAY", _G, [
                ("🔊 Vol Up","volume up"),("🔉 Vol Down","volume down"),
                ("🔇 Mute","mute"),("🔔 Unmute","unmute"),
                ("☀ Bright Up","increase brightness"),("🌙 Bright Down","decrease brightness"),
            ]),
            ("📱  APPS", "#aa55ff", [
                ("🌐 Chrome","open chrome"),("📊 Excel","open excel"),
                ("📄 Word","open word"),("📽 PowerPoint","open powerpoint"),
                ("📝 Notepad","open notepad"),("🧮 Calculator","open calculator"),
                ("📁 Explorer","open file explorer"),("⚙ Settings","open settings"),
                ("🎵 Spotify","open spotify"),("▶ VLC","open vlc"),
                ("💻 VS Code","open vs code"),("🎮 Discord","open discord"),
                ("📷 Camera","take photo"),("🎥 Record 10s","record video 10 seconds"),
            ]),
            ("🎵  MEDIA", "#ff5577", [
                ("🎵 Play Spotify","play song on spotify"),
                ("▶ Play YouTube","play song on youtube"),
                ("⏸ Pause","pause media"),("⏹ Stop","stop media"),
                ("⏭ Next Track","next track"),("⏮ Prev Track","previous track"),
                ("😂 Joke","joke"),("💪 Motivate","motivate me"),
            ]),
            ("📂  FILES", "#55aaff", [
                ("📂 Downloads","open downloads"),("🖥 Desktop","open desktop files"),
                ("📁 Documents","open documents"),("🔍 Find File","search file jarvis"),
                ("📄 Open File","open file readme"),
            ]),
            ("✍️  WRITE → NOTEPAD", "#44ffcc", [
                ("🐍 Python Code","write python code for bubble sort"),
                ("🌐 HTML Page","write html for a login page"),
                ("☕ Java Code","write java code for linked list"),
                ("📝 Essay","write essay on artificial intelligence"),
                ("📧 Email","write email to professor about project"),
                ("📄 Letter","write letter to manager requesting leave"),
                ("📖 Story","write story about space exploration"),
                ("📄 Resume","write resume for software engineer"),
                ("📋 Report","write report on project progress"),
            ]),
            ("💬  WHATSAPP", _G, [
                ("📱 Open WhatsApp","open whatsapp"),
                ("💬 Msg Mom","send message to mom hello"),
                ("💬 Msg Dad","send message to dad good morning"),
                ("👥 My Contacts","show contacts"),
            ]),
            ("🤖  AI CHAT", _C, [
                ("🤖 Chat","who is elon musk"),
                ("🧠 Explain AI","explain artificial intelligence"),
                ("💡 Fun Fact","tell me a fun fact"),
                ("🪙 Flip Coin","flip a coin"),
                ("🎲 Roll Dice","roll a dice"),
                ("❓ Help","what can you do"),
                ("🚪 Exit","exit"),
            ]),
        ]

        for title, color, cmds in cats:
            grid.addWidget(self._make_cat(title, color, cmds))
        grid.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll)
        return panel

    def _make_cat(self, title, color, cmds):
        grp = QFrame()
        grp.setStyleSheet(f"""QFrame{{background:rgba(0,0,0,55);
            border:1px solid rgba(0,180,255,18);border-left:2px solid {color};border-radius:8px;}}""")
        lay = QVBoxLayout(grp); lay.setContentsMargins(8,6,8,8); lay.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(f"color:{color};font-size:9px;font-weight:bold;letter-spacing:3px;padding:1px 0;")
        lay.addWidget(t)
        row = None
        for i,(lbl,cmd) in enumerate(cmds):
            if i%4==0:
                rw = QWidget(); rw.setStyleSheet("background:transparent;")
                row = QHBoxLayout(rw); row.setContentsMargins(0,0,0,0); row.setSpacing(3)
                lay.addWidget(rw)
            b = QPushButton(lbl); b.setFixedHeight(27)
            b.clicked.connect(lambda _,c=cmd: self.send_command(c))
            b.setStyleSheet(_btn(color, 27))
            row.addWidget(b)
        rem = len(cmds)%4
        if rem and row:
            for _ in range(4-rem):
                row.addWidget(QLabel(""),1)
        return grp

    # ─── RIGHT PANEL (chat) ──────────────────────────────────────
    def _right_panel(self):
        panel = QFrame(); panel.setFixedWidth(330)
        panel.setStyleSheet(f"""QFrame{{background:rgba(3,10,25,190);
            border:1px solid {_P}22);border-radius:12px;}}""")
        lay = QVBoxLayout(panel); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        hdr = QLabel("◈  SECURE CHANNEL")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setStyleSheet(f"""color:{_C};font-size:9px;font-weight:bold;letter-spacing:4px;
            background:{_P}10);border-radius:6px;padding:5px;border:1px solid {_P}20);""")
        lay.addWidget(hdr)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(f"""QTextEdit{{
            background:rgba(0,4,15,160);border:1px solid {_P}18);border-radius:8px;
            color:#a8d8f0;font-family:'Segoe UI';font-size:11px;padding:10px;}}
            QScrollBar:vertical{{background:transparent;width:4px;}}
            QScrollBar::handle:vertical{{background:{_P}50);border-radius:2px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}""")
        lay.addWidget(self.chat_area)

        # Input
        inf = QFrame()
        inf.setStyleSheet(f"QFrame{{background:rgba(0,8,25,180);border:1px solid {_P}30);border-radius:8px;}}")
        il = QVBoxLayout(inf); il.setContentsMargins(10,5,10,6); il.setSpacing(2)
        il.addWidget(QLabel("› TERMINAL", styleSheet=f"color:{_C};font-size:8px;font-weight:bold;letter-spacing:2px;"))
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type command or question...")
        self.input_box.setStyleSheet(f"QLineEdit{{background:transparent;border:none;color:{_C};font-size:12px;padding:2px;}}")
        self.input_box.returnPressed.connect(self.process_text_command)
        il.addWidget(self.input_box)
        lay.addWidget(inf)

        # Quick buttons
        qr = QHBoxLayout(); qr.setSpacing(4)
        for txt,cmd,tip in [("⏰","time","Time"),("☁","weather in hyderabad","Weather"),
                             ("😂","joke","Joke"),("📸","screenshot","Screenshot"),
                             ("💡","fact","Fact"),("🔋","battery status","Battery")]:
            b = QPushButton(txt); b.setFixedSize(34,34); b.setToolTip(tip)
            b.clicked.connect(lambda _,c=cmd: self.send_command(c))
            b.setStyleSheet(f"""QPushButton{{background:{_P}14);color:{_C};
                border:1px solid {_P}28);border-radius:17px;font-size:14px;}}
                QPushButton:hover{{background:{_P}35);}}""")
            qr.addWidget(b)
        lay.addLayout(qr)
        return panel

    # ─── STATUS BAR ─────────────────────────────────────────────
    def _statusbar(self):
        bar = QFrame(); bar.setFixedHeight(34)
        bar.setStyleSheet(f"""QFrame{{background:rgba(0,8,25,210);
            border-top:1px solid {_P}18);
            border-bottom-left-radius:16px;border-bottom-right-radius:16px;}}""")
        lay = QHBoxLayout(bar); lay.setContentsMargins(18,0,18,0)
        self.status_text = QLabel("STATUS: READY")
        self.status_text.setStyleSheet(f"color:{_G};font-size:9px;font-weight:bold;letter-spacing:3px;")
        lay.addWidget(self.status_text)
        lay.addStretch()
        lay.addWidget(QLabel("JARVIS v3.0  •  Iron Man Edition  •  Phi-3 Neural  •  edge-tts Christopher",
            styleSheet="color:rgba(0,180,255,35);font-size:8px;letter-spacing:1px;"))
        return bar

    # ─── TIMERS ─────────────────────────────────────────────────
    def _tick_time(self):
        self.time_label.setText(datetime.datetime.now().strftime("%I:%M:%S %p"))

    def _tick_metrics(self):
        try:
            self.cpu_lbl.setText(f"⚡ CPU: {psutil.cpu_percent(interval=None):.0f}%")
            ram = psutil.virtual_memory()
            self.ram_lbl.setText(f"🧠 RAM: {ram.percent:.0f}%  ({ram.used//(1024**2)} MB)")
            bat = psutil.sensors_battery()
            self.bat_lbl.setText(f"{'🔌' if bat and bat.power_plugged else '🔋'} "
                                  f"{'Battery: '+str(round(bat.percent))+'%' if bat else 'Desktop PC'}")
            try: dk = psutil.disk_usage("C:\\")
            except: dk = psutil.disk_usage("/")
            self.disk_lbl.setText(f"💾 {dk.free//(1024**3)}GB free / {dk.total//(1024**3)}GB")
            net = psutil.net_io_counters()
            self.net_lbl.setText(f"🌐 ↑{net.bytes_sent//(1024**2)}MB ↓{net.bytes_recv//(1024**2)}MB")
        except: pass
        QTimer.singleShot(3000, self._tick_metrics)

    # ─── SIGNALS ────────────────────────────────────────────────
    def _tog_max(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    @pyqtSlot(str, str)
    def update_status(self, status: str, color: str):
        self.status_text.setText(f"STATUS: {status}")
        s = status.upper()
        for key,(lbl,col,state) in {
            "LISTENING": ("● LISTENING...", _G,  "listening"),
            "THINKING":  ("● THINKING...",  _AM, "thinking"),
            "GENERATING":("● GENERATING...",_AM, "writing"),
            "WRITING":   ("● WRITING...",   _AM, "writing"),
            "SPEAKING":  ("● SPEAKING",     _PU, "speaking"),
            "PROCESSING":("● PROCESSING...",_AM, "thinking"),
        }.items():
            if key in s:
                self.state_lbl.setText(lbl)
                self.state_lbl.setStyleSheet(f"color:{col};font-size:12px;font-weight:bold;letter-spacing:4px;")
                self.hologram.set_state(state)
                self.mic_btn.setText("🔴   DEACTIVATE" if "LISTEN" in s else "🎤   ACTIVATE JARVIS")
                return
        self.state_lbl.setText("● STANDBY")
        self.state_lbl.setStyleSheet(f"color:{_RD};font-size:12px;font-weight:bold;letter-spacing:4px;")
        self.hologram.set_state("standby")
        self.mic_btn.setText("🎤   ACTIVATE JARVIS")

    @pyqtSlot(str, str, bool)
    def add_message(self, sender: str, msg: str, is_sys: bool = False):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if sender == "JARVIS":
            self.chat_area.append(
                f'<span style="color:#007799">[{ts}]</span> '
                f'<span style="color:#00ccff;font-weight:bold">🤖 JARVIS:</span> '
                f'<span style="color:#b8e4ff">{msg}</span>')
        else:
            self.chat_area.append(
                f'<span style="color:#007799">[{ts}]</span> '
                f'<span style="color:#ffcc33;font-weight:bold">👤 YOU:</span> '
                f'<span style="color:#ffe8a0">{msg}</span>')
        self.chat_area.ensureCursorVisible()

    def send_command(self, cmd: str):
        self.add_message_signal.emit("You", cmd, False)
        self.process_command_signal.emit(cmd)

    def toggle_listening(self):
        self.start_listening() if not self.is_listening else self.stop_listening()

    def start_listening(self):
        self.is_listening = True; self.continuous_mode = True
        self.update_status_signal.emit("CONTINUOUS LISTENING...", _G)
        self.hologram.set_state("listening")
        threading.Thread(target=self.continuous_listen, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False; self.continuous_mode = False
        self.update_status_signal.emit("READY", _G)

    def continuous_listen(self):
        while self.is_listening and self.continuous_mode:
            try:
                with sr.Microphone() as src:
                    recognizer.adjust_for_ambient_noise(src, 0.3)
                    try:
                        audio = recognizer.listen(src, timeout=4, phrase_time_limit=10)
                        query = recognizer.recognize_google(audio, language="en-IN")
                        if query and query.strip():
                            if "stop listening" in query.lower():
                                self.stop_listening_signal.emit(); break
                            self.add_message_signal.emit("You", query, False)
                            self.process_command_signal.emit(query.lower().strip())
                    except sr.WaitTimeoutError: time.sleep(0.1)
                    except sr.UnknownValueError: time.sleep(0.1)
                    except Exception: time.sleep(0.3)
            except Exception: time.sleep(0.5)

    def process_text_command(self):
        cmd = self.input_box.text().strip()
        if cmd:
            self.add_message_signal.emit("You", cmd, False)
            self.input_box.clear()
            self.process_command_signal.emit(cmd)

    @pyqtSlot(str)
    def process_command(self, cmd: str):
        self.update_status_signal.emit("PROCESSING...", _AM)
        threading.Thread(target=self._exec, args=(cmd,), daemon=True).start()

    def _exec(self, cmd: str):
        global jarvis_ui; jarvis_ui = self
        handle_command(cmd)
        if not self.continuous_mode:
            self.update_status_signal.emit("READY", _G)

    def close_app(self):
        self.is_listening = False; self.continuous_mode = False; self.close()


class ReminderThread(QThread):
    reminder_triggered = pyqtSignal(str)
    def run(self):
        while True: time.sleep(1)


# ════════════════════════════════════════════════════════════════
#  JARVIS LOADING SCREEN
# ════════════════════════════════════════════════════════════════
class JarvisLoader(QWidget):
    """Full-screen animated Iron Man boot sequence loading screen."""
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._angle   = 0.0
        self._pulse   = 0.0
        self._pd      = 1
        self._step_idx= 0
        self._alpha   = 0       # fade-in
        self._closing = False
        self._bar     = 0.0     # progress 0-100
        self._dots    = 0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        scr = QApplication.primaryScreen().geometry()
        self.setGeometry(scr)   # full screen

        # Dramatic boot sequence messages
        self._messages = [
            ("POWER CORE INITIALIZING",          "#00d4ff"),
            ("ARC REACTOR ONLINE",               "#00ccff"),
            ("LOADING JARVIS v3.0 KERNEL",       "#00bbff"),
            ("CALIBRATING NEURAL PROCESSORS",    "#00ff88"),
            ("ACTIVATING SPEECH ENGINE",         "#00ff88"),
            ("LOADING CHRISTOPHER NEURAL VOICE", "#44ffaa"),
            ("CONNECTING TO OLLAMA AI ENGINE",   "#ffaa00"),
            ("LOADING PHI-3 LANGUAGE MODEL",     "#ffcc44"),
            ("WARMING UP AI INFERENCE",          "#ffbb22"),
            ("SCANNING HARDWARE DEVICES",        "#aa55ff"),
            ("ACTIVATING SYSTEM MONITORS",       "#cc77ff"),
            ("LOADING SKILL MODULES  [6/6]",     "#ff6644"),
            ("CONFIGURING IRON MAN HUD",         "#ff8855"),
            ("RUNNING SYSTEM DIAGNOSTICS",       "#ff5533"),
            ("ALL SYSTEMS OPERATIONAL ✓",        "#00ff88"),
        ]
        self._shown_msgs = []

        # Startup beep sound — reactor powering up
        QTimer.singleShot(300, self._play_boot_sound)

        # 33ms = 30fps animation
        self._t = QTimer(self)
        self._t.timeout.connect(self._animate)
        self._t.start(33)

        # Stagger boot messages for dramatic effect
        for i, (msg, col) in enumerate(self._messages):
            delay = 500 + i * 300
            QTimer.singleShot(delay, lambda m=msg, c=col: self._show_msg(m, c))

        self._bar_t = QTimer(self)
        self._bar_t.timeout.connect(self._tick_bar)
        self._bar_t.start(33)

        total = 500 + len(self._messages) * 300 + 800
        QTimer.singleShot(total, self._begin_close)

    def _play_boot_sound(self):
        """Iron Man reactor power-up sound using Windows Beep API."""
        import ctypes as _c2
        def _beeps():
            try:
                for freq, dur in [(330,60),(440,60),(554,60),(659,80),(880,100),(1108,180),(880,60),(1108,250)]:
                    _c2.windll.kernel32.Beep(freq, dur)
                    time.sleep(0.02)
            except: pass
        threading.Thread(target=_beeps, daemon=True).start()

    def _show_msg(self, msg, col):
        self._shown_msgs.append((msg, col))
        # Subtle tick beep per message
        try:
            import ctypes as _c3
            threading.Thread(target=lambda: _c3.windll.kernel32.Beep(900, 25), daemon=True).start()
        except: pass
        self.update()

    def _tick_bar(self):
        target = min(100.0, (len(self._shown_msgs) / len(self._messages)) * 100)
        self._bar += (target - self._bar) * 0.08
        self.update()

    def _animate(self):
        self._angle = (self._angle + 2.5) % 360
        self._pulse += 0.05 * self._pd
        if self._pulse >= 1 or self._pulse <= 0: self._pd *= -1
        self._dots   = (self._dots + 1) % 90
        if self._alpha < 255: self._alpha = min(255, self._alpha + 12)
        self.update()

    def _begin_close(self):
        self._closing = True
        self._close_alpha = 255
        ct = QTimer(self)
        ct.timeout.connect(self._fade_out)
        ct.start(16)
        self._close_timer = ct

    def _fade_out(self):
        self._close_alpha -= 14
        if self._close_alpha <= 0:
            self._close_timer.stop()
            self.finished.emit()
            self.close()
        self.update()

    def paintEvent(self, event):
        import math as _m
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W = self.width(); H = self.height()
        cx = W // 2;   cy = H // 2 - 80
        al_main = self._close_alpha if self._closing else self._alpha

        # ── Full background ──────────────────────────────────
        p.fillRect(0, 0, W, H, QColor(2, 5, 12, al_main))

        # ── Subtle grid lines ────────────────────────────────
        pen = QPen(QColor(0, 180, 255, int(8 * al_main/255))); pen.setWidth(1)
        p.setPen(pen)
        for x in range(0, W, 60):
            p.drawLine(x, 0, x, H)
        for y in range(0, H, 60):
            p.drawLine(0, y, W, y)

        # ── Outer glow halo ──────────────────────────────────
        rad = 260 + int(self._pulse * 15)
        halo = QRadialGradient(cx, cy, rad)
        halo.setColorAt(0,   QColor(0, 180, 255, int(18 * al_main/255)))
        halo.setColorAt(0.5, QColor(0, 80,  200, int(8  * al_main/255)))
        halo.setColorAt(1,   QColor(0,  0,    0, 0))
        p.setBrush(halo); p.setPen(Qt.NoPen)
        p.drawEllipse(cx-rad, cy-rad, rad*2, rad*2)

        # ── Outer ring + ticks ───────────────────────────────
        a = self._angle
        for i in range(48):
            ang = _m.radians(i * 7.5 + a * 0.3)
            r1, r2 = 235, 225 if i % 6 == 0 else 230
            alf = int((100 if i%6==0 else 45) * al_main/255)
            p.setPen(QPen(QColor(0, 200, 255, alf), 1))
            p.drawLine(int(cx+_m.cos(ang)*r1), int(cy+_m.sin(ang)*r1),
                       int(cx+_m.cos(ang)*r2), int(cy+_m.sin(ang)*r2))

        p.setPen(QPen(QColor(0,180,255, int(40*al_main/255)), 1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(cx-236, cy-236, 472, 472)

        # ── 4 spinning arcs ──────────────────────────────────
        for i,(alf,span,w) in enumerate([(220,110,4),(140,75,2),(70,45,2),(30,25,1)]):
            c = QColor(0, 200+i*10, 255, int(alf*al_main/255))
            p.setPen(QPen(c, w)); p.setBrush(Qt.NoBrush)
            start = int((a + i*80) % 360 * 16)
            p.drawArc(cx-200, cy-200, 400, 400, start, span*16)

        # ── Counter-rotating ring ────────────────────────────
        for i in range(4):
            p.setPen(QPen(QColor(0,180,255, int(55*al_main/255)), 1))
            s = int((-a*1.5 + i*90) % 360 * 16)
            p.drawArc(cx-155, cy-155, 310, 310, s, 30*16)

        # ── Orbit dots ───────────────────────────────────────
        for i in range(8):
            ang = _m.radians(a*1.2 + i*45)
            dx = cx + _m.cos(ang)*178; dy = cy + _m.sin(ang)*178
            alf2 = int((80+self._pulse*130*(1 if i%2==0 else 0.4))*al_main/255)
            sz = 6 if i%2==0 else 4
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 220, 255, alf2))
            p.drawEllipse(int(dx)-sz//2, int(dy)-sz//2, sz, sz)

        # ── Sweep line ───────────────────────────────────────
        sw = _m.radians(a * 0.8)
        p.setPen(QPen(QColor(0, 200, 255, int(60*al_main/255)), 1))
        p.drawLine(cx, cy, int(cx+_m.cos(sw)*195), int(cy+_m.sin(sw)*195))

        # ── Helmet outline ───────────────────────────────────
        helm_col = QColor(0, 180, 255, int(55*al_main/255))
        p.setPen(QPen(helm_col, 1)); p.setBrush(Qt.NoBrush)
        pts = [QPoint(cx,cy-110), QPoint(cx+58,cy-88), QPoint(cx+80,cy-30),
               QPoint(cx+74,cy+28), QPoint(cx+43,cy+65), QPoint(cx,cy+80),
               QPoint(cx-43,cy+65), QPoint(cx-74,cy+28), QPoint(cx-80,cy-30),
               QPoint(cx-58,cy-88)]
        p.drawPolygon(*pts)
        # Eyes
        eye_a = int((130+self._pulse*90)*al_main/255)
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 200, 255, eye_a))
        p.drawRoundedRect(cx-50, cy-26, 36, 12, 4, 4)
        p.drawRoundedRect(cx+14, cy-26, 36, 12, 4, 4)
        p.setBrush(QColor(0,180,255, int(25*al_main/255)))
        p.drawLine(cx, cy-10, cx, cy+30); p.drawLine(cx-22,cy+30,cx+22,cy+30)

        # ── Core glow ────────────────────────────────────────
        cs = int(42 + self._pulse*12)
        cg = QRadialGradient(cx, cy, cs)
        cg.setColorAt(0, QColor(230,250,255, int((235+self._pulse*20)*al_main/255)))
        cg.setColorAt(0.45, QColor(0,200,255, int(180*al_main/255)))
        cg.setColorAt(1, QColor(0,0,0,0))
        p.setPen(Qt.NoPen); p.setBrush(cg)
        p.drawEllipse(cx-cs, cy-cs, cs*2, cs*2)
        p.setBrush(QColor(240,255,255,int(255*al_main/255)))
        p.drawEllipse(cx-7, cy-7, 14, 14)

        # ── JARVIS title ─────────────────────────────────────
        title_y = cy + 300
        f = QFont("Courier New", 38, QFont.Bold); p.setFont(f)
        p.setPen(QColor(0, 180, 255, int(30*al_main/255)))
        p.drawText(cx-152, title_y+2, "J.A.R.V.I.S")
        p.setPen(QColor(0, 220, 255, int(200*al_main/255)))
        p.drawText(cx-153, title_y, "J.A.R.V.I.S")

        f2 = QFont("Courier New", 12); p.setFont(f2)
        p.setPen(QColor(0, 180, 255, int(110*al_main/255)))
        p.drawText(cx-178, title_y+28, "Just A Rather Very Intelligent System  •  v3.0")

        f3 = QFont("Courier New", 10); p.setFont(f3)
        p.setPen(QColor(0, 160, 255, int(70*al_main/255)))
        p.drawText(cx-148, title_y+50, "Iron Man Edition  •  Phi-3 Neural AI")

        # ── Progress bar ─────────────────────────────────────
        bar_y = H - 120; bar_w = 600; bar_h = 6
        bar_x = cx - bar_w//2

        # Track
        p.setBrush(QColor(0,0,0,int(120*al_main/255)))
        p.setPen(QPen(QColor(0,180,255,int(40*al_main/255)),1))
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        # Fill
        fill_w = int((self._bar / 100) * bar_w)
        if fill_w > 0:
            grad = QLinearGradient(bar_x, 0, bar_x+fill_w, 0)
            grad.setColorAt(0, QColor(0, 120, 255, int(220*al_main/255)))
            grad.setColorAt(0.5, QColor(0, 200, 255, int(255*al_main/255)))
            grad.setColorAt(1, QColor(0, 255, 200, int(220*al_main/255)))
            p.setBrush(grad); p.setPen(Qt.NoPen)
            p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)

            # Glow tip
            tip_glow = QRadialGradient(bar_x+fill_w, bar_y+bar_h//2, 12)
            tip_glow.setColorAt(0, QColor(0,255,220,int(180*al_main/255)))
            tip_glow.setColorAt(1, QColor(0,0,0,0))
            p.setBrush(tip_glow)
            p.drawEllipse(bar_x+fill_w-12, bar_y-6, 24, 18)

        # Percentage
        f4 = QFont("Courier New", 9, QFont.Bold); p.setFont(f4)
        p.setPen(QColor(0,180,255,int(130*al_main/255)))
        p.drawText(bar_x+bar_w+10, bar_y+bar_h, f"{int(self._bar)}%")

        # ── Boot messages ─────────────────────────────────────
        msg_start_y = H - 105
        f5 = QFont("Courier New", 9); p.setFont(f5)
        for i, (msg, col) in enumerate(self._shown_msgs[-4:]):
            fade = 255 if i == len(self._shown_msgs[-4:])-1 else max(50, 200 - (len(self._shown_msgs[-4:])-1-i)*60)
            fade = int(fade * al_main/255)
            r2,g2,b2 = QColor(col).red(), QColor(col).green(), QColor(col).blue()
            p.setPen(QColor(r2,g2,b2, fade))
            dot_anim = "." * (self._dots//30 + 1) if i == len(self._shown_msgs[-4:])-1 else ""
            p.drawText(bar_x, msg_start_y + i*16, f"[BOOT]  {msg}{dot_anim}")

        p.end()


def main_gui():
    import warnings; warnings.filterwarnings("ignore")
    app = QApplication(sys.argv); app.setStyle("Fusion")
    from PyQt5.QtGui import QPalette
    pal = app.palette()
    for role, col in [(QPalette.Window,QColor(_BG)),(QPalette.WindowText,QColor("#b0d8f0")),
                      (QPalette.Base,QColor(_BG2)),(QPalette.Text,QColor("#b0d8f0")),
                      (QPalette.Button,QColor(_BG2)),(QPalette.ButtonText,QColor("#b0d8f0"))]:
        pal.setColor(role, col)
    app.setPalette(pal)

    # ── Preload check in background ──────────────────────────
    def _check_ollama():
        try: requests.get("http://localhost:11434", timeout=2); print("✅ Ollama online")
        except: print("⚠️  Run: ollama serve")
    threading.Thread(target=_check_ollama, daemon=True).start()

    # ── Show loader first ────────────────────────────────────
    loader = JarvisLoader()
    loader.show()

    global jarvis_ui
    jarvis_ui = None

    def _launch():
        global jarvis_ui
        jarvis_ui = JarvisUI()
        jarvis_ui.show()
        # Speak startup greeting in background after short delay
        threading.Thread(target=_greet, daemon=True).start()

    def _greet():
        time.sleep(0.6)
        h = datetime.datetime.now().hour
        g = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
        speak(f"{g} sir. J.A.R.V.I.S. online. All systems are operational and ready to assist.")

    loader.finished.connect(_launch)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main_gui()