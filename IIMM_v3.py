# pip install requests pandas openpyxl pillow selenium beautifulsoup4 lxml webdriver-manager
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import pandas as pd
from datetime import datetime
import os
import logging
import time
import threading
from typing import List, Dict, Optional, Set
from collections import OrderedDict
from PIL import Image, ImageTk, ImageDraw
import io
import webbrowser
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    _WDM_AVAILABLE = True
except ImportError:
    _WDM_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
SCRIPT_DIR = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════════════════════
GENRES = [
    ("Action","اکشن"),("Adventure","ماجراجویی"),("Animation","انیمیشن"),
    ("Biography","زندگینامه"),("Comedy","کمدی"),("Crime","جنایی"),
    ("Documentary","مستند"),("Drama","درام"),("Family","خانوادگی"),
    ("Fantasy","فانتزی"),("Film-Noir","فیلم نوآر"),("Game-Show","برنامه بازی"),
    ("History","تاریخی"),("Horror","ترسناک"),("Music","موزیکال"),
    ("Musical","موزیکال"),("Mystery","معمایی"),("News","اخبار"),
    ("Reality-TV","ریالیتی شو"),("Romance","عاشقانه"),("Sci-Fi","علمی تخیلی"),
    ("Short","کوتاه"),("Sport","ورزشی"),("Talk-Show","تاک شو"),
    ("Thriller","هیجان انگیز"),("War","جنگی"),("Western","وسترن"),
]
GENRE_TO_IMDB_CODE = {
    "Action":"action","Adventure":"adventure","Animation":"animation",
    "Biography":"biography","Comedy":"comedy","Crime":"crime",
    "Documentary":"documentary","Drama":"drama","Family":"family",
    "Fantasy":"fantasy","Film-Noir":"film-noir","Game-Show":"game-show",
    "History":"history","Horror":"horror","Music":"music",
    "Musical":"musical","Mystery":"mystery","News":"news",
    "Reality-TV":"reality-tv","Romance":"romance","Sci-Fi":"sci-fi",
    "Short":"short","Sport":"sport","Talk-Show":"talk-show",
    "Thriller":"thriller","War":"war","Western":"western",
}
LANGUAGES = [
    ("en","انگلیسی"),("fr","فرانسوی"),("de","آلمانی"),("hi","هندی"),
    ("it","ایتالیایی"),("pt","پرتغالی"),("es","اسپانیایی"),("zh","چینی"),
    ("ja","ژاپنی"),("ko","کره‌ای"),("ru","روسی"),("ar","عربی"),
    ("tr","ترکی"),("nl","هلندی"),("sv","سوئدی"),("da","دانمارکی"),
    ("no","نروژی"),("fi","فنلاندی"),("pl","لهستانی"),("th","تایلندی"),
]
LANG_CODE_TO_IMDB = {c: c for c, _ in LANGUAGES}
IMPORTANT_COUNTRIES = [
    ("US","ایالات متحده آمریکا"),("GB","بریتانیا"),("FR","فرانسه"),
    ("DE","آلمان"),("IT","ایتالیا"),("ES","اسپانیا"),("IN","هند"),
    ("JP","ژاپن"),("KR","کره جنوبی"),("CN","چین"),("RU","روسیه"),
    ("IR","ایران"),("CA","کانادا"),("AU","استرالیا"),("MX","مکزیک"),
    ("BR","برزیل"),("SE","سوئد"),("DK","دانمارکی"),("NO","نروژ"),
    ("FI","فنلاندی"),("PL","لهستان"),("TR","ترکیه"),("NL","هلند"),
    ("BE","بلژیک"),("CH","سوئیس"),("AT","اتریش"),("CZ","جمهوری چک"),
    ("HU","مجارستان"),("RO","رومانی"),("BG","بلغارستان"),("GR","یونان"),
    ("PT","پرتغال"),("AR","آرژانتین"),("CL","شیلی"),("CO","کلمبیا"),
    ("TH","تایلند"),("EG","مصر"),("ZA","آفریقای جنوبی"),("IL","اسرائیل"),
]
COUNTRIES = [
    ("AF","افغانستان"),("AL","آلبانی"),("DZ","الجزایر"),("AR","آرژانتین"),
    ("AM","ارمنستان"),("AU","استرالیا"),("AT","اتریش"),("AZ","آذربایجان"),
    ("BH","بحرین"),("BD","بنگلادش"),("BY","بلاروس"),("BE","بلژیک"),
    ("BO","بولیوی"),("BA","بوسنی و هرزگوین"),("BR","برزیل"),("BG","بلغارستان"),
    ("KH","کامبوج"),("CM","کامرون"),("CA","کانادا"),("CL","شیلی"),
    ("CN","چین"),("CO","کلمبیا"),("CR","کاستاریکا"),("HR","کرواسی"),
    ("CU","کوبا"),("CY","قبرس"),("CZ","جمهوری چک"),("DK","دانمارک"),
    ("DO","جمهوری دومینیکن"),("EC","اکوادور"),("EG","مصر"),("EE","استونی"),
    ("ET","اتیوپی"),("FI","فنلاندی"),("FR","فرانسه"),("GE","گرجستان"),
    ("DE","آلمان"),("GH","غنا"),("GR","یونان"),("GT","گواتمالا"),
    ("HN","هندوراس"),("HK","هنگ کنگ"),("HU","مجارستان"),("IS","ایسلند"),
    ("IN","هند"),("ID","اندونزی"),("IR","ایران"),("IQ","عراق"),
    ("IE","ایرلند"),("IL","اسرائیل"),("IT","ایتالیا"),("JM","جامائیکا"),
    ("JP","ژاپن"),("JO","اردن"),("KZ","قزاقستان"),("KE","کنیا"),
    ("KP","کره شمالی"),("KR","کره جنوبی"),("KW","کویت"),("KG","قرقیزستان"),
    ("LA","لائوس"),("LV","لتونی"),("LB","لبنان"),("LY","لیبی"),
    ("LT","لیتوانی"),("LU","لوکزامبورگ"),("MY","مالزی"),("MT","مالت"),
    ("MX","مکزیک"),("MD","مولداوی"),("MC","موناکو"),("MN","مغولستان"),
    ("ME","مونته‌نگرو"),("MA","مراکش"),("MZ","موزامبیک"),("MM","میانمار"),
    ("NP","نپال"),("NL","هلند"),("NZ","نیوزیلند"),("NI","نیکاراگوئه"),
    ("NG","نیجریه"),("NO","نروژ"),("OM","عمان"),("PK","پاکستان"),
    ("PA","پاناما"),("PY","پاراگوئه"),("PE","پرو"),("PH","فیلیپین"),
    ("PL","لهستان"),("PT","پرتغال"),("QA","قطر"),("RO","رومانی"),
    ("RU","روسیه"),("SA","عربستان سعودی"),("SN","سنگال"),("RS","صربستان"),
    ("SG","سنگاپور"),("SK","اسلواکی"),("SI","اسلوونی"),("ZA","آفریقای جنوبی"),
    ("ES","اسپانیا"),("LK","سری‌لانکا"),("SE","سوئد"),("CH","سوئیس"),
    ("SY","سوریه"),("TW","تایوان"),("TZ","تانزانیا"),("TH","تایلند"),
    ("TN","تونس"),("TR","ترکیه"),("UA","اوکراین"),("AE","امارات متحده عربی"),
    ("GB","بریتانیا"),("US","ایالات متحده آمریکا"),("UY","اوروگوئه"),
    ("UZ","ازبکستان"),("VE","ونزوئلا"),("VN","ویتنام"),("YE","یمن"),
    ("ZM","زامبیا"),("ZW","زیمبابوه"),
]
COUNTRIES.sort(key=lambda x: x[1])
COUNTRY_TO_IMDB_CODE = {code: code.lower() for code, _ in COUNTRIES}
IMDB_TYPE_MAP = {"فیلم":"feature","سریال":"tv_series","مینی سریال":"tv_miniseries"}


# ═══════════════════════════════════════════════════════════════════════════
DETAILS_WIDTH_RATIO = 0.38
POSTER_MAX_HEIGHT_RATIO = 0.88


def upgrade_poster_url(url, width=1100):
    if not url or not isinstance(url, str): return url
    if "_V1_" not in url: return url
    return re.sub(r'(_V1_).*(\.\w+)$', rf'\1_UX{width}_\2', url, flags=re.I)


def fit_resize(raw, target_w, target_h):
    rw, rh = raw.size
    if rw <= 0 or rh <= 0: return raw
    ratio = min(target_w / rw, target_h / rh)
    nw, nh = max(1, int(rw * ratio)), max(1, int(rh * ratio))
    return raw.resize((nw, nh), Image.Resampling.LANCZOS)


# ═══════════════════════════════════════════════════════════════════════════
def _get_edge_version():
    import subprocess, re
    for cmd in [
        r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon" /v version',
        r'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\EdgeUpdate\Clients\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" /v pv',
    ]:
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", out)
            if m: return m.group(1)
        except Exception:
            pass
    return None


def _build_edge_options(headless=False):
    options = EdgeOptions()
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    for a in ("--log-level=3", "--disable-gpu", "--no-sandbox",
              "--disable-dev-shm-usage", "--disable-extensions", "--disable-infobars"):
        options.add_argument(a)
    if headless:
        options.add_argument("--headless=new")
    return options


def create_edge_driver(headless=False):
    options = _build_edge_options(headless)

    # ── اولویت ۱: درایور محلی کنار اسکریپت ──────────────────────────────
    dp = SCRIPT_DIR / "edgedriver.exe"
    if dp.exists():
        logger.info("درایور محلی پیدا شد: %s", dp)
        driver = webdriver.Edge(service=Service(str(dp)), options=options)
        try: driver.maximize_window()
        except: driver.set_window_size(1920, 1080)
        return driver

    # ── اولویت ۲: دانلود خودکار با webdriver-manager ─────────────────────
    if _WDM_AVAILABLE:
        try:
            logger.info("دانلود خودکار درایور با webdriver-manager ...")
            driver_path = EdgeChromiumDriverManager().install()
            driver = webdriver.Edge(service=Service(driver_path), options=options)
            try: driver.maximize_window()
            except: driver.set_window_size(1920, 1080)
            return driver
        except Exception as e:
            logger.warning("webdriver-manager موفق نشد: %s", e)

    # ── هیچ درایوری پیدا نشد ─────────────────────────────────────────────
    edge_ver = _get_edge_version()
    major = edge_ver.split(".")[0] if edge_ver else "؟"
    msg = (f"❌ درایور Edge پیدا نشد!\n\nنسخه Edge شما: {edge_ver or 'نامشخص'}\n\n"
           f"لطفاً درایور نسخه {major} را از لینک زیر دانلود و با نام edgedriver.exe "
           f"در پوشه اسکریپت بگذارید:\n"
           f"https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/\n\n"
           f"مسیر اسکریپت: {SCRIPT_DIR}")
    logger.error(msg)
    raise FileNotFoundError(msg)


# ── تابع جستجو با retry خودکار هنگام قطعی اینترنت ─────────────────────────
NETWORK_ERRORS = ("ERR_CONNECTION_TIMED_OUT", "ERR_INTERNET_DISCONNECTED",
                  "ERR_NAME_NOT_RESOLVED", "ERR_CONNECTION_RESET",
                  "ERR_NETWORK_CHANGED", "ERR_CONNECTION_REFUSED")

def scrape_with_retry(url, max_items, progress_callback=None,
                      max_retries=3, retry_delay=15):
    """جستجو با قابلیت تلاش مجدد خودکار در صورت قطعی اینترنت"""
    for attempt in range(1, max_retries + 1):
        driver = create_edge_driver(headless=False)
        try:
            result = scrape_search_results(driver, url, max_items=max_items,
                                           progress_callback=progress_callback)
            return result
        except WebDriverException as e:
            err_msg = str(e)
            is_network = any(ne in err_msg for ne in NETWORK_ERRORS)
            if is_network and attempt < max_retries:
                logger.warning("⚠ قطعی اینترنت — تلاش %d/%d — %d ثانیه صبر می‌کنم ...",
                               attempt, max_retries, retry_delay)
                try: driver.quit()
                except: pass
                time.sleep(retry_delay)
                continue
            raise
        finally:
            try: driver.quit()
            except: pass
    return []

def wait_for_page_ready(driver, timeout=15, min_pause=0.8):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState")=="complete")
    try: WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
    except: pass
    time.sleep(min_pause)

def clean_text(el): return el.get_text(" ", strip=True) if el else None
def normalize_imdb_url(v):
    if not v: return None
    p = urlsplit(urljoin("https://www.imdb.com/", v))
    return urlunsplit((p.scheme, p.netloc, p.path.rstrip("/"), "", "")) + "/"
def _extract_tt_id(h):
    m = re.search(r"(tt\d+)", h or ""); return m.group(1) if m else None
def _safe_float(v):
    try: return float(v)
    except: return None
def _safe_int(v):
    try: return int(str(v).replace(",","").strip())
    except: return None

# ★ همه جداکننده‌ها در URL = ,
def build_imdb_search_url(title_type, start_year, end_year, min_rating, min_votes,
                          genres=None, languages=None, countries=None,
                          sort="user_rating,desc", count=250):
    params = [f"title_type={title_type}", f"release_date={start_year}-01-01,{end_year}-12-31"]
    if min_rating > 0: params.append(f"user_rating={min_rating},")
    if min_votes > 0:  params.append(f"num_votes={min_votes},")
    if genres:    params.append("genres="+",".join(GENRE_TO_IMDB_CODE.get(g,g.lower()) for g in genres))
    if languages: params.append("languages="+",".join(LANG_CODE_TO_IMDB.get(l,l) for l in languages))
    if countries: params.append("countries="+",".join(COUNTRY_TO_IMDB_CODE.get(c,c.lower()) for c in countries))
    params += [f"count={count}", f"sort={sort}"]
    return "https://www.imdb.com/search/title/?" + "&".join(params)

def scrape_search_results(driver, url, max_items=5000, progress_callback=None):
    driver.get(url); wait_for_page_ready(driver)
    try: WebDriverWait(driver,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,"ul.ipc-metadata-list")))
    except TimeoutException: return []
    SEL = "li.ipc-metadata-list-summary-item"
    loaded = len(driver.find_elements(By.CSS_SELECTOR, SEL)); failures = 0
    while loaded < max_items and failures < 5:
        try:
            btn = WebDriverWait(driver,8).until(EC.presence_of_element_located(
                (By.XPATH,"//button[contains(@class,'ipc-btn') and .//span[contains(text(),'50 more')]]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", btn); time.sleep(0.3)
            driver.execute_script("arguments[0].click();", btn); old = loaded
            WebDriverWait(driver,12).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, SEL)) > old)
            wait_for_page_ready(driver, min_pause=0.5)
            loaded = len(driver.find_elements(By.CSS_SELECTOR, SEL)); failures = 0
            if progress_callback: progress_callback(loaded)
        except Exception: failures += 1; time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    container = soup.select_one("ul.ipc-metadata-list")
    if not container: return []
    items = []
    for film in container.find_all("li", class_="ipc-metadata-list-summary-item")[:max_items]:
        try:
            title_tag = film.select_one("a.ipc-title-link-wrapper")
            link_tag  = film.select_one("a.ipc-lockup-overlay[href]")
            href = link_tag.get("href","") if link_tag else ""
            meta = [clean_text(li) for li in film.select(".dli-title-metadata li.ipc-inline-list__item")]
            rating_el = film.find("span", class_="ipc-rating-star--rating")
            votes_el  = film.find("span", class_="ipc-rating-star--voteCount")
            vt = clean_text(votes_el)
            if vt and vt.startswith("(") and vt.endswith(")"): vt = vt[1:-1].strip()
            poster_img = film.select_one("img.ipc-image")
            raw_poster = poster_img.get("src") if poster_img else None
            items.append({
                "id": _extract_tt_id(href), "primaryTitle": clean_text(title_tag),
                "originalTitle": clean_text(title_tag),
                "primaryImage": upgrade_poster_url(raw_poster, 500),
                "startYear": meta[0] if len(meta)>0 else None,
                "duration":  meta[1] if len(meta)>1 else None,
                "mpa":       meta[2] if len(meta)>2 else None,
                "rating": _safe_float(clean_text(rating_el)), "votes": _safe_int(vt),
                "plot": clean_text(film.find("div", class_="ipc-html-content-inner-div")),
                "genres": [], "country": "", "language": "", "type": "",
                "link": normalize_imdb_url(href),
            })
        except Exception as exc: logger.error("Parse error: %s", exc)
    return items


# ═══════════════════════════════════════════════════════════════════════════
def bind_recursive(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.winfo_children():
        bind_recursive(child, event, callback)

def create_gradient_image(w, h, c1, c2):
    img = Image.new('RGB', (w, h)); draw = ImageDraw.Draw(img)
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    for i in range(h):
        r = i/h
        draw.line([(0,i),(w,i)], fill=(int(r1+(r2-r1)*r),int(g1+(g2-g1)*r),int(b1+(b2-b1)*r)))
    return img


# ══════════════════════════════════════════════════════════════════════════
class LazyImageLoader:
    RAW_LIMIT = 350
    def __init__(self, canvas, scrollable_frame):
        self.canvas = canvas
        self.scrollable_frame = scrollable_frame
        self.visible_widgets = {}
        self.failed_loads = {}
        self.retry_timer = None
        self.retry_count = 0
        self.max_retries = 5
        self.image_quality = 85
        self.tile_width = 200
        self.raw_images = OrderedDict()
        self.label_map = {}
        self._photos = {}
        self.image_check_timer = None
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Enter>", self.bind_events)
        self.canvas.bind("<Leave>", self.unbind_events)
        self.schedule_image_check()

    def _render_label(self, url, label):
        raw = self.raw_images.get(url)
        if raw is None or not label.winfo_exists(): return
        w = max(80, int(self.tile_width) - 24)
        h = int(w * 1.45)
        img = fit_resize(raw, w, h)
        photo = ImageTk.PhotoImage(img)
        self._photos[url] = photo
        try:
            label.configure(image=photo, text=""); label.image = photo
        except Exception: pass

    def set_tile_width(self, w):
        w = int(w)
        if abs(w - self.tile_width) < 4: return False
        self.tile_width = w
        for url, label in list(self.label_map.items()):
            if url in self.raw_images: self._render_label(url, label)
        return True

    def _store_raw(self, url, raw):
        self.raw_images[url] = raw; self.raw_images.move_to_end(url)
        while len(self.raw_images) > self.RAW_LIMIT: self.raw_images.popitem(last=False)

    def schedule_image_check(self):
        if self.image_check_timer: self.canvas.after_cancel(self.image_check_timer)
        self.image_check_timer = self.canvas.after(20000, self.check_and_retry_failed_images)
    def check_and_retry_failed_images(self):
        if self.failed_loads: self.retry_failed_loads()
        self.schedule_image_check()
    def bind_events(self, e=None):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)
    def unbind_events(self, e=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
    def on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0: self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0: self.canvas.yview_scroll(-1, "units")
        self.check_visible_widgets()
    def on_canvas_configure(self, e): self.check_visible_widgets()

    def check_visible_widgets(self):
        h = self.canvas.winfo_height()
        for w in self.scrollable_frame.winfo_children():
            if isinstance(w, (ttk.Frame, tk.Frame)):
                wid = id(w)
                if 0 <= w.winfo_y() < h:
                    if wid not in self.visible_widgets:
                        self.visible_widgets[wid] = True
                        self.load_image_for_widget(w)
                else:
                    self.visible_widgets.pop(wid, None)

    def load_image_for_widget(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Label) and hasattr(child, "image_url"):
                url = child.image_url
                if url and url not in self.raw_images and url not in self.failed_loads:
                    t = threading.Thread(target=self.load_image_thread, args=(url, child))
                    t.daemon = True; t.start()

    def load_image_thread(self, url, label):
        try:
            resp = requests.get(url, timeout=10)
            raw = Image.open(io.BytesIO(resp.content)).convert("RGB")
            raw.thumbnail((900, 1300), Image.Resampling.LANCZOS)
            self._store_raw(url, raw)
            self.failed_loads.pop(url, None)
            self.label_map[url] = label
            self.canvas.after(0, self._render_label, url, label)
        except Exception as e:
            logger.error("Image error: %s", e)
            self.failed_loads[url] = label
            self.canvas.after(0, lambda: label.configure(text="⚠ خطا") if label.winfo_exists() else None)

    def set_image_quality(self, q): self.image_quality = max(1, min(100, q))
    def start_retry_timer(self):
        if self.retry_timer is None and self.retry_count < self.max_retries:
            self.retry_timer = self.canvas.after(3000, self.retry_failed_loads)
    def retry_failed_loads(self):
        self.retry_count += 1
        fc = self.failed_loads.copy(); self.failed_loads.clear()
        for url, l in fc.items():
            t = threading.Thread(target=self.load_image_thread, args=(url, l)); t.daemon=True; t.start()
        if self.failed_loads and self.retry_count < self.max_retries:
            self.retry_timer = self.canvas.after(3000, self.retry_failed_loads)
        else: self.retry_timer = None
    def stop_retry_timer(self):
        if self.retry_timer: self.canvas.after_cancel(self.retry_timer); self.retry_timer = None
    def stop_image_check_timer(self):
        if self.image_check_timer: self.canvas.after_cancel(self.image_check_timer); self.image_check_timer = None
    def reset(self):
        self.visible_widgets.clear(); self.failed_loads.clear()
        self.raw_images.clear(); self.label_map.clear(); self._photos.clear()
        self.stop_retry_timer(); self.stop_image_check_timer()
        self.retry_count = 0; self.schedule_image_check()


# ══════════════════════════════════════════════════════════════════════════
class IMDbApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" جستجوی پیشرفته فیلم و سریال – AvaMovie")
        self.root.geometry("1600x900"); self.root.minsize(1100, 650)
        try: self.root.state('zoomed')
        except: pass
        self.setup_dark_theme(); self.create_background()

        self.posters_dir = "posters"; os.makedirs(self.posters_dir, exist_ok=True)
        self.movies_data = []; self.series_data = []; self.miniseries_data = []
        self.current_selected_item = None
        self._driver = None
        self.image_loaders = {}
        self._poster_raw = None
        self._poster_label = None
        self._poster_df = None
        self._details_panels = {}
        self._details_parents = {}

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.setup_frame      = ttk.Frame(self.notebook)
        self.genres_frame     = ttk.Frame(self.notebook)
        self.languages_frame  = ttk.Frame(self.notebook)
        self.countries_frame  = ttk.Frame(self.notebook)
        self.movies_frame     = ttk.Frame(self.notebook)
        self.series_frame     = ttk.Frame(self.notebook)
        self.miniseries_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame,      text="  ⚙ تنظیمات پایه  ")
        self.notebook.add(self.genres_frame,     text="  🎭 ژانرها  ")
        self.notebook.add(self.languages_frame,  text="  🌐 زبان‌ها  ")
        self.notebook.add(self.countries_frame,  text="  🗺 کشورها  ")
        self.notebook.add(self.movies_frame,     text="  🎬 فیلم‌ها  ")
        self.notebook.add(self.series_frame,     text="   سریال‌ها  ")
        self.notebook.add(self.miniseries_frame, text="   مینی‌سریال‌ها  ")

        self.important_country_vars = {}; self.important_country_status_labels = {}
        self.selected_wanted_genres=set(); self.selected_unwanted_genres=set()
        self.selected_wanted_languages=set(); self.selected_unwanted_languages=set()
        self.selected_wanted_countries=set(); self.selected_unwanted_countries=set()
        self.movies_details_frame=None; self.series_details_frame=None; self.miniseries_details_frame=None

        self.setup_search_ui(); self.setup_genres_ui()
        self.setup_languages_ui(); self.setup_countries_ui(); self.disable_result_tabs()

        if "US" in self.country_wanted_vars:
            self.country_wanted_vars["US"].set(True); self.selected_wanted_countries.add("US")
            self.country_status_var.set("کشورهای خواسته: 1 | کشورهای ناخواسته: 0")
        for g in ("Animation","Documentary"):
            if g in self.genre_unwanted_vars:
                self.genre_unwanted_vars[g].set(True); self.selected_unwanted_genres.add(g)
        self.genre_status_var.set("ژانرهای خواسته: 0 | ژانرهای ناخواسته: 2")

    def create_background(self):
        try:
            bg = create_gradient_image(1600, 900, "#0d0d0d", "#1a1a2e")
            self.bg_photo = ImageTk.PhotoImage(bg)
            self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.bg_canvas.lower()
        except: pass

    def setup_dark_theme(self):
        self.bg_color="#121212"; self.fg_color="#e0e0e0"; self.accent_color="#e50914"
        self.accent_hover="#ff1a25"; self.secondary_color="#1e1e1e"; self.card_color="#252525"
        self.highlight_color="#333333"; self.yellow_color="#FFD700"; self.green_color="#4CAF50"
        self.border_color="#3a3a3a"
        s = ttk.Style(); s.theme_use('clam')
        s.configure('.', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI',10))
        s.configure('TFrame', background=self.bg_color)
        s.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI',10))
        s.configure('Title.TLabel', font=('Segoe UI',14,'bold'))
        s.configure('Subtitle.TLabel', foreground="#aaaaaa", font=('Segoe UI',9))
        s.configure('TButton', background=self.secondary_color, foreground=self.fg_color,
                    font=('Segoe UI',10,'bold'), padding=(12,6))
        s.map('TButton', background=[('active',self.highlight_color),('pressed',self.accent_color)])
        s.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color)
        s.map('TCheckbutton', background=[('active',self.highlight_color)])
        s.configure('TEntry', fieldbackground=self.secondary_color, foreground=self.fg_color, padding=4)
        s.configure('TSpinbox', fieldbackground=self.secondary_color, foreground=self.fg_color, padding=3)
        s.configure('TScale', background=self.bg_color)
        s.configure('TNotebook', background=self.bg_color, borderwidth=0)
        s.configure('TNotebook.Tab', background=self.secondary_color, foreground=self.fg_color,
                    padding=[14,8], font=('Segoe UI',10,'bold'))
        s.map('TNotebook.Tab', background=[('selected',self.accent_color),('active',self.highlight_color)],
              foreground=[('selected','#ffffff')])
        s.configure('Accent.TButton', background=self.accent_color, foreground='#fff',
                    font=('Segoe UI',11,'bold'), padding=(16,8))
        s.map('Accent.TButton', background=[('active',self.accent_hover),('pressed','#cc0000')])
        s.configure('Green.TButton', background=self.green_color, foreground='#fff',
                    font=('Segoe UI',10,'bold'), padding=(12,6))
        s.map('Green.TButton', background=[('active','#66BB6A')])
        s.configure('TProgressbar', background=self.accent_color, troughcolor=self.secondary_color, thickness=8)
        self.root.configure(background=self.bg_color)

    def disable_result_tabs(self):
        for i in range(4,7): self.notebook.tab(i, state="disabled")
    def enable_result_tabs(self):
        for i in range(4,7): self.notebook.tab(i, state="normal")

    def _update_details_width(self, event=None):
        for title, df in [("فیلم", self.movies_details_frame),
                          ("سریال", self.series_details_frame),
                          ("مینی سریال", self.miniseries_details_frame)]:
            if df is None or not df.winfo_exists(): continue
            parent = df.master
            if parent is None or not parent.winfo_exists(): continue
            pw = parent.winfo_width()
            if pw < 200: continue
            new_w = max(420, int(pw * DETAILS_WIDTH_RATIO))
            try: cur_w = df.winfo_width()
            except: cur_w = 0
            if abs(cur_w - new_w) > 4: df.configure(width=new_w)

    def setup_search_ui(self):
        mf = ttk.Frame(self.setup_frame); mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        hdr = ttk.Frame(mf); hdr.pack(fill=tk.X, pady=(0,15))
        ttk.Label(hdr, text="🎬 جستجوی پیشرفته فیلم و سریال", style='Title.TLabel').pack(side=tk.RIGHT)
        ttk.Label(hdr, text="AvaMovie – Selenium Edition", style='Subtitle.TLabel').pack(side=tk.RIGHT, padx=10)

        nb = ttk.Notebook(mf); nb.pack(fill=tk.BOTH, expand=True)
        msf = ttk.Frame(nb); nb.add(msf, text="  تنظیمات اصلی  ")
        asf = ttk.Frame(nb); nb.add(asf, text="  تنظیمات پیشرفته  ")
        self._build_inputs(msf, [
            ("حداقل امتیاز فیلم (0-10):","min_rating_movie",0,10,6.0,tk.DoubleVar,0.1),
            ("حداقل رای فیلم:","min_votes_movie",0,3_000_000,15000,tk.IntVar,1000),
            ("حداقل امتیاز سریال (0-10):","min_rating_series",0,10,6.0,tk.DoubleVar,0.1),
            ("حداقل رای سریال:","min_votes_series",0,3_000_000,5000,tk.IntVar,500),
            ("حداقل امتیاز مینی‌سریال (0-10):","min_rating_miniseries",0,10,6.0,tk.DoubleVar,0.1),
            ("حداقل رای مینی‌سریال:","min_votes_miniseries",0,3_000_000,5000,tk.IntVar,500),
        ])
        cy = datetime.now().year
        self._build_inputs(asf, [
            ("سال شروع:","start_year",1900,cy,2025,tk.IntVar,1),
            ("سال پایان:","end_year",1900,cy+5,cy,tk.IntVar,1),
            ("حداکثر صفحات:","max_pages",1,5000,500,tk.IntVar,10),
            ("کیفیت تصاویر (1-100):","image_quality_var",1,100,85,tk.IntVar,1),
        ])

        cf = ttk.Frame(mf); cf.pack(fill=tk.X, pady=10)
        bf = ttk.Frame(cf); bf.pack(fill=tk.X, pady=5)
        self.search_btn = ttk.Button(bf, text="🔍 شروع جستجو", command=self.start_search, style='Accent.TButton')
        self.search_btn.pack(side=tk.LEFT, padx=5)
        for txt,cmd in [("🔄 بازنشانی",self.reset_all_settings),("💾 ذخیره نتایج",self.save_results),
                        (" بارگذاری",self.load_results),(" دانلود عکس‌ها",self.download_all_images)]:
            ttk.Button(bf, text=txt, command=cmd).pack(side=tk.LEFT, padx=5)
        ttk.Separator(bf, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(bf, text="📅 امسال", command=self.set_this_year_settings, style='Green.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(bf, text="📅 پارسال", command=self.set_last_year_settings, style='Green.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Separator(bf, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        for txt,cmd in [("🇺🇸 آمریکا",self.set_usa_search_settings),("🌍 جهانی",self.set_global_search_settings),
                        ("🇷 کره",self.set_korea_search_settings),("🇮🇳 هند",self.set_india_search_settings)]:
            ttk.Button(bf, text=txt, command=cmd).pack(side=tk.LEFT, padx=3)

        for lbl,va in [("پیشرفت جستجو:","search_progress_var"),("پیشرفت دانلود:","download_progress_var")]:
            pf = ttk.Frame(cf); pf.pack(fill=tk.X, pady=4)
            ttk.Label(pf, text=lbl, font=('Segoe UI',9)).pack(side=tk.RIGHT, padx=5)
            var = tk.DoubleVar(); setattr(self, va, var)
            ttk.Progressbar(pf, variable=var, maximum=100, length=400).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        self.status_var = tk.StringVar(value="✅ آماده برای جستجو")
        ttk.Label(mf, textvariable=self.status_var, font=('Segoe UI',10,'bold'),
                  foreground=self.green_color).pack(pady=8)

    # ★ باکس و توضیحات 3 برابر درشت‌تر
    def _build_inputs(self, parent, cfgs):
        parent.grid_columnconfigure(0, weight=0, minsize=200)
        parent.grid_columnconfigure(1, weight=0)
        parent.grid_columnconfigure(2, weight=1)
        state = {'w': 0}
        def adjust(event=None):
            W = parent.winfo_width()
            if W > 250:
                new = max(300, W // 2 - 200)
                if new != state['w']:
                    state['w'] = new
                    parent.grid_columnconfigure(1, minsize=new)
        parent.bind("<Configure>", adjust)
        for r, (lbl, attr, frm, to, def_, vt, inc) in enumerate(cfgs):
            var = vt(value=def_); setattr(self, attr, var)
            try:
                w = ttk.Spinbox(parent, from_=frm, to=to, increment=inc, textvariable=var, width=30)
            except Exception:
                w = ttk.Entry(parent, textvariable=var, width=30)
            w.grid(row=r, column=0, sticky="w", padx=(30, 15), pady=15)
            ttk.Label(parent, text=lbl, font=('Segoe UI', 30, 'bold'),
                      anchor="e", justify="right").grid(row=r, column=1, sticky="e", padx=(0, 20), pady=15)
        parent.after(60, adjust)

    def setup_genres_ui(self):
        self._setup_filter_tab(self.genres_frame,"🎭 انتخاب ژانرها",GENRES,
            "genre_wanted_vars","genre_unwanted_vars",self.save_genre_selections,"genre_status_var")
    def setup_languages_ui(self):
        self._setup_filter_tab(self.languages_frame,"🌐 انتخاب زبان‌ها",LANGUAGES,
            "language_wanted_vars","language_unwanted_vars",self.save_language_selections,"language_status_var")
    def setup_countries_ui(self):
        mf = ttk.Frame(self.countries_frame); mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        ttk.Label(mf, text="🗺 انتخاب کشورها", style='Title.TLabel').pack(anchor="e", pady=(0,10))
        nb = ttk.Notebook(mf); nb.pack(fill=tk.BOTH, expand=True)
        imp = ttk.Frame(nb); nb.add(imp, text="  ⭐ کشورهای مهم  ")
        self.setup_important_countries_ui(imp)
        wf,uf = ttk.Frame(nb),ttk.Frame(nb)
        nb.add(wf, text="  ✅ کشورهای خواسته  "); nb.add(uf, text="  ❌ کشورهای ناخواسته  ")
        self.country_wanted_vars = {}; self._build_checkboxes(wf, COUNTRIES, self.country_wanted_vars)
        self.country_unwanted_vars = {}; self._build_checkboxes(uf, COUNTRIES, self.country_unwanted_vars)
        bf = ttk.Frame(mf); bf.pack(pady=10)
        ttk.Button(bf, text="💾 ذخیره انتخاب‌ها", command=self.save_country_selections,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        self.country_status_var = tk.StringVar(value="هیچ کشوری انتخاب نشده است")
        ttk.Label(bf, textvariable=self.country_status_var, foreground=self.yellow_color,
                  font=('Segoe UI',9)).pack(side=tk.LEFT, padx=15)

    def _setup_filter_tab(self, frame, title, items, w_attr, u_attr, save_cmd, status_attr):
        mf = ttk.Frame(frame); mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        ttk.Label(mf, text=title, style='Title.TLabel').pack(anchor="e", pady=(0,10))
        nb = ttk.Notebook(mf); nb.pack(fill=tk.BOTH, expand=True)
        wf,uf = ttk.Frame(nb),ttk.Frame(nb)
        nb.add(wf, text="  ✅ خواسته  "); nb.add(uf, text="  ❌ ناخواسته  ")
        wv={}; setattr(self,w_attr,wv); self._build_checkboxes(wf,items,wv)
        uv={}; setattr(self,u_attr,uv); self._build_checkboxes(uf,items,uv)
        bf = ttk.Frame(mf); bf.pack(pady=10)
        ttk.Button(bf, text="💾 ذخیره انتخاب‌ها", command=save_cmd, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        sv = tk.StringVar(value="هیچ موردی انتخاب نشده است"); setattr(self,status_attr,sv)
        ttk.Label(bf, textvariable=sv, foreground=self.yellow_color, font=('Segoe UI',9)).pack(side=tk.LEFT, padx=15)

    def _build_checkboxes(self, parent, items, var_dict):
        bf = ttk.Frame(parent); bf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(bf, text="انتخاب همه", command=lambda: self.select_all_items(var_dict)).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="پاک کردن همه", command=lambda: self.clear_all_items(var_dict)).pack(side=tk.LEFT, padx=5)
        sf = ttk.Frame(bf); sf.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        ttk.Label(sf, text="🔍 جستجو:").pack(side=tk.RIGHT, padx=5)
        sv = tk.StringVar(); ttk.Entry(sf, textvariable=sv).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        canvas = tk.Canvas(parent, bg=self.bg_color, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scf = ttk.Frame(canvas)
        scf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scf, anchor="nw"); canvas.configure(yscrollcommand=sb.set)
        rows = []
        for code,name in items:
            var = tk.BooleanVar(); var_dict[code] = var
            itf = ttk.Frame(scf); itf.pack(fill=tk.X, padx=5, pady=2)
            ttk.Checkbutton(itf, text=f"{name} ({code})", variable=var).pack(side=tk.LEFT, padx=5)
            rows.append((itf, name.lower(), code.lower()))
        def do_search(*_):
            t = sv.get().lower()
            for fr,n,c in rows:
                fr.pack(fill=tk.X, padx=5, pady=2) if (t in n or t in c) else fr.pack_forget()
        sv.trace('w', do_search)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

    def setup_important_countries_ui(self, parent):
        mf = ttk.Frame(parent); mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(mf, text="کشورهای مهم را انتخاب کنید:", font=('Segoe UI',10,'bold')).pack(anchor="e", pady=5)
        bf = ttk.Frame(mf); bf.pack(fill=tk.X, pady=5)
        ttk.Button(bf, text="انتخاب همه", command=self.select_all_important_countries).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="پاک کردن همه", command=self.clear_all_important_countries).pack(side=tk.LEFT, padx=5)
        canvas = tk.Canvas(mf, bg=self.bg_color, highlightthickness=0)
        sb = ttk.Scrollbar(mf, orient="vertical", command=canvas.yview)
        sf = ttk.Frame(canvas)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=sf, anchor="nw"); canvas.configure(yscrollcommand=sb.set)
        for code,name in IMPORTANT_COUNTRIES:
            var = tk.BooleanVar(); self.important_country_vars[code] = var
            cf = ttk.Frame(sf); cf.pack(fill=tk.X, padx=5, pady=2)
            ttk.Checkbutton(cf, text=f"{name} ({code})", variable=var).pack(side=tk.LEFT, padx=5)
            bc = ttk.Frame(cf); bc.pack(side=tk.RIGHT, padx=5)
            ttk.Button(bc, text="خواسته", command=lambda c=code: self.add_to_wanted_countries(c)).pack(side=tk.LEFT, padx=2)
            ttk.Button(bc, text="ناخواسته", command=lambda c=code: self.add_to_unwanted_countries(c)).pack(side=tk.LEFT, padx=2)
            sl = ttk.Label(bc, text="", foreground=self.yellow_color, font=('Segoe UI',9,'bold'))
            sl.pack(side=tk.LEFT, padx=5); self.important_country_status_labels[code] = sl
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

    def select_all_items(self,d):
        for v in d.values(): v.set(True)
    def clear_all_items(self,d):
        for v in d.values(): v.set(False)
    def select_all_important_countries(self):
        for v in self.important_country_vars.values(): v.set(True)
    def clear_all_important_countries(self):
        for v in self.important_country_vars.values(): v.set(False)
    def add_to_wanted_countries(self,cc):
        if cc in self.country_wanted_vars: self.country_wanted_vars[cc].set(True)
        if cc in self.country_unwanted_vars: self.country_unwanted_vars[cc].set(False)
        if cc in self.important_country_status_labels: self.important_country_status_labels[cc].config(text="✓ خواسته")
    def add_to_unwanted_countries(self,cc):
        if cc in self.country_unwanted_vars: self.country_unwanted_vars[cc].set(True)
        if cc in self.country_wanted_vars: self.country_wanted_vars[cc].set(False)
        if cc in self.important_country_status_labels: self.important_country_status_labels[cc].config(text="✗ ناخواسته")

    def save_genre_selections(self):
        self.selected_wanted_genres={g for g,v in self.genre_wanted_vars.items() if v.get()}
        self.selected_unwanted_genres={g for g,v in self.genre_unwanted_vars.items() if v.get()}
        self.genre_status_var.set(f"خواسته: {len(self.selected_wanted_genres)} | ناخواسته: {len(self.selected_unwanted_genres)}")
        messagebox.showinfo("ذخیره شد","انتخاب‌های ژانر ذخیره شدند.")
    def save_language_selections(self):
        self.selected_wanted_languages={l for l,v in self.language_wanted_vars.items() if v.get()}
        self.selected_unwanted_languages={l for l,v in self.language_unwanted_vars.items() if v.get()}
        self.language_status_var.set(f"خواسته: {len(self.selected_wanted_languages)} | ناخواسته: {len(self.selected_unwanted_languages)}")
        messagebox.showinfo("ذخیره شد","انتخاب‌های زبان ذخیره شدند.")
    def save_country_selections(self):
        self.selected_wanted_countries={c for c,v in self.country_wanted_vars.items() if v.get()}
        self.selected_unwanted_countries={c for c,v in self.country_unwanted_vars.items() if v.get()}
        self.country_status_var.set(f"خواسته: {len(self.selected_wanted_countries)} | ناخواسته: {len(self.selected_unwanted_countries)}")
        messagebox.showinfo("ذخیره شد","انتخاب‌های کشور ذخیره شدند.")

    def reset_all_settings(self):
        self.movies_data=[]; self.series_data=[]; self.miniseries_data=[]
        self.min_rating_movie.set(6.0); self.min_votes_movie.set(15000)
        self.min_rating_series.set(6.0); self.min_votes_series.set(5000)
        self.min_rating_miniseries.set(6.0); self.min_votes_miniseries.set(5000)
        self.start_year.set(2025); self.end_year.set(datetime.now().year); self.max_pages.set(500)
        for d in (self.genre_wanted_vars,self.genre_unwanted_vars,self.language_wanted_vars,
                  self.language_unwanted_vars,self.country_wanted_vars,self.country_unwanted_vars,
                  self.important_country_vars):
            for v in d.values(): v.set(False)
        for sl in self.important_country_status_labels.values(): sl.config(text="")
        for s in (self.selected_wanted_genres,self.selected_unwanted_genres,self.selected_wanted_languages,
                  self.selected_unwanted_languages,self.selected_wanted_countries,self.selected_unwanted_countries):
            s.clear()
        for g in ("Animation","Documentary"):
            if g in self.genre_unwanted_vars: self.genre_unwanted_vars[g].set(True); self.selected_unwanted_genres.add(g)
        if "US" in self.country_wanted_vars: self.country_wanted_vars["US"].set(True); self.selected_wanted_countries.add("US")
        self.genre_status_var.set("خواسته: 0 | ناخواسته: 2")
        self.language_status_var.set("هیچ زبانی انتخاب نشده است")
        self.country_status_var.set("خواسته: 1 | ناخواسته: 0")
        self.disable_result_tabs()
        for fr in (self.movies_frame,self.series_frame,self.miniseries_frame):
            for w in fr.winfo_children(): w.destroy()
        self.search_progress_var.set(0); self.download_progress_var.set(0)
        self.status_var.set("✅ تنظیمات بازنشانی شد"); self.notebook.select(0)

    def set_this_year_settings(self):
        y=datetime.now().year; self.start_year.set(y); self.end_year.set(y)
        self.min_rating_movie.set(6.0); self.min_votes_movie.set(15000)
        self.min_rating_series.set(6.0); self.min_votes_series.set(5000)
        self.min_rating_miniseries.set(6.0); self.min_votes_miniseries.set(5000)
        self.status_var.set(f"✅ تنظیمات امسال ({y}) اعمال شد.")
    def set_last_year_settings(self):
        y=datetime.now().year-1; self.start_year.set(y); self.end_year.set(y)
        self.min_rating_movie.set(6.0); self.min_votes_movie.set(70000)
        self.min_rating_series.set(6.0); self.min_votes_series.set(10000)
        self.min_rating_miniseries.set(6.0); self.min_votes_miniseries.set(10000)
        self.status_var.set(f"✅ تنظیمات پارسال ({y}) اعمال شد.")
    def _clear_country_ui(self):
        self.selected_wanted_countries.clear(); self.selected_unwanted_countries.clear()
        for d in (self.country_wanted_vars,self.country_unwanted_vars,self.important_country_vars):
            for v in d.values(): v.set(False)
        for sl in self.important_country_status_labels.values(): sl.config(text="")

    def set_usa_search_settings(self):
        self._clear_country_ui()
        if "US" in self.country_wanted_vars:
            self.country_wanted_vars["US"].set(True); self.selected_wanted_countries.add("US")
            if "US" in self.important_country_vars:
                self.important_country_vars["US"].set(True); self.important_country_status_labels.get("US").config(text="✓ خواسته")
        self.country_status_var.set("خواسته: 1 | ناخواسته: 0"); self.status_var.set("✅ تنظیمات آمریکا اعمال شد.")

    # ★ جستجوی جهانی - بدون هیچ فیلتر کشوری
    def set_global_search_settings(self):
        self._clear_country_ui()
        self.country_status_var.set("کشورهای خواسته: 0 | کشورهای ناخواسته: 0")
        self.status_var.set("✅ تنظیمات جهانی اعمال شد. (بدون فیلتر کشور)")

    def set_korea_search_settings(self):
        self._clear_country_ui()
        if "KR" in self.country_wanted_vars:
            self.country_wanted_vars["KR"].set(True); self.selected_wanted_countries.add("KR")
            if "KR" in self.important_country_vars:
                self.important_country_vars["KR"].set(True); self.important_country_status_labels.get("KR").config(text="✓ خواسته")
        self.min_votes_movie.set(1000); self.min_votes_series.set(1000); self.min_votes_miniseries.set(1000)
        self.country_status_var.set("خواسته: 1 | ناخواسته: 0"); self.status_var.set("✅ تنظیمات کره اعمال شد.")

    def set_india_search_settings(self):
        self._clear_country_ui()
        if "IN" in self.country_wanted_vars:
            self.country_wanted_vars["IN"].set(True); self.selected_wanted_countries.add("IN")
            if "IN" in self.important_country_vars:
                self.important_country_vars["IN"].set(True); self.important_country_status_labels.get("IN").config(text="✓ خواسته")
        self.country_status_var.set("خواسته: 1 | ناخواسته: 0"); self.status_var.set("✅ تنظیمات هند اعمال شد.")

    def save_results(self):
        if not any([self.movies_data,self.series_data,self.miniseries_data]):
            messagebox.showwarning("هشدار","نتیجه‌ای برای ذخیره نیست."); return
        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("فایل اکسل","*.xlsx")], title="ذخیره نتایج")
        if not fp: return
        try:
            with pd.ExcelWriter(fp, engine='openpyxl') as w:
                if self.movies_data: pd.DataFrame(self.movies_data).to_excel(w, sheet_name='فیلم‌ها', index=False)
                if self.series_data: pd.DataFrame(self.series_data).to_excel(w, sheet_name='سریال‌ها', index=False)
                if self.miniseries_data: pd.DataFrame(self.miniseries_data).to_excel(w, sheet_name='مینی سریال‌ها', index=False)
            messagebox.showinfo("موفقیت", f"ذخیره شد:\n{fp}")
        except Exception as e: messagebox.showerror("خطا", str(e))

    def load_results(self):
        fp = filedialog.askopenfilename(filetypes=[("فایل اکسل","*.xlsx")], title="بارگذاری نتایج")
        if not fp: return
        try:
            xls = pd.ExcelFile(fp)
            self.movies_data = pd.read_excel(xls,'فیلم‌ها').to_dict('records') if 'فیلم‌ها' in xls.sheet_names else []
            self.series_data = pd.read_excel(xls,'سریال‌ها').to_dict('records') if 'سریال‌ها' in xls.sheet_names else []
            self.miniseries_data = pd.read_excel(xls,'مینی سریال‌ها').to_dict('records') if 'مینی سریال‌ها' in xls.sheet_names else []
            self.show_loaded_results(); messagebox.showinfo("موفقیت", f"بارگذاری شد:\n{fp}")
        except Exception as e: messagebox.showerror("خطا", str(e))

    def show_loaded_results(self):
        self.enable_result_tabs()
        self.display_items(self.movies_data, self.movies_frame, "فیلم")
        self.display_items(self.series_data, self.series_frame, "سریال")
        self.display_items(self.miniseries_data, self.miniseries_frame, "مینی سریال")
        self.status_var.set(f"✅ بارگذاری شد. فیلم:{len(self.movies_data)} سریال:{len(self.series_data)} مینی:{len(self.miniseries_data)}")
        self.notebook.select(4)

    def start_search(self):
        self.search_btn.config(state="disabled"); self.status_var.set("⏳ در حال دریافت داده‌ها...")
        self.search_progress_var.set(0)
        try:
            params = dict(
                min_rating_movie=float(self.min_rating_movie.get()), min_votes_movie=int(self.min_votes_movie.get()),
                min_rating_series=float(self.min_rating_series.get()), min_votes_series=int(self.min_votes_series.get()),
                min_rating_miniseries=float(self.min_rating_miniseries.get()), min_votes_miniseries=int(self.min_votes_miniseries.get()),
                start_year=int(self.start_year.get()), end_year=int(self.end_year.get()), max_pages=int(self.max_pages.get()))
        except ValueError as e:
            messagebox.showerror("خطا", f"ورودی نامعتبر: {e}"); self.search_btn.config(state="normal"); return
        t = threading.Thread(target=self.perform_search, kwargs=params); t.daemon=True; t.start()

    def perform_search(self, **kw):
        try:
            wanted_countries = None
            if self.selected_wanted_countries: wanted_countries = self.selected_wanted_countries
            elif self.selected_unwanted_countries:
                wanted_countries = {c for c,_ in COUNTRIES if c not in self.selected_unwanted_countries}
            wanted_genres = self.selected_wanted_genres or None
            wanted_languages = self.selected_wanted_languages or None
            configs = [("فیلم","min_rating_movie","min_votes_movie","movies_data"),
                       ("سریال","min_rating_series","min_votes_series","series_data"),
                       ("مینی سریال","min_rating_miniseries","min_votes_miniseries","miniseries_data")]
            for step,(ct,rk,vk,da) in enumerate(configs,1):
                self.root.after(0, lambda c=ct,s=step: self.status_var.set(f"⏳ [{s}/3] دریافت {c}ها..."))
                self.root.after(0, lambda: self.search_progress_var.set(0))
                url = build_imdb_search_url(IMDB_TYPE_MAP[ct], kw["start_year"], kw["end_year"], kw[rk], kw[vk],
                                            wanted_genres, wanted_languages, wanted_countries)
                logger.info("URL (%s): %s", ct, url)
                items = self._scrape_with_driver(url, kw["max_pages"]*50)
                if self.selected_unwanted_genres:
                    items = [i for i in items if not (set(i.get("genres",[])) & self.selected_unwanted_genres)]
                if self.selected_unwanted_languages:
                    items = [i for i in items if i.get("language","") not in self.selected_unwanted_languages]
                setattr(self, da, items)
                self.root.after(0, lambda c=ct,n=len(items): self.status_var.set(f"✅ {c}: {n} نتیجه"))
            self.root.after(0, lambda: self.search_progress_var.set(100))
            self.root.after(0, self.show_results)
        except FileNotFoundError as e:
            # خطای درایور پیدا نشد
            self.root.after(0, lambda: messagebox.showerror("درایور پیدا نشد", str(e)))
            self.root.after(0, lambda: self.search_btn.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("❌ درایور Edge پیدا نشد"))
        except WebDriverException as e:
            err = str(e)
            if any(ne in err for ne in NETWORK_ERRORS):
                msg = ("❌ اتصال به اینترنت قطع شد!\n\n"
                       "لطفاً:\n"
                       "۱. اتصال اینترنت / VPN خود را بررسی کنید\n"
                       "۲. دوباره جستجو را شروع کنید\n\n"
                       f"جزئیات: {err[:200]}")
            else:
                msg = f"خطای مرورگر:\n{err[:300]}"
            logger.exception("Search error")
            self.root.after(0, lambda m=msg: messagebox.showerror("خطای اتصال", m))
            self.root.after(0, lambda: self.search_btn.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("❌ خطای اتصال — اینترنت را بررسی کنید"))
        except Exception as e:
            logger.exception("Search error")
            self.root.after(0, lambda: messagebox.showerror("خطا", f"خطا: {e}"))
            self.root.after(0, lambda: self.search_btn.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("❌ خطا در جستجو"))
        finally:
            self._quit_driver()

    def _scrape_with_driver(self, url, max_items):
        def pcb(loaded):
            self.root.after(0, lambda p=min(100, loaded / max(max_items, 1) * 100):
                            self.search_progress_var.set(p))
        return scrape_with_retry(url, max_items, progress_callback=pcb,
                                 max_retries=3, retry_delay=15)
    def _quit_driver(self):
        if self._driver:
            try: self._driver.quit()
            except: pass
            self._driver = None

    def show_results(self):
        self.enable_result_tabs()
        self.display_items(self.movies_data, self.movies_frame, "فیلم")
        self.display_items(self.series_data, self.series_frame, "سریال")
        self.display_items(self.miniseries_data, self.miniseries_frame, "مینی سریال")
        self.search_btn.config(state="normal")
        self.status_var.set(f"✅ کامل. فیلم:{len(self.movies_data)} سریال:{len(self.series_data)} مینی:{len(self.miniseries_data)}")
        self.search_progress_var.set(0); self.notebook.select(4)

    def display_items(self, items, frame, title):
        for w in frame.winfo_children(): w.destroy()
        if not items:
            ttk.Label(frame, text=f"هیچ {title}ی یافت نشد. 🔍", font=('Segoe UI',16)).pack(pady=80); return
        items.sort(key=lambda x: x.get('rating') or 0, reverse=True)

        sbar = ttk.Frame(frame); sbar.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(sbar, text="🔍 فیلتر سریع:", font=('Segoe UI',10,'bold')).pack(side=tk.RIGHT, padx=5)
        fvar = tk.StringVar(); ttk.Entry(sbar, textvariable=fvar, width=30).pack(side=tk.RIGHT, padx=5)
        count_lbl = ttk.Label(sbar, text=f"تعداد: {len(items)}", foreground=self.yellow_color, font=('Segoe UI',9))
        count_lbl.pack(side=tk.LEFT, padx=10)

        frame.update_idletasks()
        parent_w = frame.winfo_width()
        if parent_w < 200: parent_w = self.root.winfo_width()
        right_w = max(420, int(parent_w * DETAILS_WIDTH_RATIO))

        left = ttk.Frame(frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(frame, width=right_w)
        right.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        right.pack_propagate(False)

        self._details_panels[title] = right
        self._details_parents[title] = frame
        try: frame.unbind("<Configure>")
        except: pass
        frame.bind("<Configure>", lambda e, t=title: self._update_details_width())

        if title=="فیلم": self.movies_details_frame=right
        elif title=="سریال": self.series_details_frame=right
        else: self.miniseries_details_frame=right

        placeholder = ttk.Label(right, text="👆 برای مشاهده جزئیات،\nروی هر کاشی کلیک کنید",
                                font=('Segoe UI',13), wraplength=right_w-40, justify='center')
        placeholder.pack(expand=True, pady=80)

        canvas = tk.Canvas(left, bg=self.bg_color, highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        sf = ttk.Frame(canvas)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0,0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        loader = LazyImageLoader(canvas, sf)
        loader.set_image_quality(self.image_quality_var.get())
        self.image_loaders[title] = loader

        def make_hover(w):
            depth=[0]
            def enter(e):
                depth[0]+=1
                if depth[0]==1:
                    try: w.config(highlightbackground=self.accent_color, highlightthickness=2)
                    except: pass
            def leave(e):
                depth[0]-=1
                def _apply():
                    if depth[0]==0:
                        try: w.config(highlightbackground=self.border_color, highlightthickness=1)
                        except: pass
                w.after(15, _apply)
            return enter, leave

        all_tiles = []
        for item in items:
            itf = tk.Frame(sf, bg=self.card_color, highlightbackground=self.border_color,
                           highlightthickness=1, cursor="hand2")
            itf.grid_columnconfigure(0, weight=1)
            pu = upgrade_poster_url(item.get("primaryImage"), 500)
            if pu:
                pl = ttk.Label(itf, text=" در حال لود...", anchor='center')
                pl.image_url = pu; pl.pack(padx=8, pady=(8,4), fill=tk.X)
            else:
                ttk.Label(itf, text="🖼 پوستر موجود نیست", anchor='center').pack(padx=8, pady=(8,4))
            tt = item.get("primaryTitle","بدون عنوان")
            tk.Label(itf, text=tt, wraplength=190, bg=self.card_color, fg=self.fg_color,
                     font=('Segoe UI',9,'bold'), justify='center').pack(padx=8, pady=2, fill=tk.X)
            rating = item.get('rating','N/A'); year = item.get('startYear','N/A')
            rt = f"⭐ {rating}" if rating!='N/A' else ""
            tk.Label(itf, text=f"{year}  {rt}", bg=self.card_color, fg="#aaaaaa",
                     font=('Segoe UI',8)).pack(padx=8, pady=2)
            genres = item.get("genres",[])
            if genres:
                # ★ جداکننده | در نمایش UI
                gt = " | ".join(genres[:2]) + (" | ..." if len(genres) > 2 else "")
                tk.Label(itf, text=gt, wraplength=180, bg=self.card_color, fg="#888888",
                         font=('Segoe UI',8)).pack(padx=8, pady=(0,6))
            handler = lambda e,i=item,t=title: self.show_item_details(i,t)
            enter, leave = make_hover(itf)
            bind_recursive(itf, "<Button-1>", handler)
            bind_recursive(itf, "<Enter>", enter)
            bind_recursive(itf, "<Leave>", leave)
            all_tiles.append((itf, tt.lower()))

        hidden = set(); state = {'timer': None}
        def relayout():
            cw = canvas.winfo_width()
            if cw < 50: return
            canvas.itemconfigure(win_id, width=cw)
            cols = max(2, min(8, cw // 230))
            i = 0
            for itf,_ in all_tiles:
                if id(itf) in hidden: itf.grid_remove()
                else:
                    r,c = divmod(i, cols)
                    itf.grid(row=r, column=c, padx=6, pady=6, sticky="nsew"); i += 1
            for c in range(cols):
                sf.grid_columnconfigure(c, weight=1, uniform='tiles')
            loader.set_tile_width(cw // cols)
        def on_cfg(e):
            if state['timer']: self.root.after_cancel(state['timer'])
            state['timer'] = self.root.after(120, relayout)
        canvas.bind("<Configure>", on_cfg)
        def do_filter(*_):
            term = fvar.get().lower().strip(); hidden.clear()
            for itf,tl in all_tiles:
                if term and term not in tl: hidden.add(id(itf))
            relayout(); count_lbl.config(text=f"تعداد: {len(all_tiles)-len(hidden)}")
        fvar.trace('w', do_filter)
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        def on_enter(e): canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1*(ev.delta//120),"units"))
        def on_leave(e): canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", on_enter); canvas.bind("<Leave>", on_leave)
        self.root.after(50, relayout)
        loader.check_visible_widgets()
        self.root.after(3000, loader.start_retry_timer)

    def _load_poster_async(self, pu, df, img_lbl):
        def worker():
            try:
                big_url = upgrade_poster_url(pu, 1100)
                resp = requests.get(big_url, timeout=15)
                raw = Image.open(io.BytesIO(resp.content)).convert("RGB")
                raw.thumbnail((1300, 1900), Image.Resampling.LANCZOS)
                self.root.after(0, lambda: self._render_poster(raw, df, img_lbl))
            except Exception as e:
                logger.error("Poster error: %s", e)
                self.root.after(0, lambda: img_lbl.configure(text="⚠ پوستر قابل بارگذاری نیست")
                                if img_lbl.winfo_exists() else None)
        threading.Thread(target=worker, daemon=True).start()

    def _render_poster(self, raw, df, img_lbl):
        self._poster_raw = raw
        self._poster_label = img_lbl
        self._poster_df = df
        self._apply_poster_size()

    def _apply_poster_size(self, attempt=0):
        raw = self._poster_raw; lbl = self._poster_label; df = self._poster_df
        if raw is None or lbl is None or df is None or not lbl.winfo_exists():
            return
        try:
            df.update_idletasks()
            w = df.winfo_width()
            h = df.winfo_height()
        except Exception:
            w = 0; h = 0
        if w < 100 and attempt < 12:
            self.root.after(80, lambda: self._apply_poster_size(attempt + 1)); return

        target_w = max(w - 15, 200)
        max_h_by_panel = int(h * POSTER_MAX_HEIGHT_RATIO)
        target_h_by_width = int(target_w * 1.5)
        target_h = min(target_h_by_width, max_h_by_panel)
        target_h = max(target_h, 200)

        img = fit_resize(raw, target_w, target_h)
        photo = ImageTk.PhotoImage(img)
        try:
            lbl.configure(image=photo, text=""); lbl.image = photo
        except Exception:
            pass

    def show_item_details(self, item, content_type):
        df = {"فیلم":self.movies_details_frame,"سریال":self.series_details_frame,
              "مینی سریال":self.miniseries_details_frame}.get(content_type)
        if not df: return
        for w in df.winfo_children(): w.destroy()
        self.current_selected_item = item
        self._poster_raw = None; self._poster_label = None; self._poster_df = None

        dc = tk.Canvas(df, bg=self.bg_color, highlightthickness=0)
        dsb = ttk.Scrollbar(df, orient="vertical", command=dc.yview)
        dcf = ttk.Frame(dc)
        dcf.bind("<Configure>", lambda e: dc.configure(scrollregion=dc.bbox("all")))
        dc.create_window((0,0), window=dcf, anchor="nw"); dc.configure(yscrollcommand=dsb.set)

        panel_w = df.winfo_width()
        ttk.Label(dcf, text=f"🎬 {item.get('primaryTitle','N/A')}",
                  font=('Segoe UI',13,'bold'), wraplength=panel_w-40, justify='center').pack(pady=(5,3), padx=8)

        pu = item.get("primaryImage")
        if pu:
            self.current_poster_url = pu
            img_lbl = tk.Label(dcf, text="⏳ در حال بارگذاری پوستر...", bg=self.bg_color,
                               fg="#888888", font=('Segoe UI',10))
            img_lbl.pack(pady=5, padx=8, fill=tk.X)
            bf = ttk.Frame(dcf); bf.pack(pady=4)
            ttk.Button(bf, text="💾 ذخیره عکس",
                       command=lambda: self.save_poster_image(pu, item.get('primaryTitle','unknown')),
                       style='Green.TButton').pack(side=tk.LEFT, padx=4)
            if item.get('id'):
                ttk.Button(bf, text="🌐 صفحه IMDb",
                           command=lambda: webbrowser.open(f"https://www.imdb.com/title/{item['id']}/"),
                           style='Accent.TButton').pack(side=tk.LEFT, padx=4)
            self._load_poster_async(pu, df, img_lbl)
        else:
            self.current_poster_url = None
            ttk.Label(dcf, text="🖼 پوستر موجود نیست", font=('Segoe UI',12)).pack(pady=30)

        info_frame = tk.Frame(dcf, bg=self.secondary_color, highlightbackground=self.border_color, highlightthickness=1)
        info_frame.pack(fill=tk.X, padx=10, pady=8)
        votes = item.get('votes','N/A')
        votes_str = f"{votes:,}" if isinstance(votes,int) else str(votes)
        for label,value in [("عنوان اصلی:",item.get('originalTitle','N/A')),
                            ("سال ساخت:",item.get('startYear','N/A')),
                            ("مدت زمان:",item.get('duration','N/A')),
                            ("امتیاز:",f"⭐ {item.get('rating','N/A')}"),
                            ("تعداد رای:",votes_str),
                            # ★ جداکننده | در نمایش UI
                            ("ژانرها:"," | ".join(item.get('genres',[])) or 'N/A'),
                            ("کشور:",item.get('country','N/A')),
                            ("زبان:",item.get('language','N/A')),
                            ("رده‌بندی:",item.get('mpa','N/A'))]:
            rf = tk.Frame(info_frame, bg=self.secondary_color); rf.pack(fill=tk.X, padx=8, pady=2)
            tk.Label(rf, text=label, bg=self.secondary_color, fg=self.yellow_color,
                     font=('Segoe UI',9,'bold')).pack(side=tk.RIGHT)
            tk.Label(rf, text=str(value), bg=self.secondary_color, fg=self.fg_color,
                     wraplength=panel_w-60, justify='right', font=('Segoe UI',9)).pack(side=tk.RIGHT, padx=(0,8))

        plot = item.get('plot','خلاصه‌ای موجود نیست.')
        if plot:
            pf = tk.Frame(dcf, bg=self.bg_color); pf.pack(fill=tk.X, padx=10, pady=8)
            tk.Label(pf, text="📖 خلاصه داستان:", bg=self.bg_color, fg=self.accent_color,
                     font=('Segoe UI',10,'bold')).pack(anchor="e")
            tw = tk.Text(pf, wrap=tk.WORD, height=4, font=('Segoe UI',9),
                         bg=self.secondary_color, fg=self.fg_color, relief='flat', padx=8, pady=8)
            tw.insert(tk.INSERT, plot); tw.config(state=tk.DISABLED); tw.pack(fill=tk.X, pady=(5,0))

        link = item.get('link')
        if link:
            ttk.Button(dcf, text=" باز کردن در IMDb", command=lambda: webbrowser.open(link),
                       style='Accent.TButton').pack(pady=8)

        dc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); dsb.pack(side=tk.RIGHT, fill=tk.Y)
        def on_enter(e): dc.bind_all("<MouseWheel>", lambda ev: dc.yview_scroll(-1*(ev.delta//120),"units"))
        def on_leave(e): dc.unbind_all("<MouseWheel>")
        dc.bind("<Enter>", on_enter); dc.bind("<Leave>", on_leave)

    def save_poster_image(self, url, title):
        try:
            big_url = upgrade_poster_url(url, 1600)
            ct = re.sub(r'[<>:"/\\|?*]', '', title)
            fn = f"{ct}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            fp = os.path.join(self.posters_dir, fn)
            with open(fp,'wb') as f: f.write(requests.get(big_url, timeout=15).content)
            messagebox.showinfo("ذخیره شد", f"عکس ذخیره شد:\n{fp}")
        except Exception as e: messagebox.showerror("خطا", str(e))

    def download_all_images(self):
        folder = filedialog.askdirectory(title="پوشه ذخیره عکس‌ها")
        if not folder: return
        dirs = {}
        for name in ("فیلم","سریال","مینی سریال"):
            d = os.path.join(folder, name); os.makedirs(d, exist_ok=True); dirs[name] = d
        self.download_progress_var.set(0); self.status_var.set("⏳ در حال دانلود عکس‌ها...")
        t = threading.Thread(target=self._download_images_thread, args=(dirs,)); t.daemon=True; t.start()

    def _download_images_thread(self, dirs):
        try:
            all_items = ([(it,dirs["فیلم"]) for it in self.movies_data]+
                         [(it,dirs["سریال"]) for it in self.series_data]+
                         [(it,dirs["مینی سریال"]) for it in self.miniseries_data])
            total = len(all_items)
            for i,(item,folder) in enumerate(all_items):
                url = upgrade_poster_url(item.get("primaryImage"), 1200)
                if not url: continue
                ct = re.sub(r'[<>:"/\\|?*]', '', item.get("primaryTitle","unknown"))
                fn = f"{ct}_{item.get('id','unknown')}.jpg"
                try:
                    with open(os.path.join(folder, fn),'wb') as f: f.write(requests.get(url, timeout=30).content)
                except Exception as e: logger.error("DL error: %s", e)
                self.root.after(0, lambda p=(i+1)/max(total,1)*100: self.download_progress_var.set(p))
            self.root.after(0, lambda: messagebox.showinfo("موفقیت","دانلود عکس‌ها کامل شد."))
            self.root.after(0, lambda: self.status_var.set("✅ دانلود کامل شد."))
        except Exception as e: self.root.after(0, lambda: messagebox.showerror("خطا", str(e)))


# ═══════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    root.title("🎬 AvaMovie – جستجوی پیشرفته فیلم و سریال")
    root.geometry("1600x900"); root.minsize(1100, 650)
    try: root.state('zoomed')
    except: pass
    root.bind('<F11>', lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    app = IMDbApp(root)
    sbar = tk.Frame(root, bg="#0d0d0d", height=28); sbar.pack(fill=tk.X, side=tk.BOTTOM); sbar.pack_propagate(False)
    tk.Label(sbar, text="  AvaMovie v2.9 | Big Inputs + Global No Filter + , URL | F11: تمام‌صفحه | ESC: خروج",
             bg="#0d0d0d", fg="#666666", font=('Segoe UI',8)).pack(side=tk.LEFT, padx=5)
    tk.Label(sbar, text=f"  {datetime.now().strftime('%Y/%m/%d')}  ",
             bg="#0d0d0d", fg="#666666", font=('Segoe UI',8)).pack(side=tk.RIGHT, padx=5)
    root.mainloop()

if __name__ == "__main__":
    main()