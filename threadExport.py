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


def fetch_channel_messages(token, cookie, channel_id):
    """Kanal içerisindeki tüm mesajları alır. Thread başlatanlara thread_ts = ts, diğerlerine ''."""
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

    all_messages = []
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

            for message in messages:
                # thread_ts belirle
                if 'reply_count' in message and message['reply_count'] > 0:
                    thread_ts = message.get('ts', '')
                else:
                    thread_ts = ''

                all_messages.append({
                    'ts': message.get('ts', ''),
                    'user': message.get('user', 'Bilinmiyor'),
                    'text': message.get('text', '').replace('\n', ' '),
                    'thread_ts': thread_ts,
                    'reply_count': message.get('reply_count', 0),
                    'subtype': message.get('subtype', 'normal_message'),
                })

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

    return all_messages


def save_messages_to_csv(messages, filename='threads.csv'):
    """Mesajları bir CSV dosyasına kaydeder."""
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        # CSV başlıklarını ayarlayın
        writer.writerow(['ts', 'user', 'text', 'thread_ts', 'reply_count', 'subtype'])

        for msg in messages:
            writer.writerow([
                msg['ts'],
                msg['user'],
                msg['text'],
                msg['thread_ts'],
                msg['reply_count'],
                msg['subtype'],
            ])

    print(f"📁 Mesajlar {filename} dosyasına kaydedildi. Toplam mesaj sayısı: {len(messages)}")


def main():
    config = load_config()  # config.json'dan ayarları oku
    token = config.get('SLACK_TOKEN')
    cookie = config.get('SLACK_COOKIE', '')
    channel_id = config.get('CHANNEL_ID')

    if not token or not channel_id:
        raise ValueError("SLACK_TOKEN ve CHANNEL_ID config.json dosyasında bulunamadı.")

    print(f"🔍 {channel_id} kanalındaki mesajlar çekiliyor...")
    messages = fetch_channel_messages(token, cookie, channel_id)
    print(f"✅ Toplam {len(messages)} adet mesaj bulundu (thread başlatanlar dahil).")
    save_messages_to_csv(messages)
    print(f"📁 CSV dosyası oluşturuldu: threads.csv")


if __name__ == "__main__":
    main()
