import random
import time
import concurrent.futures
import requests
import streamlit as st

st.set_page_config(page_title="Gmail Checker By Sfvck", layout="wide")

st.title("🛡️ Gmail Checker By Sfvck")
st.markdown("Masukkan daftar email, bot akan mengecek statusnya via API dengan proteksi anti-captcha.")

email_input_text = st.text_area("Daftar Email (1 email per baris):", height=150, placeholder="contoh1@gmail.com\ncontoh2@gmail.com")

def check_email_api(email):
    url = "https://accounts.google.com/_/signin/username"
    
    # Rotasi User-Agent agar tidak terdeteksi sebagai bot tunggal
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Referer": "https://accounts.google.com/"
    }
    
    payload = f"entry=1&continue=https%3A%2F%2Fwww.google.com%2F&f.req=%5B%null%2C%5B%22{email}%22%5D%5D"
    
    try:
        # Berikan jeda acak sebentar agar mirip jeda ketik manusia (mencegah rate-limit Google)
        time.sleep(random.uniform(1.5, 3.5))
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        res_text = response.text
        
        # Deteksi status berdasarkan respons Google
        if "cha" in res_text.lower() or "recaptcha" in res_text.lower() or "challenge" in res_text.lower():
            return email, "Captcha"
        elif "bukan akun" in res_text.lower() or "tidak dapat menemukan" in res_text.lower() or "Couldn't find" in res_text:
            return email, "Tidak Ditemukan"
        elif "data-ved" in res_text or "rc=" in res_text or email.lower() in res_text.lower():
            return email, "Dapat Login"
        else:
            return email, "Tidak Ditemukan"
                
    except Exception as e:
        return email, "Tidak Ditemukan"

if st.button("Mulai Cek Email", type="primary"):
    emails_list = [e.strip() for e in email_input_text.split("\n") if e.strip()]
    
    if not emails_list:
        st.warning("Harap masukkan setidaknya satu email!")
    else:
        st.info(f"Total {len(emails_list)} email dimuat. Memproses dengan jeda anti-captcha...")
        
        results = {"Dapat Login": [], "Captcha": [], "Tidak Ditemukan": []}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total = len(emails_list)
        completed = 0
        
        # Mengurangi jumlah worker paralel (max_workers=2) agar IP cloud tidak terdeteksi spam oleh Google
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_email = {executor.submit(check_email_api, email): email for email in emails_list}
            
            for future in concurrent.futures.as_completed(future_to_email):
                email, status = future.result()
                completed += 1
                progress_bar.progress(completed / total)
                status_text.text(f"Memproses ({completed}/{total}): {email}")
                
                if status in results:
                    results[status].append(email)
                else:
                    results["Tidak Ditemukan"].append(email)
                    
        st.success("Pengecekan Selesai!")
        
        st.session_state['res_login'] = "\n".join(results["Dapat Login"])
        st.session_state['res_captcha'] = "\n".join(results["Captcha"])
        st.session_state['res_notfound'] = "\n".join(results["Tidak Ditemukan"])

if 'res_login' in st.session_state:
    st.markdown("---")
    st.subheader("📋 Hasil Pemisahan Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**🟢 Dapat Login ({len(st.session_state['res_login'].splitlines()) if st.session_state['res_login'] else 0})**")
        st.text_area("Login", value=st.session_state['res_login'], height=220, label_visibility="collapsed", key="box_login")

    with col2:
        st.markdown(f"**⚠️ Captcha ({len(st.session_state['res_captcha'].splitlines()) if st.session_state['res_captcha'] else 0})**")
        st.text_area("Captcha", value=st.session_state['res_captcha'], height=220, label_visibility="collapsed", key="box_captcha")

    with col3:
        st.markdown(f"**❌ Tidak Ditemukan ({len(st.session_state['res_notfound'].splitlines()) if st.session_state['res_notfound'] else 0})**")
        st.text_area("Not Found", value=st.session_state['res_notfound'], height=220, label_visibility="collapsed", key="box_notfound")
