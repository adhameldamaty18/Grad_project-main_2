#ws_client.py
import socketio
import threading
import time
from core.event_bus import dashboard_queue


class WSClient:
    def __init__(self, backend_url="http://192.168.201.130:5000", token=None):
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.backend_url = backend_url
        self.token = token
        self.is_running = False

        # Events
        @self.sio.event
        def connect():
            print("\n[WebSocket] 🟢 Connected to ZeinaGuard Dashboard!")

        @self.sio.event
        def disconnect():
            print("\n[WebSocket] 🔴 Disconnected from server.")

    def connect_to_server(self):
      if not self.token:
        print("[WebSocket] Cannot connect without JWT Token.")
        return

      try:
        print("[WebSocket] Connecting to server...")

        self.sio.connect(
            self.backend_url,
            transports=["websocket", "polling"]
)

        self.is_running = True

        listener_thread = threading.Thread(
            target=self._threat_listener,
            daemon=True
        )
        listener_thread.start()

        self.sio.wait()

      except Exception as e:
        print(f"[WebSocket] Connection Error: {e}")

    def _threat_listener(self):
        print("[WebSocket] Listening for threats...")

        while self.is_running:
            threat = dashboard_queue.get()

            try:
                self.sio.emit("new_threat", threat)
                print(f"[WebSocket] 🚀 Threat sent: {threat['event']['ssid']}")
            except Exception as e:
                print(f"[WebSocket] Failed to send threat: {e}")

            time.sleep(0.05)

    def disconnect_server(self):
        self.is_running = False
        self.sio.disconnect()
