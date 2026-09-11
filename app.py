import time
import streamlit as st
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Gmail Checker By Sfvck", layout="wide")

st.title("🛡️ Gmail Checker By Sfvck")
st.markdown("Masukkan daftar email, bot akan mengecek statusnya secara otomatis.")

st.sidebar.header("Pengaturan Bot")
# Di server cloud, mode headless wajib Aktif (True)
headless_mode = st.sidebar.checkbox("Mode Headless (Wajib True untuk Cloud)", value=True)

email_input_text = st.text_area("Daftar Email (1 email per baris):", height=150, placeholder="contoh1@gmail.com\ncontoh2@gmail.com")

def run_checker_sync(emails, headless):
    results = {"Dapat Login": [], "Captcha": [], "Tidak Ditemukan": []}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(emails)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for index, email in enumerate(emails):
            status_text.text(f"Memproses ({index+1}/{total}): {email}")
            result_status = "Tidak Ditemukan"
            
            try:
                page.goto("https://accounts.google.com/", timeout=60000)
                
                input_selector = "input[name='identifier']"
                page.wait_for_selector(input_selector, timeout=10000)
                
                page.fill(input_selector, email)
                page.keyboard.press("Enter")
                page.wait_for_timeout(4000)
                
                content = page.content()
                url = page.url
                
                if "captch" in content.lower() or "recaptcha" in content.lower() or "challenge" in url:
                    result_status = "Captcha"
                elif "password" in content.lower() or page.query_selector("input[name='Passwd']") or page.query_selector("input[type='password']"):
                    result_status = "Dapat Login"
                elif "Couldn't find your Google Account" in content or "tidak dapat menemukan" in content.lower():
                    result_status = "Tidak Ditemukan"
                else:
                    if "oops" in content.lower() or "rejected" in url:
                        result_status = "Tidak Ditemukan"
                    else:
                        result_status = "Dapat Login"
                        
            except Exception as e:
                result_status = "Tidak Ditemukan"
                
            results[result_status].append(email)
            progress_bar.progress((index + 1) / total)
            
        browser.close()
        
    return results

if st.button("Mulai Cek Email", type="primary"):
    emails_list = [e.strip() for e in email_input_text.split("\n") if e.strip()]
    
    if not emails_list:
        st.warning("Harap masukkan setidaknya satu email!")
    else:
        st.info(f"Total {len(emails_list)} email dimuat. Memulai pengecekan...")
        
        results = run_checker_sync(emails_list, headless_mode)
        
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
