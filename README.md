# Persian Kick VOD Clipper

سامانه‌ای ماژولار برای دانلود VOD از Kick، تبدیل گفتار به زیرنویس زمان‌دار فارسی، انتخاب محافظه‌کارانهٔ لحظه‌ها **فقط با معیار ارائه‌شده**، ساخت کلیپ و بارگذاری اختیاری در Google Drive.

## معماری و اصل تصمیم‌گیری

1. `downloader.py`: اعتبارسنجی دامنه و دریافت با `yt-dlp`؛ این مرز ماژولار است تا با تغییر Kick تعویض شود.
2. `transcription.py`: استخراج WAV با FFmpeg و Whisper با `language="fa"`، واژه‌نامه و خروجی TXT/SRT/JSON.
3. `document_rules.py`: دریافت متن، DOCX یا Google Doc و تبدیل هر خط به یک قانون بدون افزودن مفهوم. پیشوند `منع:`، `حذف:` یا `EXCLUDE:` قانون حذف می‌سازد.
4. `analysis.py`: تطبیق لفظی و fail-closed. مترادف، احساس، شدت صدا، تصویر، چت یا «وایرال بودن» استنباط نمی‌شود. این رفتار عمداً محافظه‌کارانه است؛ موارد مبهم انتخاب نمی‌شوند.
5. `clipping.py`: بازهٔ ±۱۸۰ ثانیه (محدود به طول VOD)، MP4 و شواهد/metadata.
6. `storage.py`: آپلود امن با service account و Drive API.
7. `state.py` و `reporting.py`: checkpoint اتمیک هر مرحله، جلوگیری از اجرای کامل تکراری و گزارش JSON/TXT/log.
8. `panel.py`: پنل Streamlit برای VOD و دقیقاً یکی از متن، DOCX/TXT یا Google Doc. برای امنیت production، آپلود و اجرای فایل Python دلخواه ارائه نشده است؛ اجرای کد آپلودی remote-code-execution است. خود پروژه روی هاست deploy می‌شود و فقط فایل معیار آپلود می‌شود.

> parser هیچ قاعده‌ای حدس نمی‌زند. هر خط غیرخالی معیار inclusion محسوب می‌شود. برای قواعد پیچیده لازم است سند آن‌ها را صریح و اتمیک، هر کدام در یک خط، بیان کند. اگر استخراج ممکن نباشد pipeline پیش از دانلود متوقف می‌شود.

## محدودیت‌ها و دسترسی‌ها

- **Kick:** API عمومی پایدار تضمین نشده، extractor سایت ممکن است تغییر کند، VOD خصوصی/منطقه‌ای به cookie مجاز کاربر نیاز دارد، و باید شرایط استفاده و حق نشر رعایت شود. فایل cookie با `KICK_COOKIE_FILE` داده می‌شود و commit نمی‌شود.
- **FFmpeg:** باید executable آن روی `PATH` باشد. برش پیش‌فرض stream-copy سریع است و می‌تواند به نزدیک‌ترین keyframe بیفتد؛ `--reencode` برش دقیق‌تری می‌دهد.
- **Whisper:** مدل نخستین بار دانلود می‌شود و مدل‌های بزرگ CPU/GPU و RAM قابل‌توجه می‌خواهند. تنظیم زبان فارسی صریح است؛ دقت تضمین‌پذیر نیست.
- **Google Doc:** مسیر فعلی export متن برای سندی است که service/public بتواند بخواند. سند خصوصی باید با حساب service share شود؛ در deploymentهای خصوصی می‌توان reader را با Docs API جایگزین کرد. خطای HTTP یا متن خالی، پردازش را متوقف می‌کند.
- **Drive:** Drive API باید در Google Cloud فعال باشد؛ پوشه مقصد را با ایمیل service account share کنید. scope برنامه `drive.file` است. service account ممکن است quota/storage سازمانی بخواهد.
- این ابزار به جای Google Drive folder ID به عنوان «معیار»، شناسه پوشه را فقط مقصد upload می‌داند؛ معیار حتماً از یکی از سه منبع مستقل می‌آید.

## نصب

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
ffmpeg -version
```

مقادیر محرمانه را فقط در `.env` یا secret manager هاست قرار دهید. JSON حساب سرویس را commit نکنید.

## اجرای CLI

فقط یکی از `--criteria-text`، `--criteria-file` یا `--google-doc` مجاز است:

```bash
persian-kick-clipper run \
  'https://kick.com/streamer/videos/VOD_ID' streamer \
  --criteria-file ./rules.docx --glossary 'نام‌بازی، نام‌استریمر' --upload
```

برای متن مستقیم:

```bash
persian-kick-clipper run 'https://kick.com/name/videos/id' name \
  --criteria-text $'عبارت صریح مورد نظر\nمنع: عبارت ممنوع'
```

## اجرای پنل روی هاست

```bash
streamlit run panel.py --server.address 0.0.0.0 --server.port 8501
```

هاست باید storage پایدار، FFmpeg و منابع مدل را داشته باشد. reverse proxy، TLS، احراز هویت پنل، محدودیت اندازه upload، timeout و secret manager را در سطح hosting تنظیم کنید. اجرای jobهای طولانی در production بهتر است پشت queue/worker قرار گیرد.

## خروجی و ادامه‌پذیری

هر VOD با SHA-256 URL در `outputs/<job-id>` جدا می‌شود. `state.json` مرحله‌های کامل را ثبت می‌کند؛ `processing_report.json` و `.txt` شامل شواهد پذیرفته/ردشده و لینک‌هاست. transcriptها در `transcripts/`، کلیپ‌ها در `clips/` و metadata و دلیل در `reports/` قرار می‌گیرند. اجرای VOD کاملاً پایان‌یافته رد می‌شود.

## تست

```bash
pytest
ruff check .
```

تست integration واقعی Kick/Whisper/Drive عمداً به credential، شبکه، مدل و VOD مجاز نیاز دارد و جزو unit test نیست.
