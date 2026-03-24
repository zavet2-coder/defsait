import sqlite3
import requests
import os
from flask import Flask, render_template, request, jsonify

# Указываем явно, что шаблоны в корне или в папке templates
app = Flask(__name__, template_folder='templates', static_folder='static')

TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"


def init_db():
    try:
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
    except Exception as e:
        print(f"DB Error: {e}")


@app.route('/')
def index():
    init_db()
    # Если index.html в корне, а не в templates, Flask может выдать ошибку 500
    return render_template('index.html')


@app.route('/order', methods=['POST'])
def create_order():
    data = {
        'contact': request.form.get('contact'),
        'plan': request.form.get('plan'),
        'txid': request.form.get('txid')
    }

    # Отправка в ТГ
    text = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📱 **TG:** {data['contact']}\n"
            f"💎 **PLAN:** {data['plan']}\n"
            f"🔗 **DATA/TXID:** {data['txid']}\n"
            f"━━━━━━━━━━━━━━━")

    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

        conn = sqlite3.connect('defense.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (contact, plan, txid) VALUES (?, ?, ?)",
                       (data['contact'], data['plan'], data['txid']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Для локальных тестов
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))