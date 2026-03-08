#!/bin/bash

# ==========================================
# ZeinaGuard Pro - Full System Starter
# ==========================================

# 1. التأكد من صلاحيات الرووت (مهم جداً علشان الـ Adapter)
if [ "$EUID" -ne 0 ]; then
  echo "❌ لو سمحت شغل السكريبت بصلاحيات الرووت (sudo ./start_zeinaguard.sh)"
  exit 1
fi

echo "🚀 جاري تشغيل نظام ZeinaGuard Pro..."

# 2. تشغيل الـ Backend والـ Dashboard عن طريق Docker
echo "🐳 بنقوم الـ Docker Containers..."
# بنستخدم مسار السكريبت اللي زمايلك عاملينه، أو نستخدم docker-compose مباشرة
if [ -f "./scripts/start-docker.sh" ]; then
    bash ./scripts/start-docker.sh
else
    docker-compose up -d
fi

echo "⏳ ثواني بنأكد إن السيرفرات قامت..."
sleep 5 # انتظار بسيط لحد ما الـ Database والـ Backend يشتغلوا

# 3. إعداد كارت الشبكة (الـ Adapter)
# خلي بالك: غير 'wlan1' لاسم الكارت بتاعك (تقدر تعرفه من أمر iwconfig)
INTERFACE="wlan1"

echo "📡 جاري تحويل كارت الشبكة ($INTERFACE) إلى Monitor Mode..."
# بنقفل أي خدمات ممكن تعمل تعارض
airmon-ng check kill
# بنشغل الـ Monitor mode
airmon-ng start $INTERFACE

# airmon-ng عادة بيغير اسم الكارت ويضيف عليه 'mon' (زي wlan1mon)
MON_INTERFACE="${INTERFACE}mon"

# التأكد إن الكارت اتحول فعلاً
if iwconfig $MON_INTERFACE | grep -q "Mode:Monitor"; then
    echo "✅ الكارت $MON_INTERFACE جاهز في وضع المراقبة (Monitor Mode)!"
else
    echo "⚠️ مقدرناش نتأكد من حالة الكارت، غالباً اسمه ماتغيرش. هنكمل بـ $INTERFACE"
    MON_INTERFACE=$INTERFACE
fi

# 4. تشغيل الـ Sensor بتاعك
echo "🛡️ جاري تشغيل الـ ZeinaGuard Sensor..."

# تفعيل الـ Virtual Environment بتاع البايثون (لو موجود)
if [ -d "Sensor/venv" ]; then
    source Sensor/venv/bin/activate
fi

# تصدير اسم الكارت كمتغير بيئة علشان الـ Python كود بتاعك يقرأه
export SENSOR_INTERFACE=$MON_INTERFACE

# تشغيل المايسترو (ملف main.py بتاع السنسور)
cd Sensor
python3 main.py

# ==========================================
# 5. تنظيف النظام عند القفل (Cleanup on Exit)
# ==========================================
# لما تدوس CTRL+C السكريبت هينفذ الأوامر دي علشان يرجع كل حاجة زي ما كانت
trap cleanup EXIT

cleanup() {
    echo "\n🛑 جاري إيقاف النظام..."
    
    echo "🔌 بنرجع كارت الشبكة للوضع الطبيعي (Managed Mode)..."
    airmon-ng stop $MON_INTERFACE
    systemctl restart NetworkManager
    
    echo "🐳 بنقفل الـ Docker Containers..."
    cd ..
    docker-compose down
    
    echo "✅ تم إيقاف النظام بأمان. شكراً!"
}
