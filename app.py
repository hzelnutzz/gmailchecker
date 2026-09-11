import concurrent.futures
import requests
import streamlit as st

st.set_page_config(page_title="Gmail Checker By Sfvck", layout="wide")

st.title("🛡️ Gmail Checker By Sfvck")
st.markdown("Masukkan daftar email, bot akan mengecek statusnya via HTTP API server.")

email_input_text = st.text_area("Daftar Email (1 email per baris):", height=150, placeholder="contoh1@gmail.com\ncontoh2@gmail.com")

def check_email_api(email):
    # Endpoint check account Google via Web API
    url = "https://accounts.google.com/_/signin/username"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*"
    }
    
    # Format payload request Google Signin
    payload = f"entry=1&continue=https%3A%2F%2Fwww.google.com%2F&f.req=%5B%null%2C%5B%22{email}%22%5D%5D"
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        res_text = response.text
        
        # Analisis respons teks dari server Google
        if "data-ved" in res_text or "rc=" in res_text or "identifier" in res_text:
            if "bukan akun" in res_text.lower() or "tidak dapat menemukan" in res_text.lower() or "Couldn't find" in res_text:
                return email, "Tidak Ditemukan"
            else:
                return email, "Dapat Login"
        elif "cha" in res_text.lower() or "captcha" in res_text.lower():
            return email, "Captcha"
        else:
            # Jika respons mengindikasikan akun valid/lanjut ke password
            if email.lower() in res_text.lower():
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
        st.info(f"Total {len(emails_list)} email dimuat. Memproses via API...")
        
        results = {"Dapat Login": [], "Captcha": [], "Tidak Ditemukan": []}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total = len(emails_list)
        completed = 0
        
        # Menggunakan ThreadPoolExecutor agar pengecekan berjalan cepat secara paralel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
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
