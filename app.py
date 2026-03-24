import http.server
import socketserver
import os
import json
import requests
from urllib.parse import parse_qs

# Конфиг ТГ
TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"


class MyHandler(http.server.SimpleHTTPRequestHandler):
    # 1. Отдаем index.html при заходе на сайт
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # 2. Ловим данные из формы (POST запрос)
    def do_POST(self):
        if self.path == '/order':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            # Парсим данные из формы
            params = parse_qs(post_data)
            contact = params.get('contact', [''])[0]
            plan = params.get('plan', [''])[0]
            txid = params.get('txid', [''])[0]

            # Отправка в Телеграм напрямую
            text = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📱 **TG:** {contact}\n"
                    f"💎 **PLAN:** {plan}\n"
                    f"🔗 **DATA/TXID:** {txid}\n"
                    f"━━━━━━━━━━━━━━━")

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

            # Отвечаем браузеру, что всё ок
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())


# Запуск сервера
if __name__ == "__main__":
    # Railway сам подставит PORT
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("0.0.0.0", port), MyHandler) as httpd:
        print(f"Сервер пашет на порту {port}")
        httpd.serve_forever()