import csv
import requests
import time
import json
import os


def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"{config_path} bulunamadı. Lütfen token, cookie ve channel bilgilerini içeren bir config.json oluşturun.")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def fetch_only_thread_messages(token, cookie, channel_id):
    """Kanal içerisindeki sadece thread başlatan (reply_count > 0) mesajları alır."""
    BASE_URL = "https://slack.com/api"
    url = f"{BASE_URL}/conversations.history"
    params = {
        'channel': channel_id,
        'limit': 200
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Cookie': cookie
    }

    all_threads = []
    next_cursor = None
    total_messages = 0

    while True:
        if next_cursor:
            params['cursor'] = next_cursor
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 429:  # Rate limit kontrolü
                retry_after = int(response.headers.get('Retry-After', 10))
                print(f"⚠️ Rate limit hatası. {retry_after} saniye bekleniyor...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            data = response.json()

            if not data.get('ok'):
                print(f"❌ Hata: {data.get('error')}")
                break

            messages = data.get('messages', [])
            total_messages += len(messages)

            # reply_count > 0 olanları thread olarak ekle
            for message in messages:
                if 'reply_count' in message and message['reply_count'] > 0:
                    all_threads.append({
                        'ts': message.get('ts', ''),
                        'user': message.get('user', 'Bilinmiyor'),
                        'text': message.get('text', '').replace('\n', ' '),
                        # Thread başlatan mesajın thread_ts'i kendi ts değeri olur.
                        'thread_ts': message.get('ts', ''),
                        'reply_count': message.get('reply_count', 0),
                        'subtype': message.get('subtype', 'normal_message'),
                    })
                    print(
                        f"📝 Thread bulundu: {message.get('text', '').strip()[:50]}... | reply_count: {message.get('reply_count', 0)}")

            # Next cursor kontrolü
            next_cursor = data.get('response_metadata', {}).get('next_cursor')
            if not next_cursor:
                print("⏹️ Tüm mesajlar çekildi.")
                break

            print(f"🔄 Devam ediliyor... Toplam alınan mesaj sayısı: {total_messages}")
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ İstek hatası: {e}")
            break

    return all_threads


def save_threads_to_csv(threads, filename='threads.csv'):
    """Thread mesajlarını bir CSV dosyasına kaydeder."""
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        # CSV başlıklarını ayarlayın
        writer.writerow(['ts', 'user', 'text', 'thread_ts', 'reply_count', 'subtype'])

        for thread in threads:
            writer.writerow([
                thread['ts'],
                thread['user'],
                thread['text'],
                thread['thread_ts'],
                thread['reply_count'],
                thread['subtype'],
            ])

    print(f"📁 Thread mesajları {filename} dosyasına kaydedildi. Toplam thread sayısı: {len(threads)}")


def main():
    config = load_config()  # config.json'dan ayarları oku
    token = config.get('SLACK_TOKEN')
    cookie = config.get('SLACK_COOKIE', '')
    channel_id = config.get('CHANNEL_ID')

    if not token or not channel_id:
        raise ValueError("SLACK_TOKEN ve CHANNEL_ID config.json dosyasında bulunamadı.")

    print(f"🔍 {channel_id} kanalındaki thread mesajları çekiliyor...")
    threads = fetch_only_thread_messages(token, cookie, channel_id)
    print(f"✅ Toplam {len(threads)} adet thread mesajı bulundu.")
    save_threads_to_csv(threads)
    print(f"📁 CSV dosyası oluşturuldu: threads.csv")


if __name__ == "__main__":
    main()
