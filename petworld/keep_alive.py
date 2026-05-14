"""
Lightweight Flask web server that responds to pings so UptimeRobot
(or any HTTP monitor) can keep the bot awake on Replit.

UptimeRobot setup:
  Monitor Type : HTTP(s)
  URL          : https://<your-replit-project-slug>.replit.app/ping
  Interval     : every 5 minutes
"""
import logging
from flask import Flask
from threading import Thread

log = logging.getLogger("petworld")

app = Flask("")
app.logger.disabled = True
_werkzeug_log = logging.getLogger("werkzeug")
_werkzeug_log.setLevel(logging.ERROR)


@app.route("/")
def home():
    return "🐾 PetWorld bot is online!", 200


@app.route("/ping")
def ping():
    return "pong", 200


def keep_alive(port: int = 5000):
    def _run():
        app.run(host="0.0.0.0", port=port, use_reloader=False)

    t = Thread(target=_run, daemon=True)
    t.start()
    log.info(f"Keep-alive server started on port {port}")
