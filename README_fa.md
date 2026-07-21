<h1 align="center">🚀 مدیریت پروکسی برای دستیارهای برنامه‌نویسی v2.0 (AI Coders Proxy Fixer)</h1>

<div align="center">
  <img src="https://img.shields.io/badge/Version-v2.0.0--Super--Upgrade-orange" alt="Version"/>
  <img src="https://img.shields.io/badge/OS-Windows-blue" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/Portable-Yes-success" alt="Portable"/>
  <img src="https://img.shields.io/badge/Tests-8%20Passed-brightgreen" alt="Tests"/>
  <br/><br/>
  <b><a href="README.md">🇺🇸 Read in English</a> | <a href="CHANGELOG.md">📜 مشاهده تغییرات (Changelog)</a></b>
</div>

> یک ابزار متن‌باز، هوشمند و پرتابل برای دور زدن محدودیت‌های جغرافیایی، فایروال‌های شرکتی و رفع خطاهای اتصال در دستیارهای هوش مصنوعی مانند Claude Code، Antigravity IDE، Cursor، OpenAI Codex و VS Code.

⭐️ **اگر این ابزار مشکل شما را حل کرد، لطفاً به این ریپازیتوری استار (STAR ⭐) بدهید تا سایر توسعه‌دهندگان نیز بتوانند آن را پیدا کنند!** ⭐️

<div align="center">
  <img src="assets/ui_sample.jpg" alt="تصویر محیط برنامه نسخه ۲" width="650"/>
</div>

## 🚀 چه چیزهایی در نسخه v2.0 جدید است؟

نسخه ۲.۰ برنامه را به یک **اسکنر هوشمند سیستم‌عامل و پچ‌کننده اختصاصی چندگانه** تبدیل کرده است:
- 🔍 **اسکنر هوشمند سیستم‌عامل:** شناسایی خودکار تمام ادیتورهای نصب‌شده (VS Code, Cursor, Antigravity IDE, Void, VS Code Insiders, Sublime Text)، ابزارهای AI (Claude Code, Ollama) و پروفایل‌های ترمینال (PowerShell, Git Bash).
- 🔌 **تشخیص خودکار پورت پروکسی:** اسکن و پیدا کردن پورت پروکسی فعال سیستم (`10808` برای v2rayN، `7890` برای Clash، `2080` برای Hiddify).
- ⚡ **اعمال آنی پروکسی بدون بستن برنامه:** استفاده از `wininet.dll` و ارسال پیام سیستم‌عاملی `WM_SETTINGCHANGE` برای لود آنی پروکسی **بدون نیاز به ری‌استارت مرورگرها یا End Task کردن در Task Manager**.
- 📊 **تست پینگ هوشمند latency:** محاسبه زمان تاخیر واقعی (به میلی‌ثانیه ms) برای گوگل، Claude API و Cloud Code API.
- 🎯 **پچ کردن تکی و دسته‌ای:** امکان پچ کردن اختصاصی هر ادیتور یا ترمینال یا پچ همه با یک کلیک (`Patch All`).
- 💻 **اجرای خودکار با ویندوز:** گزینه Start with Windows برای اجرای خودکار و بی‌سدا در System Tray موقع بوت سیستم.

---

## 🌍 شرح مشکل

توسعه‌دهندگانی که در مناطق تحت تحریم زندگی می‌کنند یا پشت فایروال‌های سخت‌گیرانه شرکتی قرار دارند، به طور مداوم با خطاهای شبکه‌ای در دستیارهای هوش مصنوعی مواجه می‌شوند. استفاده از برنامه‌های تغییر آی‌پی استاندارد (مانند v2ray یا Shadowsocks) معمولاً باعث بروز اختلال در مسیریابی سرورهای لوکال (Language Servers) می‌شود و کرش‌های پی‌درپی یا گیر کردن لاگین OAuth ایجاد می‌کند.

این ابزار خطاهای زیر را برای همیشه برطرف می‌کند:
- ❌ **خطای تحریم گوگل:** `User location is not supported for the API use.` (HTTP 400 Bad Request)
- ❌ **خطای کلود کد:** `Post "https://cloudcode-pa.googleapis.com/...": EOF`
- ❌ **کرش ترمینال:** `Failed to check terminal shell support` (در Antigravity و VS Code)
- ❌ **تایم‌اوت شبکه:** `connection refused` یا `ETIMEDOUT` در ادیتورهای Cursor
- ❌ **توقف ایجنت و گیر کردن OAuth:** از کار افتادن ایجنت‌های خودکار و رد و بدل نشدن توکن لاگین

<div align="center">
  <img src="assets/agent_terminated.png" alt="کرش ایجنت" width="48%"/>
  <img src="assets/cloudcode_eof.png" alt="ارور کلود کد" width="48%"/>
</div>

## 🎯 راه‌حل

برنامه **AI Coders Proxy Fixer** یک رابط کاربری گرافیکی (GUI) پیشرفته است که با یک کلیک، پیچیده‌ترین تنظیمات مسیریابی پروکسی را انجام می‌دهد. این ابزار به صورت هوشمندانه تنظیمات لازم را به IDEها و ترمینال‌های شما تزریق می‌کند و همزمان با اعمال استثنائات دقیق (مانند دور زدن `localhost` و `127.0.0.1`)، جلوی کرش کردن سرورهای لوکال را می‌گیرد.

### ✨ ویژگی‌های کلیدی
- **پروفایل‌های آماده Preset:** تنظیم یک‌کلیکه برای v2rayN, Clash, Hiddify و Custom.
- **تزریق مستقیم به IDE:** اعمال تنظیمات بهینه‌شده در `settings.json` برای **VS Code, Antigravity IDE, Cursor, Void و VS Code Insiders**.
- **پچ ترمینال‌ها:** افزودن خودکار پروکسی به پاورشل (`$PROFILE`) و گیت‌بش (`.bashrc`).
- **مدیریت متغیرهای محیطی:** تنظیم خودکار و یکپارچه در ویندوز (`HTTP_PROXY`, `HTTPS_PROXY` و غیره).
- **رفع مشکل Git:** تنظیم پروکسی گیت برای جلوگیری از فریز شدن دستورات `git push` و `git pull`.
- **پرتابل و سبک:** اجرا در پس‌زمینه و نشستن در System Tray ویندوز بدون نیاز به نصب.

## 🛠️ راهنمای نصب و استفاده

۱. به تب [Releases](../../releases) در همین ریپازیتوری بروید و فایل `AI_Coders_Proxy_Manager.exe` را دانلود کنید.
۲. برنامه را اجرا کنید (بدون نیاز به نصب).
۳. روی دکمه **Auto-Detect Port** کلیک کنید یا پروفایل پروکسی خود را انتخاب کنید.
۴. روی دکمه **Enable & Patch All Proxies** کلیک کنید.
۵. روی **Test Latency** کلیک کنید تا از سرعت اتصال پروکسی خود به سرورهای گوگل و کلود مطمئن شوید!

## 📖 مستندات و جزئیات خطاها
برای مشاهده دلایل فنی بروز خطاها فایل [docs/ERRORS.md](docs/ERRORS.md) و برای دیدن تاریخچه کامل آپدیت‌ها فایل [CHANGELOG.md](CHANGELOG.md) را مطالعه کنید.

---
*توسعه داده شده توسط یک برنامه‌نویس، برای برنامه‌نویس‌ها.*
