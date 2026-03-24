import sqlite3
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = 'psixogen_secret_key_999'

TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"


def init_db():
    conn = sqlite3.connect('defense.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT, plan TEXT, txid TEXT
        )
    ''')
    conn.commit()
    conn.close()


def send_telegram_msg(d):
    text = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📱 **TG:** {d['contact']}\n"
            f"💎 **PLAN:** {d['plan']}\n"
            f"🔗 **DATA/TXID:** {d['txid']}\n"
            f"━━━━━━━━━━━━━━━")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка сети: {e}")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'contact': request.form.get('contact'),
            'plan': request.form.get('plan'),
            'txid': request.form.get('txid')
        }

        # Шлем в ТГ
        send_telegram_msg(data)

        # Сохраняем в базу
        conn = sqlite3.connect('defense.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (contact, plan, txid) VALUES (?, ?, ?)",
                       (data['contact'], data['plan'], data['txid']))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"}), 200

    return render_template('index.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)