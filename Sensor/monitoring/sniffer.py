# monitoring/sniffer.py

from scapy.all import sniff
from scapy.layers.dot11 import Dot11, Dot11Beacon
import threading
import os
import time
import datetime

# استيراد الـ config بشكل يسمح لنا بتعديله
import config 
from utils import get_ssid, extract_channel
from core.event_bus import event_queue

clients_map = {}

def is_open_network(packet):
    if packet.haslayer(Dot11Beacon):
        cap = packet[Dot11Beacon].cap
        return not cap.privacy
    return False

def build_event(packet):
    dot11 = packet[Dot11]
    bssid = dot11.addr2
    ssid = get_ssid(packet)
    channel = extract_channel(packet)
    signal = getattr(packet, "dBm_AntSignal", None)
    clients_count = len(clients_map.get(bssid, set()))

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "bssid": bssid,
        "ssid": ssid,
        "channel": channel,
        "signal": signal,
        "encryption": "OPEN" if is_open_network(packet) else "SECURED",
        "clients": clients_count
    }

def handle_packet(packet):
    if not packet.haslayer(Dot11):
        return

    dot11 = packet[Dot11]

    if packet.haslayer(Dot11Beacon) and dot11.addr2:
        event = build_event(packet)
        event_queue.put(event)

    if dot11.type == 2:
        bssid = dot11.addr3
        src = dot11.addr2
        if bssid and src and bssid != src:
            clients_map.setdefault(bssid, set()).add(src)

def channel_hopper(interface):
    """بنمرر الـ interface للدالة علشان نضمن إنها بتغير القناة للكارت الصح"""
    print(f"[Sniffer] 🔄 Channel Hopper started on {interface}")
    while True:
        if config.LOCKED_CHANNEL is not None:
            os.system(f"sudo iwconfig {interface} channel {config.LOCKED_CHANNEL}")
            time.sleep(1)
            continue

        for ch in range(1, 14):
            if config.LOCKED_CHANNEL is not None:
                break
            os.system(f"sudo iwconfig {interface} channel {ch}")
            time.sleep(0.4)

def start_monitoring(interface=None, pcap_file=None):
    """
    الدالة دلوقتي بقت مرنة جداً:
    1. لو فيه interface: هتفتح الـ Hopper وتعمل Sniff حي.
    2. لو فيه pcap_file: هتقرأ الملف وتخلص.
    """
    if interface:
        print(f"\n[Sniffer] 📡 تشغيل وضع المراقبة الحي (Live Mode) على الكارت: {interface}")
        
        # تشغيل الـ Hopper في Thread منفصل للكارت الحقيقي
        hopper = threading.Thread(target=channel_hopper, args=(interface,))
        hopper.daemon = True
        hopper.start()
        
        # Sniff من الكارت
        sniff(iface=interface, prn=handle_packet, store=False)
        
    elif pcap_file:
        print(f"\n[Sniffer] 📁 تشغيل وضع المحاكاة (Offline Mode)...")
        print(f"[Sniffer] جاري قراءة الملف: {pcap_file}")
        
        # Sniff من الملف
        sniff(offline=pcap_file, prn=handle_packet, store=False)
        print("[Sniffer] ✅ انتهت قراءة الملف وتم إرسال البيانات للـ Queue.")
    else:
        print("[Sniffer] ❌ Error: No interface or PCAP file provided!")