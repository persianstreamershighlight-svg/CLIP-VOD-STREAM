import streamlit as st

from persian_kick_vod_clipper.config import Settings
from persian_kick_vod_clipper.document_rules import read_docx, read_google_doc, validate_criteria
from persian_kick_vod_clipper.pipeline import run_pipeline

st.set_page_config(page_title="Persian Kick VOD Clipper", page_icon="✂️")
st.title("Persian Kick VOD Clipper")
st.warning("تنها معیارهای واردشده مبنای تصمیم هستند؛ در نبود معیار پردازش آغاز نمی‌شود.")
vod_url = st.text_input("لینک VOD از Kick.com")
streamer = st.text_input("نام استریمر")
source = st.radio("منبع معیار", ["متن", "فایل DOCX/TXT", "Google Doc"])
criteria = ""
if source == "متن":
    criteria = st.text_area("معیارهای صریح (هر قانون در یک خط)", height=220)
elif source == "فایل DOCX/TXT":
    uploaded = st.file_uploader("فایل معیار", type=["docx", "txt"])
    if uploaded:
        criteria = read_docx(uploaded.getvalue()) if uploaded.name.lower().endswith(".docx") else uploaded.getvalue().decode("utf-8")
else:
    doc_url = st.text_input("نشانی یا شناسه Google Doc (سند باید برای service/public قابل خواندن باشد)")
    if doc_url and st.button("دریافت سند"):
        criteria = read_google_doc(doc_url)
        st.session_state["criteria"] = criteria
    criteria = st.session_state.get("criteria", "")
glossary = st.text_input("واژه‌نامه اختیاری تشخیص گفتار")
upload_drive = st.checkbox("بارگذاری خروجی در Google Drive")
if st.button("شروع پردازش", type="primary"):
    try:
        with st.status("در حال پردازش…", expanded=True) as status:
            result = run_pipeline(vod_url, streamer, validate_criteria(criteria), Settings(), glossary, upload_drive)
            status.update(label="پردازش کامل شد", state="complete")
        st.json(result)
    except Exception as exc:
        st.error(str(exc))

