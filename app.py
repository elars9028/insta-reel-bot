from flask import Flask, request
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        if "instagram.com/reel/" in user_message:
            send_message(chat_id, "📥 Lade dein Reel herunter, einen Moment...")

            cleaned_url = clean_url(user_message)
            video_url = download_instagram_reel(cleaned_url)
            if video_url:
                send_video(chat_id, video_url)
            else:
                send_message(chat_id, "❌ Konnte das Video nicht finden. Probiere einen anderen Link.")
        else:
            send_message(chat_id, f"Du hast mir geschickt: {user_message}")

    return "OK", 200

def clean_url(insta_url):
    parsed = urlparse(insta_url)
    clean = parsed._replace(query="")  # Entfernt ?igshid=... oder andere Query-Parameter
    return urlunparse(clean)

def download_instagram_reel(insta_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        session = requests.Session()
        response = session.post(
            "https://saveig.app/api/ajaxSearch",
            headers=headers,
            data={"q": insta_url},
            timeout=10
        )

        json_data = response.json()

        if "medias" in json_data and len(json_data["medias"]) > 0:
            # Nimm das erste gefundene Video
            video_url = json_data["medias"][0].get("url")
            if video_url:
                return video_url

        return None
    except Exception as e:
        print("Fehler beim Download:", e)
        return None

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def send_video(chat_id, video_url):
    url = f"{TELEGRAM_API_URL}/sendVideo"
    payload = {
        "chat_id": chat_id,
        "video": video_url
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run()
