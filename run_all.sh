#!/bin/bash

# --- الألوان علشان التنسيق ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}   🛡️  ZeinaGuard Full System - Smart Launcher      ${NC}"
echo -e "${GREEN}====================================================${NC}"

# 1. التأكد من صلاحيات الـ Root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ لازم تشغل السكريبت ده بـ sudo!${NC}"
   exit 1
fi

# 2. تشغيل الـ Docker Containers
echo -e "${YELLOW}🐳 [1/5] Starting Backend & Dashboard Containers...${NC}"
# استخدمنا docker compose بدون شرطة عشان النسخة الجديدة عندك
docker compose up -d

# 3. وقت الانتظار (The Waiting Stage) ⏳
WAIT_TIME=20  # هنستنى 20 ثانية، ممكن تزودهم لو جهازك تقيل
echo -e "${YELLOW}⏳ [2/5] Waiting for Flask & Next.js to stabilize...${NC}"

for (( i=$WAIT_TIME; i>0; i-- )); do
    echo -ne "   🚀 System starting in ${i} seconds... \r"
    sleep 1
done
echo -e "\n${GREEN}✅ Services should be ready now!${NC}"

# 4. تثبيت أدوات النظام (لو ناقصة)
echo -e "${YELLOW}🔍 [3/5] Checking System Dependencies...${NC}"
check_apt_pkg() {
    if ! dpkg -s "$1" >/dev/null 2>&1; then
        apt-get install -y "$1" > /dev/null
    fi
}
for pkg in "iw" "wireless-tools" "python3-pip" "libpcap-dev"; do check_apt_pkg "$pkg"; done

# 5. تثبيت مكتبات البايثون (لو ناقصة)
echo -e "${YELLOW}🔍 [4/5] Checking Python Libraries...${NC}"
check_pip_pkg() {
    if ! python3 -c "import $1" >/dev/null 2>&1; then
        pip3 install "$2" --break-system-packages --quiet
    fi
}
check_pip_pkg "scapy" "scapy"
check_pip_pkg "socketio" "python-socketio[client]"
check_pip_pkg "requests" "requests"

# 6. إطلاق السنسور
echo -e "${GREEN}🚀 [5/5] Launching ZeinaGuard Sensor...${NC}"
echo -e "----------------------------------------------------"
if [ -d "Sensor" ]; then
    cd Sensor && python3 main.py
else
    python3 main.py
fi
