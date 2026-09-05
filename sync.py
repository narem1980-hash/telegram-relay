#!/usr/bin/env python3
"""Fetches 4 Telegram channels from t.me/s/ and saves as JSON."""
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

CHANNELS = {
    "geranium_chronicles": "Хроники Гераней",
    "LPRalarm": "LPR оповещения",
    "vrv_radar": "Радар ВРВ",
    "locatorru": "Локатор России",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    "Accept-Language": "ru",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_channel(channel_name):
    url = f"https://t.me/s/{channel_name}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"  {channel_name}: HTTP {resp.status_code}")
            return None

        html = resp.text
        if "tgme_widget_message" not in html:
            print(f"  {channel_name}: no messages ({len(html)} chars)")
            return None

        soup = BeautifulSoup(html, "html.parser")

        title_el = soup.select_one(".tgme_channel_info_header_title span, .tgme_channel_info_title")
        title = title_el.get_text(strip=True) if title_el else channel_name

        posts = []
        for el in soup.select("div.tgme_widget_message"):
            data_post = el.get("data-post", "")
            post_id = data_post.split("/", 1)[1] if "/" in data_post else ""

            text_el = el.select_one(".tgme_widget_message_text")
            text = text_el.get_text(strip=True) if text_el else ""

            time_el = el.select_one("time[datetime]")
            dt = time_el.get("datetime", "") if time_el else ""

            if not post_id and not text:
                continue

            posts.append({
                "id": post_id,
                "text": text,
                "datetime": dt,
                "url": f"https://t.me/{channel_name}/{post_id}",
            })

        if not posts:
            print(f"  {channel_name}: 0 posts")
            return None

        result = {"channel": channel_name, "title": title, "posts": posts}
        print(f"  {channel_name}: {len(posts)} posts OK")
        return result

    except Exception as e:
        print(f"  {channel_name}: ERROR {e}")
        return None


def main():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"=== Telegram sync @ {now} ===")

    updated = 0
    for channel_name in CHANNELS:
        data = fetch_channel(channel_name)
        if data is None:
            continue

        out_path = os.path.join(DATA_DIR, f"{channel_name}.json")
        new_json = json.dumps(data, ensure_ascii=False)

        old_size = 0
        if os.path.exists(out_path):
            old_size = os.path.getsize(out_path)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(new_json)

        if len(new_json) != old_size:
            updated += 1
            print(f"  {channel_name}: WRITTEN ({len(new_json)} bytes)")
        else:
            print(f"  {channel_name}: unchanged")

    print(f"=== Done: {updated}/{len(CHANNELS)} updated ===")


if __name__ == "__main__":
    main()
