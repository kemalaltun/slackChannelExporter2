import csv
import requests
import time
import json
import os


# Config dosyasından token, cookie, channel bilgisini okuyalım
def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"{config_path} bulunamadı. Lütfen token, cookie ve channel bilgilerini içeren bir config.json oluşturun...")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


# threads.csv olmadan çalışmaz. Bu nedenle önce threadExport (mesajları çeken kod) çalışmalı.
THREADS_CSV = "threads.csv"
REPLIES_CSV = "replies.csv"
PROGRESS_FILE = "progress.json"


def main():
    config = load_config()
    TOKEN = config.get("SLACK_TOKEN")
    COOKIE = config.get("SLACK_COOKIE", "")
    CHANNEL = config.get("CHANNEL_ID")

    if not TOKEN or not CHANNEL:
        raise ValueError("SLACK_TOKEN ve CHANNEL_ID config.json dosyasında bulunamadı.")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Cookie": COOKIE,
    }

    # threads.csv dosyasını oku ve thread_ts listesini oluştur
    # Bu kodda thread_ts = ts kolonundan alınıyor. Eğer ts alanı boşsa o mesaj thread değil.
    thread_ts_list = []
    with open(THREADS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            thread_ts = row.get("ts")
            # Boş mu kontrol et. Eğer boşsa reply çekmeye gerek yok
            if thread_ts:
                thread_ts_list.append(thread_ts)

    # Kaldığı yerden devam etmek için progress kontrolü
    start_index = 0
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
            try:
                progress_data = json.load(pf)
                start_index = progress_data.get("last_processed_index", 0)
            except json.JSONDecodeError:
                pass

    fieldnames = ["ts", "user", "text", "thread_ts", "reply_count", "subtype"]

    # replies.csv var mı kontrol et, yoksa header yaz
    write_header = not os.path.exists(REPLIES_CSV)
    f_mode = 'a' if os.path.exists(REPLIES_CSV) else 'w'

    with open(REPLIES_CSV, f_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        if write_header:
            writer.writeheader()

        total_threads = len(thread_ts_list)
        print(f"Toplam işlenecek thread sayısı: {total_threads}")

        for i, t_ts in enumerate(thread_ts_list[start_index:], start=start_index):
            # Her 1000 threadde bir log
            if i > 0 and i % 1000 == 0:
                print(f"{i} thread işlendi...")

            url = "https://slack.com/api/conversations.replies"
            limit = 1000
            cursor = None

            while True:
                data = {
                    "channel": CHANNEL,
                    "ts": t_ts,
                    "limit": limit
                }
                if cursor:
                    data["cursor"] = cursor

                response = requests.post(url, headers=headers, data=data)
                if response.status_code == 429:
                    # Rate limit durumunda Retry-After bekle
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                        print(f"Rate limit aşıldı. {wait_time} saniye bekleniyor...")
                        time.sleep(wait_time)
                        continue
                result = response.json()

                if not result.get("ok"):
                    if result.get('error') == 'ratelimited':
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            wait_time = int(retry_after)
                            print(f"Rate limit aşıldı. {wait_time} saniye bekleniyor...")
                            time.sleep(wait_time)
                            continue
                        else:
                            print("Rate limit, ancak Retry-After header bulunamadı. Elle bekleyiniz.")
                            break
                    else:
                        print("Hata oluştu:", result)
                        break

                messages = result.get("messages", [])
                # İlk mesaj thread'in ana mesajıdır. Onu reply olarak saymayacağız.
                replies = [m for m in messages if m.get("thread_ts") and m.get("ts") != m.get("thread_ts")]

                # replies listesini CSV'ye yaz
                for r in replies:
                    writer.writerow(r)

                next_cursor = result.get("response_metadata", {}).get("next_cursor")
                if not next_cursor:
                    # Bu thread için daha fazla sayfa yok
                    break
                cursor = next_cursor

            # Bu thread bitti, progress kaydet
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump({"last_processed_index": i + 1}, pf)
                print("Bu thread bitti, progress kaydet")

        print("Tüm replies başarıyla alındı!")


if __name__ == "__main__":
    main()
