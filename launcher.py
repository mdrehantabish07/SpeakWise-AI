import threading
import time
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

import uvicorn
from backend.main import app

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

def start_backend():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def start_frontend():
    handler = partial(
        SimpleHTTPRequestHandler,
        directory=str(FRONTEND_DIR)
    )
    server = ThreadingHTTPServer(
        ("127.0.0.1", 5500), handler
    )
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(
        target=start_backend, daemon=True
    ).start()

    threading.Thread(
        target=start_frontend, daemon=True
    ).start()

    time.sleep(3)
    webbrowser.open("http://127.0.0.1:5500")

    print("SpeakWise AI is running. Close this window to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass