import csv
import requests
import time

# 1️⃣ Slack Token, Channel ID ve URL'ler
SLACK_TOKEN = ""  # User tokenınızı buraya ekleyin
CHANNEL_ID = "C07TQGGMB44"  # Slack kanal ID'sini buraya ekleyin
BASE_URL = "https://slack.com/api"

# 2️⃣ Header ve Cookie
headers = {
    'Authorization': f'Bearer {SLACK_TOKEN}',
    'Content-Type': 'application/json',
    'Cookie': ''  # Buraya Slack'e ait çerez değeri eklenmeli
}

def fetch_channel_threads(channel_id):
    """Kanal içerisindeki tüm thread mesajlarını alır (yalnızca thread ana mesajları)."""
    url = f"{BASE_URL}/conversations.history"
    params = {
        'channel': channel_id,
        'limit': 200
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

            # Sadece thread başlatan mesajları ekle
            for message in messages:
                if 'reply_count' in message and message['reply_count'] > 0:
                    all_threads.append({
                        'ts': message.get('ts', ''),
                        'user': message.get('user', 'Bilinmiyor'),
                        'text': message.get('text', '').replace('\n', ' '),
                        'thread_ts': message.get('thread_ts', message.get('ts', '')),
                        'reply_count': message.get('reply_count', 0),
                        'subtype': message.get('subtype', 'normal_message'),
                    })
                    print(f"📝 Thread bulundu: {message.get('text', '').strip()[:50]}... | reply_count: {message.get('reply_count', 0)}")

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
    print(f"🔍 {CHANNEL_ID} kanalındaki thread mesajları çekiliyor...")
    threads = fetch_channel_threads(CHANNEL_ID)
    print(f"✅ Toplam {len(threads)} adet thread mesajı bulundu.")
    save_threads_to_csv(threads)
    print(f"📁 CSV dosyası oluşturuldu: threads.csv")

if __name__ == "__main__":
    main()
