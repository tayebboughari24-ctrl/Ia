import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from twilio.rest import Client

# 1. جلب البيانات من "الخزنة" (Secrets) لضمان الأمان
try:
    ACCOUNT_SID = st.secrets["SID"]
    AUTH_TOKEN = st.secrets["TOKEN"]
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
except Exception as e:
    st.error("خطأ: تأكد من وضع SID و TOKEN في إعدادات Secrets في موقع Streamlit")
    st.stop()

# إعدادات الأرقام (ثابتة)
TWILIO_NUMBER = 'whatsapp:+14155238886'
MY_NUMBER = 'whatsapp:+213775698325'

# بيانات الدخول لموقع WebTU
MY_USERNAME = "202237581202"
MY_PASSWORD = "UkC2EJUX"

st.set_page_config(page_title="رادار WebTU", page_icon="🤖")
st.title("🤖 نظام مراقبة العلامات الآلي")

# ذاكرة البوت لمنع التكرار
if "history" not in st.session_state:
    st.session_state.history = set()

placeholder = st.empty()

def check_webtu():
    try:
        session = requests.Session()
        # محاكاة تسجيل الدخول
        session.post("https://webtu.mesrs.dz/login", data={'username': MY_USERNAME, 'password': MY_PASSWORD}, timeout=15)
        response = session.get("https://webtu.mesrs.dz/etudiant/cursus/notes", timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        extracted = []
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                matiere = cols[0].text.strip()
                note = cols[1].text.strip()
                # شرط وجود علامة حقيقية
                if note and note.replace('.', '', 1).isdigit():
                    extracted.append(f"📚 {matiere}: {note}")
        return extracted
    except:
        return []

# الحلقة الأساسية
while True:
    with placeholder.container():
        st.write(f"🔄 آخر فحص للنظام: {time.strftime('%H:%M:%S')}")
        results = check_webtu()
        
        # للتجربة الأولى: سنرسل رسالة فورية إذا وجدنا أي مادة
        if results:
            for item in results:
                if item not in st.session_state.history:
                    try:
                        client.messages.create(
                            from_=TWILIO_NUMBER,
                            body=f"🚨 بشمهندس طيب! علامة جديدة ظهرت:\n{item}",
                            to=MY_NUMBER
                        )
                        st.session_state.history.add(item)
                        st.success(f"تم إرسال: {item}")
                    except Exception as e:
                        st.error(f"خطأ في إرسال الواتساب: {e}")
        
        st.write("😴 البوت يراقب الآن... سينام 15 دقيقة ثم يعاود الفحص.")
    
    time.sleep(900)
    
