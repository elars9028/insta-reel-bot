from flask import Flask, request
import requests
import os

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_instagram_download_link(url):
    # Beispiel: Dummy-API, später anpassen!
    res = requests.get(f"https://saveig.app/api/ajaxSearch", params={"q": url})
    return res.json().get("links", [{}])[0].get("url", None)

def send_video(chat_id, video_url):
    requests.post(f"{TELEGRAM_API}/sendVideo", data={
        "chat_id": chat_id,
        "video": video_url
    })

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", {})
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")
    if "instagram.com" in text:
        video_url = get_instagram_download_link(text)
        if video_url:
            send_video(chat_id, video_url)
        else:
            requests.post(f"{TELEGRAM_API}/sendMessage", data={
                "chat_id": chat_id,
                "text": "Konnte das Reel nicht laden."
            })
    return {"ok": True}
