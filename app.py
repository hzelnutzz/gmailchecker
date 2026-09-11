import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

st.set_page_config(page_title="Gmail Checker By Sfvck", layout="wide")

st.title("🛡️ Gmail Checker By Sfvck")
st.markdown("Masukkan daftar email, bot akan mengecek statusnya secara otomatis.")

st.sidebar.header("Pengaturan Bot")
headless_mode = st.sidebar.checkbox("Mode Headless (Wajib True untuk Cloud)", value=True)

email_input_text = st.text_area("Daftar Email (1 email per baris):", height=150, placeholder="contoh1@gmail.com\ncontoh2@gmail.com")

def run_checker_selenium(emails, headless):
    results = {"Dapat Login": [], "Captcha": [], "Tidak Ditemukan": []}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(emails)
    
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Inisialisasi driver Selenium dengan WebDriver Manager (otomatis pasang driver di cloud)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        for index, email in enumerate(emails):
            status_text.text(f"Memproses ({index+1}/{total}): {email}")
            result_status = "Tidak Ditemukan"
            
            try:
                driver.get("https://accounts.google.com/")
                time.sleep(3)
                
                # Cari kotak input email
                email_input = driver.find_element(By.NAME, "identifier")
                email_input.clear()
                email_input.send_keys(email)
                email_input.send_keys(Keys.RETURN)
                time.sleep(4)
                
                page_source = driver.page_source.lower()
                current_url = driver.current_url.lower()
                
                if "captch" in page_source or "challenge" in current_url:
                    result_status = "Captcha"
                elif "password" in page_source or len(driver.find_elements(By.NAME, "Passwd")) > 0:
                    result_status = "Dapat Login"
                elif "Couldn't find your Google Account" in driver.page_source or "tidak dapat menemukan" in page_source:
                    result_status = "Tidak Ditemukan"
                else:
                    if "oops" in page_source or "rejected" in current_url:
                        result_status = "Tidak Ditemukan"
                    else:
                        result_status = "Dapat Login"
                        
            except Exception as e:
                result_status = "Tidak Ditemukan"
                
            results[result_status].append(email)
            progress_bar.progress((index + 1) / total)
            
    finally:
        driver.quit()
        
    return results

if st.button("Mulai Cek Email", type="primary"):
    emails_list = [e.strip() for e in email_input_text.split("\n") if e.strip()]
    
    if not emails_list:
        st.warning("Harap masukkan setidaknya satu email!")
    else:
        st.info(f"Total {len(emails_list)} email dimuat. Memulai pengecekan...")
        
        results = run_checker_selenium(emails_list, headless_mode)
        
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
