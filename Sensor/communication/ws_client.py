import socketio
import threading
import time
from core.event_bus import dashboard_queue

class WSClient:
    def __init__(self, backend_url="http://localhost:5000", token=None):
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        self.backend_url = backend_url
        self.token = token
        self.is_running = False

        # Events
        @self.sio.event
        def connect():
            print("\n[WebSocket] 🟢 Connected to ZeinaGuard Dashboard successfully!")

        @self.sio.event
        def disconnect():
            print("\n[WebSocket] 🔴 Disconnected from server.")

    def connect_to_server(self):
        if not self.token:
            print("[WebSocket] ❌ Cannot connect without JWT Token.")
            return

        try:
            print("[WebSocket] ⏳ Connecting to server with Auth Token...")

            # بنجهز التوكن في الـ Headers وفي الـ Auth علشان نرضي جميع إصدارات السيرفر
            headers = {"Authorization": f"Bearer {self.token}"}
            auth_data = {"token": self.token, "Authorization": f"Bearer {self.token}"}

            self.sio.connect(
                self.backend_url,
                headers=headers,
                auth=auth_data,
                wait_timeout=10
            )

            self.is_running = True

            listener_thread = threading.Thread(
                target=self._threat_listener,
                daemon=True
            )
            listener_thread.start()

            self.sio.wait()

        except socketio.exceptions.ConnectionError as e:
            print(f"\n[WebSocket] ❌ Connection Error Details: {e.args}")
        except Exception as e:
            print(f"\n[WebSocket] ❌ Unexpected Error: {e}")

    def _threat_listener(self):
        print("[WebSocket] Listening for threats in the queue...")

        while self.is_running:
            threat = dashboard_queue.get()

            try:
                self.sio.emit("new_threat", threat)
                # استخراج آمن لاسم الشبكة للطباعة
                ssid_name = threat.get('ssid', 'Unknown_SSID')
                print(f"[WebSocket] 🚀 Threat data sent to Dashboard: {ssid_name}")
            except Exception as e:
                print(f"[WebSocket] Failed to send threat: {e}")

            time.sleep(0.05)

    def disconnect_server(self):
        self.is_running = False
        self.sio.disconnect()