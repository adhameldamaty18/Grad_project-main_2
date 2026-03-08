import threading
import time
import os
import subprocess # علشان ننفذ أوامر اللينكس

from monitoring.sniffer import start_monitoring
from detection.threat_manager import ThreatManager
from prevention.response_engine import ResponseEngine
from communication.ws_client import WSClient
from communication.api_client import APIClient

def setup_monitor_mode(interface="wlan0"):
    """بتحاول تخلي الكارت في وضع المراقبة، ولو فشلت بترجع False"""
    try:
        print(f"[System] 🔍 Checking for WiFi Adapter ({interface})...")
        # بنشوف هل الكارت موجود أصلاً؟
        check_iface = subprocess.run(["iw", "dev", interface, "info"], capture_output=True, text=True)
        
        if check_iface.returncode != 0:
            print(f"[System] ⚠️  Adapter {interface} not found.")
            return False

        print(f"[System] 🛠️  Setting {interface} to Monitor Mode...")
        # أوامر تحويل الكارت لمونيتور مود
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], check=True)
        subprocess.run(["sudo", "iw", interface, "set", "type", "monitor"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], check=True)
        
        print(f"[System] ✅ {interface} is now in MONITOR MODE.")
        return True
    except Exception as e:
        print(f"[System] ❌ Failed to set Monitor Mode: {e}")
        return False

def main():
    print("🚀 Starting ZeinaGuard Sensor...")

    # 1. التوثيق (Authentication)
    api = APIClient()
    token = api.authenticate_sensor()

    # 2. الـ WebSocket
    ws = WSClient(token=token)
    threading.Thread(target=ws.connect_to_server, daemon=True).start()

    # 3. إدارة التهديدات والوقاية
    threat_manager = ThreatManager()
    threading.Thread(target=threat_manager.start, daemon=True).start()

    response_engine = ResponseEngine()
    threading.Thread(target=response_engine.start, daemon=True).start()

    # 🚀 التعديل الجوهري: اختيار مصدر البيانات
    interface_name = "wlan0" # غير الاسم ده لاسم الكارت بتاعك (زي wlan1)
    
    if setup_monitor_mode(interface_name):
        print(f"[Sniffer] 📡 Starting LIVE Monitoring on {interface_name}...")
        # بنشغل السنيفر على الكارت الحقيقي
        start_monitoring(interface=interface_name)
    else:
        print(f"[Sniffer] 📁 Switching to Offline Mode (PCAP Simulation)...")
        # لو مفيش كارت، بنرجع للملف القديم بتاعنا
        start_monitoring(pcap_file="wpa-Induction.pcap")

    # الحفاظ على السكريبت شغال
    print("\n[System] 🟢 ZeinaGuard is running. Press CTRL+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Sensor...")

if __name__ == "__main__":
    main()