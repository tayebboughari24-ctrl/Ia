import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from twilio.rest import Client

# --- إعدادات الحماية والبيانات ---
ACCOUNT_SID = 'AC4c92f7ba85364e2ac46aba9a58ec48ad'
AUTH_TOKEN = '4YVLT7YPF2X71ESRL36U3CAB'
TWILIO_NUMBER = 'whatsapp:+14155238886'
MY_NUMBER = 'whatsapp:+213775698325'

# بيانات الدخول لموقع WebTU
MY_USERNAME = "202237581202"
MY_PASSWORD = "UkC2EJUX"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

st.set_page_config(page_title="رادار WebTU", page_icon="🤖")
st.title("🤖 نظام مراقبة العلامات الآلي")
st.info(f"المراقب شغال الآن لحساب: {MY_USERNAME}")

def check_webtu_updates():
    try:
        session = requests.Session()
        login_url = "https://webtu.mesrs.dz/login"
        # الدخول للموقع
        session.post(login_url, data={'username': MY_USERNAME, 'password': MY_PASSWORD}, timeout=15)
        
        # رابط صفحة علامات التقويم المستمر والاختبارات
        target_url = "https://webtu.mesrs.dz/etudiant/cursus/notes"
        response = session.get(target_url, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr') # البحث في أسطر الجدول
        
        extracted_notes = []
        for row in rows[1:]: # تجاوز العناوين
            cols = row.find_all('td')
            if len(cols) >= 2:
                matiere = cols[0].text.strip()
                note = cols[1].text.strip()
                # التحقق إذا كانت هناك علامة حقيقية وليست فراغاً أو "-"
                if True: # تغيير مؤقت للتجربة
                    extracted_notes.append(f"📚 المادة: {matiere}\n⭐ العلامة: {note}")
        
        return extracted_notes
    except Exception as e:
        return None

# ذاكرة البوت لكي لا يكرر الرسائل
if "history" not in st.session_state:
    st.session_state.history = set()

placeholder = st.empty()

# الحلقة اللانهائية (تعمل في السحاب)
while True:
    with placeholder.container():
        st.write(f"🔄 آخر فحص: {time.strftime('%H:%M:%S')}")
        results = check_webtu_updates()
        
        if results:
            for item in results:
                if item not in st.session_state.history:
                    # إرسال الرسالة للواتساب
                    client.messages.create(
                        from_=TWILIO_NUMBER,
                        body=f"🚨 بشمهندس! علامة جديدة في WebTU:\n\n{item}\n\nبالتوفيق!",
                        to=MY_NUMBER
                    )
                    st.session_state.history.add(item)
                    st.success(f"تم إرسال تنبيه: {item.splitlines()[0]}")
        
        st.write("😴 البوت في وضع الانتظار (سيفحص ثانية بعد 15 دقيقة)...")
    
    time.sleep(900) # فحص كل 15 دقيقة
