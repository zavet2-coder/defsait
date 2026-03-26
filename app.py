import http.server
import socketserver
import os
import json
import requests
import time

# env config
T_TOKEN = os.environ.get("TELEGRAM_TOKEN")
C_ID = os.environ.get("CHAT_ID")

# flood control
cache = {}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/order':
            # ip filter
            ip = self.headers.get('x-forwarded-for', self.client_address[0])
            if ip in cache:
                self.send_response(429)
                self.end_headers()
                return

            try:
                l = int(self.headers['Content-Length'])
                raw = self.rfile.read(l)
                d = json.loads(raw)

                u = d.get('contact', '-')
                p = d.get('plan', '-')
                t = d.get('txid', '-')

                if u == '-' or t == '-':
                    self.send_response(400)
                    self.end_headers()
                    return

                # log request
                cache[ip] = time.time()

                # tg msg build
                txt = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"📱 **TG:** {u}\n"
                       f"💎 **PLAN:** {p}\n"
                       f"🔗 **DATA/TXID:** {t}\n"
                       f"━━━━━━━━━━━━━━━")

                requests.post(
                    f"https://api.telegram.org/bot{T_TOKEN}/sendMessage",
                    json={"chat_id": C_ID, "text": txt, "parse_mode": "Markdown"},
                    timeout=7
                )

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())

            except:
                self.send_response(500)
                self.end_headers()

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("0.0.0.0", p), Handler) as srv:
        print(f"init srv:{p}")
        srv.serve_forever()