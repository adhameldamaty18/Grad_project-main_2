import threading
import time  # 🚀 ضفنا المكتبة دي هنا علشان نقدر نعمل Sleep

from monitoring.sniffer import start_monitoring
from detection.threat_manager import ThreatManager
from prevention.response_engine import ResponseEngine
from communication.ws_client import WSClient
from communication.api_client import APIClient


def main():

    print("🚀 Starting ZeinaGuard Sensor...")

    # --------------------------------
    # Authenticate sensor
    # --------------------------------
    api = APIClient()
    token = api.authenticate_sensor()

    # --------------------------------
    # Start WebSocket
    # --------------------------------
    ws = WSClient(token=token)

    ws_thread = threading.Thread(
        target=ws.connect_to_server,
        daemon=True
    )
    ws_thread.start()

    # --------------------------------
    # Threat Manager
    # --------------------------------
    threat_manager = ThreatManager()

    t1 = threading.Thread(
        target=threat_manager.start,
        daemon=True
    )
    t1.start()

    # --------------------------------
    # Response Engine
    # --------------------------------
    response_engine = ResponseEngine()

    t2 = threading.Thread(
        target=response_engine.start,
        daemon=True
    )
    t2.start()

    # --------------------------------
    # Start monitoring
    # --------------------------------
    start_monitoring(pcap_file="wpa-Induction.pcap")

    # 🚀 التعديل الجديد: السكريبت هيفضل شغال علشان الـ WebSocket يبعت الداتا
    print("\n[System] 🟢 تم قراءة الملف بنجاح. النظام مستمر في العمل لإرسال البيانات للداشبورد...")
    print("[System] ⌨️  اضغط CTRL+C للإيقاف.")
    
    try:
        while True:
            time.sleep(1) # السكريبت بيريح ثانية ويلف تاني بدون ما يستهلك البروسيسور
    except KeyboardInterrupt:
        print("\n🛑 جاري إيقاف السنسور... سلام يا هندسة!")


if __name__ == "__main__":
    main()