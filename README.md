# Persian Kick VOD Clipper

<div dir="rtl" align="right">

سامانه‌ای ماژولار برای دانلود VOD از Kick، تبدیل گفتار به زیرنویس زمان‌دار فارسی، انتخاب محافظه‌کارانهٔ لحظه‌ها **فقط با معیار ارائه‌شده**، ساخت کلیپ و بارگذاری اختیاری در Google Drive.

<h2>معماری و اصل تصمیم‌گیری</h2>

<ol dir="rtl">
  <li>
    <code>downloader.py</code>:
    اعتبارسنجی دامنه و دریافت با <code>yt-dlp</code>؛ این مرز ماژولار است تا در صورت تغییر Kick قابل تعویض باشد.
  </li>
  <li>
    <code>transcription.py</code>:
    استخراج WAV با FFmpeg و Whisper با <code>language="fa"</code>، استفاده از واژه‌نامه و تولید خروجی‌های TXT، SRT و JSON.
  </li>
  <li>
    <code>document_rules.py</code>:
    دریافت متن، DOCX یا Google Doc و تبدیل هر خط به یک قانون، بدون افزودن مفهوم جدید. پیشوندهای <code>منع:</code>، <code>حذف:</code> یا <code>EXCLUDE:</code> قانون حذف ایجاد می‌کنند.
  </li>
  <li>
    <code>analysis.py</code>:
    تطبیق لفظی با رویکرد <code>fail-closed</code>. مترادف، احساس، شدت صدا، تصویر، چت یا «وایرال بودن» استنباط نمی‌شود. این رفتار عمداً محافظه‌کارانه است و موارد مبهم انتخاب نمی‌شوند.
  </li>
  <li>
    <code>clipping.py</code>:
    ایجاد بازهٔ ±۱۸۰ ثانیه، با رعایت طول VOD، تولید MP4 و ثبت شواهد و metadata.
  </li>
  <li>
    <code>storage.py</code>:
    آپلود امن با Service Account و Google Drive API.
  </li>
  <li>
    <code>state.py</code> و <code>reporting.py</code>:
    ثبت checkpoint اتمیک در هر مرحله، جلوگیری از اجرای کامل تکراری و تولید گزارش‌های JSON، TXT و log.
  </li>
  <li>
    <code>panel.py</code>:
    پنل Streamlit برای دریافت VOD و دقیقاً یکی از منابع معیار شامل متن مستقیم، فایل DOCX/TXT یا Google Doc. برای امنیت محیط production، آپلود و اجرای فایل Python دلخواه ارائه نشده است؛ زیرا اجرای کد آپلودشده نوعی Remote Code Execution محسوب می‌شود. خود پروژه روی هاست deploy می‌شود و کاربر فقط فایل یا متن معیار را ارائه می‌کند.
  </li>
</ol>

<blockquote dir="rtl">
Parser هیچ قاعده‌ای را حدس نمی‌زند. هر خط غیرخالی یک معیار inclusion محسوب می‌شود. برای قواعد پیچیده، لازم است سند آن‌ها را به‌صورت صریح و اتمیک، هر کدام در یک خط، بیان کند. اگر استخراج معیار ممکن نباشد، pipeline پیش از دانلود متوقف می‌شود.
</blockquote>

<h2>محدودیت‌ها و دسترسی‌ها</h2>

<ul dir="rtl">
  <li>
    <strong>Kick:</strong>
    API عمومی و پایدار تضمین نشده است و extractor سایت ممکن است تغییر کند. VOD خصوصی یا منطقه‌ای ممکن است به Cookie مجاز کاربر نیاز داشته باشد. شرایط استفادهٔ پلتفرم و حقوق نشر باید رعایت شوند. فایل Cookie از طریق <code>KICK_COOKIE_FILE</code> مشخص می‌شود و نباید commit شود.
  </li>
  <li>
    <strong>FFmpeg:</strong>
    فایل اجرایی FFmpeg باید در <code>PATH</code> سیستم قرار داشته باشد. برش پیش‌فرض با stream-copy سریع است، اما ممکن است روی نزدیک‌ترین keyframe قرار گیرد. گزینهٔ <code>--reencode</code> برش دقیق‌تری ایجاد می‌کند.
  </li>
  <li>
    <strong>Whisper:</strong>
    مدل در نخستین اجرا دانلود می‌شود. مدل‌های بزرگ به CPU/GPU و RAM قابل‌توجه نیاز دارند. زبان فارسی به‌صورت صریح تنظیم می‌شود، اما دقت تبدیل گفتار به متن تضمین‌شده نیست.
  </li>
  <li>
    <strong>Google Doc:</strong>
    مسیر فعلی export متن برای سندی طراحی شده است که Service Account یا دسترسی عمومی امکان خواندن آن را داشته باشد. سند خصوصی باید با Service Account به اشتراک گذاشته شود. در deploymentهای خصوصی می‌توان Reader فعلی را با Google Docs API جایگزین کرد. خطای HTTP یا دریافت متن خالی باعث توقف پردازش می‌شود.
  </li>
  <li>
    <strong>Drive:</strong>
    Google Drive API باید در Google Cloud فعال باشد و پوشهٔ مقصد با ایمیل Service Account به اشتراک گذاشته شود. Scope برنامه <code>drive.file</code> است. بسته به نوع حساب، Service Account ممکن است به quota یا storage سازمانی نیاز داشته باشد.
  </li>
  <li>
    شناسهٔ Google Drive Folder فقط به‌عنوان مقصد Upload استفاده می‌شود و هرگز «معیار انتخاب کلیپ» محسوب نمی‌شود. معیار باید الزاماً از یکی از سه منبع مستقل تعریف‌شده دریافت شود.
  </li>
</ul>

<h2>نصب</h2>

</div>

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
ffmpeg -version
```

<div dir="rtl" align="right">

مقادیر محرمانه را فقط در فایل <code>.env</code> یا Secret Manager هاست قرار دهید. فایل JSON مربوط به Service Account را commit نکنید.

<h2>اجرای CLI</h2>

فقط یکی از گزینه‌های <code>--criteria-text</code>، <code>--criteria-file</code> یا <code>--google-doc</code> مجاز است:

</div>

```bash
persian-kick-clipper run \
  'https://kick.com/streamer/videos/VOD_ID' streamer \
  --criteria-file ./rules.docx \
  --glossary 'نام‌بازی، نام‌استریمر' \
  --upload
```

<div dir="rtl" align="right">

برای واردکردن مستقیم متن معیار:

</div>

```bash
persian-kick-clipper run \
  'https://kick.com/name/videos/id' name \
  --criteria-text $'عبارت صریح مورد نظر\nمنع: عبارت ممنوع'
```

<div dir="rtl" align="right">

<h2>اجرای پنل روی هاست</h2>

</div>

```bash
streamlit run panel.py \
  --server.address 0.0.0.0 \
  --server.port 8501
```

<div dir="rtl" align="right">

هاست باید Storage پایدار، FFmpeg و منابع کافی برای اجرای مدل را داشته باشد.

در محیط production، Reverse Proxy، TLS، احراز هویت پنل، محدودیت اندازهٔ Upload، Timeout و Secret Manager باید در سطح Hosting تنظیم شوند.

برای Jobهای طولانی، بهتر است پردازش در محیط production پشت Queue/Worker اجرا شود.

<h2>خروجی و ادامه‌پذیری</h2>

هر VOD با استفاده از SHA-256 آدرس URL در مسیر <code>outputs/&lt;job-id&gt;</code> به‌صورت جداگانه ذخیره می‌شود.

فایل <code>state.json</code> مراحل کامل‌شده را ثبت می‌کند. فایل‌های <code>processing_report.json</code> و <code>processing_report.txt</code> شامل شواهد موارد پذیرفته‌شده، ردشده و لینک‌های مرتبط هستند.

ساختار کلی خروجی به این صورت است:

<ul dir="rtl">
  <li>
    <code>transcripts/</code>: زیرنویس‌ها و متن استخراج‌شده از VOD.
  </li>
  <li>
    <code>clips/</code>: کلیپ‌های نهایی.
  </li>
  <li>
    <code>reports/</code>: metadata، شواهد و دلیل پذیرش یا رد هر مورد.
  </li>
  <li>
    <code>state.json</code>: وضعیت مراحل پردازش و checkpointها.
  </li>
</ul>

اجرای دوبارهٔ VOD که پردازش آن به‌طور کامل پایان یافته باشد، رد می‌شود تا از پردازش و هزینهٔ تکراری جلوگیری شود.

<h2>تست</h2>

</div>

```bash
pytest
ruff check .
```

<div dir="rtl" align="right">

تست Integration واقعی برای Kick، Whisper و Google Drive عمداً به Credential، دسترسی شبکه، مدل Whisper و VOD مجاز نیاز دارد و جزو Unit Testهای عادی پروژه نیست.

</div>
