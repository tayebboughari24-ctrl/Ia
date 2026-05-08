import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from twilio.rest import Client

# --- 1. جلب مفاتيح السر من الخزنة (Secrets) ---
try:
    ACCOUNT_SID = st.secrets["SID"]
    AUTH_TOKEN = st.secrets["TOKEN"]
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
except Exception as e:
    st.error("🚨 خطأ: لم يتم ضبط SID و TOKEN في إعدادات Secrets")
    st.stop()

# --- 2. إعدادات الأرقام وبيانات الدخول ---
TWILIO_NUMBER = 'whatsapp:+14155238886'
MY_NUMBER = 'whatsapp:+213775698325'
MY_USERNAME = "202237581202"
MY_PASSWORD = "UkC2EJUX"

st.set_page_config(page_title="رادار WebTU الطيب", page_icon="🤖")
st.title("🤖 نظام مراقبة العلامات (النسخة النهائية)")

# ذاكرة البوت لمنع التكرار
if "history" not in st.session_state:
    st.session_state.history = set()

placeholder = st.empty()

def check_webtu():
    try:
        session = requests.Session()
        # محاولة الدخول للموقع الرسمي
        login_response = session.post("https://webtu.mesrs.dz/login", 
                                      data={'username': MY_USERNAME, 'password': MY_PASSWORD}, 
                                      timeout=15)
        
        # التوجه لصفحة النقاط
        response = session.get("https://webtu.mesrs.dz/etudiant/cursus/notes", timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        extracted = []
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                matiere = cols[0].text.strip()
                note = cols[1].text.strip()
                # ملاحظة: في وضع "الاختبار" سنقبل أي مادة حتى لو لم تظهر نقطتها بعد
                extracted.append(f"📚 {matiere}: {note if note else 'قيد الانتظار'}")
        return extracted
    except Exception as e:
        st.error(f"خطأ في الاتصال بموقع WebTU: {e}")
        return []

# --- 3. الحلقة اللانهائية للفحص (تعمل وأنت نائم) ---
while True:
    with placeholder.container():
        current_time = time.strftime('%H:%M:%S')
        st.write(f"🔄 آخر تحديث للنظام: {current_time}")
        
        results = check_webtu()
        
        if results:
            for item in results:
                # إذا كانت المادة لم ترسل من قبل، أرسلها الآن
                if item not in st.session_state.history:
                    try:
                        client.messages.create(
                            from_=TWILIO_NUMBER,
                            body=f"🚨 بشمهندس طيب! تحديث جديد في WebTU:\n\n{item}\n\n✅ النظام شغال تمام!",
                            to=MY_NUMBER
                        )
                        st.session_state.history.add(item)
                        st.success(f"تم إرسال تنبيه واتساب بنجاح لـ: {item}")
                    except Exception as e:
                        st.error(f"فشل إرسال الواتساب: {e}")
        
        st.info("😴 البوت الآن في وضع المراقبة. سيفحص مجدداً بعد 15 دقيقة...")
    
    time.sleep(900) # الانتظار 15 دقيقة بين كل فحص
    
