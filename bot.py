
# -*- coding: utf-8 -*-
"""
Diamond Self Bot
Single-file Telegram bot + self worker.

Run:
    python bot.py

Required:
    pip install -r requirements.txt
"""

import asyncio
import base64
import logging
import contextlib
import html
import inspect
import json
import os
import random
import secrets
import tempfile
import shutil
import sys
import zipfile
import re
import sqlite3
import subprocess
import time
import urllib.request
import urllib.error
import urllib.parse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon import TelegramClient, events, Button, functions, types, utils
from telethon.tl.functions.messages import (
    SetTypingRequest,
    SendReactionRequest,
    TranslateTextRequest,
    GetInlineBotResultsRequest,
    SendInlineBotResultRequest,
    GetBotCallbackAnswerRequest,
    SendMessageRequest,
)
from telethon.tl.types import SendMessageTypingAction, ReactionEmoji, TextWithEntities
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    PhoneNumberInvalidError,
    FloodWaitError,
    MessageNotModifiedError,
)


# ============================================================
# PREMIUM CUSTOM EMOJI UI LAYER
# ============================================================

PREMIUM_EMOJI = {
    "diamond": (5823211806327316872, "💎"),
    "dollar": (5938026800524301051, "💵"),
    "phone": (5316653334688446735, "📱"),
    "crown": (6332172315735891342, "👑"),
    "shield": (5900009781539639795, "🛡️"),
    "tax": (5456398075713037730, "😂"),
    "game_result": (6269400956387987689, "📣"),
    "winner": (5193209274452425995, "🎉"),
    "loser": (6302868067407890482, "❌"),
    "game_waiting": (5467742974127385274, "⏳"),
    "daily_wait": (5467742974127385274, "⏳"),
    "daily_clock": (5778605968208170641, "🕒"),
    "restrict": (5895265582139317317, "🚫"),
    "gear": (5908996231807373361, "⚙️"),
    "pin": (5900028911323976912, "📌"),
    "rocket": (5911457793528828014, "🚀"),
    "blue": (5909174430000484676, "🔵"),
    "green": (5902255053003034414, "🟢"),
    "red": (5900154642196598737, "🟥"),
    "bell": (5900209106677687966, "🔔"),
    "lightning": (5902172654055460877, "⚡"),
    "explosion": (5902473675428335360, "💥"),
    "megaphone": (5900108844960322391, "📣"),
    "star": (5909197936356495035, "⭐"),
    "warning": (6068709585756234539, "⚠️"),
    "danger": (6068769848442235245, "❗"),
    "chat": (6069154248015224050, "💬"),
    "right": (6068808528917700855, "➡️"),
    "left": (6069106664072553799, "⬅️"),
    "check": (6068847278112646315, "✔️"),
    "cross": (6068957559987905075, "❌"),
    "clock": (6068897335956480847, "🕒"),
    "user": (6068633470345684615, "👤"),
    "down": (6070871775372124486, "🔻"),

    # Additional IDs explicitly supplied in the Premium catalogue.
    "party": (6026320431798030131, "🎉"),
    "music": (5899938145780109267, "💦"),
    "apple": (5902347480699243751, "🍏"),
    "fire": (5899988023253531794, "🔥"),
    "mindblown": (5900170756913893630, "🤯"),
    "fake": (5899802532187738550, "🚫"),
    "peach": (5899837149624144611, "🍑"),
    "eggplant": (5906983580067696316, "🍆"),
    "purple": (6068717501380829765, "🟣"),
    "orange": (6068835200646084477, "🟠"),
    "yellow": (6068637739543176251, "🟡"),
    "white": (6068938657836836444, "⚪"),
    "link": (6068828040954127646, "🔗"),
    "heart": (6069047603977265523, "❤️"),
    "flame": (6068779507823681657, "🔥"),
    "lock": (6068967356808306740, "🔒"),
    "info": (6260161223308873953, "ℹ️"),
    "order": (6260349948466828028, "📦"),
    "price": (6260483981511233469, "🏷️"),
    "discount": (6260153573972121007, "🏷️"),
    "premium": (6257907623903892878, "💎"),
    "gift": (6260176972953949338, "🎁"),
    "vip": (6260058942957689914, "👑"),
    "play": (6258044972663050814, "▶️"),
    "up": (6258061040135706479, "🔼"),
    "down_shop": (6258019585111364715, "🔽"),
    "plane": (6258305024342889201, "✈️"),
    "smile": (625823423039649553, "🙂"),
    "camera": (6258210423393227403, "📷"),
    "plus": (5780899429204631677, "➕"),
    "radio": (5900034670875120000, "📻"),
    "sos": (6069140521299746273, "🚨"),
    "question": (6069002871892879300, "❕"),
    "checkbox": (6069143703870512647, "☑️"),
    "home": (6068703547032084720, "🏠"),
    "profile": (6068633470345684615, "👤"),
    "self_status": (5257965174979042426, "❌"),
    "self_back": (5260450573768990626, "🔙"),
    "self_manage": (5242663804231255682, "⚙️"),
    "self_on": (5294173918242815387, "✅"),
    "self_off": (5296312000207405897, "❌"),
    "htx_crown": (6188028548947644497, "👑"),
    "transfer_success": (5294336053258233678, "✅"),

    # HTX wordmark — three custom emoji stylized as the letters H / T / X,
    # used as the branding line inside game messages (بازی / سنگ).
    # NOTE: the fallback must be a real emoji, not a plain letter — Telegram
    # drops a custom-emoji entity that doesn't cover an emoji (same reason
    # "$" is swapped for 💵 in premium_emoji), which left plain "HTX" text.
    "htx_h": (5935880558121850370, "🔠"),
    "htx_t": (5933634127017284729, "🔠"),
    "htx_x": (5936225259312124192, "🔠"),

    # Rock-Paper-Scissors game — premium custom emoji IDs.
    "rps_rock": (5370945676974760359, "🪨"),
    "rps_paper": (6291700259085094838, "📄"),
    "rps_scissors": (5224581755691883782, "✂️"),
    "rps_tie": (None, "🔄"),
    "rps_user": (5316887736823591263, "👤"),
    "rps_clock": (5953759695226278894, "⏰"),

    "numbers": {
        "0": (5771423202341303860, "0️⃣"),
        "1": (5771785311034021057, "1️⃣"),
        "2": (5773975314858251177, "2️⃣"),
        "3": (5771591496339820740, "3️⃣"),
        "4": (5771376816694498290, "4️⃣"),
        "5": (5771694571259958563, "5️⃣"),
        "6": (5773735118812221922, "6️⃣"),
        "7": (5773913385724809382, "7️⃣"),
        "8": (5773786959067484290, "8️⃣"),
        "9": (5774138390471512165, "9️⃣"),
    },
}

PREMIUM_GLYPH_MAP = {
    "💎": "diamond", "$": "dollar", "📱": "phone", "👑": "crown",
    "🛡️": "shield", "⚙️": "gear", "📌": "pin", "🚀": "rocket",
    "🔵": "blue", "🟢": "green", "🟥": "red", "🔔": "bell",
    "⚡": "lightning", "💥": "explosion", "📣": "megaphone",
    "⭐": "star", "⚠️": "warning", "❗": "danger", "💬": "chat",
    "➡️": "right", "⬅️": "left", "✔️": "check", "✓": "check",
    "❌": "cross", "🕒": "clock", "👤": "user", "🔻": "down",
    "🎉": "party", "💦": "music", "🍏": "apple", "🔥": "fire",
    "🤯": "mindblown", "🚫": "danger", "🍑": "peach", "🍆": "eggplant",
    "🟣": "purple", "🟠": "orange", "🟡": "yellow", "⚪": "white",
    "🔗": "link", "❤️": "heart", "🚨": "sos", "❕": "question",
    "☑️": "checkbox", "🎁": "gift", "✈️": "plane",
    "📷": "camera", "➕": "plus", "▶️": "play", "🔼": "up",
    "🔽": "down_shop", "⏳": "clock", "❤": "heart", "📦": "order",
    "⚙": "gear", "🔐": "shield", "🕐": "clock",
    "🧹": "cross", "⏱": "clock", "🏓": "play", "🤖": "shield",
    "📚": "info", "🎙": "chat", "🎬": "play", "💡": "star",
    "💳": "dollar", "🛠": "gear", "🖼": "camera", "🤵": "user",
    "💱": "dollar", "🎨": "star", "🎣": "link", "📊": "info",
    "📨": "megaphone", "🔓": "shield", "🆔": "user", "🌐": "link",
    "👁": "user", "🔒": "lock", "🏷": "price", "💰": "dollar",
    "🎲": "diamond", "🔎": "blue", "🔘": "blue",
    "📸": "camera", "🎵": "music", "🎤": "chat", "🔄": "lightning",
    "👥": "user", "🕐": "clock", "🔐": "shield", "🏠": "home",
    '☑': "checkbox",
    '⚠': "warning",
    '✅': "check",
    '✈': "plane",
    '✍': "info",
    '✏': "camera",
    '✔': "check",
    '✦': "star",
    '❶': "1",
    '❷': "2",
    '❸': "3",
    '❹': "4",
    '❺': "5",
    '❻': "6",
    '❼': "7",
    '❽': "8",
    '❾': "9",
    '➖': "plus",
    '➜': "right",
    '➡': "right",
    '🅱': "info",
    '🅵': "info",
    '🆘': "sos",
    '🎖': "premium",
    '🎮': "play",
    '🎯': "rocket",
    '🏗': "gear",
    '💵': "dollar",
    '💾': "gear",
    '📁': "order",
    '📉': "red",
    '📋': "info",
    '📝': "info",
    '📢': "megaphone",
    '📥': "down",
    '📻': "radio",
    '🔁': "lightning",
    '🔊': "chat",
    '🔑': "lock",
    '🔙': "left",
    '🔢': "info",
    '🔤': "info",
    '🔴': "red",
    '🗑': "cross",
    '🚪': "right",
    '🛑': "danger",
    '🛡': "shield",
    '🛰': "plane",
    '🧠': "mindblown",
    '🧰': "gear",
    '🧾': "order",
    '🪙': "dollar",

}

_PREMIUM_TAG_RE = re.compile(
    r"<tg-emoji\b[^>]*>.*?</tg-emoji>|<code\b[^>]*>.*?</code>|"
    r"<pre\b[^>]*>.*?</pre>",
    re.IGNORECASE | re.DOTALL,
)

_PREMIUM_MARKDOWN_RE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`", re.DOTALL)

def premium_emoji(name):
    item = PREMIUM_EMOJI.get(name)
    if not item:
        return ""
    emoji_id, fallback = item

    # Custom-emoji ids are always 19 digits. A malformed id makes Telegram
    # reject the whole message edit, so fall back to the plain emoji.
    if len(str(emoji_id)) != 19:
        return fallback

    # Telegram requires valid emoji text inside <tg-emoji>.
    # "$" is not a valid fallback, so keep a real emoji there.
    if name == "dollar" or fallback == "$":
        fallback = "💵"

    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def premium_number(value):
    raw = str(value)
    return "".join(
        f'<tg-emoji emoji-id="{PREMIUM_EMOJI["numbers"][ch][0]}">{PREMIUM_EMOJI["numbers"][ch][1]}</tg-emoji>'
        if ch in PREMIUM_EMOJI["numbers"] else ch
        for ch in raw
    )

def premium_glyph(name):
    """Like premium_emoji(), but degrades to the plain fallback glyph
    instead of a broken <tg-emoji> tag when no custom emoji ID is set yet."""
    item = PREMIUM_EMOJI.get(name)
    if not item:
        return ""
    emoji_id, fallback = item
    return premium_emoji(name) if emoji_id else fallback

def htx_wordmark():
    """The 'HTX' branding line inside game messages (بازی / سنگ): three
    custom emoji stylized as H, T, X back to back."""
    return f'{premium_emoji("htx_h")} {premium_emoji("htx_t")} {premium_emoji("htx_x")}'

async def _send_game_announcement(event, build_text, buttons, refund_uid, refund_amount):
    """event.reply() with the game text; if Telegram rejects it for any
    reason (e.g. a custom-emoji id it doesn't recognize), retry once with
    the HTX wordmark swapped for plain text instead of silently losing the
    already-deducted stake and sending nothing at all."""
    try:
        return await event.reply(premium_ui_text(build_text(True)), parse_mode="html", buttons=buttons)
    except Exception as exc:
        print(f"[GAME] send with HTX wordmark failed: {type(exc).__name__}: {exc} — retrying in plain text")
    try:
        return await event.reply(premium_ui_text(build_text(False)), parse_mode="html", buttons=buttons)
    except Exception as exc:
        print(f"[GAME] plain-text retry also failed: {type(exc).__name__}: {exc} — refunding stake")
        change_balance(refund_uid, refund_amount)
        with contextlib.suppress(Exception):
            await event.reply(
                premium_ui_text("❌ ارسال پیام بازی ناموفق بود؛ مبلغ بازگردانده شد."),
                parse_mode="html"
            )
        return None

def btn_icon_label(name, label):
    """Returns (text, icon) for btn(): custom-emoji icon + plain label once
    an ID exists in PREMIUM_EMOJI, otherwise the fallback glyph baked into
    the button text with icon=None. No other code needs to change later —
    just fill in the ID in PREMIUM_EMOJI."""
    emoji_id, fallback = PREMIUM_EMOJI.get(name, (None, ""))
    if emoji_id:
        return label, emoji_id
    return f"{fallback} {label}".strip(), None

def premium_game_amount(value):
    return f'{premium_number(_fmt_diamonds(value))} {premium_emoji("dollar")}'

def _premium_markdown_to_html(text):
    return _PREMIUM_MARKDOWN_RE.sub(
        lambda m: f"<b>{m.group(1)}</b>" if m.group(1) is not None else f"<code>{m.group(2)}</code>",
        text,
    )

def _premium_plain_segment(segment):
    # Preserve ordinary HTML tags while allowing custom emoji in text nodes.
    out = []
    pos = 0
    tag_re = re.compile(r"<(?:/?[A-Za-z][^>]*|br\s*/?)>", re.DOTALL)
    for match in tag_re.finditer(segment):
        plain = segment[pos:match.start()]
        if plain:
            out.append(_premium_markdown_to_html(plain))
        out.append(match.group(0))
        pos = match.end()
    if pos < len(segment):
        out.append(_premium_markdown_to_html(segment[pos:]))
    return "".join(out)

def premium_ui_text(text):
    """Premiumize final UI text without touching HTML tags or existing custom emoji."""
    if text is None or not isinstance(text, str) or not text:
        return text

    protected = []

    def hold(match):
        token = f"\\x00PREMIUM_PROTECTED_{len(protected)}\\x00"
        protected.append(match.group(0))
        return token

    # Convert only the supported markdown subset first.
    working = _premium_markdown_to_html(text)

    # Never touch code/pre contents.
    code_re = re.compile(
        r"<code\b[^>]*>.*?</code>|<pre\b[^>]*>.*?</pre>",
        re.IGNORECASE | re.DOTALL,
    )
    working = code_re.sub(hold, working)

    # Existing custom-emoji entities are already valid. Keep the complete
    # element intact so its fallback glyph is never replaced a second time.
    tg_emoji_re = re.compile(
        r"<tg-emoji\b[^>]*>.*?</tg-emoji>",
        re.IGNORECASE | re.DOTALL,
    )
    working = tg_emoji_re.sub(hold, working)

    # Protect every remaining HTML tag. Glyph replacement must happen only
    # in actual text nodes, never in attributes such as href/alt.
    html_tags = []

    def hold_tag(match):
        token = f"\\x00PREMIUM_TAG_{len(html_tags)}\\x00"
        html_tags.append(match.group(0))
        return token

    working = re.sub(
        r"<(?:/?[A-Za-z][^>]*|br\s*/?)>",
        hold_tag,
        working,
        flags=re.DOTALL,
    )

    glyph_pattern = re.compile(
        "|".join(
            re.escape(g)
            for g in sorted(PREMIUM_GLYPH_MAP, key=len, reverse=True)
        )
    )
    working = glyph_pattern.sub(
        lambda m: premium_emoji(PREMIUM_GLYPH_MAP[m.group(0)]),
        working,
    )

    # Restore HTML tags first, then protected blocks/custom emoji.
    for idx, original in enumerate(html_tags):
        working = working.replace(
            f"\\x00PREMIUM_TAG_{idx}\\x00", original
        )
    for idx, original in enumerate(protected):
        working = working.replace(
            f"\\x00PREMIUM_PROTECTED_{idx}\\x00", original
        )

    return working


# ============================================================
# CONFIG
# ============================================================

API_ID = 32955870
API_HASH = "a40ba705a967c3c8e490f4684f42256a"

BOT_TOKEN = "8916268511:AAFWoxqnCM-PgaU30JDHG8fcYljOvLDyWOE"
ADMINS = [7727625618]

CARD_NUMBER = "5022291579049451"
CARD_HOLDER = "علی محمدی پور"

SELF_HOURLY_COST = 5
SELF_CLOCK_UPDATE_INTERVAL = 1
MIN_SELF_BALANCE = 100
MIN_DIAMOND_PURCHASE = 1000
DIAMOND_PRICE_TOMAN = 40

# Local, free speech-to-text configuration.
# No API key is required. The Persian STT engine is faster-whisper + Whisper large-v3.
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "fa")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE",
    "int8" if WHISPER_DEVICE == "cpu" else "float16",
)
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
WHISPER_BEST_OF = int(os.getenv("WHISPER_BEST_OF", "8"))
WHISPER_PATIENCE = float(os.getenv("WHISPER_PATIENCE", "1.2"))

# Free providers for currency and local media features
# Dollar prices come from CoinMarketCap first, then CoinGecko as a
# fallback — both are public/global services reachable from any host
# (unlike Nobitex, which throttles or blocks requests from non-Iranian
# IPs, e.g. cloud hosts like Railway, so it isn't used at all here).
# The Toman price is independently derived from a live USDT/Toman market
# midpoint (see _get_usd_irt_rate). USDT is a proxy, not guaranteed to equal
# the cash USD rate.
CMC_PUBLIC_BASE_URL = "https://pro-api.coinmarketcap.com/public-api"
COINGECKO_PUBLIC_BASE_URL = "https://api.coingecko.com/api/v3"
FRANKFURTER_PUBLIC_BASE_URL = "https://api.frankfurter.dev/v2"
GOLD_SPOT_URL = "https://xaus.com/api/v1/spot"
GOLD_HISTORY_URL = "https://xaus.com/api/v1/history"
# Wallex's public USDTTMN order book is the primary market-price source.
WALLEX_DEPTH_URL = "https://api.wallex.ir/v1/depth"
# Keyless Bonbast mirror is retained only as a fallback if Wallex is unreachable.
BONBAST_MIRROR_URL = "https://bonbast.amirhn.com"
CRYPTO_PROVIDER_TIMEOUT = 12

TRANSFER_TAX = 0.10
GAME_TAX = 0.10
GAME_TIMEOUT = 300

# The BOT-side game/balance features are available only in the official group.
# This restriction does NOT affect the logged-in SELF workers.
OFFICIAL_GROUP_USERNAME = "DimondSelfGap"
OFFICIAL_GROUP_ID = None
BOT_ENABLED_KEY = "bot_enabled"
BOT_UPDATE_TEXT = "ربات درحال آپدیت هست ، لطفاً منتظر بمونید!"
REFERRAL_REWARD = 70
MIN_GAME = 20
MIN_TRANSFER = 10

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "database_users"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BOT_IMAGE_PATH = BASE_DIR / "1782502761872.jpg"

# ============================================================
# DATABASE
# ============================================================

def db_path(user_id: int) -> Path:
    return DATA_DIR / f"user_{int(user_id)}.db"


def connect_db(user_id: int):
    conn = sqlite3.connect(db_path(user_id), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_user_db(user_id: int):
    with connect_db(user_id) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0,
                banned INTEGER NOT NULL DEFAULT 0,
                invited_by INTEGER NOT NULL DEFAULT 0,
                referral_reward_claimed INTEGER NOT NULL DEFAULT 0,
                self_start_time INTEGER NOT NULL DEFAULT 0,
                self_enabled INTEGER NOT NULL DEFAULT 0,
                phone_number TEXT
            )
        """)
        columns = {row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()}
        if "phone_number" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")

        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS self_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_string TEXT NOT NULL,
                sub_type INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                start_time INTEGER NOT NULL DEFAULT 0
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER PRIMARY KEY,
                reward_claimed INTEGER NOT NULL DEFAULT 0
            )
        """)
        db.execute("""
            INSERT OR IGNORE INTO users
            (user_id, balance, banned, invited_by, referral_reward_claimed,
             self_start_time, self_enabled, phone_number)
            VALUES (?, 0, 0, 0, 0, 0, 0, NULL)
        """, (user_id,))


def get_balance(user_id: int) -> float:
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()
        return float(row[0]) if row else 0.0


def _fmt_diamonds(value) -> str:
    value = float(value or 0)
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.1f}".rstrip("0").rstrip(".")


def _fmt_diamonds_plain(value) -> str:
    value = float(value or 0)
    if value.is_integer():
        return f"{int(value)}"
    return f"{value:.1f}".rstrip("0").rstrip(".")


def get_phone_number(user_id: int):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute("SELECT phone_number FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row[0] if row and row[0] else None


def normalize_iran_phone(value: str):
    """Normalize a shared-contact phone number to E.164. Despite the name,
    this now accepts any country's number, not just Iran (+98)."""
    if not value:
        return None
    value = str(value).strip().translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    value = re.sub(r"[\s()\-]", "", value)
    if value.startswith("0098"):
        value = "+98" + value[4:]
    elif value.startswith("09"):
        value = "+98" + value[1:]
    elif value.startswith("00"):
        value = "+" + value[2:]
    elif not value.startswith("+"):
        value = "+" + value
    if not re.fullmatch(r"\+[1-9]\d{7,14}", value):
        return None
    return value


def save_phone_number(user_id: int, phone: str):
    normalized = normalize_iran_phone(phone)
    if not normalized:
        return False
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute("UPDATE users SET phone_number=? WHERE user_id=?", (normalized, user_id))
    return True


def has_registered_phone(user_id: int) -> bool:
    return bool(get_phone_number(user_id))


async def send_phone_request(user_id: int):
    await bot.send_message(
        user_id,
        premium_ui_text("📱 برای ادامه، شماره موبایل خودت را از دکمه زیر به اشتراک بگذار."),
        buttons=[[Button.request_phone("اشتراک‌گذاری شماره", resize=True, style="success", icon=5258337316715373336)]],
    parse_mode="html")


def change_balance(user_id: int, amount: float):
    """Balances are always whole diamonds. Rounding the *result* (not just
    the increment) here also self-heals any already-fractional balance the
    next time it changes, not only future ones."""
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute(
            "UPDATE users SET balance = ROUND(balance + ?) WHERE user_id=?",
            (float(amount), user_id)
        )


def is_banned(user_id: int) -> bool:
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute(
            "SELECT banned FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()
        return bool(row and row[0])


def set_banned(user_id: int, value: bool):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute(
            "UPDATE users SET banned=? WHERE user_id=?",
            (1 if value else 0, user_id)
        )


def get_setting(user_id: int, key: str, default=None):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        ).fetchone()
        return row[0] if row else default


def set_setting(user_id: int, key: str, value):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
            (key, str(value))
        )


def get_active_session(user_id: int):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute("""
            SELECT session_string, sub_type, start_time
            FROM self_sessions
            WHERE is_active=1
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()
        return row


def save_active_session(user_id: int, session_string: str, sub_type: int):
    now = int(time.time())
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute("UPDATE self_sessions SET is_active=0")
        db.execute("""
            INSERT INTO self_sessions
            (session_string, sub_type, is_active, start_time)
            VALUES (?, ?, 1, ?)
        """, (session_string, sub_type, now))
        db.execute("""
            UPDATE users
            SET self_start_time=?, self_enabled=1
            WHERE user_id=?
        """, (now, user_id))


def deactivate_session(user_id: int):
    init_user_db(user_id)
    with connect_db(user_id) as db:
        db.execute("UPDATE self_sessions SET is_active=0")
        db.execute("""
            UPDATE users
            SET self_start_time=0, self_enabled=0
            WHERE user_id=?
        """, (user_id,))


def get_last_session(user_id: int):
    """Most recent session row regardless of is_active -- used to resume a
    disabled self (see reactivate_last_session) without a fresh login."""
    init_user_db(user_id)
    with connect_db(user_id) as db:
        row = db.execute("""
            SELECT session_string, sub_type, start_time
            FROM self_sessions
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()
        return row


def reactivate_last_session(user_id: int):
    """«روشن کردن»: turn a disabled self back on using its existing
    session_string -- no new login/OTP, unlike buy_self. Re-marks the most
    recent session row active. Returns (session_string, sub_type) or None
    if this account never had a self session at all."""
    init_user_db(user_id)
    now = int(time.time())
    with connect_db(user_id) as db:
        row = db.execute(
            "SELECT id, session_string, sub_type FROM self_sessions ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        session_id, session_string, sub_type = row
        db.execute("UPDATE self_sessions SET is_active=0")
        db.execute("UPDATE self_sessions SET is_active=1, start_time=? WHERE id=?", (now, session_id))
        db.execute("UPDATE users SET self_start_time=?, self_enabled=1 WHERE user_id=?", (now, user_id))
    return session_string, int(sub_type)


def all_active_sessions():
    result = []
    for file in DATA_DIR.glob("user_*.db"):
        match = re.fullmatch(r"user_(\d+)\.db", file.name)
        if not match:
            continue
        user_id = int(match.group(1))
        try:
            row = get_active_session(user_id)
            if row:
                result.append((user_id, row[0], int(row[1])))
        except Exception as exc:
            print(f"[DB] failed to load {user_id}: {exc}")
    return result


def total_diamonds_in_circulation() -> float:
    """Return the sum of all user balances stored in database_users."""
    total = 0.0
    for file in DATA_DIR.glob("user_*.db"):
        match = re.fullmatch(r"user_(\d+)\.db", file.name)
        if not match:
            continue
        user_id = int(match.group(1))
        try:
            init_user_db(user_id)
            with connect_db(user_id) as db:
                row = db.execute("SELECT COALESCE(balance, 0) FROM users WHERE user_id=?", (user_id,)).fetchone()
                if row:
                    total += float(row[0] or 0)
        except Exception as exc:
            print(f"[DB] failed to sum balance for {user_id}: {exc}")
    return total


# ============================================================
# BOT STATE
# ============================================================

bot = TelegramClient(
    str(BASE_DIR / "diamond_bot"),
    API_ID,
    API_HASH
)

pending = {}
purchase_state = {}
active_games = {}
active_rps_games = {}
self_workers = {}
self_clients = {}
_self_reply_cache = set()
_secretary_reply_cache = {}
_spam_tasks = {}

_inline_bot_cache = {}
_cleanup_tasks = {}
_cleanup_panel_messages = {}

# Channel-save is deliberately isolated: one in-memory session and one worker
# per owner. The progress message is always the exact same panel message.
_channel_save_sessions = {}
_channel_save_tasks = {}
_first_comment_ui_target = {}
_first_comment_channel_sessions = {}
_first_comment_sent_cache = set()
# Independent state for media conversions; never shares channel-save state.
media_convert_state = {}
# Independent state for voice -> text jobs.  Kept separate from media conversion
# so a slow Whisper/OpenAI request can never leave a stale "processing" flag.
stt_state = {}
# Last N incoming private messages per chat. Used only as a short-lived
# deletion snapshot so a user-cleared chat can be archived without scanning
# the whole conversation.
HTX_DELETE_SNAPSHOT_SIZE = 15      # max messages archived per deletion (wherever in the chat they were)
HTX_SNAPSHOT_CACHE_SIZE = 50       # incoming messages remembered per chat, so a message deleted far up the chat can still be recovered
_deleted_message_cache = {}
# MessageDeleted updates for private chats do not reliably carry the peer/chat id.
# Keep a tiny message-id -> chat index so an immediately deleted message can
# still be mapped back to the correct private conversation.
_deleted_message_index = {}
# Chats whose cache was already back-filled from the real server history, so
# messages received long before (or before a restart of) the bot are covered.
_snapshot_seeded = set()
_snapshot_seed_tasks = set()
# Ids already archived to Saved Messages (never archive the same message twice).
_snapshot_archived = set()
HTX_SNAPSHOT_SEED_DIALOGS = 40
# «اسنپ شات گپ»: only REPLY messages sent inside a group are kept, just long
# enough to recover their text/sender/chat if the reply itself gets deleted.
# Keyed by (uid, message_id) only — the cached message already carries its
# own chat_id, so unlike the private-chat cache above there is no need to
# resolve the chat from the deletion event at all.
HTX_SNAP_GROUP_CACHE_SIZE = 300
_snap_group_cache = {}
_snap_group_order = {}



# ============================================================
# INLINE BUTTON STYLE COMPATIBILITY
# ============================================================

def _button_style(text: str, data: bytes = b"") -> str:
    """Semantic style selection: success=positive, primary=management, danger=destructive."""
    label = (text or "").casefold()
    raw = data.decode("utf-8", errors="ignore").casefold() if isinstance(data, (bytes, bytearray)) else str(data).casefold()
    danger_words = ("لغو", "حذف", "توقف", "خاموش", "خروج", "رد", "مسدود", "بستن", "پاک", "disable", "delete", "stop", "cancel", "close", "reject")
    success_words = ("تأیید", "تایید", "خرید", "ارسال", "اجرا", "فعال", "پیوستن", "پرداخت", "ساخت", "روشن", "refresh", "update", "join", "confirm", "send", "enable")
    if any(w in label or w in raw for w in danger_words):
        return "danger"
    if any(w in label or w in raw for w in success_words):
        return "success"
    return "primary"


def btn(text: str, data, style: str | None = None, icon=None):
    """Real Telegram inline button, optionally with a custom-emoji icon."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    if data == b"fj_add":
        return Button.inline(text, b"fj_add", style="success", icon=5780899429204631677)
    if style == "none":
        # Neutral / uncoloured button: no style argument at all (used for the
        # page-navigation row, where only the active page is coloured).
        try:
            if icon is not None:
                return Button.inline(text, data, icon=icon)
            return Button.inline(text, data)
        except Exception:
            return Button.inline(text, data)
    chosen = style or _button_style(text, data)
    # Back/cancel buttons are always red/danger, regardless of caller style.
    if any(w in (text or '').casefold() for w in ('بازگشت', 'برگشت', 'لغو', 'cancel', 'back')):
        chosen = 'danger'
    try:
        return Button.inline(text, data, style=chosen, icon=icon)
    except TypeError:
        # Older Telethon versions do not know the icon= argument.
        if icon is not None:
            fallback = "💎 " if icon == PREMIUM_EMOJI.get("diamond", (None,))[0] else ""
            return Button.inline(fallback + text, data, style=chosen)
        return Button.inline(text, data, style=chosen)
    except Exception:
        if icon is not None:
            fallback = "💎 " if icon == PREMIUM_EMOJI.get("diamond", (None,))[0] else ""
            return Button.inline(fallback + text, data)
        return Button.inline(text, data)


# ============================================================
# FORCE JOIN + BACKUP
# ============================================================

FORCE_JOIN_KEY = "force_join_channels"
SUPPORT_USERNAME = "HusteRIX"
BACKUP_PREFIX = "husterix_backup_"
MAX_BACKUP_BYTES = 100 * 1024 * 1024


def _admin_state(key: str, default=None):
    return get_setting(int(ADMINS[0]), key, default) if ADMINS else default


def _set_admin_state(key: str, value):
    if ADMINS:
        set_setting(int(ADMINS[0]), key, value)


# ============================================================
# GIFT CODES
# ============================================================

GIFT_CODES_KEY = "gift_codes_v1"
_gift_lock = asyncio.Lock()


def _gift_codes():
    try:
        raw = _admin_state(GIFT_CODES_KEY, "[]")
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, list):
            return []
        out = []
        for item in data:
            if not isinstance(item, dict):
                continue
            code = str(item.get("code", "")).strip()
            if not code:
                continue
            try:
                reward = int(item.get("reward", 0))
                expires_at = float(item.get("expires_at", 0))
            except (TypeError, ValueError):
                continue
            used_by = item.get("used_by", [])
            if not isinstance(used_by, list):
                used_by = []
            out.append({
                "code": code,
                "reward": max(0, reward),
                "expires_at": expires_at,
                "created_at": float(item.get("created_at", time.time()) or time.time()),
                "used_by": [int(x) for x in used_by if str(x).lstrip("-").isdigit()],
            })
        return out
    except Exception:
        return []


def _save_gift_codes(codes):
    _set_admin_state(GIFT_CODES_KEY, json.dumps(codes, ensure_ascii=False))


def _gift_duration(raw: str):
    value = _fa_digits(str(raw or "").strip().casefold())
    match = re.fullmatch(r"(\d+)\s*(دقیقه|دقيقه|دقیقه‌|ساعت|روز|هفته|minute|minutes|min|hour|hours|hr|day|days|week|weeks)", value)
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    factors = {
        "دقیقه": 60, "دقيقه": 60, "دقیقه‌": 60,
        "minute": 60, "minutes": 60, "min": 60,
        "ساعت": 3600, "hour": 3600, "hours": 3600, "hr": 3600,
        "روز": 86400, "day": 86400, "days": 86400,
        "هفته": 604800, "week": 604800, "weeks": 604800,
    }
    seconds = amount * factors[unit]
    if amount <= 0 or seconds > 3650 * 86400:
        return None
    return seconds


def _gift_code_valid(code: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,40}", str(code or "").strip()))


def _gift_active_codes():
    now = time.time()
    return [c for c in _gift_codes() if float(c.get("expires_at", 0)) > now and c.get("reward", 0) > 0]


def _gift_format_expiry(expires_at: float) -> str:
    return datetime.fromtimestamp(float(expires_at), tz=ZoneInfo("Asia/Tehran")).strftime("%Y/%m/%d - %H:%M")


def _gift_admin_menu_text():
    active = _gift_active_codes()
    return (
        "🎁 <b>مدیریت کدهای هدیه</b>\n\n"
        f"🎟 کدهای فعال: <b>{len(active):,}</b>\n"
        "\n"
        "از این بخش می‌توانی کد هدیه بسازی یا کدهای جاری را مدیریت کنی.\n"
        "هر کد پس از پایان زمان تعیین‌شده خودکار منقضی می‌شود."
    )


def _gift_admin_menu_buttons():
    return [
        [
            btn("ساخت", b"gift_create", "success", icon=PREMIUM_EMOJI["gift"][0]),
            btn("مدیریت", b"gift_manage", "primary", icon=PREMIUM_EMOJI["gift"][0]),
        ],
        [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])],
    ]


def _gift_redeem_text():
    return (
        "🎁 <b>کد هدیه</b>\n\n"
        "یک کد هدیه داری؟ خیلی راحت واردش کن تا پاداش الماسی آن به حسابت اضافه شود.\n\n"
        "🎟 <b>کد هدیه را همین‌جا ارسال کن:</b>\n"
        "<i>مثال: GIFT2026</i>\n\n"
        "⚠️ هر کد فقط یک‌بار برای هر کاربر قابل استفاده است و بعد از انقضا دیگر قابل دریافت نیست."
    )


def is_bot_enabled() -> bool:
    """Return whether the BOT-side features are enabled. SELF workers are independent."""
    return str(_admin_state(BOT_ENABLED_KEY, "on")).lower() == "on"


def set_bot_enabled(enabled: bool):
    _set_admin_state(BOT_ENABLED_KEY, "on" if enabled else "off")


async def resolve_official_group_id():
    """Resolve the official group once after the BOT client is connected."""
    global OFFICIAL_GROUP_ID
    try:
        entity = await bot.get_entity("@" + OFFICIAL_GROUP_USERNAME)
        OFFICIAL_GROUP_ID = int(utils.get_peer_id(entity, add_mark=True))
        print(f"[BOT GROUP] Official group @{OFFICIAL_GROUP_USERNAME} -> {OFFICIAL_GROUP_ID}")
    except Exception as exc:
        OFFICIAL_GROUP_ID = None
        print(f"[BOT GROUP] Failed to resolve @{OFFICIAL_GROUP_USERNAME}: {exc}")
    return OFFICIAL_GROUP_ID


async def is_official_group_event(event) -> bool:
    """True only for messages/callbacks originating from the official group."""
    global OFFICIAL_GROUP_ID
    if not (getattr(event, "is_group", False) or getattr(event, "is_channel", False)):
        return False
    chat_id = getattr(event, "chat_id", None)
    if chat_id is None:
        return False
    if OFFICIAL_GROUP_ID is None:
        await resolve_official_group_id()
    return OFFICIAL_GROUP_ID is not None and int(chat_id) == int(OFFICIAL_GROUP_ID)


async def cancel_all_active_games_for_update():
    """Cancel pending BOT games safely when the BOT is put into update mode."""
    games = list(active_games.items())
    active_games.clear()
    for (chat_id, message_id), game in games:
        organizer = int(game.get("organizer", 0))
        amount = int(game.get("amount", 0))
        task = game.get("task")
        if task:
            task.cancel()
        if organizer and amount > 0:
            change_balance(organizer, amount)
        with contextlib.suppress(Exception):
            await bot.delete_messages(chat_id, message_id)
        if organizer:
            with contextlib.suppress(Exception):
                await bot.send_message(
                    organizer,
                    premium_ui_text(f"❌ بازی به دلیل فعال شدن حالت آپدیت لغو شد.\n💎 {amount} الماس به حساب شما برگشت.")
                , parse_mode="html")

    rps_games = list(active_rps_games.items())
    active_rps_games.clear()
    for (chat_id, message_id), game in rps_games:
        amount = int(game.get("amount", 0))
        task = game.get("task")
        if task:
            task.cancel()
        p1 = int(game.get("p1", 0))
        p2 = game.get("p2")
        if p1 and amount > 0:
            change_balance(p1, amount)
        if p2 and amount > 0:
            change_balance(int(p2), amount)
        with contextlib.suppress(Exception):
            await bot.delete_messages(chat_id, message_id)
        for uid in filter(None, [p1, p2]):
            with contextlib.suppress(Exception):
                await bot.send_message(
                    int(uid),
                    premium_ui_text(f"❌ بازی سنگ‌کاغذقیچی به دلیل فعال شدن حالت آپدیت لغو شد.\n💎 {amount} الماس به حساب شما برگشت.")
                , parse_mode="html")


def get_force_join_channels():
    try:
        raw = json.loads(_admin_state(FORCE_JOIN_KEY, "[]"))
        return raw if isinstance(raw, list) else []
    except Exception:
        return []


def save_force_join_channels(channels):
    _set_admin_state(FORCE_JOIN_KEY, json.dumps(channels, ensure_ascii=False))


def _channel_url(channel):
    username = str(channel.get("username") or "").lstrip("@")
    if username:
        return f"https://t.me/{username}"
    return channel.get("url") or ""


async def _is_joined_channel(user_id: int, channel):
    try:
        entity_ref = channel.get("username") or channel.get("id")
        entity = await bot.get_entity(entity_ref)
        participant = await bot(functions.channels.GetParticipantRequest(
            channel=entity,
            participant=await bot.get_input_entity(user_id),
        ))
        return isinstance(
            getattr(participant, "participant", None),
            (types.ChannelParticipant, types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        )
    except Exception:
        # A bot that cannot verify a channel must fail closed for force-join.
        return False


async def get_missing_force_joins(user_id: int):
    missing = []
    for channel in get_force_join_channels():
        if not await _is_joined_channel(user_id, channel):
            missing.append(channel)
    return missing


def force_join_buttons(channels):
    rows = []
    for channel in channels:
        url = _channel_url(channel)
        title = str(channel.get("title") or channel.get("username") or "کانال")
        if url:
            rows.append([Button.url(f"📢 {title}", url)])
    rows.append([btn("🟢 عضو شدم، ادامه", b"fj_check", "success")])
    return rows


async def show_force_join(event, channels=None):
    channels = channels if channels is not None else get_force_join_channels()
    if not channels:
        return False
    link_lines = []
    for channel in channels:
        title = html.escape(str(channel.get("title") or channel.get("username") or "کانال"))
        url = _channel_url(channel)
        if url:
            link_lines.append(f'• <a href="{html.escape(url, quote=True)}">📢 {title}</a>')
        else:
            link_lines.append(f"• {title}")
    text = (
        "📢 <b>عضویت اجباری</b>\n\n"
        "برای ادامه، روی نام هر کانال/گروه زیر بزن و عضو شو:\n\n"
        + "\n".join(link_lines)
        + "\n\nبعد از عضویت روی «🟢 عضو شدم، ادامه» بزن."
    )
    await edit_or_send(event, text, force_join_buttons(channels))
    return True


async def ensure_force_join(user_id: int, event=None, notify=True):
    if user_id in ADMINS:
        return True
    missing = await get_missing_force_joins(user_id)
    if not missing:
        return True
    if not notify:
        pass
    elif event is not None:
        await show_force_join(event, missing)
    else:
        await bot.send_message(
            user_id,
            premium_ui_text("🔐 برای ادامه ابتدا عضو کانال‌های اجباری شوید."),
            buttons=force_join_buttons(missing)
        , parse_mode="html")
    return False


def _safe_backup_member(name: str):
    p = Path(name)
    return not p.is_absolute() and ".." not in p.parts


def _backup_sqlite_database(source: Path, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_conn = sqlite3.connect(source, timeout=30)
    dest_conn = sqlite3.connect(destination, timeout=30)
    try:
        source_conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
        source_conn.backup(dest_conn)
        dest_conn.commit()
    finally:
        dest_conn.close()
        source_conn.close()


def create_backup_sync():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_root = Path(tempfile.mkdtemp(prefix="husterix_backup_build_"))
    archive = BASE_DIR / f"{BACKUP_PREFIX}{stamp}.zip"
    try:
        db_copy = temp_root / "database_users"
        db_copy.mkdir(parents=True, exist_ok=True)
        for source in DATA_DIR.glob("user_*.db"):
            if source.is_file():
                _backup_sqlite_database(source, db_copy / source.name)

        media_source = BASE_DIR / "banner_media"
        media_copy = temp_root / "banner_media"
        if media_source.is_dir():
            shutil.copytree(media_source, media_copy)

        manifest = {
            "format": 2,
            "created_at": datetime.now().isoformat(),
            "database_dir": "database_users",
            "banner_media_dir": "banner_media",
            "force_join_channels": get_force_join_channels(),
        }
        (temp_root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in temp_root.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(temp_root).as_posix())
        return archive
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def inspect_backup_sync(archive_path: Path):
    if archive_path.stat().st_size > MAX_BACKUP_BYTES:
        raise RuntimeError("backup_too_large")
    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            raise RuntimeError("backup_manifest_missing")
        if not all(_safe_backup_member(n) for n in names):
            raise RuntimeError("backup_path_traversal")
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        if int(manifest.get("format", 0)) not in {1, 2}:
            raise RuntimeError("backup_format")
        if not any(n.startswith("database_users/") for n in names):
            raise RuntimeError("backup_database_missing")
        if int(manifest.get("format", 1)) >= 2 and not any(n.startswith("banner_media/") for n in names):
            # banner_media is optional when there were no banner files; the DB remains authoritative.
            if manifest.get("banner_media_dir") != "banner_media":
                raise RuntimeError("backup_media_manifest")
        return manifest


def restore_backup_sync(archive_path: Path):
    manifest = inspect_backup_sync(archive_path)
    restore_root = Path(tempfile.mkdtemp(prefix="husterix_restore_"))
    old_root = BASE_DIR / f".database_users_old_{secrets.token_hex(6)}"
    old_media = BASE_DIR / f".banner_media_old_{secrets.token_hex(6)}"
    media_replaced = False
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(restore_root)
        extracted = restore_root / "database_users"
        if not extracted.is_dir():
            raise RuntimeError("backup_database_missing")

        extracted_media = restore_root / "banner_media"
        os.replace(DATA_DIR, old_root)
        os.replace(extracted, DATA_DIR)

        if extracted_media.is_dir():
            current_media = BASE_DIR / "banner_media"
            if current_media.exists():
                os.replace(current_media, old_media)
            os.replace(extracted_media, current_media)
            media_replaced = True

        fj = manifest.get("force_join_channels")
        if isinstance(fj, list):
            save_force_join_channels(fj)

        shutil.rmtree(old_root, ignore_errors=True)
        if media_replaced:
            shutil.rmtree(old_media, ignore_errors=True)
        return manifest
    except Exception:
        if not DATA_DIR.exists() and old_root.exists():
            os.replace(old_root, DATA_DIR)
        if media_replaced:
            current_media = BASE_DIR / "banner_media"
            if current_media.exists():
                shutil.rmtree(current_media, ignore_errors=True)
            if old_media.exists():
                os.replace(old_media, current_media)
        raise
    finally:
        shutil.rmtree(restore_root, ignore_errors=True)


async def stop_all_self_workers_for_backup():
    users = list(self_clients.keys())
    for uid in users:
        with contextlib.suppress(Exception):
            deactivate_session(uid)
        task = self_workers.get(uid)
        if task:
            task.cancel()
        client = self_clients.get(uid)
        if client:
            with contextlib.suppress(Exception):
                await client.disconnect()
    await asyncio.sleep(0.2)
    self_workers.clear()
    self_clients.clear()


# ============================================================
# UI
# ============================================================

def main_buttons(user_id: int):
    rows = [
        [btn("خرید سلف", b"buy_self", "success", icon=5823211806327316872)],
        [
            btn("حساب کاربری", b"user_account", "primary", icon=5258362837411045098),
            btn("مدیریت سلف", b"manage_self", "primary", icon=5226513232549664618),
        ],
        [btn("خرید موجودی", b"buy_balance", "success", icon=5769126056262898415)],
        [
            Button.url("پشتیبانی", "https://t.me/HusteRIX", style="danger", icon=5258337316715373336),
            Button.url("چنل", "https://t.me/HusteRIXDimondSelf", style="danger", icon=6021418126061605425),
        ],
        [btn("الماس رایگان", b"referral_system", "success", icon=5197350061012436657)],
    ]
    # «مدیریت» now lives inside «حساب کاربری» (admins only).
    return rows


def user_account_buttons(user_id: int):
    """«حساب کاربری»: admin -> [کد هدیه | مدیریت] / [بازگشت];
    everyone else -> [کد هدیه] / [بازگشت]."""
    gift = btn("کد هدیه", b"gift_redeem", "success", icon=PREMIUM_EMOJI["gift"][0])
    if user_id in ADMINS:
        # Keyboard order is left-to-right, so «کد هدیه» sits on the right for RTL readers.
        first_row = [btn("مدیریت", b"admin_panel", "primary", icon=5258514780469075716), gift]
    else:
        first_row = [gift]
    return [first_row, [btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]


async def send_main(target, user_id: int, text=f"{premium_emoji('htx_crown')} <b>پنل اصلی Self 𝑯𝑻𝑿</b>"):
    buttons = main_buttons(user_id)
    if BOT_IMAGE_PATH.exists():
        return await bot.send_file(
            target,
            BOT_IMAGE_PATH,
            caption=premium_ui_text(text),
            buttons=buttons
        , parse_mode="html")
    return await bot.send_message(target, premium_ui_text(text), buttons=buttons, parse_mode="html")


async def safe_answer(event, text="", alert=False):
    with contextlib.suppress(Exception):
        await event.answer(text, alert=alert)


async def _with_timeout(coro, timeout=10):
    return await asyncio.wait_for(coro, timeout=float(timeout))


async def edit_or_send(event, text, buttons=None):
    text = premium_ui_text(text)
    try:
        await event.edit(text, buttons=buttons, parse_mode="html")
    except Exception:
        await bot.send_message(event.sender_id, text, buttons=buttons, parse_mode="html")


async def user_name(user_id: int):
    try:
        entity = await bot.get_entity(user_id)
        if getattr(entity, "username", None):
            return f"@{entity.username}"
        name = getattr(entity, "first_name", None) or "کاربر"
        return name[:25]
    except Exception:
        return f"`{user_id}`"


# ============================================================
# SELF FEATURES / SELF PANEL
# ============================================================

SELF_CLOCK_FONTS = {
    "normal":"0123456789","bold":"𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟳𝟖𝟗","double":"𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    "sans":"𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫","sans_bold":"𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    "mono":"𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿","full":"０１２３４５６７８９",
    "circled":"⓪①②③④⑤⑥⑦⑧⑨","negative":"⓿❶❷❸❹❺❻❼❽❾",
    "superscript":"⁰¹²³⁴⁵⁶⁷⁸⁹","subscript":"₀₁₂₃₄₅₆₇₈₉",
    "persian":"۰۱۲۳۴۵۶۷۸۹","arabic":"٠١٢٣٤٥٦٧٨٩","devanagari":"०१२३४५६७८९",
}
SELF_FONT_ALIASES = {
    "عادی":"normal","بولد":"bold","دوبل":"double","سانس":"sans","سانس بولد":"sans_bold",
    "مونو":"mono","فول":"full","دایره":"circled","منفی":"negative",
    "بالانویس":"superscript","زیرنویس":"subscript","فارسی":"persian","عربی":"arabic","هندی":"devanagari"
}
SELF_ENGLISH_FONTS = {
    "normal": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
    "bold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "italic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"),
    "bold_italic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"),
    "monospace": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"),
    "double": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
}
SELF_ENGLISH_FONT_ALIASES = {"عادی":"normal","بولد":"bold","ایتالیک":"italic","بولد ایتالیک":"bold_italic","مونو":"monospace","دوبل":"double"}
SELF_DEFAULTS = {
    "time_name":"on", "time_bio":"off", "clock_font":"normal", "bold":"off", "persian_font":"off", "english_font":"normal",
    "translate":"off", "auto_reply":"off", "auto_reply_text":"سلام، فعلاً در دسترس نیستم.", "auto_read":"off",
    "typing":"off", "game_mode":"off", "reaction_targets":"[]", "reaction_emojis":"{}",
    "action_voice":"off", "action_round":"off", "action_video":"off", "action_photo":"off",
    "action_document":"off", "action_sticker":"off", "always_online":"off",
    "premium_emoji_map":"{}",
}
# Text-format toggles shown on the «اکشن» screen:
# (setting key, callback action, button label, open tag, close tag)
SELF_FORMAT_FLAGS = (
    ("bold", "bold", "بولد", "<strong>", "</strong>"),
    ("fmt_italic", "fx_italic", "ایتالیک", "<em>", "</em>"),
    ("fmt_mono", "fx_mono", "مونو", "<code>", "</code>"),
    ("fmt_quote", "fx_quote", "کوت", "<blockquote>", "</blockquote>"),
    ("fmt_strike", "fx_strike", "خط‌خورده", "<s>", "</s>"),
    ("fmt_underline", "fx_underline", "زیرخط", "<u>", "</u>"),
    ("fmt_spoiler", "fx_spoiler", "اسپویلر", "<tg-spoiler>", "</tg-spoiler>"),
)


STRETCH_MAP = dict(zip("بپتثجچحخدذرزژسشصضطظعغفقکگلمنهیيك", "بـپـتـثـجـچـحـخـدـذـرـزـژـسـشـصـضـطـظـعـغـفـقـکـگـلـمـنـهـیـيـكـ"))

def self_get(uid, key, default=None):
    return get_setting(uid, key, SELF_DEFAULTS.get(key) if default is None else default)

def self_set(uid, key, value):
    set_setting(uid, key, value)

def self_format_active(uid):
    return any(self_get(uid, f[0], "off") == "on" for f in SELF_FORMAT_FLAGS)


def self_apply_format(uid, text):
    """Wrap `text` (HTML) in every enabled format. Telegram doesn't allow
    monospace to be combined with other inline styles, so when مونو is on it
    is the only inline style applied (کوت can still wrap it)."""
    active = [f for f in SELF_FORMAT_FLAGS if self_get(uid, f[0], "off") == "on"]
    if not active:
        return text
    mono = any(f[0] == "fmt_mono" for f in active)
    for key, _action, _label, o, c in active:
        if key == "fmt_quote":
            continue
        if mono and key != "fmt_mono":
            continue
        text = f"{o}{text}{c}"
    if any(f[0] == "fmt_quote" for f in active):
        text = f"<blockquote>{text}</blockquote>"
    return text


def self_auto_reply_map(uid):
    try:
        raw = json.loads(self_get(uid, "auto_reply_keywords", "{}"))
        return {str(k).casefold(): str(v) for k, v in raw.items()} if isinstance(raw, dict) else {}
    except Exception:
        return {}

def self_save_auto_reply_map(uid, mapping):
    self_set(uid, "auto_reply_keywords", json.dumps(mapping, ensure_ascii=False))

def self_banners(uid):
    """Load and normalize persisted banners."""
    try:
        raw = json.loads(self_get(uid, "banners", "[]"))
        if not isinstance(raw, list):
            return []
    except Exception:
        return []
    normalized = []
    changed = False
    for item in raw:
        if not isinstance(item, dict):
            changed = True
            continue
        try:
            item["id"] = int(item.get("id", 0))
            if item["id"] < 1:
                changed = True
                continue
            item["interval"] = max(1, int(item.get("interval", 60)))
            clean_targets = set()
            for raw_target in (item.get("targets") or []):
                try:
                    target_id = int(raw_target)
                    if target_id != 0:
                        clean_targets.add(target_id)
                except (TypeError, ValueError):
                    changed = True
            item["targets"] = sorted(clean_targets)
            item["enabled"] = item.get("enabled", True) not in {False, 0, "0", "off", "false"}
            item["last_sent"] = float(item.get("last_sent", 0) or 0)
        except (TypeError, ValueError):
            changed = True
            continue
        normalized.append(item)
    if changed:
        self_set(uid, "banners", json.dumps(normalized, ensure_ascii=False))
    return normalized

def self_save_banners(uid, banners):
    self_set(uid, "banners", json.dumps(banners, ensure_ascii=False))

def _banner_is_claim_word(banner):
    """True when the banner's text is exactly «دریافت الماس»."""
    text = " ".join(str((banner or {}).get("text") or "").split()).casefold()
    return text == "دریافت الماس"


def _banner_target_is_official_group(target):
    """True when a resolved target (entity or id) is the official main group."""
    if OFFICIAL_GROUP_ID is None:
        return False
    try:
        if isinstance(target, int):
            return int(target) == int(OFFICIAL_GROUP_ID)
        return int(utils.get_peer_id(target, add_mark=True)) == int(OFFICIAL_GROUP_ID)
    except Exception:
        return False


def _next_banner_id(banners):
    return max([int(b.get("id", 0)) for b in banners] or [0]) + 1

def _banner_from_list(banners, banner_id):
    for banner in banners:
        try:
            if int(banner.get("id", 0)) == int(banner_id):
                return banner
        except (TypeError, ValueError):
            continue
    return None

def _banner_by_id(uid, banner_id):
    return _banner_from_list(self_banners(uid), banner_id)

def _banner_media_dir(uid):
    path = BASE_DIR / "banner_media" / str(int(uid))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _is_image_file(path_str):
    """True only for actual photo files -- everything else (video, gif,
    documents, etc.) is treated as non-photo for the copy-banner photo-only
    restriction."""
    if not path_str:
        return False
    import mimetypes
    guessed, _ = mimetypes.guess_type(path_str)
    return bool(guessed) and guessed.startswith("image/")


def disable_non_photo_banners_sync():
    """One-time/startup cleanup: copy-mode banners that were saved with
    non-photo media (video etc., from before the photo-only restriction)
    get disabled so they stop being sent, and their media file is removed
    to reclaim disk space / shrink future backups."""
    disabled = 0
    for db_file in sorted(DATA_DIR.glob("user_*.db")):
        match = re.fullmatch(r"user_(\d+)\.db", db_file.name)
        if not match:
            continue
        uid = int(match.group(1))
        try:
            banners = self_banners(uid)
        except Exception as exc:
            print(f"[BANNER_CLEANUP] {uid}: load failed: {exc}")
            continue
        changed = False
        for banner in banners:
            if banner.get("mode") != "copy":
                continue
            media_path = banner.get("media_path")
            if not media_path:
                continue
            if _is_image_file(media_path):
                continue
            banner["enabled"] = False
            with contextlib.suppress(Exception):
                Path(media_path).unlink(missing_ok=True)
            banner["media_path"] = None
            changed = True
            disabled += 1
        if changed:
            self_save_banners(uid, banners)
    print(f"[BANNER_CLEANUP] {disabled} non-photo banner(s) disabled.")
    return disabled

def _get_tabchi_client(uid):
    """Return only the SELF client assigned to this user for Tabchi operations."""
    return self_clients.get(int(uid))


async def _banner_send(client, uid, banner, target):
    # Never trust the caller-provided client for Tabchi sends.
    self_client = _get_tabchi_client(uid)
    if not self_client:
        raise RuntimeError("SELF client is not active")
    if banner.get("mode", "forward") == "forward":
        return await self_client.forward_messages(
            target, int(banner["source_msg_id"]),
            from_peer=int(banner["source_chat_id"])
        )
    media_path = banner.get("media_path")
    caption = banner.get("text") or ""
    if media_path and Path(media_path).exists():
        return await self_client.send_file(target, media_path, caption=caption)
    return await self_client.send_message(target, caption)

async def _banner_recent_pv(client, count):
    if not client:
        raise RuntimeError("SELF client is not active")
    result = []
    me = await client.get_me()
    async for dialog in client.iter_dialogs():
        entity = getattr(dialog, "entity", None)
        if not entity or getattr(dialog, "is_group", False) or getattr(dialog, "is_channel", False):
            continue
        if getattr(entity, "bot", False) or getattr(entity, "id", None) == me.id:
            continue
        result.append(entity)
        if len(result) >= int(count):
            break
    return result

async def _banner_dispatch_now(client, uid, banner, targets):
    client = _get_tabchi_client(uid)
    if not client:
        raise RuntimeError("SELF client is not active")
    sent = failed = 0
    claim_word = _banner_is_claim_word(banner)
    for target in targets:
        # A banner whose text is «دریافت الماس» is never posted in the main
        # group (only there — every other chat still receives it).
        if claim_word and _banner_target_is_official_group(target):
            continue
        try:
            await _banner_send(client, uid, banner, target)
            sent += 1
        except Exception as exc:
            failed += 1
            print(f"[BANNER {uid}] send {banner.get('id')} -> {getattr(target, 'id', target)} failed: {exc}")
    return sent, failed

async def _banner_dispatch_configured_now(client, uid, banner):
    """Send one configured banner immediately and record the send time.

    The caller may be the self worker or the exact client that received the
    command.  Keeping this function independent of self_clients avoids a
    race where the command arrives while the worker is still registering.
    """
    client = _get_tabchi_client(uid)
    if not client:
        raise RuntimeError("SELF client is not active")

    if not banner or not banner.get("enabled", True):
        return 0, 0

    target_ids = []
    for raw_gid in banner.get("targets", []):
        try:
            gid = int(raw_gid)
        except (TypeError, ValueError):
            print(f"[BANNER {uid}] invalid target id: {raw_gid!r}")
            continue
        if gid == 0:
            continue
        if gid not in target_ids:
            target_ids.append(gid)
    banner["targets"] = target_ids

    if not target_ids:
        return 0, 0

    targets = []
    for gid in target_ids:
        try:
            targets.append(await client.get_entity(gid))
        except Exception as exc:
            print(f"[BANNER {uid}] target resolve failed for {gid}: {exc}")

    if not targets:
        return 0, len(target_ids)

    sent, failed = await _banner_dispatch_now(client, uid, banner, targets)
    if sent:
        banner["last_sent"] = time.time()
    return sent, failed + max(0, len(target_ids) - len(targets))


async def _banner_dispatch_all_configured(client, uid):
    """Immediately send every configured banner that has at least one target."""
    client = _get_tabchi_client(uid)
    if not client:
        raise RuntimeError("SELF client is not active")
    banners = self_banners(uid)
    total_sent = total_failed = 0
    changed = False
    for banner in banners:
        if not banner.get("enabled", True) or not banner.get("targets"):
            continue
        sent, failed = await _banner_dispatch_configured_now(client, uid, banner)
        total_sent += sent
        total_failed += failed
        if sent:
            changed = True
    if changed:
        self_save_banners(uid, banners)
    return total_sent, total_failed


async def _banner_worker_tick(client, uid):
    client = _get_tabchi_client(uid)
    if not client:
        raise RuntimeError("SELF client is not active")
    if self_get(uid, "banner_auto", "off") != "on":
        return
    now = time.time()
    banners = self_banners(uid)
    changed = False
    for banner in banners:
        if not banner.get("enabled", True):
            continue
        interval = max(1, int(banner.get("interval", 60))) * 60
        last_sent = float(banner.get("last_sent", 0) or 0)
        if last_sent and now - last_sent < interval:
            continue
        sent, _ = await _banner_dispatch_configured_now(client, uid, banner)
        if sent:
            changed = True
    if changed:
        self_save_banners(uid, banners)


def self_reaction_targets(uid):
    try:
        return {int(x) for x in json.loads(self_get(uid, "reaction_targets", "[]"))}
    except Exception:
        return set()

def self_save_reaction_targets(uid, targets):
    self_set(uid, "reaction_targets", json.dumps(sorted(int(x) for x in targets)))

def self_reaction_map(uid):
    try:
        raw = json.loads(self_get(uid, "reaction_emojis", "{}"))
        return {int(k): str(v) for k, v in raw.items()} if isinstance(raw, dict) else {}
    except Exception:
        return {}

def self_set_reaction(uid, target_id, emoji):
    mapping = self_reaction_map(uid)
    mapping[int(target_id)] = emoji
    self_set(uid, "reaction_emojis", json.dumps(mapping, ensure_ascii=False))

def self_premium_emoji_map(uid):
    """normal_emoji -> [custom_emoji_id, premium_glyph]"""
    try:
        raw = json.loads(self_get(uid, "premium_emoji_map", "{}"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}

def self_save_premium_emoji_map(uid, mapping):
    self_set(uid, "premium_emoji_map", json.dumps(mapping, ensure_ascii=False))


# Pending premium-emoji relay texts, keyed by a short token.
#
# Telegram strips custom-emoji entities the moment a message is *sent*
# unless the sending account is Premium; only a later bot-driven *edit*
# of that message is exempt (same trick as poc_apply_premium_emoji).
# ------------------------------------------------------------------
# PREMIUM EMOJI RELAY STATE
# ------------------------------------------------------------------
_PREMIUM_RELAY_PENDING = {}
_PREMIUM_RELAY_TTL = 300

def _store_pending_premium_relay(uid, text):
    """Store the final HTML that the BOT must apply to the inline message."""
    now = time.time()
    for key, value in list(_PREMIUM_RELAY_PENDING.items()):
        try:
            expired = now - float(value.get("ts", 0)) > _PREMIUM_RELAY_TTL
        except Exception:
            expired = True
        if expired:
            _PREMIUM_RELAY_PENDING.pop(key, None)

    token = secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:12]
    _PREMIUM_RELAY_PENDING[token] = {
        "uid": int(uid),
        "text": str(text),
        "ts": now,
    }
    return token

def _get_pending_premium_relay(uid, token):
    entry = _PREMIUM_RELAY_PENDING.get(str(token))
    if not entry or int(entry.get("uid", -1)) != int(uid):
        return None
    if time.time() - float(entry.get("ts", 0)) > _PREMIUM_RELAY_TTL:
        _PREMIUM_RELAY_PENDING.pop(str(token), None)
        return None
    return entry

def _pop_pending_premium_relay(uid, token):
    entry = _get_pending_premium_relay(uid, token)
    if not entry:
        return None
    _PREMIUM_RELAY_PENDING.pop(str(token), None)
    return entry.get("text")

def self_remove_reaction(uid, target_id):
    mapping = self_reaction_map(uid)
    mapping.pop(int(target_id), None)
    self_set(uid, "reaction_emojis", json.dumps(mapping, ensure_ascii=False))

def self_clock(uid):
    now = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%H:%M")
    chars = SELF_CLOCK_FONTS.get(self_get(uid, "clock_font", "normal"), SELF_CLOCK_FONTS["normal"])
    return now.translate(str.maketrans("0123456789", chars))


def _clock_suffix_pattern():
    # All digit alphabets used by the clock-font selector.  This lets us
    # replace a previously formatted clock instead of accumulating old
    # Unicode digits in the profile name.
    digit_chars = "".join(SELF_CLOCK_FONTS.values())
    return re.compile(rf"\s*[{re.escape(digit_chars)}]{{1,2}}:[{re.escape(digit_chars)}]{{2}}\s*$")


_CLOCK_SUFFIX_RE = _clock_suffix_pattern()

def _clean_clock_suffix(name: str) -> str:
    return _CLOCK_SUFFIX_RE.sub("", name or "").strip()

def self_transform_english(text, uid):
    return text.translate(SELF_ENGLISH_FONTS.get(self_get(uid,"english_font","normal"), SELF_ENGLISH_FONTS["normal"]))

def self_stretch(text):
    if not text:
        return text
    non_joining_right = set("اآأإدذرزژوؤء")
    persian = set("بپتثجچحخسشصضطظعغفقکگلمنهىيیک")
    out = []
    for piece in re.split(r"(\s+)", text):
        if not piece or piece.isspace() or len(piece) < 4:
            out.append(piece)
            continue
        chars = list(piece)
        candidates = [i for i in range(len(chars)-1)
                      if chars[i] in persian and chars[i+1] in persian and chars[i] not in non_joining_right]
        selected = set(candidates[1::2][:max(1, min(2, len(chars)//5))])
        for i,ch in enumerate(chars):
            out.append(ch)
            if i in selected:
                out.append("ـ")
    return "".join(out)[:3900]

async def self_translate(client, text):
    if not text.strip():
        return None
    try:
        result = await client(TranslateTextRequest(
            to_lang="en",
            text=[TextWithEntities(text=text, entities=[])],
        ))
        values = getattr(result, "result", None)
        if values:
            translated = getattr(values[0], "text", None)
            if translated:
                return translated.strip()
    except Exception as exc:
        print(f"[SELF] Telegram translation failed: {exc}")
    try:
        import argostranslate.translate as argos
        result = argos.translate(text, "fa", "en")
        return result.strip() if result else None
    except Exception as exc:
        print(f"[SELF] Argos translation unavailable: {exc}")
        return None

def _self_cb(uid: int, action: str) -> bytes:
    return f"sp:{int(uid)}:{action}".encode("utf-8")


def _font_label(kind: str, key: str) -> str:
    labels = {
        "clock":{"normal":"عادی","bold":"بولد","double":"دوبل","sans":"سانس","sans_bold":"سانس بولد","mono":"مونو","full":"فول","circled":"دایره","negative":"منفی","superscript":"بالانویس","subscript":"زیرنویس","persian":"فارسی","arabic":"عربی","devanagari":"هندی"},
        "english":{"normal":"عادی","bold":"بولد","italic":"ایتالیک","bold_italic":"بولد ایتالیک","monospace":"مونو","double":"دوبل"},
    }
    return labels.get(kind, {}).get(key, key)

def self_panel_buttons(uid):
    """Kept as the single entry point every existing call site already uses
    for "show the main panel"; now simply page 1 of the new paginated grid
    (see PANEL_ITEMS / _panel_page_buttons below) so every one of those call
    sites gets the redesigned panel for free."""
    return _panel_page_buttons(uid, 0, _panel_pages())


def self_panel_text(uid, extra=None):
    # The panel message carries the HTX frame photo (see
    # _get_self_panel_photo_bytes / HTX_FRAME_PATH below); this only builds
    # the caption shown under that photo. Every existing call site (cleanup
    # progress, font previews, chat-lock/block/reaction guides, plain
    # "return to panel" edits) is unchanged and keeps working, since
    # editing a photo message's text just updates its caption.
    base = "› <b>𝑯𝑻𝑿</b>"
    if extra:
        return f"{base}\n\n{extra}"
    return base


# ---------------------------------------------------------------------
# Paginated .پنل — every feature guide topic lives in the main panel grid.
#
# Page 1 is a fixed [2,1,2,1] layout (6 items); every later page cycles the
# same [2,1] row pattern for whatever it holds (5 items -> [2,1,2], the
# final overflow page -> whatever is left). Items that already have a real
# toggle/action wired up (clock, translate, autoreply, presence, fonts) show
# those buttons directly; items that only had a long guide text now split
# into a short "📖 توضیحات" / "⌨️ دستورات" pair instead of one long caption,
# so nothing needs the >950-char fallback (separate sent message) anymore.
# ---------------------------------------------------------------------

PANEL_ITEMS = [
    ("clock", "🕐 ساعت روی نام"),
    ("fonts", "اکشن"),
    ("translate", "🌐 ترجمه"),
    ("presence", "⚡ اکشن آنلاین"),
    ("autoreply", "💬 پاسخ خودکار"),
    ("reaction", "❤️ ریاکشن"),
    # ---- page 1 ends here (6 items) ----
    ("cleanup", "🧹 پاکسازی"),
    ("lock", "🔒 قفل چت"),
    ("media", "🎙️ رسانه و تبدیل‌ها"),
    ("files", "📦 فایل و دانلود"),
    ("tabchi", "📢 تبچی"),
    ("spam", "اسپم"),
    ("comments", "💬 کامنت اول"),
    ("secretary", "🤵 منشی"),
    ("group", "🛡 مدیریت گروه"),
    ("globalban", "🚫 بن سراسری"),
    ("tag", "🏷 تگ اعضا"),
    ("currency", "💱 نرخ ارز"),
    ("logo", "🎨 لوگوساز"),
    ("profile", "👤 کپی پروفایل"),
    ("creation", "🏗 ساخت گروه / چنل"),
    ("dice", "🎲 تاس / سرگرمی"),
    ("stickers", "🖼 استیکر / عکس"),
    ("misc", "📋 دستورات عمومی"),
    ("channel_save", "💾 ذخیره چنل"),
    ("premium_emoji", "💎 ایموجی پریمیوم"),
    ("snoopers", "🕵️ لیست فضول‌ها"),
    ("miowy_group", "🐱 میویی"),
    ("mozy_group", "🍌 موزی"),
    ("ph_dl", "دانلودر PH"),
    ("xvid_dl", "دانلودر Xvid"),
    ("xnxx_dl", "دانلودر XNXX"),
]
PANEL_LABELS = dict(PANEL_ITEMS)
PANEL_LABELS.update({
    "miowy_pishi": "🐱 پیشی خودکار", "miowy_mew": "😼 میو خودکار",
    "miowy_fishing": "🎣 ماهیگیری خودکار", "miowy_status": "😼 وضعیت میویی",
    "mozy_banana": "🍌 موز خودکار", "mozy_spin": "🎰 اسپین خودکار",
    "mozy_monkey": "🐒 میمون",
    "mozy_status": "📢 وضعیت موزی",
})
PANEL_GROUPS = {
    "miowy_group": ("🐱 میویی", ["miowy_pishi", "miowy_mew", "miowy_fishing", "miowy_status"]),
    "mozy_group": ("🍌 موزی", ["mozy_banana", "mozy_spin", "mozy_monkey", "mozy_status"]),
}

# Items that already open a full dedicated screen elsewhere in this file —
# tapping them in the grid jumps straight there instead of a mini submenu.
PANEL_DIRECT_ACTIONS = {
    "tabchi": "banners",
    "comments": "comment_setup",
    "channel_save": "cs_open",
    "cleanup": "cleanup",
    "premium_emoji": "premium_emoji_open",
    "ph_dl": "ph_dl_info",
    "xvid_dl": "xvid_dl_info",
    "xnxx_dl": "xnxx_dl_info",
}


def _panel_chunk_pattern(n):
    """Row sizes cycling 2,1,2,1,2,... until n items are used up."""
    pattern = (2, 1)
    rows, i, remaining = [], 0, n
    while remaining > 0:
        size = min(pattern[i % 2], remaining)
        rows.append(size)
        remaining -= size
        i += 1
    return rows


def _panel_pages():
    """Page 1 = first 6 items. Later pages take 5 each, except the last
    page (which absorbs whatever remains) — keeps the grid at <= 6 pages."""
    first, rest = PANEL_ITEMS[:6], PANEL_ITEMS[6:]
    pages = [first]
    i = 0
    while i < len(rest):
        budget_left = 6 - len(pages)
        if budget_left <= 1:
            pages.append(rest[i:])
            break
        pages.append(rest[i:i + 5])
        i += 5
    return pages


def _onoff(flag):
    """Status badge used on every toggle button: ( ✓ on ) / ( ✗ off )."""
    return "( ✓ on )" if flag == "on" else "( ✗ off )"


def _panel_item_buttons(uid, key):
    """«fonts» and «lock» keep real toggle buttons; every other item is a
    plain Quote + mono command screen (see PANEL_COMMAND_SCREENS)."""
    if key == "lock":
        on = lambda flag: "success" if flag == "on" else "danger"

        def lx(label, flag_key, action):
            val = self_get(uid, flag_key, "off")
            return btn(f"قفل {label} : {_onoff(val)}", _self_cb(uid, action), on(val))

        return [
            [lx("لینک", "lock_link", "lock_link"), lx("یوزرنیم", "lock_username", "lock_username")],
            [lx("عکس", "lock_photo", "lock_photo"), lx("ریپلای", "lock_reply", "lock_reply")],
            [lx("استیکر", "lock_sticker", "lock_sticker"), lx("گیف", "lock_gif", "lock_gif")],
            [lx("فوروارد", "lock_forward", "lock_forward"), lx("پیوی", "chat_lock_global", "lock_dm")],
        ]
    if key == "presence":
        on = lambda flag: "success" if flag == "on" else "danger"

        def px(setting_key, label):
            val = self_get(uid, setting_key, "off")
            return btn(f"{label} : {_onoff(val)}", _self_cb(uid, setting_key), on(val))

        return [
            [px("typing", "تایپ"), px("action_voice", "ویس")],
            [px("action_round", "ویدیو گرد"), px("action_photo", "عکس")],
            [px("action_video", "ویدیو"), px("action_document", "سند")],
            [px("action_sticker", "استیکر"), px("game_mode", "بازی")],
            [px("auto_read", "سین"), px("always_online", "همیشه آنلاین")],
        ]
    if key != "fonts":
        return None
    on = lambda flag: "success" if flag == "on" else "danger"
    fl = {f[0]: self_get(uid, f[0], "off") for f in SELF_FORMAT_FLAGS}

    def fx(key_):
        f = next(x for x in SELF_FORMAT_FLAGS if x[0] == key_)
        return btn(f"{f[2]} : {_onoff(fl[key_])}",
                   _self_cb(uid, f[1]), on(fl[key_]))

    english = self_get(uid, "english_font", "normal")
    persian = self_get(uid, "persian_font", "off")
    return [
        [fx("bold"), fx("fmt_italic")],
        [fx("fmt_mono"), fx("fmt_quote")],
        [fx("fmt_strike"), fx("fmt_underline")],
        [fx("fmt_spoiler"),
         btn(f"فونت انگلیسی: {_font_label('english', english)}", _self_cb(uid, "engfont"), "primary")],
        [btn(f"کشیده نویس : {_onoff(persian)}", _self_cb(uid, "persian"), on(persian))],
    ]


def _panel_item_body(uid, key):
    if key == "miowy_status":
        return _miowy_status_text(uid)
    if key == "mozy_status":
        return _mozy_status_text(uid)
    return SELF_FEATURE_GUIDES.get(key, "")


def _split_guide(body):
    """Split a guide's HTML into a short description and its command list,
    at the first <code> tag, so each half stays well under the photo
    caption's ~1024-char limit instead of one long block."""
    if not body:
        return None, None
    idx = body.find("<code>")
    if idx == -1:
        return body.strip(), None
    desc = body[:idx].strip()
    cmds = body[idx:].strip()
    return (desc or None), (cmds or None)


PANEL_PING_PAGE = 4  # zero-based index -> page 5


def _panel_page_buttons(uid, page_idx, pages):
    items = pages[page_idx]
    rows = []
    # Ping lives only on page 5, alone in the very first row.
    if page_idx == PANEL_PING_PAGE:
        rows.append([btn("🏓 پینگ", _self_cb(uid, "ping"), "primary")])
    pos = 0
    for size in _panel_chunk_pattern(len(items)):
        rows.append([
            btn(label, _self_cb(uid, f"pit:{page_idx}:{key}"), "primary")
            for key, label in items[pos:pos + size]
        ])
        pos += size

    # Page 1 only: last row = اسم / محتوا / بیو (left-to-right order in the
    # keyboard is بیو, محتوا, اسم so اسم ends up on the right for RTL readers).
    if page_idx == 0:
        rows.append([
            btn("بیو", _self_cb(uid, "hx_bio"), "primary"),
            btn("📝 محتوا", _self_cb(uid, "hx_content"), "primary"),
            btn("اسم", _self_cb(uid, "hx_name"), "primary"),
        ])

    # Page 2 only: keeps the 2-1-2-1-2 rhythm — after the three item rows
    # (2,1,2) comes «متن به ویس» alone (1), then ساخت ویدیو گرد / دوست و
    # دشمن (2) right above the page navigation row (keyboard order is
    # left-to-right, so دوست و دشمن ends up on the right).
    if page_idx == PANEL_FE_PAGE:
        rows.append([
            btn("متن به ویس", _self_cb(uid, "tts_info"), "primary"),
        ])
        rows.append([
            btn("ساخت ویدیو گرد", _self_cb(uid, "vn_open"), "primary"),
            btn("دوست و دشمن", _self_cb(uid, "fe_menu"), "primary"),
        ])

    # Page 3 only: انتقال / اسکرین 📸 / موجودی, right above the page
    # navigation row (same left-to-right convention, so موجودی ends up on
    # the right, اسکرین in the middle and انتقال on the left).
    if page_idx == PANEL_BALANCE_PAGE:
        rows.append([
            btn("انتقال", _self_cb(uid, "balance_transfer_info"), "primary"),
            btn("اسکرین 📸", _self_cb(uid, "screenshot_info"), "primary"),
            btn("موجودی", _self_cb(uid, "balance_info"), "primary"),
        ])

    # Page 4 only: two rows.
    #   - دانلودر اینستاگرام alone, on top.
    #   - ماشین حساب / اسنپ شات together, one row below, right above the
    #     page navigation row (keyboard order is left-to-right, so اسنپ
    #     شات ends up on the right and ماشین حساب on the left).
    if page_idx == PANEL_CALC_PAGE:
        rows.append([
            btn("دانلودر اینستاگرام", _self_cb(uid, "ig_dl_info"), "primary"),
        ])
        rows.append([
            btn("ماشین حساب", _self_cb(uid, "calc_info"), "primary"),
            btn("اسنپ شات", _self_cb(uid, "snap_info"), "primary"),
        ])

    # Page 5 only: حذف / تایمردار / اطلاعات, right above the page navigation
    # row (keyboard order is left-to-right, so اطلاعات ends up on the left,
    # تایمردار in the middle and حذف on the right).
    if page_idx == PANEL_PING_PAGE:
        rows.append([
            btn("اطلاعات", _self_cb(uid, "info_open"), "primary"),
            btn("تایمردار", _self_cb(uid, "timerdar_info"), "primary"),
            btn("حذف", _self_cb(uid, "delete_info"), "primary"),
        ])

    # Page navigation: ⬅️ (1) (2) ... (6) ➡️ — no colour on the arrows or on
    # inactive pages; only the page you are on is "success" (green).
    prev_idx, next_idx = max(0, page_idx - 1), min(len(pages) - 1, page_idx + 1)
    nav = [btn("⬅️", _self_cb(uid, f"pg:{prev_idx}"), "none")]
    nav += [
        btn(f"({i + 1})", _self_cb(uid, f"pg:{i}"), "success" if i == page_idx else "none")
        for i in range(len(pages))
    ]
    nav.append(btn("➡️", _self_cb(uid, f"pg:{next_idx}"), "none"))
    rows.append(nav)

    # «بازگشت» -> the Panel Self start screen (the close button lives there now).
    rows.append([btn("بازگشت", _self_cb(uid, "home"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    return rows


# ---------------------------------------------------------------------
# New start screen of .پنل — «› 𝑯𝑻𝑿 Panel Self»
#   [ تنظیمات سلف | حساب کاربری ]
#   [ بستن ]
# «تنظیمات سلف» opens the paginated grid above (its bottom button is now
# «بازگشت» -> this screen); «بستن» closes the card and deletes it 3 s later.
# ---------------------------------------------------------------------
def _panel_home_text():
    return "› <b>𝑯𝑻𝑿 Panel Self</b>"


def _panel_home_buttons(uid):
    # Keyboard order is left-to-right, so تنظیمات سلف ends up on the right.
    return [
        [
            btn("👤 حساب کاربری", _self_cb(uid, "acct"), "primary"),
            btn("🤖 تنظیمات سلف", _self_cb(uid, "pg:0"), "primary"),
        ],
        [btn("بستن", _self_cb(uid, "close"), "danger")],
    ]


def _fmt_expiry(balance, hourly_cost=None):
    """Time left for a balance at SELF_HOURLY_COST diamonds/hour."""
    rate = float(hourly_cost or SELF_HOURLY_COST or 0)
    if rate <= 0 or balance <= 0:
        return "منقضی شده"
    minutes = int((float(balance) / rate) * 60)
    days, rest = divmod(minutes, 1440)
    hours, mins = divmod(rest, 60)
    parts = []
    if days:
        parts.append(f"{days} روز")
    if hours:
        parts.append(f"{hours} ساعت")
    if not days and not hours:
        parts.append(f"{max(mins, 1)} دقیقه")
    return " و ".join(parts)


async def _panel_account_info(uid, event=None):
    """(name, username, numeric id) of the self account."""
    me = None
    client = self_clients.get(int(uid))
    if client:
        with contextlib.suppress(Exception):
            me = await client.get_me()
    if me is None and event is not None:
        with contextlib.suppress(Exception):
            me = await event.get_sender()
    if me is None:
        return "-", "-", str(int(uid))
    name = " ".join(x for x in (getattr(me, "first_name", None), getattr(me, "last_name", None)) if x).strip() or "-"
    username = getattr(me, "username", None)
    if not username:
        for u in (getattr(me, "usernames", None) or []):
            if getattr(u, "active", True) and getattr(u, "username", None):
                username = u.username
                break
    return name, (f"@{username}" if username else "-"), str(int(getattr(me, "id", 0) or uid))


async def _panel_account_screen(event, uid):
    """«حساب کاربری» — value button on the left, label button on the right."""
    name, username, numeric_id = await _panel_account_info(uid, event)
    balance = get_balance(uid)
    rate = f"{_fmt_diamonds(SELF_HOURLY_COST)} الماس / ساعت"

    def row(label, value):
        return [btn(value, _self_cb(uid, "acct_noop"), "primary"),
                btn(label, _self_cb(uid, "acct_noop"), "primary")]

    rows = [
        row("🪪 نام", name),
        row("🔗 یوزرنیم", username),
        row("آیدی عددی", numeric_id),
        row("💎 موجودی", f"{_fmt_diamonds(balance)} الماس"),
        row("💠 نرخ فعلی", f"⏰ {rate}"),
        row("⏳ انقضا", _fmt_expiry(balance)),
        [btn("بازگشت", _self_cb(uid, "home"), "danger", icon=PREMIUM_EMOJI["self_back"][0])],
    ]
    await safe_callback_edit(
        event, _htx_quote(f"{HTX_TAG} • حساب کاربری"), parse_mode="html", buttons=rows
    )


def _panel_render(uid, page_idx=0):
    pages = _panel_pages()
    page_idx = max(0, min(page_idx, len(pages) - 1))
    text = self_panel_text(uid)
    return text, _panel_page_buttons(uid, page_idx, pages)


def _panel_key_page(key):
    for i, items in enumerate(_panel_pages()):
        if any(k == key for k, _ in items):
            return i
    if key in {item_key for _, feature_keys in PANEL_GROUPS.values() for item_key in feature_keys}:
        return len(_panel_pages()) - 1
    return 0


def _panel_parent_key(key):
    for group_key, (_, feature_keys) in PANEL_GROUPS.items():
        if key in feature_keys:
            return group_key
    return None


# Toggle/font actions that live inside an item submenu, mapped back to the
# PANEL_ITEMS key that submenu belongs to — used so toggling a setting
# refreshes that same submenu instead of jumping back to the old flat menu.
PANEL_TOGGLE_HOME = {
    "time": "clock", "bold": "fonts", "persian": "fonts",
    "fx_italic": "fonts", "fx_mono": "fonts", "fx_quote": "fonts",
    "fx_strike": "fonts", "fx_underline": "fonts", "fx_spoiler": "fonts",
    "clockfont": "fonts", "engfont": "fonts", "translate": "translate",
    "read": "presence", "typing": "presence", "game": "presence",
    "auto_read": "presence", "game_mode": "presence",
    "action_voice": "presence", "action_round": "presence", "action_video": "presence",
    "action_photo": "presence", "action_document": "presence", "action_sticker": "presence",
    "always_online": "presence",
    "autoreply": "autoreply",
    "lock_link": "lock", "lock_username": "lock", "lock_photo": "lock",
    "lock_reply": "lock", "lock_sticker": "lock", "lock_gif": "lock",
    "lock_forward": "lock", "lock_dm": "lock",
}


_CLOCK_PREVIEW_TOKEN = "CLKPREVIEWTOKEN"


async def _panel_show_clock(event, uid):
    """«ساعت روی نام» screen: name toggle, bio toggle + font cycle, back.
    The caption previews the clock in the currently selected font."""
    name_on = self_get(uid, "time_name") == "on"
    bio_on = self_get(uid, "time_bio", "off") == "on"
    extra = f"🕒 ساعت روی نام\n{_CLOCK_PREVIEW_TOKEN}"
    if bio_on and int(uid) in _BIO_CLOCK_TOO_LONG:
        extra += "\n\n⚠️ بیو برای اضافه‌شدن ساعت خیلی بلنده"
    rows = [
        [btn(f"ساعت نام : {_onoff('on' if name_on else 'off')}", _self_cb(uid, "time"), "success" if name_on else "danger")],
        [btn("فونت ساعت", _self_cb(uid, "clk_font"), "primary"),
         btn(f"ساعت بیو : {_onoff('on' if bio_on else 'off')}", _self_cb(uid, "timebio"), "success" if bio_on else "danger")],
        [btn("بازگشت", _self_cb(uid, "pg:0"), "danger", icon=PREMIUM_EMOJI["self_back"][0])],
    ]
    # The preview is inserted AFTER the premium-emoji pass so digits of fonts
    # like «منفی» (❶❷…) show exactly as they'll appear on the profile.
    caption = premium_ui_text(self_panel_text(uid, extra)).replace(_CLOCK_PREVIEW_TOKEN, self_clock(uid))
    try:
        await event.edit(caption, parse_mode="html", buttons=rows)
    except MessageNotModifiedError:
        pass
    except Exception:
        logging.exception("clock screen edit failed")


# ---------------------------------------------------------------------
# Command-only screens: same look as اسم / بیو / محتوا — a stack of Quote
# blocks, commands in mono, and a single «بازگشت» button.
# ---------------------------------------------------------------------
PANEL_COMMAND_SCREENS = {
    "reaction": ("ریاکشن", [
        "دستورات",
        "<code>.ریاکشن ❤️</code>\nروی پیام کاربر ریپلای کن",
        "<code>.حذف ریاکشن</code>\nروی پیام همان کاربر ریپلای کن",
    ]),
    "translate": ("ترجمه", [
        "دستورات",
        "<code>.مترجم روشن</code>\n<code>.مترجم خاموش</code>",
    ]),
    "autoreply": ("پاسخ خودکار", [
        "دستورات",
        "<code>.پاسخ خودکار روشن</code>\n<code>.پاسخ خودکار خاموش</code>",
        "<code>.پاسخ خودکار جدید سلام</code>\nثبت کلمه",
        "<code>.ذخیره پاسخ خودکار سلام</code>\nریپلای روی متن پاسخ",
        "<code>.حذف پاسخ خودکار سلام</code>\n<code>.لیست پاسخ خودکار</code>",
    ]),
    "media": ("رسانه و تبدیل‌ها", [
        "دستورات • ریپلای روی رسانه",
        "<code>.ویس به mp3</code>\n<code>.mp3 به ویس</code>",
        "<code>.ویدیو به ویس</code>\n<code>.ویدیو به mp3</code>",
        "<code>.متن</code> ← ویس به متن\n<code>.OCR</code> ← عکس به متن",
    ]),
    "currency": ("نرخ ارز", [
        "دستورات",
        "<code>.نرخ ارز</code> یا <code>.قیمت دلار</code>\nقیمت لحظه‌ای USDT به تومان و ریال از والکس؛ شاخص تقریبی دلار آزاد",
        "<code>.قیمت یورو</code>\nبرآورد بر پایه نرخ جهانی EUR/USD و نرخ بازار تتر",
        "<code>.قیمت طلا</code> یا <code>.قیمت طلای ۱۸ عیار</code>\nبرآورد هر گرم طلای خام؛ بدون اجرت و مالیات",
        "<code>.قیمت BTC</code>\n<code>.قیمت بیت کوین</code>",
        "قیمت دلاری + تومان و معادل ریالی، نمودار ۳۰ روزه\nBTC • ETH • SOL • USDT • TON • TRX • XRP • DOGE • BNB • ADA • DOT • AVAX • SHIB",
    ]),
    "tag": ("تگ اعضا", [
        "دستورات • داخل گروه",
        "<code>.تگ 20</code>\nتگ تعداد مشخص (۱ تا ۱۰۰۰)",
        "<code>.همه</code>\nتگ همه اعضا",
    ]),
    "logo": ("لوگوساز", [
        "دستورات",
        "<code>.لوگو 12 HusteRIX</code>\nعدد = شماره قالب (۱ تا ۱۲)\nزیرعنوان اختیاری: <code>.لوگو 1 HusteRIX | Premium Self</code>",
    ]),
    "profile": ("کپی پروفایل", [
        "دستورات",
        "<code>.کپی پروفایل</code>\nریپلای روی پیام کاربر",
        "<code>.حذف کپی پروفایل</code>\nبازگردانی پروفایل قبلی",
    ]),
    "creation": ("ساخت گروه / چنل", [
        "دستورات",
        "<code>.ساخت گروه نام گروه</code>\n<code>.ساخت چنل نام کانال</code>",
    ]),
    "dice": ("تاس / سرگرمی", [
        "دستورات",
        "<code>.تاس 6</code>\nعدد ۱ تا ۶",
        "<code>.هک</code>\nشوخی و سرگرمی",
    ]),
    "stickers": ("استیکر / عکس", [
        "دستورات • ریپلای روی رسانه",
        "<code>.استیکر</code>\nعکس ← استیکر",
        "<code>.عکس</code>\nاستیکر ← عکس",
    ]),
    "misc": ("دستورات عمومی", [
        "دستورات",
        "<code>.پینگ</code>\nسرعت پاسخ سلف",
        "<code>.پنل</code>\nبازکردن پنل",
    ]),
    "files": ("فایل و دانلود", [
        "دستورات • ریپلای روی پیام",
        "<code>.دانلود</code>\nدانلود / ذخیره پیام",
        "<code>.استخراج</code>\nریپلای روی فایل ZIP یا RAR",
    ]),
    "secretary": ("منشی", [
        "دستورات • فقط در پیوی",
        "<code>.تنظیم منشی</code>\nریپلای روی پیام پاسخ (متن یا مدیا)",
        "<code>.منشی روشن</code>\n<code>.منشی خاموش</code>",
        "<code>.تنظیم زمان منشی 15</code>\nفاصله پاسخ‌ها (۵ تا ۶۰ دقیقه)",
    ]),
    "group": ("مدیریت گروه", [
        "دستورات • داخل گروه + ریپلای",
        "<code>.پین</code>\n<code>.حذف پین</code>",
        "<code>.بن</code>\n<code>.سیک</code>\n<code>.آن بن</code>",
    ]),
    "spam": ("اسپم", [
        "دستورات • ریپلای روی پیام",
        "<code>.تکرار 20</code>\nتعداد ۱ تا ۱۰۰۰",
    ]),
    "mozy_status": ("وضعیت موزی", [
        "دستورات",
        "<code>.وضعیت موزی</code>\nوضعیت موز، اسپین و درآمد میمون گروه",
    ]),
    "mozy_banana": ("موز خودکار", [
        "دستورات • داخل گروه",
        "<code>.موز خودکار روشن</code>\n<code>.موز خودکار خاموش</code>\nهر ۳ دقیقه",
    ]),
    "mozy_monkey": ("میمون", [
        "درآمد خودکار میمون • داخل گروه",
        "<code>.درآمد میمون روشن</code>\n<code>.درآمد میمون خاموش</code>\n"
        "هر ۱۲ ساعت داخل همان گپی که روشن شده «میمون» ارسال می‌شود و روی پیامی که ربات "
        "در جواب (ریپلای) همان پیام می‌فرستد، دکمه «💰 برداشت همه» زده می‌شود.",
    ]),
    "mozy_spin": ("اسپین خودکار", [
        "دستورات • داخل گروه",
        "<code>.اسپین خودکار روشن</code>\n<code>.اسپین خودکار خاموش</code>\nهر ۶ ساعت",
    ]),
    "miowy_fishing": ("ماهیگیری خودکار", [
        "دستورات • داخل گروه",
        "<code>.تنظیم زمان ماهیگیری 10</code>\nفاصله به دقیقه",
        "<code>.ماهیگیری خودکار روشن</code>\n<code>.ماهیگیری خودکار خاموش</code>",
    ]),
    "miowy_mew": ("میو خودکار", [
        "دستورات • داخل گروه",
        "<code>.تنظیم زمان میو 10</code>\nفاصله به دقیقه",
        "<code>.میو خودکار روشن</code>\n<code>.میو خودکار خاموش</code>",
    ]),
    "miowy_pishi": ("پیشی خودکار", [
        "دستورات • داخل گروه",
        "<code>.تنظیم زمان پیشی 10</code>\nفاصله به دقیقه",
        "<code>.پیشی خودکار روشن</code>\n<code>.پیشی خودکار خاموش</code>",
    ]),
    "miowy_status": ("وضعیت میویی", [
        "دستورات",
        "<code>.وضعیت میویی</code>\nوضعیت پیشی، میو و ماهیگیری خودکار گروه",
    ]),
    "snoopers": ("لیست فضول‌ها", [
        "دستورات",
        "<code>.لیست فضول ها</code>\nپاک‌سازی خودکار هر شب ۰۰:۰۰",
    ]),
}


def _panel_command_screen(uid, key):
    title, blocks = PANEL_COMMAND_SCREENS[key]
    page_idx = _panel_key_page(key)
    text = _htx_stack(f"{HTX_TAG} • {title}", *blocks)
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


async def _panel_show_fonts(event, uid, extra_text=None):
    """«اکشن» screen: text-format toggles only (no guide/commands buttons)."""
    page_idx = _panel_key_page("fonts")
    blocks = [f"{HTX_TAG} • اکشن"]
    if extra_text:
        blocks.append(extra_text)
    rows = list(_panel_item_buttons(uid, "fonts"))
    rows.append([btn("بازگشت", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    await safe_callback_edit(event, _htx_stack(*blocks), parse_mode="html", buttons=rows)


async def _panel_show_action(event, uid):
    """«⚡ اکشن آنلاین» screen: chat-activity toggles only (typing / voice /
    round video / photo / video / document / sticker / game / سین / همیشه
    آنلاین) — no guide/commands buttons, just live toggle buttons."""
    page_idx = _panel_key_page("presence")
    rows = list(_panel_item_buttons(uid, "presence"))
    rows.append([btn("بازگشت", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    await safe_callback_edit(event, _htx_stack(f"{HTX_TAG} • ⚡ اکشن آنلاین"), parse_mode="html", buttons=rows)


def _panel_lock_status_text(uid):
    """Caption for «🔒 قفل چت»: one quote line per pair, live status — styled
    like the reference screenshot (self vtr's «قفل ها» screen)."""
    def val(key):
        return _onoff(self_get(uid, key, "off"))

    def pair(a_label, a_key, b_label, b_key):
        return f"{a_label} : {val(a_key)} • {b_label} : {val(b_key)}"

    return _htx_stack(
        f"{HTX_TAG} • قفل ها",
        pair("لینک", "lock_link", "یوزرنیم", "lock_username"),
        pair("عکس", "lock_photo", "ریپلای", "lock_reply"),
        pair("استیکر", "lock_sticker", "گیف", "lock_gif"),
        pair("فوروارد", "lock_forward", "پیوی", "chat_lock_global"),
    )


async def _panel_show_lock(event, uid):
    """«🔒 قفل چت» screen: live status blocks + real toggle buttons, styled
    like the reference screenshot (self vtr)."""
    page_idx = _panel_key_page("lock")
    rows = list(_panel_item_buttons(uid, "lock"))
    rows.append([btn("📖 توضیحات", _self_cb(uid, "lock_help"), "primary")])
    rows.append([btn("بازگشت", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    await safe_callback_edit(event, _panel_lock_status_text(uid), parse_mode="html", buttons=rows)


_PREMIUM_EMOJI_EXAMPLE_ID = PREMIUM_EMOJI["fire"][0]  # a real, already-verified
# custom-emoji id — used only so the example in the guide shows an actual
# working premium emoji instead of a placeholder glyph.


async def _panel_show_premium_emoji(event, uid):
    """Dedicated Premium Emoji screen. Never routes through the generic guide."""
    uid = int(uid)
    page_idx = _panel_key_page("premium_emoji")
    mapping = self_premium_emoji_map(uid)

    valid = []
    for normal_emoji, entry in mapping.items():
        if not isinstance(entry, (list, tuple)) or len(entry) < 2:
            continue
        try:
            emoji_id = int(entry[0])
        except (TypeError, ValueError):
            continue
        glyph = str(entry[1] or normal_emoji)
        valid.append((str(normal_emoji), emoji_id, glyph))

    blocks = [
        f"{HTX_TAG} • 💎 ایموجی پریمیوم",
        f"تعداد ثبت‌شده : <b>{len(valid)}</b>",
        "",
        "<b>ثبت:</b>",
        "<code>.ثبت ایموجی [پریمیوم] [عادی]</code>",
        "یا ریپلای روی پیام پریمیوم:",
        "<code>.ثبت ایموجی [عادی]</code>",
        "",
        "<b>حذف:</b> <code>.حذف ایموجی [پریمیوم/عادی]</code>",
        "",
        "<b>📋 لیست:</b> <code>.لیست پرمیوم</code>",
    ]

    for i, (normal, emoji_id, glyph) in enumerate(valid[:5], 1):
        blocks.append(
            f"ایموجی {i} : {html.escape(normal)}  ➜  "
            f'<tg-emoji emoji-id="{emoji_id}">{html.escape(glyph)}</tg-emoji>'
        )

    if len(valid) > 5:
        blocks.append(f"… و {len(valid) - 5} مورد دیگر")

    rows = [
        [btn(
            "بازگشت",
            _self_cb(uid, f"pg:{page_idx}"),
            "danger",
            icon=PREMIUM_EMOJI["self_back"][0],
        )],
    ]

    await safe_callback_edit(
        event,
        _htx_stack(*blocks),
        parse_mode="html",
        buttons=rows,
    )


async def _panel_show_group(event, uid, key):
    title, feature_keys = PANEL_GROUPS[key]
    page_idx = _panel_key_page(key)
    rows = []
    for size in _panel_chunk_pattern(len(feature_keys)):
        start = sum(len(row) for row in rows)
        rows.append([
            btn(PANEL_LABELS[item_key], _self_cb(uid, f"pit:{page_idx}:{item_key}"), "primary")
            for item_key in feature_keys[start:start + size]
        ])
    rows.append([btn("بازگشت", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    await safe_callback_edit(event, f"<b>{html.escape(title)}</b>\n\nقابلیت موردنظر را انتخاب کن:", parse_mode="html", buttons=rows)


async def _panel_show_item(event, uid, key, extra_text=None):
    if key in PANEL_GROUPS:
        await _panel_show_group(event, uid, key)
        return
    if key == "clock":
        await _panel_show_clock(event, uid)
        return
    if key == "fonts":
        await _panel_show_fonts(event, uid, extra_text)
        return
    if key == "premium_emoji":
        await _panel_show_premium_emoji(event, uid)
        return
    if key == "presence":
        await _panel_show_action(event, uid)
        return
    if key == "lock":
        await _panel_show_lock(event, uid)
        return
    if key in PANEL_COMMAND_SCREENS:
        text, buttons = _panel_command_screen(uid, key)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return
    page_idx = _panel_key_page(key)
    toggle_rows = _panel_item_buttons(uid, key)
    desc, cmds = _split_guide(_panel_item_body(uid, key))
    rows = list(toggle_rows) if toggle_rows else []
    if desc:
        rows.append([btn("📖 توضیحات", _self_cb(uid, f"pdesc:{page_idx}:{key}"), "primary")])
    if cmds:
        rows.append([btn("⌨️ دستورات", _self_cb(uid, f"pcmd:{page_idx}:{key}"), "primary")])
    parent_key = _panel_parent_key(key)
    rows.append([btn("بازگشت", _self_cb(uid, f"pgrp:{parent_key}") if parent_key else _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["home"][0])])
    title = PANEL_LABELS.get(key, key)
    caption = f"<b>{html.escape(title)}</b>"
    if extra_text:
        caption += f"\n\n{extra_text}"
    await safe_callback_edit(event, self_panel_text(uid, caption), parse_mode="html", buttons=rows)


# ---------------------------------------------------------------------
# اسم / محتوا / بیو — three account features on page 1 of the panel.
#   .اسم + متن انگلیسی                    -> sets the account (first) name
#   .بیو + متن                            -> sets the account bio
#   .محتوا (متن نقطه‌دار) (متن جواب)      -> saves a shortcut; from then on
#                                            sending the dotted text edits
#                                            itself into the saved answer
# Every screen is a stack of blockquotes and starts with the fixed "› 𝑯𝑻𝑿".
# ---------------------------------------------------------------------
HTX_TAG = "› <b>𝑯𝑻𝑿</b>"
HTX_CONTENT_KEY = "htx_content_map"
HTX_CONTENT_SHOWN = 12          # max triggers listed on the content screen
HTX_CONTENT_MAX_REPLY = 4000    # Telegram message limit is 4096


def _htx_quote(text):
    return f"<blockquote>{text}</blockquote>"


def _htx_stack(*blocks):
    """Blockquote per block, blank line between them (panel screen style)."""
    return "\n\n".join(_htx_quote(b) for b in blocks if b)


def _htx_balance_text(uid):
    """«.موجودی» / the «موجودی» panel button — same text either way."""
    balance = get_balance(uid)
    toman = balance * DIAMOND_PRICE_TOMAN
    block = _htx_quote(
        "<code>.موجودی</code>\n\n"
        f"💎 موجودی الماس: <code>{_fmt_diamonds(balance)}</code>\n"
        f"💰 معادل تومانی: <code>{_fmt_diamonds(toman)} تومان</code>"
    )
    return f"موجودی شما\n\n{block}\n<b>𝑯𝑻𝑿</b>"


def _htx_transfer_info_text():
    """The panel's «انتقال» button just explains the command -- it needs a
    reply target, which a button tap can't provide."""
    block = _htx_quote(
        "<code>.انتقال 500</code>\n\n"
        "روی پیام گیرنده ریپلای کن و همین دستور را بفرست.\n"
        "هم داخل پی‌وی هم داخل گروه‌های دیگر کار می‌کند."
    )
    return f"انتقال الماس\n\n{block}\n<b>𝑯𝑻𝑿</b>"


async def _self_transfer_command(event, uid, amount):
    """«.انتقال <عدد>» -- reply to someone's message in ANY chat (private
    or any group, not just the official group) to send them diamonds from
    this account. Same tax/limits as the group's «انتقال» command; this is
    the SELF-side equivalent so it isn't gated to one group."""
    if amount < 1:
        await event.edit(premium_ui_text("❌ مبلغ انتقال باید حداقل ۱ الماس باشد."), parse_mode="html")
        return

    if not event.is_reply:
        await event.edit(premium_ui_text("❌ روی پیام گیرنده ریپلای کن و بعد «.انتقال 500» را بفرست."), parse_mode="html")
        return

    reply = await event.get_reply_message()
    if not reply or not reply.sender_id:
        await event.edit(premium_ui_text("❌ گیرنده پیدا نشد."), parse_mode="html")
        return

    receiver = reply.sender_id
    if receiver == uid:
        await event.edit(premium_ui_text("❌ نمی‌توانید به خودتان انتقال دهید."), parse_mode="html")
        return

    try:
        receiver_entity = await reply.get_sender()
    except Exception:
        receiver_entity = None

    receiver_username = (getattr(receiver_entity, "username", None) or "")
    if getattr(receiver_entity, "bot", False) or receiver_username.lower().endswith("bot"):
        await event.edit(
            premium_ui_text(f"{premium_emoji('loser')} انتقال الماس به حساب‌های ربات (Bot) امکان‌پذیر نیست."),
            parse_mode="html")
        return

    tax = max(1, round(amount * TRANSFER_TAX))
    total = amount + tax

    balance = get_balance(uid)
    if balance < total:
        await event.edit(premium_ui_text(
            f"{premium_emoji('loser')} موجودی شما کافی نیست\n\n"
            f"مبلغ انتقال:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
            f"کسر کل با مالیات:\n{premium_number(_fmt_diamonds_plain(total))}\n\n"
            f"موجودی شما:\n{premium_number(_fmt_diamonds_plain(balance))}"
        ), parse_mode="html")
        return

    # Atomic enough for per-user SQLite databases.
    change_balance(uid, -total)
    init_user_db(receiver)
    change_balance(receiver, amount)

    async def _display_name(user_id):
        try:
            entity = await event.client.get_entity(int(user_id))
            username = getattr(entity, "username", None)
        except Exception:
            username = None
        return f"@{username}" if username else str(int(user_id))

    sender_display = await _display_name(uid)
    receiver_display = await _display_name(receiver)
    sender_balance_after = get_balance(uid)
    receiver_balance_after = get_balance(receiver)

    await event.edit(premium_ui_text(
        f"{premium_emoji('transfer_success')} انتقال انجام شد\n\n"
        f"فرستنده: {sender_display}\n"
        f"گیرنده: {receiver_display}\n\n"
        f"مبلغ انتقال:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
        f"مالیات:\n{premium_number(_fmt_diamonds_plain(tax))}\n\n"
        f"کسر کل:\n{premium_number(_fmt_diamonds_plain(total))}\n\n"
        f"موجودی فرستنده:\n{premium_number(_fmt_diamonds_plain(sender_balance_after))}\n\n"
        f"موجودی گیرنده:\n{premium_number(_fmt_diamonds_plain(receiver_balance_after))}"
    ), parse_mode="html")

    try:
        await bot.send_message(
            receiver_entity,
            premium_ui_text(
                f"{premium_emoji('diamond')} انتقال الماس دریافت شد\n\n"
                f"فرستنده: {sender_display}\n"
                f"مبلغ:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
                f"موجودی جدید شما:\n{premium_number(_fmt_diamonds_plain(receiver_balance_after))}"
            ),
            parse_mode="html"
        )
    except Exception as exc:
        print(f"[SELF TRANSFER NOTIFY] failed to notify {receiver}: {exc}")


# ---------------------------------------------------------------------
# «اسکرین 📸» — «.اسکرین» (reply) turns the replied message into a quote
# sticker made by @QuotLyBot.
#
#   1. the replied message is forwarded to @QuotLyBot (with its author)
#   2. the bot's sticker is grabbed the moment it arrives
#   3. the sticker is sent to the chat as a reply to the ORIGINAL message
#   4. the «.اسکرین» command message is deleted and the whole chat with
#      @QuotLyBot is deleted for BOTH sides
# ---------------------------------------------------------------------
QUOTLY_BOT_USERNAME = "QuotLyBot"
QUOTLY_WAIT_SECONDS = 25.0     # give up if the bot never answers
QUOTLY_POLL_INTERVAL = 0.8     # safety-net poll while waiting for the event
_QUOTLY_BOT_IDS = set()        # filled on first use; used by the guards in
                               # self_handle_incoming / self_handle_outgoing
_quotly_locks = {}             # uid -> asyncio.Lock (one screenshot at a time)


def _htx_screenshot_screen(uid):
    """(text, buttons) of the «اسکرین 📸» button on page 3 of the panel."""
    text = _htx_stack(
        f"{HTX_TAG} • اسکرین",
        "دستورات",
        "<code>.اسکرین</code>",
        "روی پیام موردنظر ریپلای کن",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_BALANCE_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _htx_delete_screen(uid):
    """(text, buttons) of the «حذف» button on page 5 of the panel."""
    text = _htx_stack(
        f"{HTX_TAG} • حذف پیام",
        "دستورات",
        "<code>.حذف 50</code>",
        "۵۰ پیام آخر چت به‌صورت دوطرفه پاک می‌شود.",
        "داخل گروه: اگر ادمین باشید هم قابل اجراست.",
        "داخل چنل خودتان هم قابل اجراست.",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_PING_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _htx_info_screen(uid):
    """(text, buttons) of the «اطلاعات» button on page 5 of the panel."""
    text = _htx_stack(
        f"{HTX_TAG} • اطلاعات",
        "دستورات",
        "<code>.آیدی</code>",
        "برای اطلاعات شخص، روی پیام او ریپلای کن",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_PING_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _htx_timerdar_screen(uid):
    """(text, buttons) of the «تایمردار» button on page 5 of the panel."""
    status = "روشن ✅" if self_get(uid, "timer_saver", "off") == "on" else "خاموش ❌"
    text = _htx_stack(
        f"{HTX_TAG} • تایمردار",
        f"وضعیت: {status}",
        "دستورات",
        "<code>.تایمردار روشن</code>\n<code>.تایمردار خاموش</code>",
        "وقتی روشن باشد، هر عکس/ویدیوی تایمردار که برای اکانت ارسال شود، خودکار و بی‌سروصدا داخل سیو مسیج کپی می‌شود.",
        "پیش‌فرض همیشه خاموش است.",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_PING_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


# ---------------------------------------------------------------------
# «ماشین حساب» — «.e 50+25» edits the message into a quote like
#     50+25 = 75 | 𝑯𝑻𝑿
# Exact decimal arithmetic (0.1+0.2 = 0.3), own tiny parser — nothing is
# ever passed to eval().  + - * / ÷ × % ^ ( ) and decimals; Persian/Arabic
# digits work too.
# ---------------------------------------------------------------------
import decimal as _decimal

CALC_MAX_LEN = 120             # characters of the expression
CALC_MAX_EXPONENT = 1000       # |exponent| limit for «^»
_CALC_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?|\.\d+|[-+*/%^()]")
_CALC_INVISIBLE_RE = re.compile(r"[\s\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]+")


class _CalcError(Exception):
    """kind: «invalid» | «div0» | «big»"""

    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


class _CalcParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def parse(self):
        value = self._expr()
        if self._peek() is not None:
            raise _CalcError("invalid")
        return value

    def _expr(self):
        value = self._term()
        while self._peek() in ("+", "-"):
            op = self._next()
            rhs = self._term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def _term(self):
        value = self._unary()
        while self._peek() in ("*", "/", "%"):
            op = self._next()
            rhs = self._unary()
            if op == "*":
                value = value * rhs
            elif rhs == 0:
                raise _CalcError("div0")
            elif op == "/":
                value = value / rhs
            else:
                value = value % rhs
        return value

    def _unary(self):
        tok = self._peek()
        if tok == "-":
            self._next()
            return -self._unary()
        if tok == "+":
            self._next()
            return self._unary()
        return self._power()

    def _power(self):
        base = self._primary()
        if self._peek() == "^":
            self._next()
            exponent = self._unary()          # right-associative, 2^-1 works
            if abs(exponent) > CALC_MAX_EXPONENT:
                raise _CalcError("big")
            if base == 0 and exponent < 0:
                raise _CalcError("div0")
            return base ** exponent
        return base

    def _primary(self):
        tok = self._next()
        if tok is None:
            raise _CalcError("invalid")
        if tok == "(":
            value = self._expr()
            if self._next() != ")":
                raise _CalcError("invalid")
            return value
        if tok[0].isdigit() or tok[0] == ".":
            return Decimal(tok)
        raise _CalcError("invalid")


def _calc_format(value):
    """Decimal -> plain text: no trailing zeros, no exponent for normal sizes."""
    if abs(value) >= Decimal(10) ** 30:
        return format(value, ".6e")
    try:
        value = value.quantize(Decimal("1e-10"), rounding=ROUND_HALF_UP)
    except _decimal.DecimalException:
        pass
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _calc_evaluate(expr):
    """Returns (shown_expression, result_text). Raises _CalcError."""
    shown = _CALC_INVISIBLE_RE.sub("", _fa_digits(expr))
    if not shown or len(shown) > CALC_MAX_LEN:
        raise _CalcError("invalid")
    calc = shown.translate(str.maketrans({"×": "*", "÷": "/", "−": "-", "–": "-", "٫": "."}))
    calc = re.sub(r"(?<=[\d)])[xX](?=[\d(.])", "*", calc).replace("**", "^")
    tokens = []
    pos = 0
    while pos < len(calc):
        m = _CALC_TOKEN_RE.match(calc, pos)
        if not m:
            raise _CalcError("invalid")
        tokens.append(m.group())
        pos = m.end()
    try:
        with _decimal.localcontext() as ctx:
            ctx.prec = 50
            result = _CalcParser(tokens).parse()
            text = _calc_format(result)
    except _CalcError:
        raise
    except (_decimal.DivisionByZero, _decimal.DivisionUndefined):
        raise _CalcError("div0")
    except _decimal.Overflow:
        raise _CalcError("big")
    except (_decimal.DecimalException, RecursionError, ArithmeticError):
        raise _CalcError("invalid")
    return shown, text


_CALC_ERRORS = {
    "invalid": "❌ عبارت نامعتبر است",
    "div0": "❌ تقسیم بر صفر ممکن نیست",
    "big": "❌ عدد خیلی بزرگ است",
}


async def _self_calc_command(event, uid, text):
    """«.e <عبارت>» — returns True when the message was a calculator command."""
    m = re.fullmatch(r"e\s+(\S.*)", (text or "").strip(), re.IGNORECASE | re.DOTALL)
    if not m:
        return False
    try:
        shown, result = _calc_evaluate(m.group(1))
        out = f"{html.escape(shown)} = {result} | 𝑯𝑻𝑿"
    except _CalcError as exc:
        out = f"{_CALC_ERRORS.get(exc.kind, _CALC_ERRORS['invalid'])} | 𝑯𝑻𝑿"
    await event.edit(_htx_quote(out), parse_mode="html")
    return True


def _htx_calc_screen(uid):
    """(text, buttons) of the «ماشین حساب» button on page 4 of the panel."""
    text = _htx_stack(
        f"{HTX_TAG} • ماشین حساب",
        "دستورات",
        "<code>.e 50+25</code>",
        "<code>.e 2*2</code>",
        "<code>.e 30÷2</code>",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_CALC_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _quotly_is_result(msg):
    """True for the bot's answer: a sticker (normally) or an image."""
    if msg is None or getattr(msg, "out", False):
        return False
    if getattr(msg, "sticker", None) or getattr(msg, "photo", None):
        return True
    doc = getattr(msg, "document", None)
    return bool(doc and str(getattr(doc, "mime_type", "") or "").startswith("image/"))


def _tg_is_blocked_error(exc):
    """True when Telegram refuses because the account itself has the bot
    BLOCKED (Telethon: YouBlockedUserError / YOU_BLOCKED_USER). The
    «پاکسازی» tool blocks every bot it cleans, which is how helper bots such
    as @QuotLyBot and the downloader end up blocked. «UserIsBlockedError» is
    the opposite case (the bot blocked us) — kept only for old behaviour."""
    return type(exc).__name__ in ("YouBlockedUserError", "UserIsBlockedError")


async def _tg_call_unblocking(client, peer, factory):
    """Run factory(); if the bot turns out to be blocked, unblock it and run
    it once more — so the helper bots never stop working because of a block."""
    try:
        return await factory()
    except Exception as exc:
        if not _tg_is_blocked_error(exc):
            raise
    await client(functions.contacts.UnblockRequest(id=peer))
    return await factory()


async def _quotly_forget_sticker(client, media):
    """The sticker that was just sent lands in the account's recent stickers;
    take it out again (and out of the favourites, just in case). Done twice:
    Telegram sometimes records the sticker a moment after it was sent."""
    doc = getattr(media, "document", None)
    if doc is None:
        return
    try:
        inp = utils.get_input_document(doc)
    except Exception:
        return
    for attempt in range(2):
        for req in (
            functions.messages.SaveRecentStickerRequest(id=inp, unsave=True),
            functions.messages.FaveStickerRequest(id=inp, unfave=True),
        ):
            with contextlib.suppress(Exception):
                await client(req)
        if attempt == 0:
            await asyncio.sleep(2.0)


async def _quotly_purge(client, entity):
    """Delete the whole chat with @QuotLyBot, for both sides."""
    try:
        await asyncio.wait_for(_cleanup_delete_private(client, entity), 30)
    except Exception as exc:
        print(f"[SELF] screenshot cleanup: {type(exc).__name__}: {exc}")


async def _self_screenshot_command(event, uid):
    """«.اسکرین» — reply to a message, get its quote sticker as a reply."""
    uid = int(uid)

    async def fail(text):
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(text), parse_mode="html")

    if not event.is_reply:
        await fail("❌ روی پیام موردنظر ریپلای کن و «.اسکرین» را بفرست.")
        return

    # One screenshot at a time per account, so two quick commands can never
    # pick up each other's sticker from the bot chat.
    lock = _quotly_locks.setdefault(uid, asyncio.Lock())
    async with lock:
        await _self_screenshot_run(event, uid, fail)


async def _self_screenshot_run(event, uid, fail):
    client = event.client

    with contextlib.suppress(Exception):
        await event.edit(_htx_quote(f"{HTX_TAG} | درحال ساخت اسکرین"), parse_mode="html")

    reply_msg, quotly = await asyncio.gather(
        event.get_reply_message(),
        client.get_entity(QUOTLY_BOT_USERNAME),
        return_exceptions=True,
    )
    if isinstance(reply_msg, BaseException) or not reply_msg:
        await fail("❌ پیام ریپلای‌شده پیدا نشد.")
        return
    if isinstance(quotly, BaseException):
        print(f"[SELF {uid}] screenshot: cannot resolve @{QUOTLY_BOT_USERNAME}: {quotly}")
        await fail(f"❌ ربات @{QUOTLY_BOT_USERNAME} پیدا نشد.")
        return

    # Registered BEFORE anything is forwarded: the guards in the incoming /
    # outgoing handlers then already know this chat, so the forwarded copy
    # is never run as a command (a replied message starting with «.») and
    # the bot's answer never triggers secretary / auto-reply / archive.
    quotly_id = int(quotly.id)
    _QUOTLY_BOT_IDS.add(quotly_id)

    loop = asyncio.get_running_loop()
    answer = loop.create_future()
    state = {"after": 0, "text": ""}

    async def _on_quotly_message(ev):
        msg = ev.message
        if answer.done() or int(getattr(msg, "id", 0) or 0) <= state["after"]:
            return
        if _quotly_is_result(msg):
            answer.set_result(msg)
        else:
            note = (getattr(msg, "raw_text", "") or "").strip()
            if note:
                state["text"] = note

    client.add_event_handler(_on_quotly_message, events.NewMessage(chats=quotly_id, incoming=True))
    forwarded = False
    success = False
    hidden = False
    sticker_media = None
    try:
        # Same as the downloader: the chat with the bot is muted and moved to
        # the Archive BEFORE the message goes out, and again right after, so
        # it never shows up in the chat list.
        hidden = True
        await _dl_hide(client, quotly, log_errors=False)
        fwd = await _tg_call_unblocking(
            client, quotly, lambda: client.forward_messages(quotly, reply_msg)
        )
        forwarded = True
        if isinstance(fwd, (list, tuple)):
            fwd = fwd[0] if fwd else None
        state["after"] = int(getattr(fwd, "id", 0) or 0)
        await _dl_hide(client, quotly, mute=False, log_errors=False)

        # The new-message event normally fires within a moment; the short
        # poll below is only a safety net if that update is late/missed.
        result = None
        deadline = loop.time() + QUOTLY_WAIT_SECONDS
        while result is None and loop.time() < deadline:
            done, _ = await asyncio.wait({answer}, timeout=QUOTLY_POLL_INTERVAL)
            if done:
                result = answer.result()
                break
            with contextlib.suppress(Exception):
                recent = await client.get_messages(quotly, limit=6, min_id=state["after"])
                for msg in reversed(list(recent)):
                    if _quotly_is_result(msg):
                        result = msg
                        break

        if result is None:
            note = state["text"]
            detail = f"\n<code>{html.escape(note[:200])}</code>" if note else ""
            await fail(f"❌ ربات @{QUOTLY_BOT_USERNAME} جواب نداد.{detail}")
            return

        # Reuses the sticker already on Telegram's servers (no re-upload).
        sent = await client.send_file(event.chat_id, result.media, reply_to=reply_msg)
        sticker_media = getattr(sent, "media", None) or result.media
        success = True
    except Exception as exc:
        name = type(exc).__name__
        print(f"[SELF {uid}] screenshot failed: {name}: {exc}")
        if name == "ChatForwardsRestrictedError":
            await fail("❌ این چت فوروارد را محدود کرده؛ اسکرین ساخته نمی‌شود.")
        elif isinstance(exc, FloodWaitError):
            await fail(f"❌ تلگرام محدودیت موقت گذاشته؛ {int(getattr(exc, 'seconds', 0) or 0)} ثانیه بعد دوباره امتحان کن.")
        else:
            await fail(f"❌ ساخت اسکرین ناموفق بود.\n<code>{html.escape(name)}</code>")
    finally:
        client.remove_event_handler(_on_quotly_message)
        jobs = []
        if forwarded:
            # Whole chat with the bot, for both sides.
            jobs.append(_quotly_purge(client, quotly))
        if success:
            jobs.append(event.delete())                                 # the «.اسکرین» message
            jobs.append(_quotly_forget_sticker(client, sticker_media))  # not kept in the account's stickers
        if jobs:
            for res in await asyncio.gather(*jobs, return_exceptions=True):
                if isinstance(res, Exception):
                    print(f"[SELF {uid}] screenshot cleanup: {type(res).__name__}: {res}")
        if hidden:
            # Reset the mute and the bot's spot in «frequent contacts».
            await _dl_forget(client, quotly, unmute=True)


DELETE_MAX_COUNT = 1000


async def _self_delete_command(event, uid, count):
    """«.حذف N» — deletes the last N messages of the chat for both sides.
    Works in PV, in groups (admin only) and in channels (admin only)."""
    client = event.client
    if count < 1:
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text("❌ عدد باید بزرگتر از صفر باشد."), parse_mode="html")
        return
    count = min(count, DELETE_MAX_COUNT)

    if (event.is_group or event.is_channel) and not await _is_group_admin(client, event.chat_id, uid):
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text("❌ فقط ادمین می‌تواند پیام‌ها را حذف کند."), parse_mode="html")
        return

    try:
        msgs = await client.get_messages(event.chat_id, limit=count)
        ids = [int(m.id) for m in msgs]
        if ids:
            await client.delete_messages(event.chat_id, ids, revoke=True)
    except Exception as exc:
        print(f"[SELF {uid}] delete failed: {type(exc).__name__}: {exc}")
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(f"❌ حذف پیام‌ها ناموفق بود.\n<code>{html.escape(type(exc).__name__)}</code>"), parse_mode="html")


async def _self_id_info_command(event, uid):
    """«.آیدی» (reply) — shows نام / نام خانوادگی / یوزرنیم / آیدی عددی of
    the replied message's sender, in place, keeping the native reply-quote
    to their message visible above it."""
    async def fail(text):
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(text), parse_mode="html")

    if not event.is_reply:
        await fail("❌ روی پیام موردنظر ریپلای کن.")
        return
    replied = await event.get_reply_message()
    if not replied or not replied.sender_id:
        await fail("❌ فرستنده پیام پیدا نشد.")
        return

    try:
        sender = await event.client.get_entity(int(replied.sender_id))
    except Exception as exc:
        print(f"[SELF {uid}] id info failed: {type(exc).__name__}: {exc}")
        await fail("❌ اطلاعات کاربر پیدا نشد.")
        return

    first = html.escape(getattr(sender, "first_name", None) or "—")
    last = html.escape(getattr(sender, "last_name", None) or "—")
    username = getattr(sender, "username", None)
    uname_text = html.escape(f"@{username}") if username else "—"
    block = _htx_quote(
        f"نام: {first}\n"
        f"نام خانوادگی: {last}\n"
        f"یوزرنیم: {uname_text}\n"
        f"آیدی عددی: <code>{int(replied.sender_id)}</code>\n\n"
        f"{HTX_TAG}"
    )
    with contextlib.suppress(Exception):
        await event.edit(block, parse_mode="html")


# ---------------------------------------------------------------------
# «دانلودر اینستاگرام» — «.دانلود <لینک>»
#
# The downloader (Riva) runs on its own server as a Telegram bot. The self
# talks to it with the user's OWN account and does everything hidden:
#   1. the chat with the bot is muted and moved to the Archive — before the
#      message goes out and again right after — so nothing shows up in the
#      chat list
#   2. "<link>-480p" is sent: the suffix makes the bot answer quietly, at
#      480p, with no quality buttons
#   3. the file is picked up the moment the bot sends it and re-sent to the
#      chat (no re-upload — it already lives on Telegram's servers)
#   4. the whole chat with the bot is deleted for BOTH sides, and so is the
#      «.دانلود» message; the mute and the bot's spot in Telegram's «frequent
#      contacts» are reset too, so nothing is left behind
# Only Instagram links are accepted.
# ---------------------------------------------------------------------
DL_BACKEND_USERNAME = "tirexxxxxxbot"   # the downloader bot — never shown to users
DL_QUALITY_SUFFIX = "-480p"             # tells the bot: 480p, no menu, quiet
DL_WAIT_SECONDS = 600.0                 # give up if the bot never answers
DL_POLL_INTERVAL = 4.0                  # safety-net poll while waiting for the event
DL_MAX_LINK_LEN = 500
_DL_BOT_IDS = set()      # filled on first use; used by the incoming/outgoing guards
_dl_locks = {}           # uid -> asyncio.Lock (one download at a time per account)
_dl_active = set()       # uids with a download running right now
_dl_stale = {}           # uid -> ids of requests that timed out (their late answers are ignored)
_dl_bg_tasks = set()

_DL_HOSTS = {
    "instagram": ("instagram.com", "instagr.am"),
    "ph": ("pornhub.com", "pornhub.org"),
    "xvid": ("xvideos.com", "xvideos2.com"),
    "xnxx": ("xnxx.com", "www.xnxx.com"),
}
_DL_HTTP_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
_DL_BARE_RE = re.compile(
    r"(?<![\w./@-])((?:[a-z0-9-]+\.)*(?:instagram\.com|instagr\.am)/[^\s<>\"']*)",
    re.I,
)
_DL_INVISIBLE_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]")

_DL_ERRORS = {
    "need_url": "❌ لینک معتبر نیست",
    "bad_url": "❌ لینک خوانده نشد؛ ممکن است خصوصی، حذف‌شده یا پشتیبانی‌نشده باشد",
    "restricted": "❌ این محتوا خصوصی است یا نیاز به ورود دارد",
    "blocked": "❌ درخواست رد شد؛ کمی بعد دوباره امتحان کن",
    "timeout": "❌ پاسخ دیر رسید؛ دوباره امتحان کن",
    "too_big": "❌ حجم فایل از سقف ارسال تلگرام بیشتر است",
    "error": "❌ دانلود ناموفق بود",
}


def _htx_dl_screen(uid, title, example, hint, note, back_page=None):
    """(text, buttons) of a downloader button. «بازگشت» returns to the panel
    page the button actually sits on (back_page), page 4 by default."""
    if back_page is None:
        back_page = PANEL_CALC_PAGE
    text = _htx_stack(
        f"{HTX_TAG} • {title}",
        "دستورات",
        f"<code>{example}</code>",
        hint,
        note,
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{back_page}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _htx_tts_screen(uid):
    """(text, buttons) of the «متن به ویس» button on page 2 of the panel."""
    text = _htx_stack(
        f"{HTX_TAG} • تبدیل متن به ویس",
        "دستورات",
        "<code>.ویس متن</code>\nصدای زن",
        "<code>.ویس مرد متن</code>\nصدای مرد",
        "<code>.ویس</code>\nریپلای روی پیام متنی",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_FE_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _htx_ig_dl_screen(uid):
    return _htx_dl_screen(
        uid,
        "دانلودر اینستاگرام",
        ".اینستا https://www.instagram.com/reel/…",
        "لینک ریل یا پست اینستاگرام را بعد از دستور بنویس",
        "ویدیو یا عکس همین‌جا برایت ارسال می‌شود",
    )


def _htx_extra_dl_screen(uid, title, command, example, hint, item_key=None):
    # The back step is resolved from PANEL_ITEMS, so it always returns to the
    # exact page the button was opened from (no hard-coded page number).
    back_page = _panel_key_page(item_key) if item_key else None
    return _htx_dl_screen(uid, title, f"{command} {example}", hint,
                          "فایل همین‌جا برایت ارسال می‌شود", back_page=back_page)


def _htx_ph_dl_screen(uid):
    return _htx_extra_dl_screen(uid, "دانلودر PH", ".ph", "https://pornhub.com/view_video.php?viewkey=…",
                                "لینک Pornhub را بعد از دستور بنویس", item_key="ph_dl")


def _htx_xvid_dl_screen(uid):
    return _htx_extra_dl_screen(uid, "دانلودر Xvid", ".xvid", "https://xvideos.com/video/…",
                                 "لینک Xvid را بعد از دستور بنویس", item_key="xvid_dl")


def _htx_xnxx_dl_screen(uid):
    return _htx_extra_dl_screen(uid, "دانلودر XNXX", ".xnxx", "https://xnxx.com/video/…",
                                "لینک XNXX را بعد از دستور بنویس", item_key="xnxx_dl")


def _htx_snap_screen(uid):
    """(text, buttons) of the «اسنپ شات» button on page 4 of the panel."""
    group_status = "روشن ✅" if self_get(uid, "snap_group", "off") == "on" else "خاموش ❌"
    private_status = "روشن ✅" if self_get(uid, "snap_private", "off") == "on" else "خاموش ❌"
    text = _htx_stack(
        f"{HTX_TAG} • اسنپ شات",
        f"وضعیت گپ: {group_status}\nوضعیت پیوی: {private_status}",
        "دستورات",
        "<code>.اسنپ شات گپ روشن</code>\n<code>.اسنپ شات گپ خاموش</code>\n<code>.اسنپ شات پیوی روشن</code>\n<code>.اسنپ شات پیوی خاموش</code>",
        "گپ: وقتی کسی داخل گروه روی یک نفر ریپلای بزند و بعد همان ریپلای را حذف کند، متن آن ریپلای همراه با آیدی فرستنده و آیدی گروه داخل سیو مسیج ذخیره می‌شود.",
        "پیوی: پیام‌های خصوصی حذف‌شده به همین شکل در سیو مسیج ذخیره می‌شوند.",
        "پیش‌فرض هر دو خاموش است.",
    )
    buttons = [[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_CALC_PAGE}"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]]
    return text, buttons


def _dl_parse_link(arg):
    """(url, platform): platform is «instagram»; url is None when
    there is no usable link, platform is None for any other site."""
    arg = _DL_INVISIBLE_RE.sub("", arg or "")
    m = _DL_HTTP_RE.search(arg)
    url = m.group(0) if m else None
    if not url:
        m = _DL_BARE_RE.search(arg)
        url = ("https://" + m.group(1)) if m else None
    if not url:
        return None, None
    url = url.rstrip(").,;]}>\"'،؛")
    if not url or len(url) > DL_MAX_LINK_LEN:
        return None, None
    try:
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return None, None
    for platform, domains in _DL_HOSTS.items():
        if any(host == d or host.endswith("." + d) for d in domains):
            return url, platform
    return url, None


async def _dl_mute(client, peer):
    await client(functions.account.UpdateNotifySettingsRequest(
        peer=types.InputNotifyPeer(peer=peer),
        settings=types.InputPeerNotifySettings(show_previews=False, silent=True, mute_until=2147483647),
    ))


async def _dl_archive(client, peer):
    await client(functions.folders.EditPeerFoldersRequest(
        folder_peers=[types.InputFolderPeer(peer=peer, folder_id=1)]
    ))


async def _dl_hide(client, backend, *, mute=True, log_errors=True):
    """Mute the chat with the downloader bot and move it to the Archive
    (best effort — before the first message there may be no dialog yet)."""
    try:
        peer = await client.get_input_entity(backend)
        jobs = [_dl_archive(client, peer)]
        if mute:
            jobs.append(_dl_mute(client, peer))
        results = await asyncio.gather(*jobs, return_exceptions=True)
    except Exception as exc:
        results = [exc]
    if log_errors:
        for res in results:
            if isinstance(res, Exception):
                print(f"[SELF] download: hiding the chat failed: {type(res).__name__}: {res}")


async def _dl_purge(client, entity):
    """Delete the whole chat with the downloader bot, for both sides."""
    try:
        await asyncio.wait_for(_cleanup_delete_private(client, entity), 30)
    except Exception as exc:
        print(f"[SELF] download: cleanup failed: {type(exc).__name__}: {exc}")


async def _dl_forget(client, backend, *, unmute):
    """Remove the traces the chat leaves besides the messages themselves: the bot
    in Telegram's «frequent contacts» suggestions and the notification exception
    created by the mute (best effort)."""
    try:
        peer = await client.get_input_entity(backend)
        jobs = [
            client(functions.contacts.ResetTopPeerRatingRequest(category=types.TopPeerCategoryBotsPM(), peer=peer)),
            client(functions.contacts.ResetTopPeerRatingRequest(category=types.TopPeerCategoryCorrespondents(), peer=peer)),
        ]
        if unmute:
            jobs.append(client(functions.account.UpdateNotifySettingsRequest(
                peer=types.InputNotifyPeer(peer=peer), settings=types.InputPeerNotifySettings(),
            )))
        results = await asyncio.gather(*jobs, return_exceptions=True)
    except Exception as exc:
        results = [exc]
    for res in results:
        if isinstance(res, Exception):
            print(f"[SELF] download: forgetting the chat failed: {type(res).__name__}: {res}")


def _dl_sweep_later(client, sender_id):
    async def _sweep():
        with contextlib.suppress(Exception):
            await _dl_purge(client, await client.get_input_entity(sender_id))

    task = asyncio.get_running_loop().create_task(_sweep())
    _dl_bg_tasks.add(task)
    task.add_done_callback(_dl_bg_tasks.discard)


_DL_CAPTION_LABEL = {
    "instagram": "instagram downloader",
}


def _dl_caption(platform):
    """Fixed, branded caption for the re-sent file — never the bot's own
    caption (so its username/links can never leak through)."""
    label = _DL_CAPTION_LABEL.get(platform, "downloader")
    return _htx_quote(f"{HTX_TAG} Self Bot\n{label}")


async def _self_download_command(event, uid, arg, expected_platform=None):
    """Downloader commands: .اینستا, .ph, and .xvid."""
    uid = int(uid)

    async def say(text):
        with contextlib.suppress(Exception):
            await event.edit(_htx_quote(f"{text} | 𝑯𝑻𝑿"), parse_mode="html")

    url, platform = _dl_parse_link(arg)
    if not url:
        await say(_DL_ERRORS["need_url"])
        return
    if not platform or (expected_platform and platform != expected_platform):
        await say("❌ لینک با دانلودر انتخاب‌شده سازگار نیست")
        return

    # One download at a time per account, so answers can never be mixed up.
    lock = _dl_locks.setdefault(uid, asyncio.Lock())
    if lock.locked():
        await say("⏳ در صف قرار گرفت")
    async with lock:
        await _self_download_run(event, uid, url, platform, say)


async def _self_download_run(event, uid, url, platform, say):
    client = event.client
    try:
        backend = await client.get_entity(DL_BACKEND_USERNAME)
    except Exception as exc:
        print(f"[SELF {uid}] download: cannot reach the downloader: {type(exc).__name__}: {exc}")
        await say(_DL_ERRORS["error"])
        return

    # Known BEFORE anything is sent: the guards in the incoming/outgoing
    # handlers then already leave this chat alone.
    backend_id = int(backend.id)
    _DL_BOT_IDS.add(backend_id)
    _dl_active.add(uid)

    loop = asyncio.get_running_loop()
    answer = loop.create_future()
    state = {"sent": 0}
    stale = _dl_stale.setdefault(uid, set())

    def classify(msg):
        """'media' / 'error' for an answer to the current request, else None."""
        if msg is None or getattr(msg, "out", False):
            return None
        if state["sent"] and int(getattr(msg, "id", 0) or 0) <= state["sent"]:
            return None
        if getattr(msg, "reply_to_msg_id", None) in stale:
            return None  # late answer to a request that already timed out
        if (getattr(msg, "raw_text", "") or "").strip().startswith("❌"):
            return "error"
        if getattr(msg, "photo", None) or getattr(msg, "document", None):
            return "media"
        return None

    async def _on_backend_message(ev):
        if answer.done():
            return
        kind = classify(ev.message)
        if kind:
            answer.set_result((kind, ev.message))

    client.add_event_handler(_on_backend_message, events.NewMessage(chats=backend_id, incoming=True))
    success = False
    keep_muted = False   # after a timeout a late answer may still arrive: stay muted
    try:
        await asyncio.gather(say("⏳ در حال دانلود"), _dl_hide(client, backend, log_errors=False))

        sent = await _tg_call_unblocking(
            client, backend,
            lambda: client.send_message(
                backend, url + DL_QUALITY_SUFFIX, link_preview=False, parse_mode=None
            ),
        )
        state["sent"] = int(getattr(sent, "id", 0) or 0)
        # The dialog exists now: make sure it sits in the Archive.
        await _dl_hide(client, backend, mute=False)

        # The new-message event normally fires the moment the bot answers; the
        # slow poll is only a safety net in case that update is late/missed.
        result = None
        deadline = loop.time() + DL_WAIT_SECONDS
        while result is None and loop.time() < deadline:
            done, _ = await asyncio.wait({answer}, timeout=DL_POLL_INTERVAL)
            if done:
                result = answer.result()
                break
            with contextlib.suppress(Exception):
                recent = await client.get_messages(backend, limit=6, min_id=state["sent"])
                for msg in reversed(list(recent)):
                    kind = classify(msg)
                    if kind:
                        result = (kind, msg)
                        break

        if result is None:
            keep_muted = True
            stale.add(state["sent"])
            if len(stale) > 50:
                stale.discard(min(stale))
            await say(_DL_ERRORS["timeout"])
            return

        kind, msg = result
        if kind == "error":
            m = re.match(r"❌\s*([a-z_]+)", (msg.raw_text or "").strip())
            await say(_DL_ERRORS.get(m.group(1) if m else "error", _DL_ERRORS["error"]))
            return

        caption = _dl_caption(platform)
        # Reuses the file already on Telegram's servers (no re-upload).
        await client.send_file(
            event.chat_id,
            msg.media,
            caption=caption,
            parse_mode="html",
            reply_to=event.message.reply_to_msg_id,
        )
        success = True
    except Exception as exc:
        print(f"[SELF {uid}] download failed: {type(exc).__name__}: {exc}")
        if isinstance(exc, FloodWaitError):
            await say(f"❌ تلگرام محدودیت موقت گذاشته؛ {int(getattr(exc, 'seconds', 0) or 0)} ثانیه بعد دوباره امتحان کن")
        else:
            await say(_DL_ERRORS["error"])
    finally:
        client.remove_event_handler(_on_backend_message)
        jobs = [_dl_purge(client, backend)]      # the chat with the bot: gone, both sides
        if success:
            jobs.append(event.delete())          # and the «.دانلود» message
        for res in await asyncio.gather(*jobs, return_exceptions=True):
            if isinstance(res, Exception):
                print(f"[SELF {uid}] download cleanup: {type(res).__name__}: {res}")
        await _dl_forget(client, backend, unmute=not keep_muted)
        _dl_active.discard(uid)


def _fake_ping_ms():
    """Displayed ping: always a low, steady 20–23 ms (not the real latency)."""
    return round(random.uniform(20.0, 23.0), 2)


def _ping_text():
    return _htx_stack("پینگ › <b>𝑯𝑻𝑿</b> Self :", f"<code>{_fake_ping_ms():.2f} ms</code>")


def _htx_reply(title, *lines):
    """Text used when an .اسم/.بیو/.محتوا command message edits itself."""
    return _htx_stack(f"{HTX_TAG} • {title}", *lines)


def _htx_norm_key(value):
    """Canonical form of a content trigger (also used to match messages)."""
    value = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]", "", value or "")
    value = value.replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"\s+", " ", value).strip().casefold()


def htx_content_map(uid):
    try:
        raw = json.loads(self_get(uid, HTX_CONTENT_KEY, "{}"))
        return {str(k): str(v) for k, v in raw.items()} if isinstance(raw, dict) else {}
    except Exception:
        return {}


def htx_save_content_map(uid, mapping):
    self_set(uid, HTX_CONTENT_KEY, json.dumps(mapping, ensure_ascii=False))


def _htx_screen(uid, kind):
    """(caption, buttons) for the اسم / محتوا / بیو screens."""
    back = btn("بازگشت", _self_cb(uid, "pg:0"), "danger", icon=PREMIUM_EMOJI["self_back"][0])
    if kind == "name":
        text = _htx_stack(
            f"{HTX_TAG} • اسم",
            "دستورات",
            "<code>.اسم + متن انگلیسی</code>",
        )
        return text, [[back]]
    if kind == "bio":
        text = _htx_stack(
            f"{HTX_TAG} • بیو",
            "دستورات",
            "<code>.بیو + متن</code>",
        )
        return text, [[back]]

    keys = list(htx_content_map(uid).keys())
    blocks = [
        f"{HTX_TAG} • محتوا",
        "نحوه استفاده",
        "<code>.محتوا + (متن نقطه دار) + (متن جواب)</code>",
        "مثال : شما میخواید شماره کارت خود ثبت کنید",
        "مینویسید :",
        "<code>.محتوا ( .شماره کارت ) (610433.....)</code>",
        "وقتی ثبت شد از الان هر وقت بنویسید .شماره کارت به 610433..... ادیت میشه",
        f"تعداد محتوای ثبت‌شده : {len(keys)}",
    ]
    if not keys:
        blocks.append("هنوز محتوایی ثبت نکردی")
    else:
        # Only the triggers are listed — never the saved answers, since the
        # panel can be opened in a chat other people can see.
        lines = [f"{i}. <code>{html.escape(k[:30])}</code>" for i, k in enumerate(keys[:HTX_CONTENT_SHOWN], 1)]
        if len(keys) > HTX_CONTENT_SHOWN:
            lines.append(f"… و {len(keys) - HTX_CONTENT_SHOWN} مورد دیگر")
        blocks.append("\n".join(lines))
    buttons = [
        [btn("پاکسازی همه محتواها", _self_cb(uid, "hx_content_clear"), "danger")],
        [back],
    ]
    return _htx_stack(*blocks), buttons


_HTX_NAME_RE = re.compile(r"^\.\s*اسم\s+(?:\+\s+)?(.+)$", re.S)
_HTX_BIO_RE = re.compile(r"^\.\s*ب[یي]و\s+(?:\+\s+)?(.+)$", re.S)
_HTX_CONTENT_RE = re.compile(r"^\.\s*محتوا\s*\+?\s*\(\s*(.+?)\s*\)\s*\+?\s*\(\s*(.+)\s*\)$", re.S)
_HTX_RESERVED_TRIGGERS = {".پنل", ".اسم", ".بیو", ".محتوا"}


async def _htx_edit(event, text):
    # Plain HTML on purpose (no premium_ui_text): a non-premium SELF account
    # can fail to edit a message into containing a custom-emoji entity.
    with contextlib.suppress(Exception):
        await event.edit(text, parse_mode="html")


async def _htx_set_name(event, uid, name):
    if len(name) > 64:
        await _htx_edit(event, _htx_reply("اسم", "❌ اسم نباید بیشتر از ۶۴ کاراکتر باشد."))
        return
    client = event.client
    try:
        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(first_name=name))
        # If the clock-on-name feature is on, re-append the clock right away
        # so the worker doesn't fight the new name.
        if time_name_enabled(uid):
            await update_time_name(uid, client)
    except Exception as exc:
        await _htx_edit(event, _htx_reply("اسم", f"❌ تغییر اسم انجام نشد: <code>{html.escape(str(exc))}</code>"))
        return
    await _htx_edit(event, _htx_reply("اسم", f"✅ اسم اکانت روی <code>{html.escape(name)}</code> تنظیم شد."))


async def _htx_set_bio(event, uid, bio):
    client = event.client
    try:
        me = await client.get_me()
        limit = _bio_limit(me)
        # With the bio clock on, the clock is appended after the new bio.
        suffix = f" | {self_clock(uid)}" if time_bio_enabled(uid) else ""
        if len(bio) + len(suffix) > limit:
            room = limit - len(suffix)
            await _htx_edit(event, _htx_reply("بیو", f"❌ بیو نباید بیشتر از {room} کاراکتر باشد. (الان {len(bio)})"))
            return
        await client(functions.account.UpdateProfileRequest(about=bio + suffix))
        _BIO_CLOCK_TOO_LONG.discard(int(uid))
    except Exception as exc:
        await _htx_edit(event, _htx_reply("بیو", f"❌ تغییر بیو انجام نشد: <code>{html.escape(str(exc))}</code>"))
        return
    await _htx_edit(event, _htx_reply("بیو", "✅ بیو اکانت تنظیم شد."))


async def _htx_save_content(event, uid, trigger, answer):
    trigger = trigger.strip()
    if "\n" in trigger:
        await _htx_edit(event, _htx_reply("محتوا", "❌ متن نقطه‌دار باید تک‌خطی باشد."))
        return
    if not trigger.startswith("."):
        trigger = "." + trigger
    key = _htx_norm_key(trigger)
    if len(key) < 2 or key in _HTX_RESERVED_TRIGGERS:
        await _htx_edit(event, _htx_reply("محتوا", "❌ این متن نقطه‌دار قابل ثبت نیست؛ یک متن دیگر انتخاب کن."))
        return
    if len(answer) > HTX_CONTENT_MAX_REPLY:
        await _htx_edit(event, _htx_reply("محتوا", f"❌ متن جواب نباید بیشتر از {HTX_CONTENT_MAX_REPLY} کاراکتر باشد."))
        return
    mapping = htx_content_map(uid)
    mapping[key] = answer
    htx_save_content_map(uid, mapping)
    print(f"[SELF {uid}] content saved: {key!r} (total {len(mapping)})")
    # The saved answer is deliberately NOT echoed back: the command message
    # (which contained it) is replaced, so e.g. a card number doesn't stay
    # visible in the chat.
    await _htx_edit(event, _htx_reply(
        "محتوا",
        f"✅ ثبت شد: <code>{html.escape(key)}</code>",
        f"تعداد محتوای ثبت‌شده : {len(mapping)}",
    ))


_HTX_CONTENT_LOOSE_RE = re.compile(r"^\.\s*محتوا(?=[\s(+])\s*\+?\s*(.*)$", re.S)
_HTX_CONTENT_USAGE = (
    "❌ فرمت درست:",
    "<code>.محتوا .شماره کارت 5022291580208</code>",
    "برای جواب چندکلمه‌ای یا چندخطی:",
    "<code>.محتوا ( .آدرس ) (متن جواب)</code>",
)


def _htx_split_loose(rest):
    """`.محتوا <trigger> <answer>` without parentheses.

    Several lines: first line = trigger, the rest = answer.
    One line:      the LAST word = answer, everything before it = trigger.
    """
    rest = rest.strip()
    if "\n" in rest:
        first, others = rest.split("\n", 1)
        if first.strip() and others.strip():
            return first.strip(), others.strip()
    parts = rest.replace("\n", " ").rsplit(None, 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None


async def _handle_htx_profile_command(event, uid, text):
    """«.اسم» / «.بیو» / «.محتوا». Returns True when the message was handled."""
    norm = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]", "", text).strip()
    if not norm.startswith("."):
        return False
    m = _HTX_NAME_RE.match(norm)
    if m:
        await _htx_set_name(event, uid, m.group(1).strip())
        return True
    m = _HTX_BIO_RE.match(norm)
    if m:
        await _htx_set_bio(event, uid, m.group(1).strip())
        return True
    m = _HTX_CONTENT_RE.match(norm)          # .محتوا (متن نقطه‌دار) (متن جواب)
    if m:
        await _htx_save_content(event, uid, m.group(1), m.group(2).strip())
        return True
    m = _HTX_CONTENT_LOOSE_RE.match(norm)    # .محتوا .شماره کارت 5022...
    if m or re.fullmatch(r"\.\s*محتوا", norm):
        trigger, answer = _htx_split_loose(m.group(1)) if m else (None, None)
        if not trigger or not answer:
            await _htx_edit(event, _htx_reply("محتوا", *_HTX_CONTENT_USAGE))
            return True
        await _htx_save_content(event, uid, trigger, answer)
        return True
    return False


def _htx_content_regex(keys):
    parts = [
        r"\s+".join(re.escape(tok) for tok in k.split(" "))
        for k in sorted(keys, key=len, reverse=True)
    ]
    return re.compile(r"(?<![\w.])(?:" + "|".join(parts) + r")(?![\w\u200c])", re.IGNORECASE)


async def _htx_apply_content(event, uid, text):
    """Replace every saved dotted trigger inside the sent message with its
    saved answer (the trigger can be the whole message or sit anywhere in
    it, e.g. on its own line between other text)."""
    if "." not in text:
        return False
    mapping = htx_content_map(uid)
    if not mapping:
        return False
    # Same-length normalisation (ي→ی, ك→ک) so match positions map 1:1 onto
    # the original text.
    search = text.replace("ي", "ی").replace("ك", "ک")
    rx = _htx_content_regex(mapping.keys())
    out, pos, hits = [], 0, 0
    for m in rx.finditer(search):
        answer = mapping.get(_htx_norm_key(m.group(0)))
        if answer is None:
            continue
        out.append(text[pos:m.start()])
        out.append(answer)
        pos = m.end()
        hits += 1
    if not hits:
        return False
    out.append(text[pos:])
    # A space typed after a trigger that ends a line shouldn't leak into the result.
    new_text = re.sub(r"[ \t]+\n", "\n", "".join(out))
    try:
        await event.edit(new_text, parse_mode=None)
    except MessageNotModifiedError:
        pass
    except Exception as exc:
        print(f"[SELF {uid}] content shortcut edit failed: {exc}")
    return True


# ---------------------------------------------------------------------
# دوست و دشمن — two per-account user lists that get an instant auto-reply.
# Sits on page 2 of the panel (above «بستن»), next to «ساخت ویدیو گرد».
#
#   .تنظیم دشمن + ریپلی   -> the replied user becomes an enemy. From then on
#                            every message that user sends in any group or
#                            private chat this account is in gets an instant
#                            reply with a random saved «فحش».
#   .تنظیم دوست + ریپلی   -> exactly the same, with its own user list and its
#                            own saved «جواب» texts.
#
# The reply texts start out as the built-in HTX_FE_DEFAULT_TEXTS pool
# (seeded into the account's own list on first use) and from then on are
# edited like any normal saved list («.افزودن فحش متن» /
# «.افزودن جواب دوست متن», «.حذف … شماره», «.پاکسازی لیست …»).
# A user can only be in one of the two lists at a time.
# ---------------------------------------------------------------------
PANEL_FE_PAGE = 1                 # zero-based index -> page 2 of the panel
PANEL_BALANCE_PAGE = 2             # zero-based index -> page 3 of the panel
PANEL_CALC_PAGE = 3                # zero-based index -> page 4 of the panel
HTX_FE_MAX_TEXTS = 200
HTX_FE_MAX_TEXT_LEN = 4000        # Telegram message limit is 4096
HTX_FE_LIST_CHARS = 3300          # keep list replies under the 4096 limit

_HTX_FE_KEYS = {
    "enemy": ("htx_enemy_users", "htx_enemy_texts"),
    "friend": ("htx_friend_users", "htx_friend_texts"),
}
_HTX_FE_WORDS = {
    "enemy": {
        "one": "دشمن", "many": "دشمنان",
        "text": "فحش", "texts": "فحش‌ها",
        "add_cmd": ".افزودن فحش متن",
        "del_cmd": ".حذف فحش شماره",
    },
    "friend": {
        "one": "دوست", "many": "دوستان",
        "text": "جواب", "texts": "جواب‌ها",
        "add_cmd": ".افزودن جواب دوست متن",
        "del_cmd": ".حذف جواب دوست شماره",
    },
}
_HTX_FE_OTHER = {"enemy": "friend", "friend": "enemy"}

# Built-in reply pools. A fresh account starts with these (seeded into the
# account's own editable list the first time it's touched — see
# _htx_fe_texts below), so «تنظیم دشمن/دوست» works out of the box without
# the owner having to type each line in first with «.افزودن …». Once
# seeded they're just normal saved texts: «.حذف فحش شماره N» removes one,
# «.پاکسازی لیست فحش» empties the whole thing, «.افزودن فحش متن» appends
# more — same as if the owner had typed these in themselves.
HTX_FE_DEFAULT_TEXTS = {
    "enemy": [
        "عره برقی تو کس ننت😂",
        "بالا باش ننه کیر دزد",
        "ننت رومه بیا ببرش",
        "کص آبجیت😂",
        "کس مغز",
        "ننتو میکنم😂",
        "کیر سگ تو کص ننت",
        "کس دست ریدی با تایپ کردنت چچچ",
        "و اما مادر جندت",
        "برج میلاد تو کونت",
        "ننت تو جنده خونس برو جمش کن",
        "ساک بزن برام مثل مادرت",
        "حروم زاده",
        "دهن ننت بوی آبکیر گرفته😂",
        "کیر تو خواهر و مادرت",
        "دسته بیل تو کص مادرت",
        "گاییدمت",
        "دسته بیل تو کص مادرت",
        "شاش تو کص ننت",
        "ماشین با سرعت ۲۲۰ تا تو کس خارت",
    ],
    "friend": [
        "دوست دارم💘",
        "من خیلی خوش شانسم که تو در زندگی منی",
        "نبض زندگیم با صدای نفس های تو میزند",
        "زیباترین فرشته قلبم",
        "عاشقتم عزیزم❤️",
        "دُچارت شده‌ اَم بیا و چاره‌ ام باش",
        "وقتی تو هستی درد هایم یادم میرود",
        "با ارزش ترین فرد زندگیمی",
        "بودنت برام آرامشه💖",
        "گرمای دستات آرامش منه",
        "دورت بگردم",
        "وقتی تو هستی غرق در آرامشم",
        "صندلیت را کنار صندلیم بگذار",
        "دوست خوب من",
        "تو برام خیلی مقدسی",
        "کنار تو بودن بهترین حس دنیاست💕",
        "تو هستی قرص آرام بخش من",
        "تو همیشه پشتمی",
        "حس بودنت قشنگ ترین حس دنیــــــاست💝",
        "تو دنیای منی",
        "از ته دل دوستت دارم",
        "تا نَفَس دارَم قَلبـــ❤️ـــم اِقامتگاهِ توست…",
    ],
}

# Parsed lists are cached in memory: the incoming handler runs for every
# single message the account receives, so it must not hit SQLite each time.
_HTX_FE_CACHE = {}
_HTX_FE_LAST_PICK = {}

_HX_REPLY = r"(?:\s*\+?\s*ری\u200c?پل(?:ی|ای)?)?"
_HX_NUM = r"[0-9۰-۹٠-٩]+"
_HTX_FE_CMDS = {
    "enemy": {
        "set":    rf"تنظیم\s+دشمن{_HX_REPLY}",
        "del":    rf"حذف\s+دشمن{_HX_REPLY}(?:\s+(?P<n>{_HX_NUM}))?",
        "list":   r"لیست\s+دشمن(?:ان)?",
        "clear":  r"پاکسازی\s+لیست\s+دشمن(?:ان)?",
        "tadd":   r"افزودن\s+فحش(?P<arg>(?:\s+.*)?)",
        "tdel":   rf"حذف\s+فحش(?:\s+(?P<n>{_HX_NUM}))?",
        "tlist":  r"لیست\s+(?:فحش|جواب(?:[\u200c ]?ها[ی]?)?\s+دشمن(?:ان)?)",
        "tclear": r"پاکسازی\s+لیست\s+فحش",
    },
    "friend": {
        "set":    rf"تنظیم\s+دوست{_HX_REPLY}",
        "del":    rf"حذف\s+دوست{_HX_REPLY}(?:\s+(?P<n>{_HX_NUM}))?",
        "list":   r"لیست\s+دوست(?:ان)?",
        "clear":  r"پاکسازی\s+لیست\s+دوست(?:ان)?",
        "tadd":   r"افزودن\s+جواب\s+دوست(?P<arg>(?:\s+.*)?)",
        "tdel":   rf"حذف\s+جواب\s+دوست(?:\s+(?P<n>{_HX_NUM}))?",
        "tlist":  r"لیست\s+جواب(?:[\u200c ]?ها[ی]?)?\s+دوست(?:ان)?",
        "tclear": r"پاکسازی\s+جواب\s+دوست",
    },
}
_HTX_FE_CMDS = {
    kind: {act: re.compile(pat, re.S) for act, pat in cmds.items()}
    for kind, cmds in _HTX_FE_CMDS.items()
}


def _htx_fe_load(uid, setting_key, want):
    """Cached JSON list/dict stored under `setting_key` (returned as-is:
    treat it as read-only, mutate a copy and pass it to _htx_fe_save)."""
    ck = (int(uid), setting_key)
    if ck not in _HTX_FE_CACHE:
        try:
            raw = json.loads(self_get(uid, setting_key, "{}" if want is dict else "[]"))
        except Exception:
            raw = None
        _HTX_FE_CACHE[ck] = raw if isinstance(raw, want) else want()
    return _HTX_FE_CACHE[ck]


def _htx_fe_save(uid, setting_key, value):
    self_set(uid, setting_key, json.dumps(value, ensure_ascii=False))
    _HTX_FE_CACHE[(int(uid), setting_key)] = value


def _htx_fe_users(uid, kind):
    return dict(_htx_fe_load(uid, _HTX_FE_KEYS[kind][0], dict))


def _htx_fe_texts(uid, kind):
    """The account's own فحش/جواب texts. Seeded once, the very first time
    this list is touched (no row for it in the settings table yet), from
    HTX_FE_DEFAULT_TEXTS — after that it's a completely normal saved list:
    «.پاکسازی» empties it for real and it stays empty until texts are
    added again, exactly like before defaults existed."""
    texts_key = _HTX_FE_KEYS[kind][1]
    ck = (int(uid), texts_key)
    if ck not in _HTX_FE_CACHE and get_setting(uid, texts_key, None) is None:
        _htx_fe_save(uid, texts_key, list(HTX_FE_DEFAULT_TEXTS.get(kind, [])))
    return list(_htx_fe_load(uid, texts_key, list))


def _htx_fe_screen(uid, action):
    """(caption, buttons) for the دوست و دشمن menu, the دشمن / دوست command
    screens and the «ساخت ویدیو گرد» screen."""
    def back_btn(target):
        return btn("بازگشت", _self_cb(uid, target), "danger", icon=PREMIUM_EMOJI["self_back"][0])

    if action == "fe_menu":
        # Just the plain «› 𝑯𝑻𝑿» tag, no quote block and no description.
        text = HTX_TAG
        return text, [
            [btn("❤️ دوست", _self_cb(uid, "fe_friend"), "success"),
             btn("💀 دشمن", _self_cb(uid, "fe_enemy"), "danger")],
            [back_btn(f"pg:{PANEL_FE_PAGE}")],
        ]

    if action == "fe_enemy":
        cmds = (
            ".تنظیم دشمن", ".حذف دشمن", ".لیست دشمن", ".لیست دشمنان",
            ".پاکسازی لیست دشمن", ".افزودن فحش متن", ".حذف فحش شماره",
            ".لیست فحش", ".لیست جواب‌های دشمن", ".پاکسازی لیست فحش",
        )
        title = "دشمن"
    elif action == "fe_friend":
        cmds = (
            ".تنظیم دوست", ".حذف دوست", ".لیست دوست", ".لیست دوستان",
            ".پاکسازی لیست دوست", ".افزودن جواب دوست متن", ".حذف جواب دوست شماره",
            ".لیست جواب دوست", ".لیست جواب‌های دوست", ".پاکسازی جواب دوست",
        )
        title = "دوست"
    else:  # "vn_open" — ساخت ویدیو گرد
        text = _htx_stack(
            f"{HTX_TAG} • ساخت ویدیو گرد",
            "دستورات",
            "<code>.ویدیو مسیج</code>",
            "روی یک ویدیو ریپلای کن؛ خروجی به صورت ویدیو گرد در همان چت ارسال می‌شود.",
        )
        return text, [[back_btn(f"pg:{PANEL_FE_PAGE}")]]

    text = _htx_stack(
        f"{HTX_TAG} • {title}",
        "دستورات",
        *[f"<code>{c}</code>" for c in cmds],
    )
    return text, [[back_btn("fe_menu")]]


async def _htx_fe_target(event, uid):
    """(user_id, display) of the user a friend/enemy command is aimed at:
    the sender of the replied message, or — in a private chat, with no
    reply — the person on the other side of that chat."""
    if event.is_reply:
        replied = await event.get_reply_message()
        if not replied or not replied.sender_id:
            return None, None
        sid = int(replied.sender_id)
        sender = None
        with contextlib.suppress(Exception):
            sender = await replied.get_sender()
        return sid, _format_snooper_display(sender, sid)
    if event.is_private and event.chat_id and int(event.chat_id) != int(uid):
        cid = int(event.chat_id)
        sender = None
        with contextlib.suppress(Exception):
            sender = await event.get_chat()
        return cid, _format_snooper_display(sender, cid)
    return None, None


def _htx_fe_short(text, limit=60):
    one_line = re.sub(r"\s+", " ", text).strip()
    return one_line if len(one_line) <= limit else one_line[:limit - 1] + "…"


async def _htx_fe_run(event, uid, kind, action, m, base):
    w = _HTX_FE_WORDS[kind]
    one, many, tword, texts_word = w["one"], w["many"], w["text"], w["texts"]
    users_key, texts_key = _HTX_FE_KEYS[kind]
    reply = lambda *lines, title=one: _htx_edit(event, _htx_reply(title, *lines))

    # ---- .تنظیم دشمن / .تنظیم دوست ------------------------------------
    if action == "set":
        target, display = await _htx_fe_target(event, uid)
        if not target:
            await reply(f"❌ روی پیام کاربر ریپلای کن و «.تنظیم {one}» را بفرست.")
            return
        if target == int(uid):
            await reply("❌ نمی‌توانی خودت را ثبت کنی.")
            return
        users = _htx_fe_users(uid, kind)
        users[str(target)] = display
        _htx_fe_save(uid, users_key, users)
        # One user can only be on one side.
        other = _HTX_FE_OTHER[kind]
        other_users = _htx_fe_users(uid, other)
        moved = other_users.pop(str(target), None) is not None
        if moved:
            _htx_fe_save(uid, _HTX_FE_KEYS[other][0], other_users)
        lines = [f"✅ {html.escape(display)} به لیست {many} اضافه شد."]
        if moved:
            lines.append(f"از لیست {_HTX_FE_WORDS[other]['many']} خارج شد.")
        if not _htx_fe_texts(uid, kind):
            lines.append(f"⚠️ هنوز {tword}ی ثبت نکردی: <code>{w['add_cmd']}</code>")
        print(f"[SELF {uid}] {kind} set: {target} (total {len(users)})")
        await reply(*lines)
        return

    # ---- .حذف دشمن / .حذف دوست ----------------------------------------
    if action == "del":
        users = _htx_fe_users(uid, kind)
        n = m.group("n")
        if n:
            idx = int(_fa_digits(n)) - 1
            keys = list(users)
            if not 0 <= idx < len(keys):
                await reply("❌ شماره‌ای که نوشتی در لیست نیست.")
                return
            key = keys[idx]
        else:
            target, _display = await _htx_fe_target(event, uid)
            if not target:
                await reply(f"❌ روی پیام کاربر ریپلای کن و «.حذف {one}» را بفرست.")
                return
            key = str(target)
        if key not in users:
            await reply(f"❌ این کاربر در لیست {many} نیست.")
            return
        display = users.pop(key)
        _htx_fe_save(uid, users_key, users)
        await reply(f"✅ {html.escape(display)} از لیست {many} حذف شد.")
        return

    # ---- .لیست دشمن / .لیست دشمنان ------------------------------------
    if action == "list":
        users = _htx_fe_users(uid, kind)
        if not users:
            await reply(f"لیست {many} خالی است.", title=f"لیست {many}")
            return
        lines, used = [], 0
        for i, display in enumerate(users.values(), 1):
            line = f"{i}. {html.escape(display)}"
            if used + len(line) > HTX_FE_LIST_CHARS:
                lines.append(f"… و {len(users) - i + 1} مورد دیگر")
                break
            lines.append(line)
            used += len(line) + 1
        await reply(f"تعداد {many} : {len(users)}", "\n".join(lines), title=f"لیست {many}")
        return

    # ---- .پاکسازی لیست دشمن / .پاکسازی لیست دوست ------------------------
    if action == "clear":
        _htx_fe_save(uid, users_key, {})
        await reply(f"✅ لیست {many} پاکسازی شد.")
        return

    # ---- .افزودن فحش متن / .افزودن جواب دوست متن -------------------------
    if action == "tadd":
        body = base[m.start("arg"):m.end("arg")].strip()
        if not body and event.is_reply:
            replied = await event.get_reply_message()
            body = ((replied.raw_text if replied else "") or "").strip()
        if not body:
            await reply(f"❌ فرمت درست: <code>{w['add_cmd']}</code>")
            return
        if len(body) > HTX_FE_MAX_TEXT_LEN:
            await reply(f"❌ متن نباید بیشتر از {HTX_FE_MAX_TEXT_LEN} کاراکتر باشد.")
            return
        texts = _htx_fe_texts(uid, kind)
        if body in texts:
            await reply("❌ این متن قبلاً ثبت شده.")
            return
        if len(texts) >= HTX_FE_MAX_TEXTS:
            await reply(f"❌ حداکثر {HTX_FE_MAX_TEXTS} متن قابل ثبت است.")
            return
        texts.append(body)
        _htx_fe_save(uid, texts_key, texts)
        # The text itself is deliberately NOT echoed back: the command
        # message that contained it is replaced by this confirmation.
        await reply(f"✅ ثبت شد • شماره {len(texts)}", f"تعداد {texts_word} : {len(texts)}")
        return

    # ---- .حذف فحش شماره / .حذف جواب دوست شماره ---------------------------
    if action == "tdel":
        n = m.group("n")
        if not n:
            await reply(f"❌ فرمت درست: <code>{w['del_cmd']}</code>")
            return
        texts = _htx_fe_texts(uid, kind)
        idx = int(_fa_digits(n)) - 1
        if not 0 <= idx < len(texts):
            await reply("❌ شماره‌ای که نوشتی در لیست نیست.")
            return
        texts.pop(idx)
        _htx_fe_save(uid, texts_key, texts)
        await reply(f"✅ شماره {idx + 1} حذف شد.", f"تعداد {texts_word} : {len(texts)}")
        return

    # ---- .لیست فحش / .لیست جواب دوست ------------------------------------
    if action == "tlist":
        texts = _htx_fe_texts(uid, kind)
        if not texts:
            await reply(f"لیست {texts_word} خالی است.", title=f"لیست {texts_word}")
            return
        lines, used = [], 0
        for i, item in enumerate(texts, 1):
            line = f"{i}. {html.escape(_htx_fe_short(item))}"
            if used + len(line) > HTX_FE_LIST_CHARS:
                lines.append(f"… و {len(texts) - i + 1} مورد دیگر")
                break
            lines.append(line)
            used += len(line) + 1
        await reply(f"تعداد {texts_word} : {len(texts)}", "\n".join(lines), title=f"لیست {texts_word}")
        return

    # ---- .پاکسازی لیست فحش / .پاکسازی جواب دوست --------------------------
    if action == "tclear":
        _htx_fe_save(uid, texts_key, [])
        await reply(f"✅ لیست {texts_word} پاکسازی شد.")
        return


async def _handle_htx_fe_command(event, uid, text):
    """All دوست / دشمن dotted commands. Returns True when handled."""
    norm = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]", "", text or "").strip()
    if not norm.startswith("."):
        return False
    base = norm[1:].strip()
    # Same-length normalisation (ي→ی, ك→ک): match positions map 1:1 onto `base`.
    key = base.replace("ي", "ی").replace("ك", "ک")
    if "دوست" not in key and "دشمن" not in key and "فحش" not in key:
        return False
    for kind, cmds in _HTX_FE_CMDS.items():
        for action, rx in cmds.items():
            m = rx.fullmatch(key)
            if m:
                try:
                    await _htx_fe_run(event, uid, kind, action, m, base)
                except Exception as exc:
                    print(f"[SELF {uid}] {kind} command {action} failed: {type(exc).__name__}: {exc}")
                    await _htx_edit(event, _htx_reply(
                        _HTX_FE_WORDS[kind]["one"],
                        f"❌ انجام نشد: <code>{html.escape(str(exc))}</code>",
                    ))
                return True
    return False


async def _htx_fe_incoming(event, uid):
    """Instant reply to every message from a registered دشمن / دوست, with a
    random saved text. Returns True when a reply was sent."""
    sender_id = int(event.sender_id) if event.sender_id else 0
    if not sender_id or sender_id == int(uid):
        return False
    if event.is_channel and not event.is_group:      # broadcast channel post
        return False
    if getattr(event.message, "action", None):       # join/leave/pin… service message
        return False

    key = str(sender_id)
    for kind in ("enemy", "friend"):
        users_key, texts_key = _HTX_FE_KEYS[kind]
        if key not in _htx_fe_load(uid, users_key, dict):
            continue
        texts = _htx_fe_texts(uid, kind)
        if not texts:
            return False
        # Random, but never the same text twice in a row for the same user.
        pick_key = (int(uid), kind, sender_id)
        last = _HTX_FE_LAST_PICK.get(pick_key)
        choices = [i for i in range(len(texts)) if i != last] or [0]
        idx = random.choice(choices)
        _HTX_FE_LAST_PICK[pick_key] = idx
        try:
            await event.reply(texts[idx], parse_mode=None, link_preview=False)
        except FloodWaitError as exc:
            print(f"[SELF {uid}] {kind} auto-reply flood wait {getattr(exc, 'seconds', '?')}s")
        except Exception as exc:
            print(f"[SELF {uid}] {kind} auto-reply failed: {type(exc).__name__}: {exc}")
        return True
    return False


# ---------------------------------------------------------------------
# HTX panel photo card
# ---------------------------------------------------------------------
# Measured from the ORIGINAL 1672x941 frame art (inner edge of the metal
# ring): centre (836.5, 448.3), radius 250.3 px. The frame shipped with this
# panel is now the resized 960x540 htx_frame asset (outer white border baked
# in), so every one of these numbers is scaled down by that same factor
# (960/1672 ≈ 0.5742) -- this is what was actually out of sync and made the
# photo land off to the side instead of inside the ring: the code was still
# placing/cropping using the OLD 1672-space coordinates on a frame that is
# now only 960px wide.
HTX_FRAME_SCALE = 960 / 1672   # update together with the frame asset's width
HTX_CIRCLE_CENTER = (836.5 * HTX_FRAME_SCALE, 448.3 * HTX_FRAME_SCALE)
HTX_CIRCLE_RADIUS = 250.3 * HTX_FRAME_SCALE
# The photo is drawn this many px LARGER than the ring's opening and the ring
# is then drawn back over it, so the photo tucks under the metal edge with no
# gap and no white/black seam between photo and frame.
HTX_PHOTO_BLEED = 3.5 * HTX_FRAME_SCALE
# Soft inner shadow at the photo's rim so it feels set into the ring.
HTX_PHOTO_VIGNETTE = 0.10      # fraction of the radius the shadow covers
HTX_PHOTO_VIGNETTE_MAX = 0.55  # darkest point (0..1)

# The white ring is now baked directly into the htx_frame asset itself
# (drawn once, flush against the circle opening, when the frame image was
# produced) instead of being recalculated on every panel build. The
# "restore original frame pixels over the bleed" step in _htx_static_layers
# (the ring_zone / restore mask) is what pulls that baked-in ring back over
# the pasted photo -- see there for the actual band width used.

# uid -> (profile_photo_id, composited_png_bytes). Avoids re-downloading /
# re-compositing / re-uploading the card on every "پنل" open; only rebuilt
# when the SELF account's profile photo actually changes.
_SELF_PANEL_PHOTO_CACHE = {}


def _find_htx_frame_path():
    """Locate the htx_frame asset next to bot.py, tolerant of case
    differences (e.g. HTX_Frame.PNG) and of the .png/.jpg extension, so a
    renamed/re-uploaded asset doesn't silently break the panel. .png is
    preferred when both exist (no recompression artifacts to composite
    every profile photo onto)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ("png", "jpg", "jpeg"):
        exact = os.path.join(base_dir, f"htx_frame.{ext}")
        if os.path.isfile(exact):
            return exact
    try:
        by_ext = {}
        for name in os.listdir(base_dir):
            stem, _, ext = name.lower().rpartition(".")
            if stem == "htx_frame" and ext in ("png", "jpg", "jpeg"):
                by_ext[ext] = os.path.join(base_dir, name)
        for ext in ("png", "jpg", "jpeg"):
            if ext in by_ext:
                return by_ext[ext]
    except Exception:
        pass
    return os.path.join(base_dir, "htx_frame.png")  # let open() raise a clear error


# Cache of the parts of the panel composite that are identical on every
# call (decoded frame, crop box, anti-aliased disc mask, ring-restore
# mask). These used to be rebuilt from scratch -- including three
# expensive 4x-supersampled ellipse renders -- on every single "پنل"
# open; that redundant work was the main reason building the card (and,
# since it ran synchronously on the event loop, the whole bot) felt heavy.
# Built once, lazily, on first use.
_HTX_STATIC_LAYERS = {}


def _htx_static_layers():
    if _HTX_STATIC_LAYERS:
        return _HTX_STATIC_LAYERS

    import math
    from PIL import Image, ImageDraw, ImageChops

    frame_path = _find_htx_frame_path()
    frame = Image.open(frame_path).convert("RGB")

    cx, cy = HTX_CIRCLE_CENTER
    r_open = HTX_CIRCLE_RADIUS
    r_photo = r_open + HTX_PHOTO_BLEED
    size = int(math.ceil(r_photo * 2)) + 4
    left = int(math.floor(cx - r_photo)) - 2
    top = int(math.floor(cy - r_photo)) - 2
    box = (left, top, left + size, top + size)
    lcx, lcy = cx - left, cy - top            # centre inside the work box

    def disc_mask(radius):
        """Anti-aliased filled circle at the exact (sub-pixel) centre."""
        ss = 4
        big = Image.new("L", (size * ss, size * ss), 0)
        ImageDraw.Draw(big).ellipse(
            ((lcx - radius) * ss, (lcy - radius) * ss,
             (lcx + radius) * ss, (lcy + radius) * ss), fill=255)
        return big.resize((size, size), Image.LANCZOS)

    orig = frame.crop(box)
    photo_mask = disc_mask(r_photo)

    # ring's own metal back over the bleed (photo tucks under it) -- the +2/-6
    # were tuned in the old 1672-wide frame's pixel space, so scale them down
    # with everything else instead of leaving them as fixed absolute pixels
    ring_zone = ImageChops.subtract(
        disc_mask(r_photo + 2 * HTX_FRAME_SCALE),
        disc_mask(r_open - 6 * HTX_FRAME_SCALE),
    )
    lum = orig.convert("L").point(
        lambda v: 0 if v <= 45 else 255 if v >= 95 else int((v - 45) * 255 / 50)
    )
    restore = ImageChops.multiply(lum, ring_zone)

    dia = int(round(r_photo * 2))
    grad = Image.radial_gradient("L").resize((dia, dia), Image.BILINEAR)  # 0 centre .. 255 at radius

    _HTX_STATIC_LAYERS.update(dict(
        frame=frame, box=box, size=size, lcx=lcx, lcy=lcy, dia=dia,
        orig=orig, photo_mask=photo_mask, restore=restore, grad=grad,
    ))
    return _HTX_STATIC_LAYERS


def _compose_htx_panel_image(profile_photo_bytes):
    """Composite a profile photo into the HTX frame's circular opening.

    The photo FILLS the circle (centre-cropped to a square — no white
    padding), is centred exactly on the ring, and is drawn a few pixels
    bigger than the opening; the frame's metal edge is then blended back on
    top so the photo appears to slide under the ring. A soft inner shadow
    at the rim adds depth. If profile_photo_bytes is None the opening is
    filled dark instead of white.

    Only the part that actually depends on the caller's photo runs here;
    the frame/masks/geometry come from _htx_static_layers() and are built
    only once per process (see there). Runs synchronously -- call it via
    asyncio.to_thread so it never blocks the event loop for other users.
    """
    from io import BytesIO
    from PIL import Image

    static = _htx_static_layers()
    frame = static["frame"].copy()   # never mutate the shared cached frame
    box = static["box"]
    size = static["size"]
    lcx, lcy = static["lcx"], static["lcy"]
    dia = static["dia"]
    orig = static["orig"]
    photo_mask = static["photo_mask"]
    restore = static["restore"]
    grad = static["grad"]

    # ---- photo layer: centre-crop to a square, scale to cover the disc
    if profile_photo_bytes:
        photo = Image.open(BytesIO(profile_photo_bytes)).convert("RGB")
        side = min(photo.width, photo.height)
        photo = photo.crop((
            (photo.width - side) // 2, (photo.height - side) // 2,
            (photo.width + side) // 2, (photo.height + side) // 2,
        )).resize((dia, dia), Image.LANCZOS)
    else:
        photo = Image.new("RGB", (dia, dia), (12, 14, 22))
    layer = Image.new("RGB", (size, size), (0, 0, 0))
    layer.paste(photo, (int(round(lcx - dia / 2)), int(round(lcy - dia / 2))))

    # inner shadow: transparent in the middle, darkening towards the rim
    start = 1.0 - HTX_PHOTO_VIGNETTE
    peak = int(255 * HTX_PHOTO_VIGNETTE_MAX)

    def _shade(v):
        t = (v / 255.0 - start) / max(1e-6, 1.0 - start)
        t = 0.0 if t <= 0 else 1.0 if t >= 1 else t
        return int(peak * t * t)

    shade = Image.new("L", (size, size), 0)
    shade.paste(grad.point(_shade), (int(round(lcx - dia / 2)), int(round(lcy - dia / 2))))
    layer = Image.composite(Image.new("RGB", (size, size), (0, 0, 0)), layer, shade)

    # ---- put the photo into the frame (the white ring is baked into the
    # frame art itself; `restore` pulls it back over the photo's bleed so
    # there's no seam, same as it already does for the metal edge)
    region = Image.composite(layer, orig, photo_mask)
    region = Image.composite(orig, region, restore)

    frame.paste(region, box[:2])
    out = BytesIO()
    frame.save(out, format="PNG")
    out.seek(0)
    out.name = "htx_panel.png"  # some Telethon upload paths key off .name
    return out


# uid -> (checked_at_monotonic, me_object, photo_id). client.get_me() is a
# real API round trip (GetUsersRequest) every time it's called; profile
# photos don't change often enough to justify paying that on every single
# "پنل" open, so we only re-check every _SELF_ME_CACHE_TTL seconds.
_SELF_ME_CACHE = {}
_SELF_ME_CACHE_TTL = 300


_HTX_PANEL_PHOTO_SETTING_KEY = "htx_panel_photo_cache"

_HTX_FRAME_VERSION = None


def _htx_frame_version():
    """Cheap fingerprint (mtime + size) of whichever htx_frame.* file is
    currently on disk. Folded into every cache key below so replacing the
    frame asset (new geometry, new art, whatever) invalidates every
    previously-cached composed panel immediately -- otherwise a user whose
    Telegram profile photo hasn't changed since before the swap would keep
    getting served their OLD panel (old frame baked in) straight out of
    cache, forever. Computed once per process and reused."""
    global _HTX_FRAME_VERSION
    if _HTX_FRAME_VERSION is None:
        try:
            st = os.stat(_find_htx_frame_path())
            _HTX_FRAME_VERSION = f"{st.st_mtime_ns}:{st.st_size}"
        except Exception:
            _HTX_FRAME_VERSION = "0"
    return _HTX_FRAME_VERSION


def _htx_panel_photo_cache_load(uid):
    """Disk-backed counterpart of _SELF_PANEL_PHOTO_CACHE (this account's
    own settings row, so it's a local read -- no network). The in-memory
    cache is wiped on every process restart (e.g. a Railway redeploy); this
    one isn't, so the first "پنل" open after a restart still skips the
    profile-photo download + PIL composition instead of paying for both
    again. Returns (photo_id, png_bytes) or None -- None if there's no
    cache entry, or if it was built against a since-replaced frame asset."""
    raw = get_setting(uid, _HTX_PANEL_PHOTO_SETTING_KEY, None)
    if not raw:
        return None
    try:
        import base64
        data = json.loads(raw)
        photo_id, png_b64 = data.get("photo_id"), data.get("png")
        if photo_id is None or not png_b64:
            return None
        if data.get("frame_version") != _htx_frame_version():
            return None
        return photo_id, base64.b64decode(png_b64)
    except Exception:
        return None


def _htx_panel_photo_cache_save(uid, photo_id, composed_bytes):
    import base64
    with contextlib.suppress(Exception):
        self_set(uid, _HTX_PANEL_PHOTO_SETTING_KEY, json.dumps({
            "photo_id": photo_id,
            "frame_version": _htx_frame_version(),
            "png": base64.b64encode(composed_bytes).decode("ascii"),
        }))


async def _get_self_panel_photo_bytes(uid):
    """Build (or reuse from cache) the HTX panel card for this SELF account.
    Returns a BytesIO ready to hand straight to Telethon's inline photo
    builder (it carries a .name so upload_file never has to guess)."""
    from io import BytesIO

    client = self_clients.get(uid)
    if not client:
        return await asyncio.to_thread(_compose_htx_panel_image, None)

    now = time.monotonic()
    cached_me = _SELF_ME_CACHE.get(uid)
    if cached_me and now - cached_me[0] < _SELF_ME_CACHE_TTL:
        me, photo_id = cached_me[1], cached_me[2]
    else:
        me = None
        photo_id = None
        try:
            me = await client.get_me()
            photo_id = getattr(getattr(me, "photo", None), "photo_id", None)
        except Exception:
            pass
        _SELF_ME_CACHE[uid] = (now, me, photo_id)

    cached = _SELF_PANEL_PHOTO_CACHE.get(uid)
    if cached and photo_id is not None and cached[0] == photo_id and cached[2] == _htx_frame_version():
        buf = BytesIO(cached[1])
        buf.name = "htx_panel.png"
        return buf

    if photo_id is not None:
        persisted = _htx_panel_photo_cache_load(uid)
        if persisted and persisted[0] == photo_id:
            # warm the in-memory tier too -- _htx_panel_photo_cache_load already
            # checked frame_version, so it's safe to stamp the current one here
            _SELF_PANEL_PHOTO_CACHE[uid] = (persisted[0], persisted[1], _htx_frame_version())
            buf = BytesIO(persisted[1])
            buf.name = "htx_panel.png"
            return buf

    photo_bytes = None
    try:
        photo_bytes = await client.download_profile_photo(me or "me", file=bytes)
    except Exception:
        photo_bytes = None

    # Composition is synchronous PIL work -- always hand it to a thread so
    # a cold/rebuilt card for one user never stalls the event loop (and
    # therefore every other user's messages/buttons) while it renders.
    composed = await asyncio.to_thread(_compose_htx_panel_image, photo_bytes)
    composed_bytes = composed.getvalue()
    if photo_id is not None:
        _SELF_PANEL_PHOTO_CACHE[uid] = (photo_id, composed_bytes, _htx_frame_version())
        _htx_panel_photo_cache_save(uid, photo_id, composed_bytes)
    return composed


async def _report_panel_bug(uid, where, exc):
    """No server-log access on this deploy, so mirror the failure straight
    into the SELF account's own Saved Messages ("me") — visible instantly
    in Telegram, no hosting dashboard needed. Never allowed to raise."""
    import traceback
    try:
        client = self_clients.get(uid)
        if not client:
            return
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-3500:]
        await client.send_message(
            "me",
            f"⚠️ <b>HTX panel debug</b> — failed at: <code>{html.escape(where)}</code>\n\n"
            f"<code>{html.escape(tb)}</code>",
            parse_mode="html",
        )
    except Exception:
        pass


SELF_FEATURE_GUIDES = {
    "clock": ("""🕐 <b>ساعت روی نام پروفایل</b>

این قابلیت ساعت ایران را به انتهای نام پروفایل سلف اضافه می‌کند و به‌صورت خودکار آن را به‌روزرسانی می‌کند.

<b>فعال‌سازی:</b> از پنل سلف روی «🕐 ساعت» بزن یا دستور زیر را ارسال کن:
<code>.ساعت روشن</code>

<b>خاموش‌کردن:</b>
<code>.ساعت خاموش</code>

<b>تغییر ظاهر ساعت:</b>
<code>.فونت ساعت بولد</code>
<code>.فونت ساعت دایره</code>
<code>.فونت ساعت فارسی</code>

فونت‌های موجود شامل عادی، بولد، دوبل، سانس، سانس بولد، مونو، فول، دایره، منفی، بالانویس، زیرنویس، فارسی، عربی و هندی هستند. تغییر فونت فقط ظاهر ساعت را عوض می‌کند و منطق سلف را تغییر نمی‌دهد."""),

    "channel_save": ("""💾 <b>ذخیره چنل؛ انتقال پیام‌های کانال به Saved Messages</b>

این قابلیت برای برداشتن تعداد مشخصی از پیام‌های یک کانال و ذخیره‌کردن آن‌ها در <b>Saved Messages</b> اکانت SELF ساخته شده است. عملیات با خود اکانت SELF انجام می‌شود، نه با ربات.

<b>روش استفاده:</b>
① از پنل سلف روی «💾 ذخیره چنل» بزن.
② کانال موردنظر را از لیست انتخاب کن.
③ نوع محتوا را انتخاب کن:
• 🖼 تصویر
• 🎬 ویدیو
• 🎵 موسیقی
• 🎤 ویس
• 📝 متن
• 📦 همه
④ تعداد را با صفحه اعداد وارد کن.
⑤ روی «✅ تأیید و شروع» بزن.

در زمان اجرا، همان پیام پنل ویرایش می‌شود و نوار پیشرفت، تعداد بررسی‌شده، موفق و ناموفق را نشان می‌دهد. در پایان موارد موفق داخل <b>Saved Messages</b> قرار می‌گیرند.

<b>حداکثر تعداد:</b> ۱۰۰۰ مورد در هر عملیات.

⚠️ اگر کانالی در لیست نمی‌آید، باید آن کانال برای اکانت SELF قابل دسترسی باشد."""),

    "tabchi": ("""📢 <b>تبچی؛ بنر و ارسال خودکار</b>

تبچی برای ساخت «بنر» از یک پیام و ارسال آن به مقصدهای مشخص با فاصله زمانی تعیین‌شده است. هر بنر شماره مخصوص خودش را دارد؛ مثلاً <b>۱</b>.

<b>① ساخت بنر</b>
روی پیام موردنظر ریپلای کن:
<code>.تنظیم بنر فور</code>
یعنی پیام به شکل Forward ارسال می‌شود.

یا:
<code>.تنظیم بنر کپی</code>
یعنی محتوای پیام به‌صورت کپی/ارسال مجدد استفاده می‌شود؛ برای مدیا فایل محلی نیز نگهداری می‌شود.

بعد از ساخت، مثلاً پیام می‌گوید بنر <b>#۱</b> ساخته شده است. از همین شماره در دستورات بعدی استفاده کن.

<b>② اضافه‌کردن همین گپ به مقصد بنر</b>
داخل همان گروه بنویس:
<code>.تنظیم گپ هدف بنر ۱</code>
گروه فعلی به مقصدهای بنر ۱ اضافه می‌شود.

<b>③ حذف گپ از مقصد</b>
داخل همان گروه:
<code>.حذف گپ هدف بنر ۱</code>

<b>④ قرار دادن تمام گپ‌های قابل‌دسترسی به‌عنوان مقصد</b>
<code>.تنظیم هدف بنر ۱ تمام گپ ها</code>
این دستور گپ‌های گروهی قابل‌دسترسی سلف را بررسی و به مقصدهای بنر اضافه می‌کند.

<b>⑤ زمان‌بندی ارسال</b>
<code>.تنظیم عدد بنر ۱ ۳۰ دقیقه</code>
یعنی بنر ۱ با فاصله ۳۰ دقیقه‌ای ارسال شود. حداقل زمان ۱ دقیقه است.

<b>⑥ ارسال به پیوی‌های اخیر</b>
<code>.فور بنر در ۱۰ پیوی اخیر</code>
بنر شماره ۱ را نمی‌گوید؛ پس حتماً شماره را مشخص کن، مثال کامل:
<code>.فور بنر در ۱ ۱۰ پیوی اخیر</code>
یعنی بنر ۱ به ۱۰ پیوی اخیر ارسال شود.

<b>⑦ کنترل تبچی</b>
<code>.تبچی روشن</code>
<code>.تبچی خاموش</code>
با روشن‌شدن تبچی، بنرهای فعالِ دارای مقصد می‌توانند ارسال خودکار داشته باشند و ارسال فوری بنرهای تنظیم‌شده نیز انجام می‌شود.

<b>⑧ مشاهده وضعیت و لیست</b>
<code>.وضعیت تبچی</code>
<code>.لیست بنر هام</code>

<b>⑨ حذف بنر</b>
<code>.حذف بنر ۱</code>

<b>⑩ پاک‌کردن تمام بنرها</b>
<code>.پاکسازی لیست بنر ها</code>

💡 اگر چند بنر داری، همیشه شماره صحیح را جایگزین «۱» کن. مثلاً برای بنر ۳ بنویس <code>.حذف بنر ۳</code>."""),

    "comments": ("""💬 <b>کامنت اول کانال</b>

این قابلیت یک متن ثابت را برای پست‌های کانال در Discussion متصل‌شده به‌عنوان کامنت اول ارسال می‌کند. برای کارکرد صحیح، کانال باید Discussion متصل داشته باشد.

<b>مرحله ۱ — انتخاب کانال</b>
از پنل «💬 کامنت اول» وارد شو و کانال را از لیست انتخاب کن.

<b>مرحله ۲ — تنظیم متن</b>
بعد از انتخاب کانال، روی پیام متنی‌ای که می‌خواهی کامنت باشد ریپلای کن و بنویس:
<code>.تنظیم کامنت</code>

متن پیام ریپلای‌شده برای همان کانال ذخیره و قابلیت فعال می‌شود.

<b>تنظیم کانال با دستور:</b>
<code>.تنظیم کامنت اول @Channel</code>
یا آیدی کانال را بده.

<b>حذف تنظیم یک کانال:</b>
<code>.حذف کامنت اول @Channel</code>

<b>دیدن تنظیمات:</b>
<code>.لیست کامنت</code>

<b>پاک‌کردن تمام تنظیمات:</b>
<code>.پاکسازی لیست کامنت</code>

در پنل هر کانال امکان روشن/خاموش‌کردن و حذف تنظیمات نیز وجود دارد. اگر کانال Discussion نداشته باشد، کامنت اول قابل تنظیم نیست."""),

    "globalban": ("""🚫 <b>بن سراسری</b>

بن سراسری یک لیست داخلی از کاربران مسدودشده برای همان سلف ایجاد می‌کند و با آن می‌توانی یک کاربر را در سطح قابلیت‌های مربوط به سلف مسدود نگه داری.

<b>افزودن با یوزرنیم/آیدی:</b>
<code>.بن سراسری @username</code>

<b>افزودن با ریپلای:</b>
روی پیام کاربر ریپلای کن و فقط بنویس:
<code>.بن سراسری</code>

<b>حذف از لیست:</b>
<code>.حذف بن سراسری @username</code>
یا با ریپلای به کاربر هدف.

<b>مشاهده لیست:</b>
<code>.لیست بن سراسری</code>

اگر دستور افزودن در یک گروه اجرا شود و SELF ادمین باشد، منطق فعلی می‌تواند همان کاربر را در آن گروه نیز محدود کند.

⚠️ «.بن سراسری» با بن عادی گروه فرق دارد؛ لیست آن جداگانه ذخیره می‌شود."""),

    "premium_emoji": ("""💎 <b>ایموجی پریمیوم</b>

با این قابلیت می‌توانی یک ایموجی پریمیوم را برای یک ایموجی عادی «ثبت» کنی؛ از آن پس هر پیامی که همان ایموجی عادی را داشته باشد، به‌صورت خودکار ویرایش می‌شود و ایموجی عادی با ایموجی پریمیوم ثبت‌شده نمایش داده می‌شود.

⚠️ ثبت و حذف فقط داخل <b>Saved Messages</b> خودت انجام می‌شود؛ ولی خودِ جایگزینی خودکار در همه چت‌ها فعال است.

<b>ثبت ایموجی</b>
با این دستور می‌توانید ایموجی پریمیوم مورد نظر را در Saved Messages خود تنظیم کنید تا هر زمان از ایموجی معمولی منبع استفاده کردید، پیام به‌صورت خودکار ویرایش شود.
<code>.ثبت ایموجی [ایموجی‌پریمیوم] [ایموجی‌عادی]</code>

اگر پیامی که ارسال می‌کنی نتواند ایموجی پریمیوم را نگه دارد، می‌توانی روی پیامی که همان ایموجی پریمیوم را دارد ریپلای کنی و فقط بنویسی:
<code>.ثبت ایموجی [ایموجی‌عادی]</code>

<b>حذف ایموجی</b>
با ریپلای یا فرستادن این دستور همراه با خود ایموجی پریمیوم در Saved Messages، ثبت آن حذف می‌شود.
<code>.حذف ایموجی [ایموجی‌پریمیوم]</code>
یا با خود ایموجی عادی ثبت‌شده:
<code>.حذف ایموجی [ایموجی‌عادی]</code>

<b>📋 لیست پرمیوم</b>
برای دیدن تمام ایموجی‌های ثبت‌شده:
<code>.لیست پرمیوم</code>

در لیست، ایموجی عادی و ایموجی پریمیومِ متصل به آن نمایش داده می‌شود. از همان بخش می‌توانی با دکمه «پاکسازی لیست پرمیوم» تمام ثبت‌ها را یکجا حذف کنی.

مثال:
<code>.ثبت ایموجی 💎 💵</code>
یعنی از این پس هر جا 💵 در پیام‌های خروجی باشد، با همان ایموجی پریمیوم جایگزین می‌شود."""),

}



def self_font_preview(uid, kind):
    if kind == "clock":
        return (
            f"🕐 پیش‌نمایش ساعت\n\n<b>{self_clock(uid)}</b>\n"
            f"فونت فعلی: <b>{_font_label('clock', self_get(uid,'clock_font','normal'))}</b>"
        )
    return (
        f"🔤 پیش‌نمایش فونت انگلیسی\n\n<b>{self_transform_english('Hello Telegram', uid)}</b>\n"
        f"فونت فعلی: <b>{_font_label('english', self_get(uid,'english_font','normal'))}</b>"
    )


async def _get_inline_bot_entity(client):
    """Resolve the bot entity once per logged-in self client."""
    cache_key = id(client)
    cached = _inline_bot_cache.get(cache_key)
    if cached is not None:
        return cached

    me = await bot.get_me()
    if not me:
        raise RuntimeError("Bot entity could not be resolved")

    username = getattr(me, "username", None)
    entity = await client.get_input_entity(f"@{username}" if username else me.id)
    _inline_bot_cache[cache_key] = entity
    return entity


# uid -> (peer, message_id) of the last "پنل" inline card inserted by the
# self account. Lets the "close" button actually delete that real message
# (bots can't delete inline-result messages themselves; the self client can,
# since it's the one that inserted it).
_LAST_PANEL_MSG = {}

# «بستن»: first the buttons vanish at once (photo + caption stay), then after
# this short beat the whole card is deleted -- so the keyboard never hangs
# under the photo while the card is waiting to be removed.
HTX_PANEL_CLOSE_DELETE_DELAY = 0.5  # pause between "buttons gone" and "card deleted"
HTX_PANEL_CMD_DELETE_DELAY = 0.5    # «.پنل» command message is removed 0.5s after the card lands


async def _delete_closed_panel(uid, peer, message_id, delay=HTX_PANEL_CLOSE_DELETE_DELAY):
    """A few seconds after «بستن» is pressed, delete the پنل card outright
    (not just strip its buttons). Must go through the SELF client — it's
    the account that actually inserted the inline-result message, so it's
    the only one allowed to delete it; the bot itself can't."""
    if delay and delay > 0:
        await asyncio.sleep(delay)
    client = self_clients.get(int(uid))
    if not client:
        return False
    try:
        await client.delete_messages(peer, [message_id])
        return True
    except Exception:
        return False


async def _htx_strip_panel_buttons(event, uid):
    """Remove ONLY the inline buttons of the panel card, instantly. The photo
    and its caption are left exactly as they are. Returns True when the
    keyboard is gone."""
    try:
        await event.edit(buttons=None)
        return True
    except MessageNotModifiedError:
        return True
    except Exception:
        pass
    # Fallback: some Telethon/Telegram combos refuse a markup-only edit, so
    # re-send the caption with no buttons.
    try:
        await event.edit(premium_ui_text(self_panel_text(uid)), parse_mode="html", buttons=None)
        return True
    except MessageNotModifiedError:
        return True
    except Exception:
        return False


async def _htx_panel_placeholder_edit(event):
    """Fire-and-forget "در حال ساخت پنل..." edit, run as a background task
    so its own round trip never blocks the start of the real inline flow."""
    with contextlib.suppress(Exception):
        await event.edit(premium_ui_text("در حال ساخت پنل..."), parse_mode="html")


async def send_self_inline_result(event, query: str):
    """Insert the bot's inline result using the logged-in user account.

    Unlike bot.send_message(), this does not require the bot to be a member
    of the target chat.
    """
    if not event.peer_id:
        raise RuntimeError("Target peer is unavailable")

    bot_entity = await _get_inline_bot_entity(event.client)
    results = await event.client(
        GetInlineBotResultsRequest(
            bot=bot_entity,
            peer=event.peer_id,
            geo_point=None,
            query=query,
            offset="",
        )
    )

    if not getattr(results, "results", None):
        raise RuntimeError(f"Inline bot returned no result for query: {query}")

    result = results.results[0]
    sent = await event.client(
        SendInlineBotResultRequest(
            peer=event.peer_id,
            query_id=results.query_id,
            id=result.id,
            hide_via=True,
            clear_draft=True,
        )
    )

    if query == "پنل":
        # The Updates object returned above already carries the new message
        # -- pulling the id out of it saves a whole extra network round
        # trip (get_messages) on every single "پنل" open compared to
        # fetching it separately afterwards.
        msg_id = None
        for upd in getattr(sent, "updates", None) or []:
            msg = getattr(upd, "message", None)
            if msg is not None and getattr(msg, "id", None):
                msg_id = msg.id
        if msg_id is not None:
            _LAST_PANEL_MSG[event.sender_id] = (event.peer_id, msg_id)
        else:
            # Fallback for the rare case the update shape doesn't match.
            with contextlib.suppress(Exception):
                msgs = await event.client.get_messages(event.peer_id, limit=1)
                if msgs:
                    _LAST_PANEL_MSG[event.sender_id] = (event.peer_id, msgs[0].id)



class _PremiumRelayPostSendError(RuntimeError):
    """The relay inline message is ALREADY in the chat but pressing its button
    failed. Callers must NEVER send the inline result again after this."""

    def __init__(self, message, source_deleted=False):
        super().__init__(message)
        self.source_deleted = bool(source_deleted)


def _premium_relay_callback_data(msg):
    """relay:<token> callback bytes of a message's inline button, or None."""
    if msg is None:
        return None
    markup = getattr(msg, "reply_markup", None)
    for row in getattr(markup, "rows", None) or []:
        for button in getattr(row, "buttons", None) or []:
            data = getattr(button, "data", None)
            if isinstance(data, str):
                data = data.encode()
            if isinstance(data, (bytes, bytearray)) and data.startswith(b"relay:"):
                return bytes(data)
    return None


async def _premium_relay_recent(event, limit):
    """Latest messages of the chat (chat_id first, peer_id as fallback)."""
    last_exc = None
    for target in (getattr(event, "chat_id", None), event.peer_id):
        if target is None:
            continue
        try:
            return await event.client.get_messages(target, limit=limit)
        except Exception as exc:
            last_exc = exc
    if last_exc is not None:
        raise last_exc
    return []


async def _premium_relay_applied(event, message_id, timeout=1.2):
    """True once the relay message is no longer the '.' placeholder (the bot
    edit landed), False if it is still '.', None if it can't be read."""
    deadline = time.time() + timeout
    while True:
        try:
            msg = await event.client.get_messages(event.peer_id, ids=message_id)
        except Exception:
            return None
        if msg is None:
            return None
        if (getattr(msg, "raw_text", None) or "").strip() != ".":
            return True
        if time.time() >= deadline:
            return False
        await asyncio.sleep(0.08)


async def _send_self_premium_inline_and_click(event, query: str):
    """Send the premium relay inline result ONCE, delete the source message
    right away, then press the relay button as SELF.

    Same method as the original build:
      GetInlineBotResultsRequest -> SendInlineBotResultRequest(hide_via=True)
      -> GetBotCallbackAnswerRequest(peer, msg_id, relay:<token>)

    The relay is addressed by IDs instead of searching the chat:
      * token      = the inline result id (the bot builds the article with
                     id=token, and the button payload is relay:<token>)
      * message id = UpdateMessageID matched by OUR random_id

    Nothing is ever sent twice: failures before the send raise a normal error
    (safe to retry); failures after the send raise _PremiumRelayPostSendError.
    Returns True when the source message was deleted.
    """
    if not event.peer_id:
        raise RuntimeError("Target peer is unavailable")

    uid = getattr(event, "sender_id", None)

    # Lower bound for the fallback lookup: never pick an older leftover relay.
    # Runs in parallel with the inline query instead of in front of it.
    async def _latest_id():
        try:
            latest = await _premium_relay_recent(event, 1)
            return int(latest[0].id) if latest else None
        except Exception as exc:
            print(f"[PREMIUM AUTO CLICK] pre-send message lookup failed: {exc!r}")
            return None

    bot_entity = await _get_inline_bot_entity(event.client)
    before_id, results = await asyncio.gather(
        _latest_id(),
        event.client(
            GetInlineBotResultsRequest(
                bot=bot_entity,
                peer=event.peer_id,
                geo_point=None,
                query=query,
                offset="",
            )
        ),
    )
    if not getattr(results, "results", None):
        raise RuntimeError(f"Inline bot returned no result for query: {query}")

    result = results.results[0]

    # The relay's ID: the inline result id IS the token in the button payload.
    callback_data = None
    relay_token = getattr(result, "id", None)
    if isinstance(relay_token, str) and relay_token:
        callback_data = b"relay:" + relay_token.encode()

    # The inline result is a NEW Telegram message, not an edit of the
    # original command message. Therefore the reply relationship must be
    # explicitly copied to SendInlineBotResultRequest.
    reply_to_msg_id = getattr(event.message, "reply_to_msg_id", None)
    if reply_to_msg_id is None:
        reply_header = getattr(event.message, "reply_to", None)
        reply_to_msg_id = getattr(reply_header, "reply_to_msg_id", None)

    reply_to_obj = None
    if reply_to_msg_id is not None:
        try:
            reply_to_obj = types.InputReplyToMessage(
                reply_to_msg_id=int(reply_to_msg_id)
            )
        except (TypeError, ValueError):
            reply_to_obj = None

    # Our own random_id: Telegram answers with UpdateMessageID(random_id -> id),
    # which is the exact id of the message this send created.
    random_id = random.randrange(-(2 ** 63), 2 ** 63)

    print(
        f"[PREMIUM AUTO CLICK] inserting inline result chat={getattr(event, 'chat_id', None)} "
        f"reply_to={reply_to_msg_id!r} before_id={before_id!r} token={relay_token!r}"
    )

    sent = await event.client(
        SendInlineBotResultRequest(
            peer=event.peer_id,
            query_id=results.query_id,
            id=result.id,
            hide_via=True,
            clear_draft=True,
            reply_to=reply_to_obj,
            random_id=random_id,
        )
    )

    # ------------------------------------------------------------------
    # From here on the relay message EXISTS in the chat. Never send again.
    # ------------------------------------------------------------------

    # Delete the user's plain source message in the BACKGROUND so the button
    # press below goes out immediately (no extra round trip in between).
    async def _delete_source():
        try:
            await event.delete()
            return True
        except Exception as exc:
            print(f"[PREMIUM AUTO CLICK] source delete failed: {type(exc).__name__}: {exc!r}")
            return False

    delete_task = asyncio.create_task(_delete_source())
    source_deleted = False

    # Exact message id of the relay (matched by our random_id).
    message_id = None
    message = None
    if isinstance(sent, types.UpdateShortSentMessage):
        message_id = int(sent.id)
    for update in getattr(sent, "updates", []) or []:
        if isinstance(update, types.UpdateMessageID) and int(update.random_id) == random_id:
            message_id = int(update.id)
            break
    for update in getattr(sent, "updates", []) or []:
        candidate = getattr(update, "message", None)
        cid = getattr(candidate, "id", None)
        if cid is None:
            continue
        if message_id is None or int(cid) == message_id:
            message = candidate
            message_id = int(cid)
            break

    if callback_data is None and message is not None:
        callback_data = _premium_relay_callback_data(message)

    # Fallback only when the ids could not be read from Telegram's answer:
    # look for the NEW message carrying the relay button.
    if message_id is None or callback_data is None:
        for _ in range(60):
            await asyncio.sleep(0.03)
            try:
                recent = await _premium_relay_recent(event, 15)
            except Exception as exc:
                print(f"[PREMIUM AUTO CLICK] fresh-message lookup error: {exc!r}")
                recent = []
            found = None
            for candidate in recent or []:
                cid = getattr(candidate, "id", None)
                if cid is None:
                    continue
                if message_id is not None:
                    if int(cid) != message_id:
                        continue
                elif before_id is not None and int(cid) <= before_id:
                    continue
                data = _premium_relay_callback_data(candidate)
                if data:
                    found = (int(cid), data)
                    break
            if found:
                message_id = found[0]
                if callback_data is None:
                    callback_data = found[1]
                break

    if message_id is None or callback_data is None:
        source_deleted = await delete_task
        raise _PremiumRelayPostSendError(
            "Fresh premium inline message could not be located",
            source_deleted=source_deleted,
        )

    print(
        f"[PREMIUM AUTO CLICK] uid={uid} "
        f"chat_id={getattr(event, 'chat_id', None)} "
        f"message_id={message_id} data={callback_data!r}"
    )

    # This is the real Telegram button press, performed by the logged-in
    # self user. It triggers the existing bot CallbackQuery -> relay: path.
    # Only the PRESS is retried (fresh RPC each time), the message is not.
    last_error = None
    for attempt, delay in enumerate((0.0, 0.1, 0.3, 0.7), 1):
        if delay:
            await asyncio.sleep(delay)
        try:
            await asyncio.wait_for(
                event.client(
                    GetBotCallbackAnswerRequest(
                        peer=event.peer_id,
                        msg_id=message_id,
                        data=callback_data,
                    )
                ),
                timeout=5,
            )
            last_error = None
        except asyncio.TimeoutError:
            # The press was sent; the bot may just be slow to answer. Verify below.
            print(f"[PREMIUM AUTO CLICK] press attempt={attempt} got no answer in 5s")
            last_error = None
        except Exception as exc:
            last_error = exc
            print(
                f"[PREMIUM AUTO CLICK] press attempt={attempt} raised "
                f"{type(exc).__name__}: {exc!r}"
            )
            # BOT_RESPONSE_TIMEOUT = the bot received the press but answered
            # late; the edit may still land, so verify below instead of failing.
            if type(exc).__name__ != "BotResponseTimeoutError":
                continue
            last_error = None

        applied = await _premium_relay_applied(event, message_id)
        if applied is False:
            print(f"[PREMIUM AUTO CLICK] press attempt={attempt} sent but not applied yet")
            last_error = RuntimeError("press sent but relay message was not edited")
            continue

        print(
            f"[PREMIUM AUTO CLICK] success uid={uid} "
            f"message_id={message_id} attempt={attempt} applied={applied!r}"
        )
        return await delete_task

    # Could not press it: remove the dead relay message so no stray "." is
    # left behind; the caller then delivers the plain text instead.
    with contextlib.suppress(Exception):
        await event.client.delete_messages(event.peer_id, [message_id])
    source_deleted = await delete_task
    raise _PremiumRelayPostSendError(
        f"press failed after retries: {type(last_error).__name__}: {last_error!r}",
        source_deleted=source_deleted,
    )


async def _send_self_premium_list(event):
    """Send the premium-emoji list through the bot inline mode.

    The command can itself be a reply; preserve that reply on the inserted
    inline message so the list behaves like the original SELF command.
    """
    if not event.peer_id:
        raise RuntimeError("Target peer is unavailable")

    bot_entity = await _get_inline_bot_entity(event.client)
    results = await event.client(
        GetInlineBotResultsRequest(
            bot=bot_entity,
            peer=event.peer_id,
            geo_point=None,
            query="لیست پرمیوم",
            offset="",
        )
    )
    if not getattr(results, "results", None):
        raise RuntimeError("Inline bot returned no result for: لیست پرمیوم")

    result = results.results[0]
    reply_to_msg_id = getattr(event.message, "reply_to_msg_id", None)
    if reply_to_msg_id is None:
        reply_header = getattr(event.message, "reply_to", None)
        reply_to_msg_id = getattr(reply_header, "reply_to_msg_id", None)
    reply_to_obj = None
    if reply_to_msg_id is not None:
        try:
            reply_to_obj = types.InputReplyToMessage(reply_to_msg_id=int(reply_to_msg_id))
        except (TypeError, ValueError):
            reply_to_obj = None

    sent = await event.client(
        SendInlineBotResultRequest(
            peer=event.peer_id,
            query_id=results.query_id,
            id=result.id,
            hide_via=True,
            clear_draft=True,
            reply_to=reply_to_obj,
        )
    )
    print(
        f"[PREMIUM LIST] uid={int(event.sender_id)} chat={getattr(event, 'chat_id', None)} "
        f"reply_to={reply_to_msg_id!r}"
    )
    return sent


def _event_inline_message_id(event):
    """Return the real inline-message identifier from a Telethon callback.

    Telethon exposes this value differently across versions/update types:
    sometimes directly on the event, and sometimes on the raw callback query.
    Do not rely only on ``via_inline`` because that flag is not consistently
    populated for callbacks coming from an inline result.
    """
    candidates = [
        getattr(event, "inline_message_id", None),
        getattr(getattr(event, "query", None), "msg_id", None),
        getattr(getattr(event, "original_update", None), "msg_id", None),
    ]
    for value in candidates:
        if value is not None:
            return value
    return None



def _serialize_inline_message_id(value):
    """Serialize Telethon's InputBotInlineMessageID for durable per-operation state."""
    if value is None:
        return None
    try:
        return {
            "dc_id": int(value.dc_id),
            "id": int(value.id),
            "access_hash": int(value.access_hash),
        }
    except Exception:
        return None


def _deserialize_inline_message_id(value):
    """Rebuild an InputBotInlineMessageID from saved state."""
    if not isinstance(value, dict):
        return None
    try:
        return types.InputBotInlineMessageID(
            dc_id=int(value["dc_id"]),
            id=int(value["id"]),
            access_hash=int(value["access_hash"]),
        )
    except Exception:
        return None


async def _edit_panel_message(*, text, buttons=None, inline_message_id=None,
                              chat_id=None, message_id=None, parse_mode="html"):
    """Edit either an inline message or a normal bot-owned message."""
    if inline_message_id is not None:
        target = (
            inline_message_id
            if isinstance(inline_message_id, types.InputBotInlineMessageID)
            else _deserialize_inline_message_id(inline_message_id)
        )
        if target is None:
            raise RuntimeError("invalid inline_message_id")
        return await bot.edit_message(
            target,
            text,
            parse_mode=parse_mode,
            buttons=buttons,
        )

    if chat_id is None or message_id is None:
        raise RuntimeError(
            f"panel message identity missing: chat_id={chat_id} message_id={message_id}"
        )

    return await bot.edit_message(
        int(chat_id),
        int(message_id),
        text,
        parse_mode=parse_mode,
        buttons=buttons,
    )


async def _transfer_sender_label(client, user_id: int) -> str:
    """@username when available, otherwise the numeric Telegram ID."""
    try:
        entity = await client.get_entity(int(user_id))
        username = getattr(entity, "username", None)
        if username:
            return f"@{username}"
    except Exception:
        pass
    return str(int(user_id))



def self_chat_lock_targets(uid):
    try:
        raw = json.loads(self_get(uid, "chat_lock_targets", "[]"))
        return {int(x) for x in raw}
    except Exception:
        return set()


def self_save_chat_lock_targets(uid, targets):
    self_set(uid, "chat_lock_targets", json.dumps(sorted(int(x) for x in targets)))


_LOCK_USERNAME_RE = re.compile(r"(?<!\w)@\w{4,}")


def _self_content_lock_hit(uid, message):
    """«قفل ها»: True when any of the per-type content locks (link, username,
    photo, reply, sticker, gif, forward) is on and this incoming private
    message matches it. «قفل پیوی» reuses chat_lock_global directly and is
    already checked by the caller, so it is not repeated here."""
    if self_get(uid, "lock_reply", "off") == "on" and getattr(message, "is_reply", False):
        return True
    if self_get(uid, "lock_forward", "off") == "on" and getattr(message, "forward", None):
        return True
    if self_get(uid, "lock_photo", "off") == "on" and getattr(message, "photo", None):
        return True
    if self_get(uid, "lock_sticker", "off") == "on" and getattr(message, "sticker", None):
        return True
    if self_get(uid, "lock_gif", "off") == "on" and getattr(message, "gif", None):
        return True
    if self_get(uid, "lock_link", "off") == "on":
        text = message.raw_text or ""
        entities = getattr(message, "entities", None) or []
        if _DL_HTTP_RE.search(text) or "t.me/" in text.lower() or any(
            isinstance(e, (types.MessageEntityUrl, types.MessageEntityTextUrl)) for e in entities
        ):
            return True
    if self_get(uid, "lock_username", "off") == "on":
        text = message.raw_text or ""
        entities = getattr(message, "entities", None) or []
        if _LOCK_USERNAME_RE.search(text) or any(
            isinstance(e, (types.MessageEntityMention, types.MessageEntityMentionName)) for e in entities
        ):
            return True
    return False














async def _tg_call_with_flood_retry(call_factory, *, label="telegram", max_retries=20):
    """Retry Telegram API calls after FloodWait instead of aborting a long operation."""
    for attempt in range(max_retries):
        try:
            return await call_factory()
        except FloodWaitError as exc:
            wait = max(1, int(getattr(exc, "seconds", 1)))
            print(f"[TELEGRAM] FloodWait during {label}: sleeping {wait}s (attempt {attempt + 1})")
            await asyncio.sleep(wait)
    raise RuntimeError(f"Telegram kept rate-limiting {label} after {max_retries} retries")


async def _cleanup_delete_private(client, entity):
    # revoke=True performs the two-sided deletion where Telegram permits it.
    await _tg_call_with_flood_retry(
        lambda: client(functions.messages.DeleteHistoryRequest(
            peer=entity, max_id=0, just_clear=False, revoke=True
        )),
        label="delete private history",
    )


async def _cleanup_leave_dialog_safe(client, entity, uid):
    try:
        if isinstance(entity, types.Channel):
            await _tg_call_with_flood_retry(
                lambda: client(functions.channels.LeaveChannelRequest(channel=entity)),
                label="leave channel/group",
            )
        elif isinstance(entity, types.Chat):
            me = await client.get_me()
            input_me = await client.get_input_entity(me)
            await _tg_call_with_flood_retry(
                lambda: client(functions.messages.DeleteChatUserRequest(
                    chat_id=entity.id, user_id=input_me
                )),
                label="leave basic group",
            )
        return True, None
    except Exception as exc:
        return False, str(exc)


async def _cleanup_contacts(client):
    result = await _tg_call_with_flood_retry(
        lambda: client(functions.contacts.GetContactsRequest(hash=0)),
        label="get contacts",
    )
    users = getattr(result, "users", None) or []
    input_users = [types.InputUser(u.id, u.access_hash) for u in users if getattr(u, "access_hash", None) is not None]
    if not input_users:
        return 0
    await _tg_call_with_flood_retry(
        lambda: client(functions.contacts.DeleteContactsRequest(id=input_users)),
        label="delete contacts",
    )
    return len(input_users)


async def _cleanup_dialog_snapshot(client, uid):
    dialogs = []
    async for dialog in client.iter_dialogs():
        entity = getattr(dialog, "entity", None)
        if not entity or getattr(entity, "id", None) == uid:
            continue
        dialogs.append(dialog)
    return dialogs


def _cleanup_categories(dialogs):
    chats = []
    bots = []
    groups = []
    channels = []
    for dialog in dialogs:
        entity = getattr(dialog, "entity", None)
        if getattr(dialog, "is_group", False):
            groups.append(dialog)
        elif getattr(dialog, "is_channel", False):
            channels.append(dialog)
        elif getattr(dialog, "is_user", False):
            if getattr(entity, "bot", False):
                bots.append(dialog)
            else:
                chats.append(dialog)
    return chats, bots, groups, channels


async def _cleanup_private_dialogs(client, dialogs, uid, label, block_bots=False, progress_cb=None):
    total = len(dialogs)
    if not total:
        return 0

    # Telegram rate-limits long cleanup jobs.  A small amount of concurrency
    # makes private-history cleanup substantially faster without hammering the API.
    semaphore = asyncio.Semaphore(3)
    lock = asyncio.Lock()
    done = 0

    async def one(dialog):
        nonlocal done
        entity = dialog.entity
        async with semaphore:
            try:
                # This cleanup action is explicitly initiated by the account owner.
                # Never archive from this path. Automatic archiving is handled by
                # MessageDeleted for incoming messages only.
                await _cleanup_delete_private(client, entity)
                if block_bots and getattr(entity, "bot", False):
                    await _tg_call_with_flood_retry(
                        lambda e=entity: client(functions.contacts.BlockRequest(id=e)),
                        label="block bot",
                    )
            except Exception as exc:
                print(f"[CLEANUP {uid}] private {getattr(entity,'id','?')}: {exc}")
            finally:
                async with lock:
                    done += 1
                    current = done
                # Updating the Telegram panel for every dialog was a major
                # source of slowness.  Refresh only every 5 items and at the end.
                if progress_cb and (current == total or current % 5 == 0):
                    await progress_cb(f"🧹 {label}… {current}/{total}")

    await asyncio.gather(*(one(dialog) for dialog in dialogs))
    return done


async def _cleanup_leave_dialogs(client, dialogs, uid, label, progress_cb=None):
    total = len(dialogs)
    if not total:
        return 0

    semaphore = asyncio.Semaphore(3)
    lock = asyncio.Lock()
    done = 0

    async def one(dialog):
        nonlocal done
        entity = dialog.entity
        async with semaphore:
            ok, err = await _cleanup_leave_dialog_safe(client, entity, uid)
            if not ok:
                print(f"[CLEANUP {uid}] leave {getattr(entity,'id','?')}: {err}")
            async with lock:
                done += 1
                current = done
            if progress_cb and (current == total or current % 5 == 0):
                await progress_cb(f"🚪 {label}… {current}/{total}")

    await asyncio.gather(*(one(dialog) for dialog in dialogs))
    return done


async def _cleanup_run(uid, target, panel_chat_id=None, panel_message_id=None, panel_inline_message_id=None):
    client = self_clients.get(uid)
    if not client:
        self_set(uid, "cleanup_progress", "❌ سلف فعال نیست")
        return

    last_panel_update = 0.0

    async def progress(text, force=False):
        nonlocal last_panel_update
        self_set(uid, "cleanup_progress", text)
        if panel_inline_message_id is not None or (panel_chat_id is not None and panel_message_id is not None):
            now = time.monotonic()
            # Never edit the same Telegram message dozens/hundreds of times per
            # second. State is still saved on every call; UI is throttled.
            if not force and (now - last_panel_update) < 0.75:
                return
            last_panel_update = now
            with contextlib.suppress(Exception):
                await _edit_panel_message(
                    # The status line must actually change between edits, or
                    # Telegram rejects the edit as "not modified" and the panel
                    # looks frozen with no feedback until the very end.
                    text=self_panel_text(uid, extra=f"🧹 <b>پاکسازی</b>\n{html.escape(text)}"),
                    buttons=self_panel_buttons(uid),
                    inline_message_id=panel_inline_message_id,
                    chat_id=panel_chat_id,
                    message_id=panel_message_id,
                    parse_mode="html",
                )

    try:
        self_set(uid, "cleanup_running", "on")
        await progress("⏳ در حال آماده‌سازی پاکسازی…")
        dialogs = await _cleanup_dialog_snapshot(client, uid)
        chats, bots, groups, channels = _cleanup_categories(dialogs)
        total = 0

        if target in {"chats", "all"}:
            total += await _cleanup_private_dialogs(client, chats, uid, "پاکسازی چت‌ها به‌صورت دوطرفه", progress_cb=progress)

        if target in {"bots", "all"}:
            total += await _cleanup_private_dialogs(client, bots, uid, "پاکسازی و بلاک ربات‌ها", block_bots=True, progress_cb=progress)

        if target in {"groups", "all"}:
            total += await _cleanup_leave_dialogs(client, groups, uid, "ترک گپ‌ها", progress_cb=progress)

        if target in {"channels", "all"}:
            total += await _cleanup_leave_dialogs(client, channels, uid, "ترک کانال‌ها", progress_cb=progress)

        contact_count = 0
        if target in {"contacts", "all"}:
            await progress("👥 در حال حذف مخاطبین…")
            try:
                contact_count = await _cleanup_contacts(client)
            except Exception as exc:
                print(f"[CLEANUP {uid}] contacts: {exc}")

        labels = {
            "chats": "چت‌ها", "bots": "ربات‌ها", "groups": "گپ‌ها",
            "channels": "کانال‌ها", "contacts": "مخاطبین", "all": "همه"
        }
        await progress(f"✅ {labels.get(target, 'پاکسازی')} انجام شد • {total} گفتگو • {contact_count} مخاطب", force=True)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[CLEANUP {uid}] fatal: {exc}")
        await progress(f"⚠️ پاکسازی با خطا متوقف شد: {exc}", force=True)
    finally:
        self_set(uid, "cleanup_running", "off")
        _cleanup_tasks.pop(uid, None)


async def _cleanup_account(uid, panel_chat_id=None, panel_message_id=None, panel_inline_message_id=None):
    # Backward-compatible entry point: "all" is the old full-cleanup behavior.
    await _cleanup_run(uid, "all", panel_chat_id, panel_message_id, panel_inline_message_id)



# ============================================================
# CHANNEL SAVE — CLEAN IMPLEMENTATION
# ============================================================

CHANNEL_SAVE_MAX_COUNT = 1000
CHANNEL_SAVE_PROGRESS_INTERVAL = 0.75


def _cs_session(uid):
    return _channel_save_sessions.get(int(uid))


def _cs_clear(uid):
    _channel_save_sessions.pop(int(uid), None)


def _cs_editor_from_event(event):
    # Keep the original callback event as the primary editor.  This is important
    # for inline-result messages: the callback event already knows exactly which
    # message Telegram delivered the button press from, so progress edits do not
    # accidentally switch to a different message/client identity.
    return {
        "event": event,
        "inline_message_id": _event_inline_message_id(event),
        "chat_id": getattr(event, "chat_id", None),
        "message_id": getattr(event, "message_id", None),
    }


async def _cs_edit(editor, text, buttons=None):
    """Edit the exact message that produced the confirm callback."""
    event = editor.get("event")
    last_exc = None

    # First use the original callback event.  It is the most reliable way to
    # edit the same inline message throughout the whole save lifecycle.
    if event is not None:
        try:
            return await event.edit(premium_ui_text(text), parse_mode="html", buttons=buttons)
        except Exception as exc:
            last_exc = exc

    # Fallback for normal bot-owned messages / environments where event.edit is
    # unavailable after the callback has returned.
    try:
        return await _edit_panel_message(
            text=text,
            buttons=buttons,
            inline_message_id=editor.get("inline_message_id"),
            chat_id=editor.get("chat_id"),
            message_id=editor.get("message_id"),
            parse_mode="html",
        )
    except Exception as exc:
        last_exc = exc
        raise last_exc


def _cs_progress_bar(done, total, width=16):
    if total <= 0:
        return "░" * width, 0
    ratio = max(0.0, min(1.0, float(done) / float(total)))
    filled = round(width * ratio)
    return "█" * filled + "░" * (width - filled), int(ratio * 100)


def _cs_media_match(message, kind):
    if kind == "photos":
        return bool(getattr(message, "photo", None))
    if kind == "videos":
        return bool(getattr(message, "video", None))
    if kind == "music":
        return bool(getattr(message, "audio", None)) and not bool(getattr(message, "voice", None))
    if kind == "voice":
        return bool(getattr(message, "voice", None))
    if kind == "text":
        return bool((getattr(message, "raw_text", "") or "").strip()) and not bool(getattr(message, "media", None))
    return bool(getattr(message, "media", None) or (getattr(message, "raw_text", "") or "").strip())


async def _cs_channels(client):
    """Return broadcast channels the logged-in self account can actually read."""
    result = []
    async for dialog in client.iter_dialogs():
        entity = getattr(dialog, "entity", None)
        if not isinstance(entity, types.Channel):
            continue
        if not getattr(entity, "broadcast", False):
            continue
        if getattr(entity, "megagroup", False):
            continue
        title = (getattr(entity, "title", None) or getattr(dialog, "name", None) or "بدون نام").strip()
        result.append({
            "id": int(entity.id),
            "access_hash": int(entity.access_hash) if getattr(entity, "access_hash", None) is not None else None,
            "title": title,
            "username": getattr(entity, "username", None),
        })
    result.sort(key=lambda x: x["title"].casefold())
    return result


def _cs_channel_buttons(uid, channels):
    rows = []
    for idx, item in enumerate(channels):
        title = item["title"]
        if len(title) > 42:
            title = title[:39] + "..."
        rows.append([btn(f"📢 {title}", _self_cb(uid, f"cs_pick:{idx}"), "primary")])
    rows.append([btn("بازگشت", _self_cb(uid, "panel"), "danger", icon=PREMIUM_EMOJI["self_back"][0])])
    return rows


def _cs_media_buttons(uid):
    return [
        [btn("🖼 تصویر", _self_cb(uid, "cs_media:photos"), "primary"), btn("🎬 ویدیو", _self_cb(uid, "cs_media:videos"), "primary")],
        [btn("🎵 موسیقی", _self_cb(uid, "cs_media:music"), "primary"), btn("🎤 ویس", _self_cb(uid, "cs_media:voice"), "primary")],
        [btn("📝 متن", _self_cb(uid, "cs_media:text"), "primary"), btn("📦 همه", _self_cb(uid, "cs_media:all"), "primary")],
        [btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])],
    ]


def _cs_count_buttons(uid, value):
    return [
        [btn("1", _self_cb(uid, "cs_num:1")), btn("2", _self_cb(uid, "cs_num:2")), btn("3", _self_cb(uid, "cs_num:3"))],
        [btn("4", _self_cb(uid, "cs_num:4")), btn("5", _self_cb(uid, "cs_num:5")), btn("6", _self_cb(uid, "cs_num:6"))],
        [btn("7", _self_cb(uid, "cs_num:7")), btn("8", _self_cb(uid, "cs_num:8")), btn("9", _self_cb(uid, "cs_num:9"))],
        [btn("⌫", _self_cb(uid, "cs_back"), "danger"), btn("0", _self_cb(uid, "cs_num:0")), btn("🗑", _self_cb(uid, "cs_clear"), "danger")],
        [btn("✅ تأیید و شروع", _self_cb(uid, "cs_confirm"), "success")],
        [btn("بازگشت", _self_cb(uid, "cs_media_back"), "primary", icon=PREMIUM_EMOJI["self_back"][0])],
    ]


def _cs_count_text(state):
    labels = {"photos":"تصویر", "videos":"ویدیو", "music":"موسیقی", "voice":"ویس", "text":"متن", "all":"همه مدیاها"}
    return (
        f"💾 <b>ذخیره چنل</b>\n\n"
        f"📢 چنل: <b>{html.escape(state['channel_title'])}</b>\n"
        f"📦 نوع: <b>{labels.get(state['media'], state['media'])}</b>\n\n"
        f"🔢 تعداد: <b>{state.get('count', 0)}</b>\n\n"
        f"تعداد موردنظر را انتخاب کن و بعد «تأیید و شروع» را بزن."
    )


async def _cs_save_one(client, entity, message):
    """Save one channel message into Saved Messages, with a safe fallback."""
    # First choice: server-side copy/forward. This preserves the original media
    # without downloading large files through the bot process.
    try:
        result = await _tg_call_with_flood_retry(
            lambda: client.forward_messages("me", message, from_peer=entity),
            label="save channel message",
        )
        return bool(result)
    except Exception as forward_exc:
        # Protected content may reject forwarding. For downloadable media/text,
        # try a real re-upload/copy as a fallback.
        if not getattr(message, "media", None):
            try:
                await _tg_call_with_flood_retry(
                    lambda: client.send_message("me", getattr(message, "raw_text", "") or ""),
                    label="save text fallback",
                )
                return True
            except Exception:
                raise forward_exc

        tmp_dir = Path(tempfile.mkdtemp(prefix="channel_save_"))
        try:
            path = await _tg_call_with_flood_retry(
                lambda: client.download_media(message, file=str(tmp_dir)),
                label="download protected channel media",
            )
            if not path:
                raise forward_exc
            await _tg_call_with_flood_retry(
                lambda: client.send_file(
                    "me", path, caption=(getattr(message, "raw_text", "") or "")[:4096]
                ),
                label="upload protected channel media",
            )
            return True
        except Exception:
            raise forward_exc
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


async def _cs_worker(uid, client, state, editor):
    current = asyncio.current_task()
    requested = int(state["count"])
    kind = state["media"]
    title = state["channel_title"]
    success = 0
    failed = 0
    found = 0
    last_ui = 0.0

    async def update(text, buttons=None):
        try:
            await _cs_edit(editor, text, buttons)
        except Exception as exc:
            # UI failure must never kill the actual save operation.
            print(f"[CHANNEL_SAVE {uid}] progress edit failed: {exc}")

    try:
        access_hash = state.get("access_hash")
        if access_hash is not None:
            entity = await _tg_call_with_flood_retry(
                lambda: client.get_entity(types.InputPeerChannel(int(state["channel_id"]), int(access_hash))),
                label="resolve save channel",
            )
        else:
            entity = await _tg_call_with_flood_retry(
                lambda: client.get_entity(int(state["channel_id"])),
                label="resolve save channel",
            )

        await update(
            f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(title)}</b>\n\n"
            "🔎 در حال پیدا کردن پیام‌های موردنظر...\n"
            f"📦 درخواست: <b>{requested}</b>\n"
            "⏳ لطفاً صبر کن..."
        )

        selected = []
        async for message in client.iter_messages(entity):
            if not message or not _cs_media_match(message, kind):
                continue
            selected.append(message)
            found = len(selected)
            now = time.monotonic()
            if now - last_ui >= CHANNEL_SAVE_PROGRESS_INTERVAL or found == requested:
                last_ui = now
                scan_percent = min(20, int(found * 20 / max(1, requested)))
                scan_bar, _ = _cs_progress_bar(scan_percent, 100)
                await update(
                    f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(title)}</b>\n\n"
                    f"🔎 در حال یافتن پیام‌ها... <b>{found}/{requested}</b>\n"
                    f"<code>{scan_bar}</code> <b>{scan_percent}%</b>\n\n"
                    "⏳ تاریخچه در حال بررسی است..."
                )
            if len(selected) >= requested:
                break

        if not selected:
            await update(
                f"❌ <b>ذخیره چنل</b>\n\n📢 {html.escape(title)}\n\n"
                "هیچ مورد قابل ذخیره‌ای با نوع انتخاب‌شده پیدا نشد.",
                [[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
            )
            return

        selected.reverse()  # oldest -> newest for a natural Saved Messages order
        total = len(selected)
        await update(
            f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(title)}</b>\n\n"
            f"🔄 شروع ذخیره <b>{total}</b> مورد...\n"
            f"<code>{_cs_progress_bar(0, total)[0]}</code> <b>0%</b>\n\n"
            "✅ موفق: 0\n❌ ناموفق: 0"
        )

        last_ui = 0.0
        for index, message in enumerate(selected, 1):
            try:
                if await _cs_save_one(client, entity, message):
                    success += 1
                else:
                    failed += 1
            except Exception as exc:
                failed += 1
                print(f"[CHANNEL_SAVE {uid}] item {index} failed: {exc}")

            now = time.monotonic()
            # Update the same Telegram message at a safe cadence.  For short
            # jobs every item is shown; for large jobs we avoid FloodWait while
            # still guaranteeing a moving percentage and a final 100% update.
            if index == total or total <= 20 or (now - last_ui) >= CHANNEL_SAVE_PROGRESS_INTERVAL:
                last_ui = now
                bar, percent = _cs_progress_bar(index, total)
                await update(
                    f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(title)}</b>\n\n"
                    f"<code>{bar}</code> <b>{percent}%</b>\n\n"
                    f"📦 پیشرفت: <b>{index}/{total}</b>\n"
                    f"✅ موفق: <b>{success}</b>\n"
                    f"❌ ناموفق: <b>{failed}</b>"
                )

        status = "✅ ذخیره با موفقیت کامل شد" if failed == 0 else "⚠️ ذخیره با تعدادی خطا تمام شد"
        await update(
            f"{status}\n\n"
            f"📢 چنل: <b>{html.escape(title)}</b>\n"
            f"📦 درخواست: <b>{requested}</b>\n"
            f"📚 پیدا شده: <b>{total}</b>\n"
            f"✅ ذخیره‌شده: <b>{success}</b>\n"
            f"❌ ناموفق: <b>{failed}</b>\n\n"
            "📁 موارد موفق در <b>Saved Messages</b> ذخیره شدند.",
            [[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )

    except asyncio.CancelledError:
        with contextlib.suppress(Exception):
            await update(
                "⚠️ <b>عملیات ذخیره متوقف شد.</b>",
                [[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
            )
        raise
    except Exception as exc:
        logging.exception("channel save worker crashed")
        await update(
            "❌ <b>ذخیره چنل با خطا متوقف شد.</b>\n\n"
            f"<code>{html.escape(str(exc))}</code>",
            [[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
    finally:
        if _channel_save_tasks.get(uid) is current:
            _channel_save_tasks.pop(uid, None)
        session = _cs_session(uid)
        if session and session.get("editor") == editor:
            # Keep the final message visible; only remove in-memory state.
            _cs_clear(uid)


async def _cs_open(event, uid):
    if uid in _channel_save_tasks and not _channel_save_tasks[uid].done():
        await safe_answer(event, "⏳ یک ذخیره‌سازی در حال اجراست.", True)
        return True
    client = self_clients.get(uid)
    if not client:
        await event.edit(
            premium_ui_text("❌ سلف فعال نیست. ابتدا سلف را فعال کن."),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True
    try:
        channels = await _cs_channels(client)
        if not channels:
            await event.edit(
                premium_ui_text("💾 <b>ذخیره چنل</b>\n\n❌ هیچ چنل قابل دسترسی پیدا نشد."),
                parse_mode="html",
                buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]],
            )
            return True
        _channel_save_sessions[uid] = {"step": "channel", "channels": channels, "editor": _cs_editor_from_event(event)}
        await event.edit(
            premium_ui_text("💾 <b>ذخیره چنل</b>\n\nچنلی را که می‌خواهی از آن ذخیره کنی انتخاب کن:"),
            parse_mode="html",
            buttons=_cs_channel_buttons(uid, channels),
        )
    except Exception as exc:
        logging.exception("channel list failed")
        await event.edit(
            premium_ui_text("❌ <b>لیست چنل‌ها دریافت نشد.</b>\n\n"
            f"<code>{html.escape(str(exc))}</code>"),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
    return True

async def safe_callback_edit(event, *args, **kwargs):
    """Premiumize callback message text without touching buttons/callback data."""
    if args and isinstance(args[0], str):
        args = (premium_ui_text(args[0]),) + args[1:]
        kwargs.setdefault("parse_mode", "html")
    elif "message" in kwargs and isinstance(kwargs["message"], str):
        kwargs["message"] = premium_ui_text(kwargs["message"])
        kwargs.setdefault("parse_mode", "html")
    try:
        return await event.edit(*args, **kwargs)
    except MessageNotModifiedError:
        return None
    except Exception:
        # Never change or remove the supplied buttons on retry.
        try:
            return await event.edit(*args, **kwargs)
        except MessageNotModifiedError:
            return None
        except Exception as exc:
            # Silently eating this made broken screens look "frozen" with no
            # feedback at all. Log it AND tell the user something failed so
            # a tap never just does nothing.
            logging.exception("callback edit failed")
            with contextlib.suppress(Exception):
                await safe_answer(event, f"⚠️ خطا: {exc}", True)
            return None


async def handle_self_panel_callback(event):
    data = event.data.decode("utf-8", errors="ignore")
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "sp":
        return False
    try:
        uid = int(parts[1])
    except ValueError:
        await safe_answer(event, "❌ پنل نامعتبر است.", True)
        return True

    if event.sender_id != uid:
        await safe_answer(event, "❌ این پنل متعلق به شما نیست.", True)
        return True

    action = parts[2]


    await safe_answer(event)

    if action == "home":
        await safe_callback_edit(event, _panel_home_text(), parse_mode="html", buttons=_panel_home_buttons(uid))
        return True

    if action == "acct":
        await _panel_account_screen(event, uid)
        return True

    if action == "acct_noop":
        return True

    if action.startswith("pg:"):
        try:
            page_idx = int(action.split(":", 1)[1])
        except ValueError:
            page_idx = 0
        text, buttons = _panel_render(uid, page_idx)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action.startswith("pdesc:") or action.startswith("pcmd:"):
        wanted = "desc" if action.startswith("pdesc:") else "cmd"
        _, page_str, key = action.split(":", 2)
        page_idx = int(page_str) if page_str.isdigit() else 0
        desc, cmds = _split_guide(_panel_item_body(uid, key))
        body = desc if wanted == "desc" else cmds
        if not body:
            await safe_answer(event, "❌ چیزی برای نمایش نیست.", True)
            return True
        title = PANEL_LABELS.get(key, key)
        heading = "📖 توضیحات" if wanted == "desc" else "⌨️ دستورات"
        await safe_callback_edit(
            event,
            f"<b>{html.escape(title)}</b> — {heading}\n\n{body}",
            parse_mode="html",
            buttons=[
                [btn("بازگشت", _self_cb(uid, f"pgrp:{_panel_parent_key(key)}") if _panel_parent_key(key) else _self_cb(uid, f"pit:{page_idx}:{key}"), "primary", icon=PREMIUM_EMOJI["self_back"][0])],
                [btn("🏠 صفحه اصلی", _self_cb(uid, f"pg:{page_idx}"), "danger", icon=PREMIUM_EMOJI["home"][0])],
            ],
        )
        return True

    if action in ("hx_name", "hx_bio", "hx_content", "hx_content_clear"):
        if action == "hx_content_clear":
            htx_save_content_map(uid, {})
        kind = "content" if action.startswith("hx_content") else action[3:]
        text, buttons = _htx_screen(uid, kind)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action in ("fe_menu", "fe_enemy", "fe_friend", "vn_open"):
        text, buttons = _htx_fe_screen(uid, action)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action.startswith("pgrp:"):
        group_key = action.split(":", 1)[1]
        if group_key in PANEL_GROUPS:
            await _panel_show_group(event, uid, group_key)
        else:
            await safe_answer(event, "❌ این بخش پیدا نشد.", True)
        return True

    if action.startswith("pit:"):
        _, page_str, key = action.split(":", 2)
        page_idx = int(page_str) if page_str.isdigit() else 0
        direct = PANEL_DIRECT_ACTIONS.get(key)
        if direct:
            # Falls through to that action's own existing handler below —
            # these already build their full dedicated screen.
            action = direct
        else:
            await _panel_show_item(event, uid, key)
            return True

    # NOTE: these two must stay AFTER the "pit:" block above. PANEL_DIRECT_ACTIONS
    # reassigns `action` to "premium_emoji_open" for the 💎 grid button, and that
    # reassignment only takes effect for checks that come later in this function.
    # They used to sit *before* "pit:", so the reassigned action never matched
    # anything again and the tap silently did nothing (same bug class as the
    # other direct actions below, e.g. "cs_open", which are correctly placed here).
    if action == "premium_emoji_open":
        await _panel_show_premium_emoji(event, uid)
        return True

    if action == "cs_open":
        return await _cs_open(event, uid)

    if action.startswith("cs_"):
        session = _cs_session(uid)
        if not session:
            await safe_answer(event, "❌ این عملیات دیگر فعال نیست.", True)
            return True

        if action.startswith("cs_pick:"):
            try:
                idx = int(action.split(":", 1)[1])
                item = session["channels"][idx]
            except (ValueError, IndexError, KeyError):
                await safe_answer(event, "❌ چنل انتخابی معتبر نیست.", True)
                return True
            session.update({
                "step": "media",
                "channel_id": item["id"],
                "access_hash": item.get("access_hash"),
                "channel_title": item["title"],
            })
            await safe_callback_edit(event, 
                f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(item['title'])}</b>\n\nنوع مدیا را انتخاب کن:",
                parse_mode="html", buttons=_cs_media_buttons(uid)
            )
            return True

        if action.startswith("cs_media:"):
            kind = action.split(":", 1)[1]
            if kind not in {"photos", "videos", "music", "voice", "text", "all"} or session.get("step") != "media":
                return True
            session.update({"step": "count", "media": kind, "count": 0})
            await safe_callback_edit(event, _cs_count_text(session), parse_mode="html", buttons=_cs_count_buttons(uid, 0))
            return True

        if action == "cs_media_back":
            session["step"] = "media"
            await safe_callback_edit(event, 
                f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(session.get('channel_title','چنل'))}</b>\n\nنوع مدیا را انتخاب کن:",
                parse_mode="html", buttons=_cs_media_buttons(uid)
            )
            return True

        if action.startswith("cs_num:") and session.get("step") == "count":
            digit = action.split(":", 1)[1]
            if digit.isdigit():
                value = str(session.get("count", 0))
                value = "" if value == "0" else value
                candidate = (value + digit).lstrip("0") or "0"
                if len(candidate) <= 4 and int(candidate) <= CHANNEL_SAVE_MAX_COUNT:
                    session["count"] = int(candidate)
                else:
                    await safe_answer(event, f"⚠️ حداکثر {CHANNEL_SAVE_MAX_COUNT} مورد است.", True)
                    return True
            await safe_callback_edit(event, _cs_count_text(session), parse_mode="html", buttons=_cs_count_buttons(uid, session["count"]))
            return True

        if action == "cs_back" and session.get("step") == "count":
            value = str(session.get("count", 0))
            session["count"] = int(value[:-1] or "0")
            await safe_callback_edit(event, _cs_count_text(session), parse_mode="html", buttons=_cs_count_buttons(uid, session["count"]))
            return True

        if action == "cs_clear" and session.get("step") == "count":
            session["count"] = 0
            await safe_callback_edit(event, _cs_count_text(session), parse_mode="html", buttons=_cs_count_buttons(uid, 0))
            return True

        if action == "cs_confirm" and session.get("step") == "count":
            count = int(session.get("count", 0))
            if count < 1:
                await safe_answer(event, "⚠️ ابتدا تعداد را انتخاب کن.", True)
                return True
            if uid in _channel_save_tasks and not _channel_save_tasks[uid].done():
                await safe_answer(event, "⏳ یک عملیات ذخیره در حال اجراست.", True)
                return True
            client = self_clients.get(uid)
            if not client:
                await safe_callback_edit(event, "❌ سلف فعال نیست.", parse_mode="html", buttons=self_panel_buttons(uid))
                _cs_clear(uid)
                return True

            # Capture the exact message identity once. The same message is edited
            # for the whole lifecycle; a UI edit failure must never cancel saving.
            editor = _cs_editor_from_event(event)
            session["step"] = "processing"
            session["count"] = count
            session["editor"] = editor
            worker_state = dict(session)

            # Give the user immediate feedback when possible, but never make this
            # cosmetic edit a prerequisite for the actual save worker.
            with contextlib.suppress(Exception):
                await safe_callback_edit(event, 
                    f"💾 <b>ذخیره چنل</b>\n\n📢 <b>{html.escape(session['channel_title'])}</b>\n\n"
                    "⏳ در حال آماده‌سازی...\n"
                    "<code>░░░░░░░░░░░░░░░░</code> <b>0%</b>",
                    parse_mode="html",
                    buttons=None,
                )

            task = asyncio.create_task(_cs_worker(uid, client, worker_state, editor))
            _channel_save_tasks[uid] = task
            return True

        return True

    if action == "panel":
        _first_comment_channel_sessions.pop(int(uid), None)

    if action == "close":
        _first_comment_channel_sessions.pop(int(uid), None)
        last_panel = _LAST_PANEL_MSG.pop(int(uid), None)
        # Step 1 (instant): popup + strip the buttons, photo stays on screen.
        strip_results = await asyncio.gather(
            safe_answer(event, "پنل با موفقیت بسته شد."),
            _htx_strip_panel_buttons(event, uid),
            return_exceptions=True,
        )
        buttons_removed = strip_results[1] is True
        # Step 2 (after a short beat): delete the now button-less card.
        deleted = False
        if last_panel:
            peer, message_id = last_panel
            deleted = await _delete_closed_panel(uid, peer, message_id, delay=HTX_PANEL_CLOSE_DELETE_DELAY) is True
        if not deleted and not buttons_removed:
            # Last resort: nothing worked, at least try once more to strip the buttons.
            with contextlib.suppress(Exception):
                await safe_callback_edit(event, self_panel_text(uid), parse_mode="html", buttons=None)
        return True
    if action == "comment_setup":
        try:
            client=self_clients.get(int(uid))
            if not client:
                raise RuntimeError("SELF session is not connected")

            # IMPORTANT: channel discovery and rendering deliberately mirror
            # «💾 ذخیره چنل».  Do not put channel ids/entities inside callback_data.
            # Only a tiny numeric index is sent; the full channel data stays in
            # this in-memory session. This avoids Telegram's reply-markup limit.
            channels=await _cs_channels(client)
            _first_comment_channel_sessions[int(uid)] = channels

            rows=[]
            for idx,item in enumerate(channels):
                title=item["title"]
                if len(title)>42:
                    title=title[:39]+"..."
                rows.append([btn(f"📢 {title}",_self_cb(uid,f"fc_pick:{idx}"),"primary")])

            if not rows:
                rows=[[btn("بازگشت",_self_cb(uid,"panel"),"primary", icon=PREMIUM_EMOJI["self_back"][0])]]
                text="💬 <b>کامنت اول</b>\n\n❌ هیچ کانال پخشی که SELF به آن دسترسی دارد پیدا نشد."
            else:
                rows.append([btn("بازگشت",_self_cb(uid,"panel"),"primary", icon=PREMIUM_EMOJI["self_back"][0])])
                text="💬 <b>کامنت اول</b>\n\nکانال را انتخاب کن:"

            await safe_callback_edit(event, text,parse_mode="html",buttons=rows)
        except Exception as exc:
            logging.exception("first comment channel list failed")
            await safe_callback_edit(event, 
                f"❌ <b>دریافت کانال‌ها ناموفق بود.</b>\n\n<code>{html.escape(str(exc))}</code>",
                parse_mode="html",
                buttons=[[btn("بازگشت",_self_cb(uid,"panel"),"primary", icon=PREMIUM_EMOJI["self_back"][0])]]
            )
        return True

    if action.startswith("fc_pick:"):
        try:
            idx=int(action.split(":",1)[1])
            channels=_first_comment_channel_sessions.get(int(uid),[])
            item=channels[idx]
            cid=int(item["id"])
            client=self_clients.get(int(uid))
            if not client:
                raise RuntimeError("SELF session is not connected")
            if not client: raise RuntimeError("SELF session is not connected")
            entity=await client.get_entity(cid)
            if not isinstance(entity,types.Channel) or getattr(entity,"megagroup",False): raise RuntimeError("این مورد کانال پخش نیست")
            full=await client(functions.channels.GetFullChannelRequest(channel=entity))
            did=getattr(getattr(full,"full_chat",None),"linked_chat_id",None)
            if not did:
                await safe_callback_edit(event, f"❌ <b>{html.escape(getattr(entity,'title','کانال'))}</b>\n\nاین کانال Discussion متصل ندارد.",parse_mode="html",buttons=[[btn("🔄 انتخاب کانال دیگر",_self_cb(uid,"comment_setup"),"primary")],[btn("🏠 پنل اصلی",_self_cb(uid,"panel"),"danger")]])
                return True
            discussion=await client.get_entity(int(did)); old=_first_comment_config(uid,cid) or {}
            item={"id":int(entity.id),"access_hash":getattr(entity,"access_hash",None),"title":getattr(entity,"title","کانال"),"username":getattr(entity,"username",None),"discussion_id":int(did),"discussion_access_hash":getattr(discussion,"access_hash",None),"text":str(old.get("text") or "")[:4096],"enabled":bool(old.get("enabled",True))}
            _upsert_first_comment_config(uid,item); _set_comment_target(uid,cid)
            status="🟢 فعال" if item["enabled"] and item["text"] else ("🟡 بدون متن" if item["enabled"] else "🔴 خاموش")
            preview=html.escape(item["text"][:500]) if item["text"] else "❌ تنظیم نشده"
            await safe_callback_edit(event, f"💬 <b>کامنت اول</b>\n\n📢 <b>{html.escape(item['title'])}</b>\n💬 Discussion: <b>{html.escape(getattr(discussion,'title','گروه گفتگو'))}</b>\n\nوضعیت: <b>{status}</b>\n📝 متن فعلی: <blockquote>{preview}</blockquote>\n\nروی یک پیام متنی ریپلای کن و <code>تنظیم کامنت</code> بفرست.",parse_mode="html",buttons=[[btn("✏️ راهنمای تنظیم متن",_self_cb(uid,"comment_text_help"),"success"),btn("🗑 حذف تنظیم کانال",_self_cb(uid,"comment_remove"),"danger")],[btn("🔴 خاموش" if item["enabled"] else "🟢 فعال",_self_cb(uid,"comment_toggle"),"danger" if item["enabled"] else "success"),btn("🔄 کانال دیگر",_self_cb(uid,"comment_setup"),"primary")],[btn("🏠 پنل اصلی",_self_cb(uid,"panel"),"danger")]])
        except Exception as exc:
            await safe_callback_edit(event, f"❌ <b>تنظیم کانال ناموفق بود.</b>\n\n<code>{html.escape(str(exc))}</code>",parse_mode="html",buttons=[[btn("🔄 تلاش دوباره",_self_cb(uid,"comment_setup"),"primary")],[btn("🏠 پنل اصلی",_self_cb(uid,"panel"),"danger")]])
        return True

    if action == "comment_toggle":
        cid=_comment_target(uid); cfg=_first_comment_config(uid,cid) if cid else None
        if not cfg: await safe_answer(event,"❌ ابتدا کانال را انتخاب کن.",True); return True
        cfg["enabled"]=not bool(cfg.get("enabled",True)); _upsert_first_comment_config(uid,cfg)
        await safe_callback_edit(event, f"{'🟢 کامنت اول فعال شد.' if cfg['enabled'] else '🔴 کامنت اول خاموش شد.'}",parse_mode="html",buttons=[[btn("بازگشت",_self_cb(uid,"comment_setup"),"primary")]], icon=PREMIUM_EMOJI["self_back"][0])
        return True

    if action == "comment_remove":
        cid=_comment_target(uid)
        if not cid or not _remove_first_comment_config(uid,cid): await safe_answer(event,"❌ تنظیمی برای حذف پیدا نشد.",True); return True
        await safe_callback_edit(event, "✅ <b>تنظیمات این کانال کامل حذف شد.</b>",parse_mode="html",buttons=[[btn("📢 لیست کانال‌ها",_self_cb(uid,"comment_setup"),"primary")],[btn("🏠 پنل اصلی",_self_cb(uid,"panel"),"danger")]])
        return True

    if action == "comment_text_help":
        cid=_comment_target(uid); cfg=_first_comment_config(uid,cid) if cid else None
        if not cfg: await safe_answer(event,"❌ ابتدا کانال را انتخاب کن.",True); return True
        await safe_callback_edit(event, f"✏️ <b>تنظیم متن کامنت</b>\n\n📢 {html.escape(str(cfg.get('title') or 'کانال'))}\n\nروی یک پیام متنی ریپلای کن و بنویس:\n<code>.تنظیم کامنت</code>\n\nمتن برای همین کانال ذخیره و کامنت اول فعال می‌شود.",parse_mode="html",buttons=[[btn("بازگشت",_self_cb(uid,"comment_setup"),"primary")]], icon=PREMIUM_EMOJI["self_back"][0])
        return True

    if action == "comment_help":
        await safe_callback_edit(event, "💬 <b>کامنت اول</b>\n\n📢 کانال را از لیست انتخاب کن.\n✏️ روی پیام متنی ریپلای + <code>.تنظیم کامنت</code>\n🟢/🔴 فعال و خاموش از پنل همان کانال\n🗑 حذف تنظیمات از پنل همان کانال",parse_mode="html",buttons=[[btn("بازگشت",_self_cb(uid,"comment_setup"),"primary")]], icon=PREMIUM_EMOJI["self_back"][0])
        return True

    if action == "secretary_help":
        await safe_callback_edit(event, 
            "🤵 <b>منشی</b>\n\n"
            "<code>.تنظیم منشی</code> + ریپلای روی متن/مدیا\n"
            "<code>.منشی روشن</code> / <code>.منشی خاموش</code>\n"
            "<code>.تنظیم زمان منشی 15</code>\n\n"
            "فقط پیوی؛ هر کاربر در هر بازه فقط یک پاسخ.",
            parse_mode="html", buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return True
    if action == "group_help":
        await safe_callback_edit(event, 
            "🛡 <b>مدیریت گروه</b>\n\n"
            "<code>.پین</code> / <code>.حذف پین</code> با ریپلای\n"
            "<code>.بن</code> یا <code>.سیک</code> با ریپلای\n"
            "<code>.آن بن</code> با ریپلای\n"
            "<code>.بن سراسری @user</code>\n<code>.حذف بن سراسری @user</code>\n<code>.لیست بن سراسری</code>",
            parse_mode="html", buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return True
    if action == "tag_help":
        await safe_callback_edit(event, 
            "🏷 <b>تگ اعضا</b>\n\n<code>.تگ 20</code>\n<code>.همه</code>\n\nپیام دستور حذف و تگ‌ها گروهی ارسال می‌شوند.",
            parse_mode="html", buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return True
    if action == "ping":
        await safe_callback_edit(event, 
            _ping_text(),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_PING_PAGE}"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "balance_info":
        await safe_callback_edit(event,
            _htx_balance_text(uid),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_BALANCE_PAGE}"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "balance_transfer_info":
        await safe_callback_edit(event,
            _htx_transfer_info_text(),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, f"pg:{PANEL_BALANCE_PAGE}"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "screenshot_info":
        text, buttons = _htx_screenshot_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "calc_info":
        text, buttons = _htx_calc_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "tts_info":
        text, buttons = _htx_tts_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "ig_dl_info":
        text, buttons = _htx_ig_dl_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "ph_dl_info":
        text, buttons = _htx_ph_dl_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "xvid_dl_info":
        text, buttons = _htx_xvid_dl_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "xnxx_dl_info":
        text, buttons = _htx_xnxx_dl_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "snap_info":
        text, buttons = _htx_snap_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "delete_info":
        text, buttons = _htx_delete_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "info_open":
        text, buttons = _htx_info_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "timerdar_info":
        text, buttons = _htx_timerdar_screen(uid)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    if action == "banners":
        banners = self_banners(uid)
        value = self_get(uid, "banner_auto", "off")
        status = "روشن ✅" if value == "on" else "خاموش ❌"
        body = [f"📢 <b>مدیریت بنرها</b>\n\n🔘 ارسال خودکار: {status}"]
        for b in banners:
            body.append(
                f"\n<b>#{int(b['id'])}</b> • "
                f"{'فوروارد' if b.get('mode') == 'forward' else 'کپی'} • "
                f"هر {int(b.get('interval', 60))} دقیقه • "
                f"مقصد: {len(b.get('targets', []))}"
            )
        if not banners:
            body.append("\nهنوز بنری ثبت نشده است.")
        await safe_callback_edit(event, 
            "".join(body), parse_mode="html",
            buttons=[
                [btn("🟢 روشن کردن تبچی" if value != "on" else "🔴 خاموش کردن تبچی", _self_cb(uid, "banner_toggle"), "success" if value != "on" else "danger")],
                [btn("📚 راهنمای دستورات بنر", _self_cb(uid, "banner_help"), "primary")],
                [btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])],
            ],
        )
        return True

    if action == "banner_toggle":
        current = self_get(uid, "banner_auto", "off")
        value = "off" if current == "on" else "on"
        sent = failed = 0
        if value == "on":
            client = _get_tabchi_client(uid)
            if not client:
                await safe_callback_edit(event, 
                    "❌ <b>سلف فعال نیست.</b>\n\nتبچی فقط با اکانت SELF اجرا می‌شود و با BOT ارسال نخواهد کرد.",
                    parse_mode="html",
                )
                return
            self_set(uid, "banner_auto", value)
            sent, failed = await _banner_dispatch_all_configured(client, uid)
        else:
            self_set(uid, "banner_auto", value)
        banners = self_banners(uid)
        status = "روشن ✅" if value == "on" else "خاموش ❌"
        body = [f"📢 <b>مدیریت بنرها</b>\n\n🔘 ارسال خودکار: {status}"]
        if value == "on" and (sent or failed):
            body.append(f"\n📨 ارسال فوری: {sent} مقصد")
            if failed:
                body.append(f"\n⚠️ ناموفق: {failed}")
        for b in banners:
            body.append(
                f"\n<b>#{int(b['id'])}</b> • "
                f"{'فوروارد' if b.get('mode') == 'forward' else 'کپی'} • "
                f"هر {int(b.get('interval', 60))} دقیقه • "
                f"مقصد: {len(b.get('targets', []))}"
            )
        if not banners:
            body.append("\nهنوز بنری ثبت نشده است.")
        await safe_callback_edit(event, 
            "".join(body), parse_mode="html",
            buttons=[
                [btn("🟢 روشن کردن تبچی" if value != "on" else "🔴 خاموش کردن تبچی", _self_cb(uid, "banner_toggle"), "success" if value != "on" else "danger")],
                [btn("📚 راهنمای دستورات بنر", _self_cb(uid, "banner_help"), "primary")],
                [btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])],
            ],
        )
        return True

    if action == "banner_help":
        await safe_callback_edit(event, 
            "🤖 <b>راهنمای تبچی</b>\n<i>مدیریت بنر، مقصدها و ارسال خودکار</i>\n\n"
            "<blockquote>📌 <b>نکته:</b> عدد یعنی شماره بنر؛ مثلاً <code>۱</code>.</blockquote>\n\n"
            "<b>① روشن / خاموش</b>\n<code>.تبچی روشن</code>\n<code>.تبچی خاموش</code>\n"
            "فعال یا غیرفعال‌کردن ارسال خودکار بنرها.\n\n"
            "<b>② ساخت بنر</b>\nروی پیام موردنظر ریپلای کن:\n"
            "<code>.تنظیم بنر فور</code> → فوروارد\n"
            "<code>.تنظیم بنر کپی</code> → کپی پیام\n\n"
            "<b>③ حذف و پاکسازی</b>\n<code>.حذف بنر ۱</code>\n<code>.پاکسازی لیست بنر ها</code>\n\n"
            "<b>④ زمان‌بندی</b>\n<code>.تنظیم عدد بنر ۱ ۳۰ دقیقه</code>\n"
            "بنر ۱ را هر ۳۰ دقیقه ارسال می‌کند.\n\n"
            "<b>⑤ مقصد یک گروه</b>\nداخل گروه هدف: <code>.تنظیم گپ هدف بنر ۱</code>\n"
            "حذف همان مقصد: <code>.حذف گپ هدف بنر ۱</code>\n\n"
            "<b>⑥ تمام گروه‌ها</b>\n<code>.تنظیم هدف بنر ۱ تمام گپ ها</code>\n"
            "تمام گروه‌های قابل دسترسی سلف را مقصد بنر می‌کند.\n\n"
            "<b>⑦ ارسال فوری به پیوی‌ها</b>\n<code>.فور بنر ۱ در ۲۰ پیوی اخیر</code>\n"
            "بنر ۱ را همان لحظه برای ۲۰ پیوی اخیر ارسال می‌کند.\n\n"
            "<blockquote>💡 <b>ترتیب پیشنهادی:</b> ریپلای پیام → ساخت بنر → تعیین مقصد → تعیین زمان → تبچی روشن.</blockquote>",
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "banners"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "currency":
        await safe_callback_edit(event, 
            "💱 <b>نرخ لحظه‌ای ارز</b>\n\n"
            "قیمت را با این دستور بگیر:\n\n"
            "<code>.نرخ ارز</code>\n<code>.قیمت دلار</code>\n<code>.قیمت یورو</code>\n<code>.قیمت طلا</code>\n<code>.قیمت BTC</code>\n<code>.قیمت ETH</code>\n<code>.قیمت SOL</code>\n<code>.قیمت USDT</code>\n\n"
            "⚡ نرخ لحظه‌ای USDT/TMN از دفتر سفارش عمومی والکس؛ برای تبدیل از میانگین خرید و فروش استفاده می‌شود.\n"
            "💶 یورو با نرخ جهانی EUR/USD و نرخ بازار تتر برآورد می‌شود.\n"
            "🟡 طلا، برآورد خام هر گرم ۱۸ عیار از اونس جهانی است؛ اجرت و هزینه‌های بازار لحاظ نشده.\n"
            "⚠️ نرخ تتر شاخص تقریبی دلار آزاد است و معادل تضمین‌شده دلار نقدی نیست؛ در خطای والکس منبع پشتیبان فعال می‌شود.",
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True
    if action == "logo":
        await safe_callback_edit(event, 
            "🎨 <b>لوگوساز</b>\n\n"
            "ساخت لوگوی حرفه‌ای با ۱۲ قالب:\n<code>.لوگو 12 HusteRIX</code>\n"
            "با زیرعنوان: <code>.لوگو 1 HusteRIX | Premium Self</code>\n\n"
            + "\n".join(f"{i}. {name}" for i, (_k, name) in LOGO_TEMPLATES.items()),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True


    if action == "panel":
        text, buttons = _panel_render(uid, 0)
        await safe_callback_edit(event, text, parse_mode="html", buttons=buttons)
        return True

    # Cleanup UI intentionally bypasses the global Premium Emoji text transformer.
    # This section must use plain Unicode emojis so callback edits stay reliable.
    async def _cleanup_plain_edit(event, *args, **kwargs):
        if args and isinstance(args[0], str):
            kwargs.setdefault("parse_mode", "html")
        elif "message" in kwargs and isinstance(kwargs["message"], str):
            kwargs.setdefault("parse_mode", "html")
        try:
            return await event.edit(*args, **kwargs)
        except MessageNotModifiedError:
            return None
        except Exception as exc:
            logging.exception("cleanup plain edit failed")
            with contextlib.suppress(Exception):
                await safe_answer(event, f"⚠️ خطا در پاکسازی: {exc}", True)
            return None

    if action == "cleanup":
        try:
            await _cleanup_plain_edit(event, 
                "🧹 <b>پاکسازی اکانت</b>\n\n"
                "هر بخش مستقل است و فقط همان بخش را پاک می‌کند.\n"
                "💾 Saved Messages دست‌نخورده می‌ماند.",
                parse_mode="html",
                buttons=[
                    [btn("💬 پاکسازی چت‌ها (دوطرفه)", _self_cb(uid, "cleanup_choose:chats"), "danger")],
                    [btn("👥 پاکسازی گپ‌ها", _self_cb(uid, "cleanup_choose:groups"), "danger")],
                    [btn("📢 پاکسازی کانال‌ها", _self_cb(uid, "cleanup_choose:channels"), "danger")],
                    [btn("👤 پاکسازی مخاطبین", _self_cb(uid, "cleanup_choose:contacts"), "danger")],
                    [btn("🤖 پاکسازی و بلاک ربات‌ها", _self_cb(uid, "cleanup_choose:bots"), "danger")],
                    [btn("🧹 پاکسازی همه", _self_cb(uid, "cleanup_choose:all"), "danger")],
                    [btn("↩️ برگشت", _self_cb(uid, "panel"), "primary")],
                ],
            )
        except Exception as exc:
            logging.exception("cleanup menu open failed")
            with contextlib.suppress(Exception):
                await safe_answer(event, f"⚠️ خطا در باز کردن پاکسازی: {exc}", True)
        return True

    if action.startswith("cleanup_choose:"):
        try:
            target = action.split(":", 1)[1]
            labels = {
                "chats": "💬 پاکسازی چت‌ها به‌صورت دوطرفه",
                "groups": "👥 پاکسازی گپ‌ها",
                "channels": "📢 پاکسازی کانال‌ها",
                "contacts": "👤 پاکسازی مخاطبین",
                "bots": "🤖 پاکسازی و بلاک ربات‌ها",
                "all": "🧹 پاکسازی همه",
            }
            if target not in labels:
                return True
            await _cleanup_plain_edit(event, 
                f"⚠️ <b>{labels[target]}</b>\n\n"
                "این عملیات قابل برگشت نیست.\n"
                "Saved Messages دست‌نخورده می‌ماند.\n\n"
                "برای شروع تأیید کن:",
                parse_mode="html",
                buttons=[
                    [btn("⚠️ تأیید و اجرا", _self_cb(uid, f"cleanup_confirm:{target}"), "danger")],
                    [btn("↩️ برگشت به پاکسازی", _self_cb(uid, "cleanup"), "primary")],
                ],
            )
        except Exception as exc:
            logging.exception("cleanup_choose failed: action=%s", action)
            with contextlib.suppress(Exception):
                await safe_answer(event, f"⚠️ خطا در انتخاب دسته: {exc}", True)
        return True

    if action.startswith("cleanup_confirm:"):
        try:
            target = action.split(":", 1)[1]
            if target not in {"chats", "groups", "channels", "contacts", "bots", "all"}:
                return True
            if self_get(uid, "cleanup_running", "off") == "on":
                current = self_get(uid, "cleanup_progress", "⏳ در حال اجرا…")
                await _cleanup_plain_edit(
                    event,
                    f"⏳ یک پاکسازی همین الان در حال اجراست.\n\n{current}",
                    parse_mode="html",
                    buttons=self_panel_buttons(uid),
                )
                return True
            client = self_clients.get(uid)
            if not client:
                await _cleanup_plain_edit(event, "❌ سلف فعال نیست.", buttons=self_panel_buttons(uid))
                return True
            _cleanup_panel_messages[uid] = (
                getattr(event, "chat_id", None),
                getattr(event, "message_id", None),
                _event_inline_message_id(event),
            )
            task = asyncio.create_task(
                _cleanup_run(
                    uid,
                    target,
                    getattr(event, "chat_id", None),
                    getattr(event, "message_id", None),
                    _event_inline_message_id(event),
                )
            )
            _cleanup_tasks[uid] = task
            await _cleanup_plain_edit(event, "⏳ پاکسازی شروع شد…\nپیشرفت لحظه‌ای در همین پنل نمایش داده می‌شود.", parse_mode="html", buttons=self_panel_buttons(uid))
        except Exception as exc:
            logging.exception("cleanup_confirm failed: action=%s", action)
            with contextlib.suppress(Exception):
                await safe_answer(event, f"⚠️ خطا در اجرای پاکسازی: {exc}", True)
        return True

    if action == "lock_help":
        page_idx = _panel_key_page("lock")
        await safe_callback_edit(
            event,
            _htx_stack(
                f"{HTX_TAG} • قفل چت",
                "دستورات • پیوی + ریپلای",
                "<code>.قفل چت</code>\n<code>.بازکردن قفل چت</code>",
                "روی پیام یک نفر خاص در پیوی ریپلای کن و این دستور را بفرست؛ پیام‌های او از این پس به‌صورت دوطرفه پاک می‌شود.",
                "دکمه‌های صفحه قبل (لینک، یوزرنیم، عکس، ریپلای، استیکر، گیف، فوروارد، پیوی) هرکدام یک نوع پیام را برای همه در پیوی جدا از هم قفل می‌کنند؛ «پیوی» همان قفل چت همگانی است.",
            ),
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, f"pit:{page_idx}:lock"), "danger", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "block_help":
        await safe_callback_edit(event, 
            self_panel_text(uid) + "\n\n🚫 داخل گروه روی پیام کاربر ریپلای کن و بنویس: <b>.بلاک + ریپلای</b>",
            parse_mode="html", buttons=self_panel_buttons(uid)
        )
        return True

    toggles = {
        "time": "time_name", "timebio": "time_bio", "bold": "bold", "persian": "persian_font",
        "translate": "translate", "read": "auto_read", "typing": "typing",
        "game": "game_mode", "autoreply": "auto_reply",
        "lock_link": "lock_link", "lock_username": "lock_username", "lock_photo": "lock_photo",
        "lock_reply": "lock_reply", "lock_sticker": "lock_sticker", "lock_gif": "lock_gif",
        "lock_forward": "lock_forward", "lock_dm": "chat_lock_global",
        "auto_read": "auto_read", "game_mode": "game_mode",
        "action_voice": "action_voice", "action_round": "action_round", "action_video": "action_video",
        "action_photo": "action_photo", "action_document": "action_document", "action_sticker": "action_sticker",
        "always_online": "always_online",
    }
    toggles.update({f[1]: f[0] for f in SELF_FORMAT_FLAGS})
    if action in toggles:
        key = toggles[action]
        current = self_get(uid, key, "off")
        self_set(uid, key, "off" if current == "on" else "on")
        if action in ("time", "timebio"):
            # on -> write the clock right now; off -> remove it from the
            # name / bio right now (it is no longer left behind).
            with contextlib.suppress(Exception):
                await apply_clock_toggle(uid, "name" if action == "time" else "bio")
        await _panel_show_item(event, uid, PANEL_TOGGLE_HOME.get(action, "clock"))
        return True

    if action == "clk_font":
        names = list(SELF_CLOCK_FONTS)
        cur = self_get(uid, "clock_font", "normal")
        self_set(uid, "clock_font", names[(names.index(cur) + 1) % len(names)] if cur in names else names[0])
        with contextlib.suppress(Exception):
            await apply_clock_font(uid)
        await _panel_show_clock(event, uid)
        return True

    if action == "clockfont":
        names = list(SELF_CLOCK_FONTS)
        cur = self_get(uid, "clock_font", "normal")
        nxt = names[(names.index(cur) + 1) % len(names)] if cur in names else names[0]
        self_set(uid, "clock_font", nxt)

        # Apply the selected font immediately to the profile name (and bio
        # clock) instead of waiting for the worker's next polling tick.
        with contextlib.suppress(Exception):
            await apply_clock_font(uid)

        await _panel_show_item(event, uid, "fonts", extra_text=self_font_preview(uid, "clock"))
        return True

    if action == "engfont":
        names = list(SELF_ENGLISH_FONTS)
        cur = self_get(uid, "english_font", "normal")
        nxt = names[(names.index(cur) + 1) % len(names)] if cur in names else names[0]
        self_set(uid, "english_font", nxt)
        await _panel_show_item(event, uid, "fonts", extra_text=self_font_preview(uid, "english"))
        return True

    if action == "autoreply":
        current = self_get(uid, "auto_reply", "off")
        self_set(uid, "auto_reply", "off" if current == "on" else "on")
        mapping = self_auto_reply_map(uid)
        status = "روشن ✅" if self_get(uid, "auto_reply") == "on" else "خاموش ❌"
        await safe_callback_edit(event, 
            f"💬 <b>پاسخ خودکار</b>\\n\\nوضعیت: {status}\\nکلمات ثبت‌شده: {len(mapping)}\\n\\n"
            "دستورات:\\n"
            "<code>.پاسخ خودکار جدید [کلمه]</code>\\n"
            "<code>.ذخیره پاسخ خودکار [کلمه]</code> + ریپلای\\n"
            "<code>.حذف پاسخ خودکار [کلمه]</code>\\n"
            "<code>.لیست پاسخ خودکار</code>",
            parse_mode="html",
            buttons=[[btn("بازگشت", _self_cb(uid, "panel"), "primary", icon=PREMIUM_EMOJI["self_back"][0])]],
        )
        return True

    if action == "reaction":
        await safe_callback_edit(event, 
            self_panel_text(uid) + "\n\n❤️ برای فعال‌سازی: روی پیام کاربر ریپلای کن و «.ریاکشن ❤️» بفرست.\nبرای حذف: «.حذف ریاکشن»." ,
            parse_mode="html",
            buttons=self_panel_buttons(uid),
        )
        return True

    return True



async def _media_reply_message(event):
    if not event.is_reply:
        return None, "❌ روی عکس یا استیکر ریپلای کن."
    replied = await event.get_reply_message()
    if not replied:
        return None, "❌ پیام ریپلای‌شده پیدا نشد."
    return replied, None


def _is_animated_image(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return bool(getattr(im, "is_animated", False) and getattr(im, "n_frames", 1) > 1)
    except Exception:
        return False


def _image_to_webp(path, out_path):
    from PIL import Image, ImageOps
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGBA")
        # Telegram sticker canvas: max 512x512, transparent background preserved.
        im.thumbnail((512, 512), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        x = (512 - im.width) // 2
        y = (512 - im.height) // 2
        canvas.alpha_composite(im, (x, y))
        canvas.save(out_path, "WEBP", lossless=True, quality=95, method=6)


def _animated_to_gif(path, out_path):
    # Pillow handles GIF and animated WebP. TGS (Telegram animated sticker)
    # is decoded with python-lottie when available; WebM falls back to ffmpeg.
    if str(path).lower().endswith(".tgs"):
        try:
            from lottie.parsers.tgs import parse_tgs
            from lottie.exporters.gif import export_gif
            animation = parse_tgs(str(path))
            export_gif(animation, str(out_path))
            return out_path.exists()
        except Exception:
            pass
    try:
        from PIL import Image
        with Image.open(path) as im:
            if getattr(im, "is_animated", False):
                frames = []
                durations = []
                for i in range(getattr(im, "n_frames", 1)):
                    im.seek(i)
                    frame = im.convert("RGBA")
                    frames.append(frame.copy())
                    durations.append(int(im.info.get("duration", 100) or 100))
                if frames:
                    frames[0].save(
                        out_path, "GIF", save_all=True, append_images=frames[1:],
                        duration=durations, loop=0, disposal=2
                    )
                    return True
    except Exception:
        pass

    import subprocess
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(path), "-vf", "fps=15,scale='min(512,iw)':-1:flags=lanczos",
             "-loop", "0", str(out_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60
        )
        return out_path.exists()
    except Exception:
        return False


async def _self_image_to_sticker(event, uid, keep_reply=False):
    replied, error = await _media_reply_message(event)
    if error:
        return error
    if not getattr(replied, "photo", False):
        return "❌ پیام ریپلای‌شده عکس نیست."
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_sticker_{uid}_"))
    try:
        src = await replied.download_media(file=str(tmp_dir))
        if not src:
            return "❌ دانلود عکس ناموفق بود."
        out = tmp_dir / "sticker.webp"
        _image_to_webp(src, out)
        await event.client.send_file(
            event.chat_id, str(out), force_document=False,
            caption=None, reply_to=(replied.id if keep_reply else None),
            attributes=[types.DocumentAttributeSticker(alt="🙂", stickerset=types.InputStickerSetEmpty(), mask=False)]
        )
        return "✅ عکس به استیکر تبدیل شد."
    except ImportError:
        return "❌ برای تبدیل عکس به استیکر نصب Pillow لازم است."
    except Exception as exc:
        print(f"[SELF {uid}] image->sticker failed: {exc}")
        return "❌ تبدیل عکس به استیکر انجام نشد."
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def _self_sticker_to_photo(event, uid, keep_reply=False):
    replied, error = await _media_reply_message(event)
    if error:
        return error
    if not getattr(replied, "sticker", False):
        return "❌ پیام ریپلای‌شده استیکر نیست."
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_photo_{uid}_"))
    try:
        src = await replied.download_media(file=str(tmp_dir))
        if not src:
            return "❌ دانلود استیکر ناموفق بود."
        animated = bool(getattr(replied, "gif", False) or _is_animated_image(src) or str(src).lower().endswith((".tgs", ".webm")))
        reply_to = replied.id if keep_reply else None
        if animated:
            out = tmp_dir / "sticker.gif"
            if not _animated_to_gif(src, out):
                return "❌ استیکر متحرک بود، اما تبدیل آن به GIF انجام نشد. برای TGS نصب python-lottie هم لازم است."
            await event.client.send_file(event.chat_id, str(out), force_document=False, reply_to=reply_to)
        else:
            from PIL import Image
            out = tmp_dir / "photo.png"
            with Image.open(src) as im:
                im.convert("RGBA").save(out, "PNG")
            await event.client.send_file(event.chat_id, str(out), force_document=False, reply_to=reply_to)
        return "✅ استیکر به تصویر تبدیل شد."
    except ImportError:
        return "❌ برای تبدیل استیکر به تصویر نصب Pillow لازم است."
    except Exception as exc:
        print(f"[SELF {uid}] sticker->photo failed: {exc}")
        return "❌ تبدیل استیکر به تصویر انجام نشد."
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def _self_save_replied_message(event, uid):
    """Save the replied message/media into Telegram Saved Messages."""
    if not event.is_reply:
        return "❌ روی پیام موردنظر ریپلای کن و سپس «.دانلود» را بفرست."
    replied = await event.get_reply_message()
    if not replied:
        return "❌ پیام ریپلای‌شده پیدا نشد."

    client = event.client
    try:
        await client.forward_messages("me", replied, from_peer=event.chat_id)
        return "✅ پیام با موفقیت به پیام‌های ذخیره‌شده ارسال شد."
    except Exception:
        pass

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_save_{uid}_"))
    try:
        if replied.media:
            path = await replied.download_media(file=str(tmp_dir))
            if not path:
                return "❌ این رسانه قابل دانلود نیست یا زمان آن تمام شده است."
            await client.send_file("me", path, caption=replied.raw_text or "")
        else:
            await client.send_message("me", replied.raw_text or "")
        return "✅ پیام به پیام‌های ذخیره‌شده منتقل شد."
    except Exception as exc:
        print(f"[SELF {uid}] save message failed: {exc}")
        return "❌ ذخیره پیام انجام نشد؛ ممکن است پیام محافظت‌شده یا منقضی‌شده باشد."
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _normalize_persian_transcript(text: str) -> str:
    """Conservative Persian cleanup after Whisper; never uses a cloud API."""
    if not text:
        return ""
    table = str.maketrans({
        "ي": "ی", "ى": "ی", "ك": "ک", "ۀ": "هٔ", "ة": "ه",
        "ؤ": "و", "إ": "ا", "أ": "ا", "ٱ": "ا",
        "٠": "۰", "١": "۱", "٢": "۲", "٣": "۳", "٤": "۴",
        "٥": "۵", "٦": "۶", "٧": "۷", "٨": "۸", "٩": "۹",
    })
    text = text.translate(table)
    text = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"([؟!،؛,:.])\1{1,}", r"\1", text)
    text = re.sub(r" +([،؛؟!:.])", r"\1", text)
    text = re.sub(r"([،؛؟!])(?=\S)", r"\1 ", text)
    return text.strip()


# ------------------------------------------------------------------ generic auto-installer
_PIP_STATE = {}


async def _ensure_pip_module(module, package, force=False, timeout=900):
    """Import `module`; if missing, pip-install `package` into THIS python.
    One install at a time per package, 5-minute cooldown after a failure."""
    import importlib

    def importable():
        importlib.invalidate_caches()
        try:
            importlib.import_module(module)
            return True
        except ImportError:
            sys.modules.pop(module, None)
            return False
        except Exception as exc:
            print(f"[PIP] importing {module} failed: {exc}")
            return False

    if importable():
        return True
    if os.getenv("AUTO_PIP_INSTALL", "1") == "0":
        return False
    st = _PIP_STATE.setdefault(package, {"lock": asyncio.Lock(), "failed_at": 0.0})
    async with st["lock"]:
        if importable():
            return True
        if not force and time.time() - st["failed_at"] < 300:
            return False
        base = [sys.executable, "-m", "pip", "install", "-U", "--disable-pip-version-check", "-q", *package.split()]
        for extra in ([], ["--user"], ["--break-system-packages"], ["--user", "--break-system-packages"]):
            try:
                proc = await asyncio.create_subprocess_exec(
                    *base, *extra, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                _, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[PIP] {package} install error ({' '.join(extra) or 'default'}): {exc}")
                continue
            if proc.returncode == 0:
                if "--user" in extra:
                    import site
                    with contextlib.suppress(Exception):
                        us = site.getusersitepackages()
                        if us and us not in sys.path:
                            sys.path.append(us)
                if importable():
                    print(f"[PIP] {package} installed automatically ✅")
                    return True
            else:
                print(f"[PIP] {package} failed ({' '.join(extra) or 'default'}): "
                      + err.decode("utf-8", "ignore").strip()[-300:])
        st["failed_at"] = time.time()
        return False


# ------------------------------------------------------------------ speech to text
# Default = Whisper large-v3-turbo (CTranslate2): near large-v3 accuracy for
# Persian but ~6x faster on CPU. Set WHISPER_MODEL to override (e.g. large-v3, medium).
_STT_MODEL_CANDIDATES = (
    [WHISPER_MODEL] if os.getenv("WHISPER_MODEL")
    else ["mobiuslabsgmbh/faster-whisper-large-v3-turbo", "large-v3-turbo", "medium", "small"]
)
_stt_model = {"obj": None, "name": None}
_stt_model_lock = None  # threading.Lock, created lazily
_stt_run_lock = None    # asyncio.Lock: one transcription at a time (CPU bound)
STT_MAX_SECONDS = float(os.getenv("STT_MAX_AUDIO_SECONDS", "1800"))


def _stt_bar(percent, cells=10):
    percent = max(0.0, min(100.0, float(percent)))
    full = int(round(percent / 100 * cells))
    return "▰" * full + "▱" * (cells - full) + f"  {int(percent)}٪"


def _stt_status_text(state):
    elapsed = int(time.monotonic() - state["started"])
    stage = state["stage"]
    if stage == "queue":
        return f"⏳ <b>در صف تبدیل…</b>\nیک ویس دیگر در حال پردازش است.\n\n⏱ {elapsed} ثانیه"
    if stage == "download":
        return f"📥 <b>دانلود ویس</b>\n{_stt_bar(state['percent'])}\n\n⏱ {elapsed} ثانیه"
    if stage == "model":
        note = "\n<i>بار اول مدل دانلود می‌شود و چند دقیقه طول می‌کشد؛ دفعه‌های بعد سریع است.</i>" if state.get("first_load") else ""
        return f"🧠 <b>آماده‌سازی موتور تشخیص گفتار…</b>{note}\n\n⏱ {elapsed} ثانیه"
    if stage == "transcribe":
        return f"✍️ <b>در حال تبدیل ویس به متن</b>\n{_stt_bar(state['percent'])}\n\n⏱ {elapsed} ثانیه"
    return f"⏳ در حال پردازش…\n\n⏱ {elapsed} ثانیه"


def _stt_get_model(state):
    """Load (once) the Whisper model; tries the candidates in order."""
    import threading
    global _stt_model_lock
    if _stt_model_lock is None:
        _stt_model_lock = threading.Lock()
    with _stt_model_lock:
        if _stt_model["obj"] is not None:
            return _stt_model["obj"]
        from faster_whisper import WhisperModel
        state["first_load"] = True
        last_exc = None
        for name in _STT_MODEL_CANDIDATES:
            try:
                model = WhisperModel(
                    name, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE,
                    cpu_threads=int(os.getenv("WHISPER_CPU_THREADS", "0")) or 0,
                    num_workers=1,
                )
                _stt_model.update(obj=model, name=name)
                print(f"[STT] model loaded: {name} ({WHISPER_DEVICE}/{WHISPER_COMPUTE_TYPE}) ✅")
                return model
            except Exception as exc:
                last_exc = exc
                print(f"[STT] could not load model {name}: {type(exc).__name__}: {exc}")
        raise RuntimeError(f"model_load_failed: {last_exc}")


def _stt_dedupe(text):
    """Remove Whisper's classic hallucination loops (same phrase repeated)."""
    words = text.split()
    for n in range(1, 8):
        i, out = 0, []
        while i < len(words):
            chunk = words[i:i + n]
            out.extend(chunk)
            j = i + n
            reps = 0
            while words[j:j + n] == chunk and len(chunk) == n:
                j += n
                reps += 1
            i = j if reps >= (3 if n == 1 else 2) else i + n
        words = out
    return " ".join(words)


def _stt_transcribe_sync(path, state):
    model = _stt_get_model(state)
    state["stage"] = "transcribe"
    state["percent"] = 0.0
    segments, info = model.transcribe(
        str(path), language=WHISPER_LANGUAGE or None, task="transcribe",
        beam_size=WHISPER_BEAM_SIZE, temperature=[0.0, 0.2, 0.4],
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 300},
        condition_on_previous_text=False,
        compression_ratio_threshold=2.4, log_prob_threshold=-1.0, no_speech_threshold=0.6,
        initial_prompt="متن فارسی محاوره‌ای با علائم نگارشی درست.",
    )
    duration = float(getattr(info, "duration", 0) or 0)
    pieces = []
    for seg in segments:
        if state.get("cancel"):
            raise RuntimeError("cancelled")
        part = _normalize_persian_transcript(getattr(seg, "text", "") or "")
        if part:
            pieces.append(part)
        if duration > 0:
            state["percent"] = min(99.0, float(getattr(seg, "end", 0) or 0) / duration * 100)
    state["percent"] = 100.0
    text = _normalize_persian_transcript(_stt_dedupe(" ".join(pieces)))
    return text, getattr(info, "language", None)


async def _stt_edit(event, text):
    try:
        await event.edit(premium_ui_text(text), parse_mode="html")
        return True
    except MessageNotModifiedError:
        return True
    except FloodWaitError as exc:
        print(f"[STT] edit flood-wait {getattr(exc, 'seconds', '?')}s (progress skipped)")
        return False
    except Exception as exc:
        print(f"[STT] edit failed: {type(exc).__name__}: {exc}")
        return False


async def _stt_deliver(event, uid, body_html):
    """Show the final result; never lose it (flood-wait / long text / deleted msg)."""
    chunks, cur = [], ""
    for line in body_html.split("\n"):
        while len(line) > 3500:
            chunks.append(cur + line[:3500]); cur = ""; line = line[3500:]
        if len(cur) + len(line) + 1 > 3500:
            chunks.append(cur); cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur)
    chunks = [c.strip() for c in chunks if c.strip()] or [body_html]
    for attempt in range(3):
        try:
            await event.edit(premium_ui_text(chunks[0]), parse_mode="html")
            break
        except MessageNotModifiedError:
            break
        except FloodWaitError as exc:
            await asyncio.sleep(min(int(getattr(exc, "seconds", 3)) + 1, 30))
        except Exception as exc:
            print(f"[SELF {uid}] STT final edit failed: {type(exc).__name__}: {exc}")
            with contextlib.suppress(Exception):
                await event.client.send_message(event.chat_id, premium_ui_text(chunks[0]), parse_mode="html",
                                                reply_to=getattr(event, "reply_to_msg_id", None))
            break
    else:
        with contextlib.suppress(Exception):
            await event.client.send_message(event.chat_id, premium_ui_text(chunks[0]), parse_mode="html")
    for extra in chunks[1:]:
        with contextlib.suppress(Exception):
            await event.client.send_message(event.chat_id, premium_ui_text(extra), parse_mode="html")


async def _self_transcribe_reply(event, uid):
    """Voice/audio/video-note -> Persian text with local faster-whisper.
    Returns the final HTML (or an error line). Progress is real, not fake."""
    global _stt_run_lock
    if not event.is_reply:
        return "❌ روی ویس یا فایل صوتی ریپلای کن و «.متن» را بفرست."
    replied = await event.get_reply_message()
    kind = _message_media_kind(replied) if replied else None
    if kind not in {"voice", "audio", "video"} and not getattr(replied, "video_note", None):
        return "❌ روی ویس، فایل صوتی یا ویدیو ریپلای کن."

    doc = getattr(replied, "document", None)
    dur = 0
    for attr in (getattr(doc, "attributes", None) or []):
        dur = max(dur, int(getattr(attr, "duration", 0) or 0))
    if dur and dur > STT_MAX_SECONDS:
        return f"❌ ویس خیلی طولانیه؛ حداکثر {int(STT_MAX_SECONDS // 60)} دقیقه."

    state = {"stage": "download", "percent": 0.0, "started": time.monotonic(), "cancel": False}
    stt_state[uid] = state

    async def progress_loop():
        last = None
        while True:
            txt = _stt_status_text(state)
            key = (state["stage"], int(state.get("percent", 0)) // 5, int(time.monotonic() - state["started"]) // 10)
            if key != last:
                if await _stt_edit(event, txt):
                    last = key
            await asyncio.sleep(3.0)

    progress_task = asyncio.create_task(progress_loop())
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_stt_{uid}_"))
    try:
        if not await _ensure_pip_module("faster_whisper", "faster-whisper"):
            return "❌ نصب خودکار موتور ویس‌به‌متن انجام نشد؛ دستی بزن: <code>pip install -U faster-whisper</code>"

        def dl_progress(cur, total):
            if total:
                state["percent"] = cur * 100.0 / total

        try:
            path = await asyncio.wait_for(
                replied.download_media(file=str(tmp_dir), progress_callback=dl_progress),
                timeout=float(os.getenv("STT_DOWNLOAD_TIMEOUT_SECONDS", "300")),
            )
        except asyncio.TimeoutError:
            return "❌ دانلود ویس بیش از حد طول کشید؛ دوباره تلاش کن."
        except Exception as exc:
            print(f"[SELF {uid}] STT download failed: {exc}")
            return "❌ دانلود ویس ناموفق بود."
        if not path:
            return "❌ دانلود ویس ناموفق بود."

        if _stt_run_lock is None:
            _stt_run_lock = asyncio.Lock()
        if _stt_run_lock.locked():
            state["stage"] = "queue"
        async with _stt_run_lock:
            state["stage"] = "model" if _stt_model["obj"] is None else "transcribe"
            state["percent"] = 0.0
            # Budget: model load (first time can include a download) + ~3x real time on CPU.
            budget = float(os.getenv("STT_TIMEOUT_SECONDS", "0")) or (
                (900 if _stt_model["obj"] is None else 0) + max(120.0, (dur or 60) * 4)
            )
            fut = asyncio.ensure_future(asyncio.to_thread(_stt_transcribe_sync, path, state))
            try:
                result, lang = await asyncio.wait_for(asyncio.shield(fut), timeout=budget)
            except asyncio.TimeoutError:
                state["cancel"] = True
                with contextlib.suppress(Exception):
                    await asyncio.wait_for(fut, timeout=30)
                return "❌ تبدیل ویس به متن بیش از حد طول کشید؛ سرور ضعیفه، WHISPER_MODEL=small رو امتحان کن."
            except Exception as exc:
                msg = str(exc)
                print(f"[SELF {uid}] local transcription failed: {type(exc).__name__}: {msg}")
                if "model_load_failed" in msg:
                    return ("❌ مدل تشخیص گفتار دانلود/بارگذاری نشد (اینترنت سرور به huggingface یا رم کافی رو چک کن).\n"
                            "برای سرور ضعیف: <code>WHISPER_MODEL=small</code>")
                if "Invalid data" in msg or "avcodec" in msg.casefold() or "decode" in msg.casefold():
                    return "❌ فایل صوتی خراب است یا قابل خواندن نیست."
                return "❌ موتور تبدیل ویس خطا داد؛ دوباره تلاش کن."

        if not result:
            return "❌ صحبتی در این ویس پیدا نشد."
        if lang and WHISPER_LANGUAGE and lang != WHISPER_LANGUAGE:
            print(f"[SELF {uid}] Whisper detected language={lang}, forced={WHISPER_LANGUAGE}")
        return f"📝 <b>متن ویس</b>\n\n{html.escape(result)}"
    except asyncio.CancelledError:
        state["cancel"] = True
        raise
    except Exception as exc:
        print(f"[SELF {uid}] transcription failed: {type(exc).__name__}: {exc}")
        return "❌ تبدیل ویس به متن انجام نشد؛ دوباره تلاش کن."
    finally:
        progress_task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await progress_task
        stt_state.pop(uid, None)
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def _self_ocr_reply(event, uid):
    """Image -> clean text. Tesseract (fas+eng, best models when available),
    multi-polarity preprocessing, per-line confidence filtering and merging."""
    if not event.is_reply:
        return "❌ روی تصویر ریپلای کن و «.OCR» را بفرست."
    replied = await event.get_reply_message()
    if not replied or not _ocr_is_image_message(replied):
        return "❌ روی یک عکس (یا فایل تصویری) ریپلای کن."

    size = _message_media_size(replied) if "_message_media_size" in globals() else 0
    if size and size > OCR_MAX_MB * 1024 * 1024:
        return f"❌ حجم تصویر بیشتر از {OCR_MAX_MB} مگابایته."

    if not await _ensure_pip_module("pytesseract", "pytesseract"):
        return "❌ نصب خودکار pytesseract انجام نشد؛ دستی بزن: <code>pip install -U pytesseract pillow</code>"
    try:
        import pytesseract
        from PIL import Image  # noqa: F401
    except ImportError:
        return "❌ قابلیت OCR نیاز به نصب <code>pytesseract</code> و <code>Pillow</code> دارد."

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    if not Path(TESSERACT_CMD).exists() and shutil.which(TESSERACT_CMD) is None:
        return "❌ موتور OCR روی سرور نصب نیست؛ روی سرور بزن: <code>apt install -y tesseract-ocr tesseract-ocr-fas</code>"

    with contextlib.suppress(Exception):
        await event.edit(premium_ui_text("🔎 <b>در حال خواندن متن تصویر…</b>"), parse_mode="html")

    try:
        tess_dir, langs = await _ocr_prepare_languages()
    except Exception as exc:
        print(f"[SELF {uid}] OCR language probe failed: {exc}")
        return "❌ Tesseract روی سرور قابل اجرا نیست."
    if not langs:
        return f"❌ فایل زبان OCR نصب نیست ({TESSERACT_LANG}); روی سرور بزن: <code>apt install -y tesseract-ocr-fas</code>"

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_ocr_{uid}_"))
    try:
        try:
            path = await asyncio.wait_for(replied.download_media(file=str(tmp_dir)), timeout=120)
        except Exception as exc:
            print(f"[SELF {uid}] OCR download failed: {exc}")
            path = None
        if not path:
            return "❌ دانلود تصویر ناموفق بود."

        try:
            result = await asyncio.wait_for(
                _ocr_run(str(path), langs, tess_dir),
                timeout=float(os.getenv("OCR_TIMEOUT_SECONDS", "180")),
            )
        except asyncio.TimeoutError:
            return "❌ خواندن متن بیش از حد طول کشید؛ تصویر کوچک‌تر یا واضح‌تر بفرست."
        missing = [l for l in TESSERACT_LANG.split("+") if l and l not in langs]
        note = ""
        if missing:
            note = ("\n\n⚠️ زبان " + html.escape("+".join(missing)) + " روی سرور نصب نیست؛ "
                    "بزن: <code>apt install -y tesseract-ocr-fas</code>")
        if result:
            return f"🔎 <b>متن تصویر:</b>\n\n{html.escape(result)}{note}"
        return "❌ متنی در تصویر پیدا نشد." + note
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[SELF {uid}] OCR failed: {type(exc).__name__}: {exc}")
        text = str(exc).casefold()
        if "tesseractnotfound" in text or "no such file" in text:
            return "❌ موتور OCR روی سرور نصب یا قابل اجرا نیست؛ Tesseract را نصب کن."
        if "failed loading language" in text or "couldn't load any languages" in text:
            return f"❌ فایل زبان OCR نصب نیست: {html.escape('+'.join(langs))}"
        if "cannot identify image" in text:
            return "❌ این فایل تصویر قابل خواندن نیست."
        return "❌ OCR انجام نشد؛ دوباره تلاش کن."
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ------------------------------------------------------------------ OCR core
OCR_MAX_MB = int(os.getenv("OCR_MAX_MB", "20"))
OCR_BEST_DIR = Path(os.getenv("OCR_TESSDATA_DIR", "") or (Path(__file__).resolve().parent / "tessdata_best"))
OCR_BEST_URL = "https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
OCR_AUTO_DOWNLOAD = os.getenv("OCR_AUTO_DOWNLOAD", "1") != "0"
_OCR_DL_LOCK = None
_OCR_DL_FAILED_AT = 0.0


def _ocr_is_image_message(msg):
    if getattr(msg, "photo", None):
        return True
    doc = getattr(msg, "document", None)
    if not doc:
        return False
    mime = (getattr(doc, "mime_type", None) or "").casefold()
    if mime in {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff", "image/jpg"}:
        return True
    return False


def _ocr_download_best_sync(langs):
    """Fetch tessdata_best models (much more accurate than the apt 'fast' ones)."""
    OCR_BEST_DIR.mkdir(parents=True, exist_ok=True)
    for lang in langs:
        dst = OCR_BEST_DIR / f"{lang}.traineddata"
        if dst.exists() and dst.stat().st_size > 1_000_000:
            continue
        tmp = dst.with_suffix(".part")
        req = urllib.request.Request(OCR_BEST_URL.format(lang=lang), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as fh:
            shutil.copyfileobj(resp, fh, 1 << 16)
        if tmp.stat().st_size < 1_000_000:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"bad download for {lang}")
        os.replace(tmp, dst)
        print(f"[OCR] downloaded best model: {lang} ✅")


async def _ocr_ensure_best_models(force=False):
    global _OCR_DL_LOCK, _OCR_DL_FAILED_AT
    wanted = [x for x in TESSERACT_LANG.split("+") if x]
    if all((OCR_BEST_DIR / f"{l}.traineddata").exists() for l in wanted):
        return True
    if not OCR_AUTO_DOWNLOAD:
        return False
    if _OCR_DL_LOCK is None:
        _OCR_DL_LOCK = asyncio.Lock()
    async with _OCR_DL_LOCK:
        if all((OCR_BEST_DIR / f"{l}.traineddata").exists() for l in wanted):
            return True
        if not force and time.time() - _OCR_DL_FAILED_AT < 600:
            return False
        try:
            await asyncio.to_thread(_ocr_download_best_sync, wanted)
            return True
        except Exception as exc:
            _OCR_DL_FAILED_AT = time.time()
            print(f"[OCR] best-model download failed ({exc}); using system tessdata")
            return False


def _ocr_langs_in(tess_dir):
    import pytesseract
    config = f'--tessdata-dir "{tess_dir}"' if tess_dir else ""
    return set(pytesseract.get_languages(config=config))


async def _ocr_prepare_languages():
    """-> (tessdata_dir or None, [langs to use]). Prefers tessdata_best."""
    wanted = [x for x in TESSERACT_LANG.split("+") if x]
    await _ocr_ensure_best_models()
    best = set()
    if OCR_BEST_DIR.exists():
        with contextlib.suppress(Exception):
            best = await asyncio.to_thread(_ocr_langs_in, str(OCR_BEST_DIR))
    if best and all(l in best for l in wanted):
        return str(OCR_BEST_DIR), wanted
    system = await asyncio.to_thread(_ocr_langs_in, None)
    usable = [l for l in wanted if l in system]
    if len(usable) < len(wanted):
        print(f"[OCR] missing languages: {sorted(set(wanted) - set(usable))}")
    return None, usable


def _ocr_variants(path):
    """Return a list of (name, PIL image, psm) passes over the same geometry."""
    from PIL import Image, ImageOps, ImageFilter
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    gray = im.convert("L")

    # Scale so glyphs land around Tesseract's sweet spot (~30px x-height).
    long_side = max(gray.size)
    target = 2400
    scale = max(0.5, min(4.0, target / float(long_side)))
    if abs(scale - 1.0) > 0.05:
        gray = gray.resize((max(1, int(gray.width * scale)), max(1, int(gray.height * scale))), Image.Resampling.LANCZOS)

    try:
        import numpy as np
    except ImportError:
        np = None

    def normalize(img):
        # Flatten uneven lighting / gradients: divide by a heavy blur of the background.
        radius = max(12, int(max(img.size) / 45))
        if np is None:
            return ImageOps.autocontrast(img, cutoff=1)
        a = np.asarray(img, dtype=np.float32)
        bg = np.asarray(img.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)
        out = np.clip(a / np.maximum(bg, 1.0) * 255.0, 0, 255).astype(np.uint8)
        return ImageOps.autocontrast(Image.fromarray(out), cutoff=1)

    def sauvola(img, window=41, k=0.25):
        if np is None:
            hist = img.histogram()
            total = sum(hist); sum_all = sum(i * h for i, h in enumerate(hist))
            w_b = s_b = 0; best = (0, 128)
            for t in range(256):
                w_b += hist[t]
                if w_b == 0 or w_b == total:
                    continue
                s_b += t * hist[t]
                m_b = s_b / w_b; m_f = (sum_all - s_b) / (total - w_b)
                var = w_b * (total - w_b) * (m_b - m_f) ** 2
                if var > best[0]:
                    best = (var, t)
            return img.point(lambda p, t=best[1]: 255 if p > t else 0)
        a = np.asarray(img, dtype=np.float64)
        pad = window // 2
        p = np.pad(a, pad + 1, mode="reflect")
        ii = p.cumsum(0).cumsum(1)
        ii2 = (p * p).cumsum(0).cumsum(1)
        h, w = a.shape
        def box(s):
            return s[window:window + h, window:window + w] - s[0:h, window:window + w] - s[window:window + h, 0:w] + s[0:h, 0:w]
        n = float(window * window)
        mean = box(ii) / n
        std = np.sqrt(np.maximum(box(ii2) / n - mean * mean, 0))
        thresh = mean * (1 + k * (std / 128.0 - 1))
        return Image.fromarray(np.where(a > thresh, 255, 0).astype(np.uint8))

    def pad(img):
        return ImageOps.expand(img, border=24, fill=255)

    dark_on_light = normalize(gray)
    light_on_dark = normalize(ImageOps.invert(gray))
    variants = [
        ("norm", pad(dark_on_light), 6),
        ("inv", pad(light_on_dark), 6),
        ("norm_bin", pad(sauvola(dark_on_light)), 6),
        ("inv_bin", pad(sauvola(light_on_dark)), 6),
        ("norm_sparse", pad(dark_on_light), 11),
        ("inv_sparse", pad(light_on_dark), 11),
    ]
    return variants


_OCR_ALNUM_RE = re.compile(r"[0-9A-Za-z\u0600-\u06FF\u06F0-\u06F9]")


def _ocr_lines_from_data(data, name):
    """Group Tesseract words into lines with bbox + confidence; drop junk words."""
    groups = {}
    n = len(data.get("text", []))
    for i in range(n):
        word = (data["text"][i] or "").strip()
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = -1
        if not word or conf < 0:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        g = groups.setdefault(key, {"words": [], "confs": [], "box": [10**9, 10**9, 0, 0], "order": i})
        # Words that are pure symbols or very low confidence are OCR noise.
        if conf < 40 or not _OCR_ALNUM_RE.search(word):
            if not (conf >= 75 and word in {":", "-", "/", "!", "؟", "?", ".", "،", "%", "+", "=", "@", "#"}):
                continue
        g["words"].append(word)
        g["confs"].append((conf, len(word)))
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        b = g["box"]
        b[0] = min(b[0], x); b[1] = min(b[1], y); b[2] = max(b[2], x + w); b[3] = max(b[3], y + h)
    lines = []
    for g in groups.values():
        items = list(zip(g["words"], [c for c, _ in g["confs"]]))

        def alnum_len(w):
            return len(_OCR_ALNUM_RE.findall(w))

        def junk(w, c):
            n = alnum_len(w)
            if n <= 2 and c < 92:
                return True
            core = _OCR_ALNUM_RE.findall(w)
            if len(core) >= 3 and len(set(core)) == 1 and c < 90:
                return True  # «0000», «1111» — texture read as digits
            return False

        # Trim junk tokens hanging off either end of the line.
        while items and junk(*items[0]):
            items.pop(0)
        while items and junk(*items[-1]):
            items.pop()
        if not items:
            continue
        text = " ".join(w for w, _ in items)
        weights = [(c, max(1, alnum_len(w))) for w, c in items]
        chars = sum(n for _, n in weights)
        conf = sum(c * n for c, n in weights) / max(1, chars)
        useful = len(_OCR_ALNUM_RE.findall(text))
        real = sum(alnum_len(w) for w, _ in items if alnum_len(w) >= 3)
        if real == 0 or real / max(1, useful) < 0.6:
            continue  # mostly 1-2 char fragments = background noise
        if conf < 55 or (useful <= 4 and conf < 80):
            continue
        lines.append({"text": text, "conf": conf, "chars": useful, "box": tuple(g["box"]), "src": name})
    return lines


def _ocr_overlap(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    if not inter:
        return 0.0
    area = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])) or 1
    return inter / area


def _ocr_merge(all_lines):
    """Greedy: best-quality lines first, skip anything overlapping an accepted line."""
    import math
    ranked = sorted(all_lines, key=lambda l: l["conf"] * math.sqrt(l["chars"]), reverse=True)
    chosen = []
    for line in ranked:
        if any(_ocr_overlap(line["box"], c["box"]) > 0.35 for c in chosen):
            continue
        chosen.append(line)
    # Reading order: top-to-bottom; same row -> right-to-left for Persian, else left-to-right.
    def row_key(l):
        return (l["box"][1] + l["box"][3]) / 2
    chosen.sort(key=row_key)
    rows = []
    for l in chosen:
        h = l["box"][3] - l["box"][1]
        if rows and abs(row_key(l) - row_key(rows[-1][-1])) < h * 0.5:
            rows[-1].append(l)
        else:
            rows.append([l])
    out = []
    for row in rows:
        rtl = sum(1 for l in row for ch in l["text"] if "\u0600" <= ch <= "\u06ff") > sum(1 for l in row for ch in l["text"] if ch.isascii() and ch.isalpha())
        row.sort(key=lambda l: l["box"][0], reverse=rtl)
        out.append("   ".join(l["text"] for l in row))
    return "\n".join(out)


def _ocr_clean(text, langs):
    if not text:
        return ""
    text = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]", "", text)
    if "fas" in langs:
        text = text.translate(str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"}))
    text = re.sub(r"[ \t]{2,}", "  ", text)
    text = re.sub(r" +([،؛؟!:.,])", r"\1", text)
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()


def _ocr_pass(image, psm, langs, tess_dir, name):
    import pytesseract
    config = f"--oem 1 --psm {psm} -c preserve_interword_spaces=1"
    if tess_dir:
        config = f'--tessdata-dir "{tess_dir}" ' + config
    data = pytesseract.image_to_data(
        image, lang="+".join(langs), config=config,
        output_type=pytesseract.Output.DICT, timeout=90,
    )
    return _ocr_lines_from_data(data, name)


async def _ocr_run(path, langs, tess_dir=None):
    variants = await asyncio.to_thread(_ocr_variants, path)
    # One thread per Tesseract process; run passes side by side.
    os.environ.setdefault("OMP_THREAD_LIMIT", "1")
    sem = asyncio.Semaphore(max(1, min(len(variants), (os.cpu_count() or 2))))

    async def one(name, img, psm):
        async with sem:
            try:
                return await asyncio.to_thread(_ocr_pass, img, psm, langs, tess_dir, name)
            except Exception as exc:
                print(f"[OCR] pass {name}/psm{psm} failed: {exc}")
                if "language" in str(exc).casefold():
                    raise
                return []

    results = await asyncio.gather(*(one(n, i, p) for n, i, p in variants))
    all_lines = [l for r in results for l in r]
    return _ocr_clean(_ocr_merge(all_lines), langs)


async def _self_create_chat_or_channel(event, uid, kind, title):
    """Create a Telegram supergroup or channel."""
    title = re.sub(r"\s+", " ", title or "").strip()
    if not title:
        return f"❌ اسم {kind} را وارد کن."

    try:
        from telethon.tl import functions
        result = await event.client(functions.channels.CreateChannelRequest(
            title=title,
            about="ساخته‌شده توسط HusteRIX Self",
            broadcast=(kind == "چنل"),
            megagroup=(kind == "گروه"),
        ))
        created = getattr(result, "chats", None) or []
        if created:
            username = getattr(created[0], "username", None)
            extra = f"\n🔗 @{username}" if username else ""
            return f"✅ {kind} «{title}» ساخته شد.{extra}"
        return f"✅ {kind} «{title}» ساخته شد."
    except Exception as exc:
        print(f"[SELF {uid}] create {kind} failed: {exc}")
        return f"❌ ساخت {kind} ناموفق بود.\n{exc}"


async def _delete_dice_message(client, chat_id, message_id):
    """Delete an unsuccessful dice result reliably in Saved Messages and private chats."""
    message_id = int(message_id)

    # First use Telethon's peer-aware helper. This is important for normal
    # private dialogs where Telegram can apply different revoke semantics.
    try:
        await _tg_call_with_flood_retry(
            lambda: client.delete_messages(chat_id, [message_id], revoke=True),
            label="delete failed dice (peer-aware)",
        )
        return True
    except Exception as first_exc:
        print(f"[DICE] peer-aware delete failed chat={chat_id} message={message_id}: {first_exc}")

    # Raw API fallback for Saved Messages and peers where the convenience
    # wrapper cannot resolve the dialog in time.
    try:
        from telethon.tl.functions.messages import DeleteMessagesRequest
        await _tg_call_with_flood_retry(
            lambda: client(DeleteMessagesRequest(
                id=[message_id],
                revoke=True,
            )),
            label="delete failed dice",
        )
        return True
    except Exception as exc:
        print(f"[DICE] raw delete failed chat={chat_id} message={message_id}: {exc}")
        return False


async def _self_roll_guaranteed_value(event, uid, target):
    """Send a real Telegram dice and reroll until Telegram returns the requested value."""
    try:
        from telethon.tl import types

        target = int(target)
        if target < 1 or target > 6:
            return False

        for _ in range(60):
            msg = await _tg_call_with_flood_retry(
                lambda: event.client.send_file(
                    event.chat_id,
                    types.InputMediaDice("🎲"),
                ),
                label="dice roll",
            )

            value = getattr(getattr(msg, "media", None), "value", None)
            if value == target:
                return True

            # Failed results must never remain visible.  Use the raw Telegram
            # DeleteMessagesRequest as the primary path; it is more reliable
            # than the convenience wrapper for private dialogs/Saved Messages.
            await _delete_dice_message(event.client, event.chat_id, msg.id)
            await asyncio.sleep(0.15)

        return False
    except Exception as exc:
        print(f"[SELF {uid}] forced dice {target} failed: {exc}")
        return False


# Backward-compatible alias for any existing internal references.
async def _self_roll_guaranteed_six(event, uid):
    return await _self_roll_guaranteed_value(event, uid, 6)
























# ============================================================
# MEDIA CONVERSION (SELF)
# ============================================================

MEDIA_CONVERT_MAX_MB = int(os.getenv("MEDIA_CONVERT_MAX_MB", "2048"))
MEDIA_CONVERT_PROGRESS_INTERVAL = float(os.getenv("MEDIA_CONVERT_PROGRESS_INTERVAL", "0.8"))

# Resolve media binaries once per process.  Servers often install ffmpeg/ffprobe
# outside the Python virtualenv, so relying only on a shell PATH is fragile.
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "").strip() or shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "").strip() or shutil.which("ffprobe") or "/usr/bin/ffprobe"

# Tesseract itself is a native binary; pytesseract is only its Python wrapper.
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip() or shutil.which("tesseract") or "/usr/bin/tesseract"
TESSERACT_LANG = os.getenv("TESSERACT_LANG", "fas+eng")


def _media_conversion_commands():
    # کاربر فقط از دستورات فارسی استفاده می‌کند.
    return {
        "voice_to_mp3": {"ویس به mp3"},
        "mp3_to_voice": {"mp3 به ویس"},
        "video_to_voice": {"ویدیو به ویس"},
        "video_to_mp3": {"ویدیو به mp3"},
    }


def _media_conversion_command(text: str):
    low = (text or "").strip().casefold()
    for operation, aliases in _media_conversion_commands().items():
        if low in {x.casefold() for x in aliases}:
            return operation
    return None


def _message_media_kind(message):
    """Detect Telegram media using Message fields, MIME type and document attributes."""
    if not message:
        return None
    if getattr(message, "voice", None):
        return "voice"
    if getattr(message, "video", None):
        return "video"
    if getattr(message, "audio", None):
        return "audio"

    document = getattr(message, "document", None)
    if not document:
        return None

    mime = (getattr(document, "mime_type", None) or "").casefold()
    attrs = getattr(document, "attributes", None) or []
    has_video_attr = False
    has_audio_attr = False
    audio_is_voice = False
    for attr in attrs:
        name = type(attr).__name__.casefold()
        if "video" in name:
            has_video_attr = True
        if "audio" in name:
            has_audio_attr = True
            audio_is_voice = bool(getattr(attr, "voice", False))

    if audio_is_voice:
        return "voice"
    if has_video_attr or mime.startswith("video/"):
        return "video"
    if has_audio_attr or mime.startswith("audio/"):
        return "audio"
    return None


def _message_is_mp3(message):
    """Accept real MP3 audio even when Telegram did not preserve a filename."""
    if _message_media_kind(message) != "audio":
        return False
    document = getattr(message, "document", None)
    mime = (getattr(document, "mime_type", None) or "").casefold()
    if mime in {"audio/mpeg", "audio/mp3", "audio/x-mp3"}:
        return True
    names = []
    file_obj = getattr(message, "file", None)
    if file_obj is not None:
        names.append(getattr(file_obj, "name", None))
    for attr in getattr(document, "attributes", None) or []:
        if type(attr).__name__.casefold().endswith("filename"):
            names.append(getattr(attr, "file_name", None))
    return any(str(name or "").casefold().endswith(".mp3") for name in names)


def _message_media_size(message):
    media = getattr(message, "media", None)
    document = getattr(message, "document", None) or getattr(media, "document", None)
    try:
        return int(getattr(document, "size", 0) or 0)
    except Exception:
        return 0


def _media_progress_text(percent, operation):
    labels = {
        "voice_to_mp3": "🎵 تبدیل ویس به MP3",
        "mp3_to_voice": "🎵 تبدیل MP3 به ویس",
        "video_to_voice": "🎬 ➜ 🎙️ تبدیل ویدیو به ویس",
        "video_to_mp3": "🎬 ➜ 🎵 تبدیل ویدیو به MP3",
    }
    percent = max(0, min(100, int(percent)))
    slots = 16
    filled = round(slots * percent / 100)
    bar = "█" * filled + "░" * (slots - filled)
    return f"{labels.get(operation, '🎵 در حال تبدیل فایل')}\n\n🔄 در حال پردازش...\n\n<code>{bar}</code> {percent}%"


def _media_error_message(exc):
    text = str(exc or "").casefold()
    if "ffmpeg_not_found" in text or "ffprobe_not_found" in text:
        return "❌ موتور تبدیل رسانه روی سرور فعال نیست."
    if "download_failed" in text:
        return "❌ دانلود فایل شکست خورد."
    if "timeout" in text:
        return "❌ زمان پردازش فایل به پایان رسید."
    if "no_audio_track" in text:
        return "❌ فایل صوتی قابل استخراج از این ویدیو پیدا نشد."
    if "invalid_media" in text or "invalid data" in text or "could not find codec" in text:
        return "❌ فایل خراب است یا فرمت آن معتبر نیست."
    if "floodwait" in text:
        return "❌ ارسال فایل به‌دلیل محدودیت تلگرام موقتاً متوقف شد."
    if "file_too_large" in text:
        return f"❌ فایل بیش از حد بزرگ است. حداکثر حجم مجاز تبدیل: {MEDIA_CONVERT_MAX_MB:,} مگابایت."
    if "send_failed" in text:
        return "❌ خطای ارسال فایل رخ داد."
    if "ffmpeg_failed" in text:
        return "❌ تبدیل ناموفق بود."
    return "❌ تبدیل انجام نشد.\nدلیل: خطای پردازش فایل رسانه‌ای."


def _media_binary_path(binary):
    if binary == "ffmpeg":
        return FFMPEG_BIN
    if binary == "ffprobe":
        return FFPROBE_BIN
    return shutil.which(binary) or binary


async def _media_binary_exists(binary):
    path = _media_binary_path(binary)
    try:
        proc = await asyncio.create_subprocess_exec(
            path, "-version",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.communicate()
        return proc.returncode == 0
    except (FileNotFoundError, OSError):
        return False


async def _ffprobe_duration(path):
    if not await _media_binary_exists("ffprobe"):
        raise RuntimeError("ffprobe_not_found")
    proc = await asyncio.create_subprocess_exec(
        _media_binary_path("ffprobe"), "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode("utf-8", errors="ignore")
        if "Invalid data" in err or "could not find codec" in err:
            raise RuntimeError("invalid_media")
        raise RuntimeError("ffprobe_failed")
    try:
        duration = float(stdout.decode().strip())
        if duration <= 0:
            raise ValueError
        return duration
    except Exception:
        raise RuntimeError("invalid_media")


async def _ffprobe_has_audio(path):
    if not await _media_binary_exists("ffprobe"):
        raise RuntimeError("ffprobe_not_found")
    proc = await asyncio.create_subprocess_exec(
        _media_binary_path("ffprobe"), "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return proc.returncode == 0 and bool(stdout.decode("utf-8", errors="ignore").strip())


async def _ffmpeg_convert_with_progress(input_path, output_path, operation, duration, progress_cb):
    if not await _media_binary_exists("ffmpeg"):
        raise RuntimeError("ffmpeg_not_found")

    if operation in {"voice_to_mp3", "video_to_mp3"}:
        args = [
            _media_binary_path("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(input_path), "-vn", "-map", "0:a:0?",
            "-c:a", "libmp3lame", "-b:a", "192k", "-map_metadata", "-1",
            "-progress", "pipe:1", "-nostats", str(output_path),
        ]
    else:
        # Telegram voice notes are Opus in an OGG container. Strip metadata
        # and video completely; -map 0:a:0? makes missing audio a hard error below.
        args = [
            _media_binary_path("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(input_path), "-vn", "-map", "0:a:0?",
            "-c:a", "libopus", "-b:a", "48k", "-vbr", "on",
            "-application", "voip", "-map_metadata", "-1",
            "-progress", "pipe:1", "-nostats", str(output_path),
        ]

    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    last_ui = 0.0
    last_percent = -1
    stderr_task = asyncio.create_task(proc.stderr.read())
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            raw = line.decode("utf-8", errors="ignore").strip()
            if not raw.startswith("out_time_ms="):
                continue
            try:
                out_us = int(raw.split("=", 1)[1])
                percent = int(max(0.0, min(100.0, (out_us / 1_000_000.0) / duration * 100.0)))
            except (ValueError, ZeroDivisionError):
                continue
            now = time.monotonic()
            if percent != last_percent and (now - last_ui) >= MEDIA_CONVERT_PROGRESS_INTERVAL:
                await progress_cb(percent)
                last_ui = now
                last_percent = percent

        await proc.wait()
        stderr = (await stderr_task).decode("utf-8", errors="ignore")
    except asyncio.CancelledError:
        with contextlib.suppress(ProcessLookupError):
            proc.kill()
        with contextlib.suppress(Exception):
            await proc.wait()
        raise
    if proc.returncode != 0:
        low_err = stderr.casefold()
        if "stream map '0:a:0?' matches no streams" in low_err or "matches no streams" in low_err:
            raise RuntimeError("no_audio_track")
        if "invalid data" in low_err or "could not find codec" in low_err:
            raise RuntimeError("invalid_media")
        raise RuntimeError("ffmpeg_failed")
    if not Path(output_path).exists() or Path(output_path).stat().st_size <= 0:
        raise RuntimeError("ffmpeg_failed")
    await progress_cb(100, force=True)


async def _self_media_convert(event, uid, operation):
    if not event.is_reply:
        return "❌ ابتدا روی فایل موردنظر ریپلای کن."

    replied = await event.get_reply_message()
    if not replied:
        return "❌ فایل رسانه‌ای قابل تبدیل پیدا نشد."

    kind = _message_media_kind(replied)
    requirements = {
        "voice_to_mp3": {"voice"},
        "mp3_to_voice": {"audio"},
        "video_to_voice": {"video"},
        "video_to_mp3": {"video"},
    }
    if kind not in requirements.get(operation, set()):
        if operation == "voice_to_mp3":
            return "❌ این فایل برای تبدیل به MP3 مناسب نیست."
        if operation == "mp3_to_voice":
            return "❌ این فایل MP3/Audio برای تبدیل به ویس مناسب نیست."
        return "❌ این فایل برای تبدیل ویدیو به صدا مناسب نیست."

    if operation == "mp3_to_voice" and not _message_is_mp3(replied):
        return "❌ این فایل MP3 نیست و برای این تبدیل مناسب نیست."

    size = _message_media_size(replied)
    if size and size > MEDIA_CONVERT_MAX_MB * 1024 * 1024:
        raise RuntimeError("file_too_large")

    if uid in media_convert_state:
        return "⏳ یک تبدیل رسانه‌ای همین حالا در حال انجام است."

    state = {"status": "processing", "operation": operation, "message_id": int(event.id), "started": time.time()}
    media_convert_state[uid] = state
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_media_{uid}_"))
    input_path = None
    output_path = None

    async def progress_cb(percent, force=False):
        now = time.monotonic()
        if not force and now - state.get("last_ui", 0.0) < MEDIA_CONVERT_PROGRESS_INTERVAL:
            return
        state["last_ui"] = now
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(_media_progress_text(percent, operation)), parse_mode="html", buttons=None)

    try:
        if not await _media_binary_exists("ffmpeg") or not await _media_binary_exists("ffprobe"):
            raise RuntimeError("ffmpeg_not_found")

        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(_media_progress_text(0, operation)), parse_mode="html", buttons=None)

        try:
            input_path = await replied.download_media(file=str(tmp_dir))
        except Exception as exc:
            raise RuntimeError("download_failed") from exc
        if not input_path:
            raise RuntimeError("download_failed")
        input_path = Path(input_path)

        duration = await _ffprobe_duration(input_path)
        if not await _ffprobe_has_audio(input_path):
            raise RuntimeError("no_audio_track")
        suffix = ".mp3" if operation in {"voice_to_mp3", "video_to_mp3"} else ".ogg"
        output_path = tmp_dir / f"converted{suffix}"
        await _ffmpeg_convert_with_progress(input_path, output_path, operation, duration, progress_cb)

        try:
            if operation in {"voice_to_mp3", "video_to_mp3"}:
                # Send as Telegram audio, not as a generic document.  The old
                # force_document=True made Telegram show the .mp3 like an
                # installation/file attachment without the in-app audio player.
                audio_attributes = [
                    types.DocumentAttributeAudio(
                        duration=max(1, int(round(duration))),
                        voice=False,
                    )
                ]
                await event.client.send_file(
                    event.chat_id,
                    str(output_path),
                    caption="🎵 فایل MP3 آماده است.",
                    force_document=False,
                    mime_type="audio/mpeg",
                    attributes=audio_attributes,
                    supports_streaming=True,
                )
            else:
                # Telethon's voice_note=True sends this as a Telegram Voice Message,
                # not as a document merely carrying an .ogg filename.
                await event.client.send_file(
                    event.chat_id, str(output_path),
                    voice_note=True,
                )
        except FloodWaitError as exc:
            raise RuntimeError("floodwait") from exc
        except Exception as exc:
            raise RuntimeError("send_failed") from exc

        return "__SUCCESS__"
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[SELF {uid}] media conversion {operation} failed: {exc}")
        return _media_error_message(exc)
    finally:
        media_convert_state.pop(uid, None)
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ============================================================
# ساخت ویدیو گرد (SELF)  —  «.ویدیو مسیج» + ریپلی روی ویدیو
# ============================================================
# Reply to any video with «.ویدیو مسیج»: the video is centre-cropped to a
# square, scaled to 384×384 (Telegram's video-message size), cut to the
# 60 s Telegram allows and sent to the same chat as a round video message.

HTX_VIDEO_NOTE_SIZE = 384
HTX_VIDEO_NOTE_MAX_SEC = 60
_HTX_VIDEO_NOTE_RE = re.compile(
    r"\.\s*وید(?:ی|ئ)و[\u200c\s]*مسیج(?:\s*\+?\s*ری\u200c?پل(?:ی|ای)?)?"
)


def _htx_video_note_progress(percent):
    percent = max(0, min(100, int(percent)))
    slots = 16
    filled = round(slots * percent / 100)
    bar = "█" * filled + "░" * (slots - filled)
    return _htx_reply("ویدیو مسیج", "🔄 در حال ساخت ویدیو گرد...", f"<code>{bar}</code> {percent}%")


def _htx_video_note_error(exc):
    low = str(exc or "").casefold()
    if "no_video_track" in low:
        return "❌ این فایل تصویر ندارد و برای ویدیو گرد مناسب نیست."
    if "send_failed" in low:
        return "❌ ارسال ویدیو گرد ناموفق بود."
    if "ffmpeg_failed" in low:
        return "❌ ساخت ویدیو گرد ناموفق بود."
    return _media_error_message(exc)


async def _ffmpeg_video_note(input_path, output_path, limit, progress_cb):
    """Square-crop + 384x384 + H.264/AAC mp4, at most HTX_VIDEO_NOTE_MAX_SEC."""
    if not await _media_binary_exists("ffmpeg"):
        raise RuntimeError("ffmpeg_not_found")
    size = HTX_VIDEO_NOTE_SIZE
    vf = f"crop='min(iw,ih)':'min(iw,ih)',scale={size}:{size}:flags=lanczos,setsar=1,format=yuv420p"
    args = [
        _media_binary_path("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(input_path), "-t", str(HTX_VIDEO_NOTE_MAX_SEC),
        "-map", "0:v:0", "-map", "0:a:0?", "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-profile:v", "main",
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart", "-map_metadata", "-1",
        "-progress", "pipe:1", "-nostats", str(output_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    last_percent = -1
    stderr_task = asyncio.create_task(proc.stderr.read())
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            raw = line.decode("utf-8", errors="ignore").strip()
            if not raw.startswith("out_time_ms="):
                continue
            try:
                out_us = int(raw.split("=", 1)[1])
                percent = int(max(0.0, min(100.0, (out_us / 1_000_000.0) / max(limit, 0.1) * 100.0)))
            except (ValueError, ZeroDivisionError):
                continue
            if percent != last_percent:
                await progress_cb(percent)
                last_percent = percent
        await proc.wait()
        stderr = (await stderr_task).decode("utf-8", errors="ignore")
    except asyncio.CancelledError:
        with contextlib.suppress(ProcessLookupError):
            proc.kill()
        with contextlib.suppress(Exception):
            await proc.wait()
        raise
    if proc.returncode != 0:
        low_err = stderr.casefold()
        if "matches no streams" in low_err:
            raise RuntimeError("no_video_track")
        if "invalid data" in low_err or "could not find codec" in low_err:
            raise RuntimeError("invalid_media")
        raise RuntimeError("ffmpeg_failed")
    if not Path(output_path).exists() or Path(output_path).stat().st_size <= 0:
        raise RuntimeError("ffmpeg_failed")


async def _handle_htx_video_note_command(event, uid, text):
    """«.ویدیو مسیج» (reply on a video). Returns True when handled."""
    norm = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]", "", text or "").strip()
    norm = norm.replace("ي", "ی").replace("ك", "ک")
    if not _HTX_VIDEO_NOTE_RE.fullmatch(norm):
        return False

    if not event.is_reply:
        await _htx_edit(event, _htx_reply("ویدیو مسیج", "❌ روی یک ویدیو ریپلای کن و «.ویدیو مسیج» را بفرست."))
        return True
    replied = await event.get_reply_message()
    if not replied or _message_media_kind(replied) != "video":
        await _htx_edit(event, _htx_reply("ویدیو مسیج", "❌ پیامی که ریپلای کردی ویدیو نیست."))
        return True
    size = _message_media_size(replied)
    if size and size > MEDIA_CONVERT_MAX_MB * 1024 * 1024:
        await _htx_edit(event, _htx_reply("ویدیو مسیج", _media_error_message(RuntimeError("file_too_large"))))
        return True
    if uid in media_convert_state:
        await _htx_edit(event, _htx_reply("ویدیو مسیج", "⏳ یک تبدیل رسانه‌ای همین حالا در حال انجام است."))
        return True

    state = {"status": "processing", "operation": "video_note", "message_id": int(event.id), "started": time.time()}
    media_convert_state[uid] = state
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_vnote_{uid}_"))

    async def progress_cb(percent):
        now = time.monotonic()
        if percent < 100 and now - state.get("last_ui", 0.0) < MEDIA_CONVERT_PROGRESS_INTERVAL:
            return
        state["last_ui"] = now
        await _htx_edit(event, _htx_video_note_progress(percent))

    try:
        if not await _media_binary_exists("ffmpeg") or not await _media_binary_exists("ffprobe"):
            raise RuntimeError("ffmpeg_not_found")
        await _htx_edit(event, _htx_video_note_progress(0))

        try:
            input_path = await replied.download_media(file=str(tmp_dir))
        except Exception as exc:
            raise RuntimeError("download_failed") from exc
        if not input_path:
            raise RuntimeError("download_failed")

        duration = await _ffprobe_duration(input_path)
        limit = min(duration, HTX_VIDEO_NOTE_MAX_SEC)
        output_path = tmp_dir / "video_note.mp4"
        await _ffmpeg_video_note(input_path, output_path, limit, progress_cb)

        try:
            # video_note=True + round_message=True makes Telegram show it as a
            # real round video message, not a normal square video.
            await event.client.send_file(
                event.chat_id, str(output_path),
                video_note=True,
                supports_streaming=True,
                attributes=[types.DocumentAttributeVideo(
                    duration=max(1, int(round(limit))),
                    w=HTX_VIDEO_NOTE_SIZE, h=HTX_VIDEO_NOTE_SIZE,
                    round_message=True, supports_streaming=True,
                )],
            )
        except FloodWaitError as exc:
            raise RuntimeError("floodwait") from exc
        except Exception as exc:
            raise RuntimeError("send_failed") from exc

        await _htx_edit(event, _htx_reply("ویدیو مسیج", "✅ ویدیو گرد آماده شد."))
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[SELF {uid}] video note failed: {exc}")
        await _htx_edit(event, _htx_reply("ویدیو مسیج", _htx_video_note_error(exc)))
    finally:
        media_convert_state.pop(uid, None)
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return True


# ============================================================
# ARCHIVE EXTRACTION (ZIP / RAR)
# ============================================================

_UNZIP_COMMANDS = {
    "unzip",
    "unzip + ریپلای",
    "unzip ریپلای",
    "unzip + ریپلی",
    "unzip ریپلی",
    "استخراج",
    "استخراج + ریپلای",
    "استخراج ریپلای",
    "استخراج + ریپلی",
    "استخراج ریپلی",
}


def _safe_archive_target(root: Path, member_name: str) -> Path:
    """Resolve an archive member safely and reject path traversal."""
    raw = str(member_name).replace("\\", "/")
    # Archives are allowed to contain nested directories, but never absolute
    # paths or ../ entries that could escape the temporary extraction folder.
    target = (root / raw).resolve()
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError:
        raise RuntimeError("archive_path_traversal")
    return target


def _extract_zip_archive(archive_path: Path, output_dir: Path):
    files = []
    with zipfile.ZipFile(archive_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            target = _safe_archive_target(output_dir, info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            files.append(target)
    return files


def _extract_rar_archive(archive_path: Path, output_dir: Path):
    """RAR extraction with rarfile first, then common system extractors."""
    try:
        import rarfile
        files = []
        with rarfile.RarFile(archive_path) as rf:
            for info in rf.infolist():
                if info.isdir():
                    continue
                target = _safe_archive_target(output_dir, info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with rf.open(info) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
                files.append(target)
        return files
    except ImportError:
        pass

    # Keep the bot dependency-light: if rarfile is not installed, use an
    # already-installed 7z/7zz/unar binary when available.
    extractor = next((shutil.which(x) for x in ("7z", "7zz", "unar") if shutil.which(x)), None)
    if not extractor:
        raise RuntimeError("rar_backend_missing")

    if Path(extractor).name.lower() in {"7z", "7zz"}:
        cmd = [extractor, "x", "-y", f"-o{output_dir}", str(archive_path)]
    else:
        cmd = [extractor, "-o", str(output_dir), str(archive_path)]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError("rar_extract_failed")

    # Validate the extractor output too, so a malicious archive cannot leave
    # files outside the temporary directory unnoticed.
    root_resolved = output_dir.resolve()
    files = []
    for path in output_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(root_resolved)
        except ValueError:
            raise RuntimeError("archive_path_traversal")
        files.append(path)
    return files


def _extract_archive_sync(archive_path: Path, output_dir: Path):
    suffix = archive_path.suffix.casefold()
    if suffix == ".zip":
        return _extract_zip_archive(archive_path, output_dir)
    if suffix == ".rar":
        return _extract_rar_archive(archive_path, output_dir)
    raise RuntimeError("unsupported_archive")


def _archive_progress_text(percent: int, phase: str = "منتظر بمانید", current: int = 0, total: int = 0):
    percent = max(0, min(100, int(percent)))
    slots = 16
    filled = round(slots * percent / 100)
    bar = "█" * filled + "░" * (slots - filled)
    return (
        f"📦 در حال استخراج آرشیو\n"
        f"{bar}\n"
        f"{html.escape(phase)}"
    )


async def _archive_progress_5s(event, started_at: float, phase="در حال استخراج…"):
    """Animate a predictable five-second progress bar without blocking Telethon."""
    while True:
        elapsed = time.monotonic() - started_at
        if elapsed >= 5.0:
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text(_archive_progress_text(100, phase)), parse_mode="html")
            return
        percent = int((elapsed / 5.0) * 95)
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(_archive_progress_text(percent, phase)), parse_mode="html")
        await asyncio.sleep(0.6)


async def _self_unzip_reply(event, uid):
    """Extract a replied ZIP/RAR and send every extracted file separately."""
    if not event.is_reply:
        return "❌ روی فایل .zip یا .rar ریپلای کن و سپس «.unzip + ریپلی» یا «.استخراج + ریپلی» را بفرست."

    replied = await event.get_reply_message()
    if not replied or not getattr(replied, "media", None):
        return "❌ فایل آرشیو پیدا نشد."

    suffix = ""
    name = ""
    document = getattr(replied, "document", None)
    if document:
        for attr in getattr(document, "attributes", None) or []:
            filename = getattr(attr, "file_name", None)
            if filename:
                name = str(filename)
                break
        name = name or "archive"
        suffix = Path(name).suffix.casefold()

    if suffix not in {".zip", ".rar"}:
        return "❌ فقط فایل‌های .zip و .rar قابل استخراج هستند."

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_unzip_{uid}_"))
    archive_path = tmp_dir / (Path(name).name or f"archive{suffix}")
    extract_dir = tmp_dir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    progress_task = None

    try:
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(_archive_progress_text(0, "منتظر بمانید")), parse_mode="html")

        downloaded = await replied.download_media(file=str(archive_path))
        if not downloaded:
            return "❌ دانلود آرشیو ناموفق بود."

        # The five-second bar starts after download and covers the extraction
        # phase. Extraction itself runs in a worker thread so Telethon stays
        # responsive and the progress message can keep updating.
        progress_started = time.monotonic()
        progress_task = asyncio.create_task(
            _archive_progress_5s(event, progress_started, "منتظر بمانید")
        )
        try:
            files = await asyncio.to_thread(_extract_archive_sync, archive_path, extract_dir)
        finally:
            if progress_task:
                await progress_task
                progress_task = None

        files = sorted(
            [p for p in files if p.is_file()],
            key=lambda x: str(x).casefold(),
        )
        if not files:
            await event.edit(premium_ui_text("❌ آرشیو خالی است یا فایل قابل‌ارسالی داخل آن پیدا نشد."), parse_mode="html")
            return "__DONE__"

        # Send extracted files one-by-one. The progress message is reused for
        # the send phase and shows the actual file counter.
        total = len(files)
        sent = 0
        failed = 0
        await event.edit(premium_ui_text(_archive_progress_text(0, "منتظر بمانید", 0, total)), parse_mode="html")

        for index, file_path in enumerate(files, 1):
            try:
                rel = file_path.relative_to(extract_dir)
                caption = f"📦 {rel.as_posix()}"
                await event.client.send_file(
                    event.chat_id,
                    str(file_path),
                    force_document=True,
                    caption=caption,
                    reply_to=replied.id,
                )
                sent += 1
            except FloodWaitError as exc:
                wait = max(1, int(getattr(exc, "seconds", 1)))
                await asyncio.sleep(wait)
                try:
                    rel = file_path.relative_to(extract_dir)
                    await event.client.send_file(
                        event.chat_id,
                        str(file_path),
                        force_document=True,
                        caption=f"📦 {rel.as_posix()}",
                        reply_to=replied.id,
                    )
                    sent += 1
                except Exception as exc2:
                    failed += 1
                    print(f"[UNZIP {uid}] resend failed {file_path}: {exc2}")
            except Exception as exc:
                failed += 1
                print(f"[UNZIP {uid}] send failed {file_path}: {exc}")

            percent = int(index * 100 / total)
            with contextlib.suppress(Exception):
                await event.edit(
                    premium_ui_text(_archive_progress_text(percent, "منتظر بمانید", index, total))
                , parse_mode="html")

        result = f"✅ استخراج تمام شد.\n📦 ارسال شد: {sent} فایل"
        if failed:
            result += f"\n⚠️ ناموفق: {failed} فایل"
        await event.edit(premium_ui_text(result), parse_mode="html")
        return "__DONE__"

    except RuntimeError as exc:
        messages = {
            "archive_path_traversal": "❌ آرشیو نامعتبر است؛ مسیر خطرناک داخل فایل پیدا شد.",
            "rar_backend_missing": "❌ برای استخراج RAR روی سرور، `rarfile` یا یکی از ابزارهای 7z/7zz/unar لازم است.",
            "rar_extract_failed": "❌ استخراج فایل RAR ناموفق بود.",
            "unsupported_archive": "❌ فقط فایل‌های .zip و .rar پشتیبانی می‌شوند.",
        }
        return messages.get(str(exc), "❌ استخراج آرشیو انجام نشد.")
    except zipfile.BadZipFile:
        return "❌ فایل ZIP خراب یا نامعتبر است."
    except Exception as exc:
        print(f"[UNZIP {uid}] extraction failed: {exc}")
        return "❌ استخراج آرشیو انجام نشد؛ فایل ممکن است خراب یا ناقص باشد."
    finally:
        if progress_task:
            progress_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await progress_task
        shutil.rmtree(tmp_dir, ignore_errors=True)



# ============================================================
# FREE MEDIA / CRYPTO FEATURES
# ============================================================

_CRYPTO_ALIASES = {
    "btc": ("BTC", "بیت‌کوین"), "بیت کوین": ("BTC", "بیت‌کوین"), "بیتکوین": ("BTC", "بیت‌کوین"),
    "eth": ("ETH", "اتریوم"), "اتریوم": ("ETH", "اتریوم"),
    "sol": ("SOL", "سولانا"), "سول": ("SOL", "سولانا"), "سولانا": ("SOL", "سولانا"),
    "usdt": ("USDT", "تتر"), "تتر": ("USDT", "تتر"),
    "ton": ("TON", "تون‌کوین"), "toncoin": ("TON", "تون‌کوین"), "تون کوین": ("TON", "تون‌کوین"), "تون‌کوین": ("TON", "تون‌کوین"),
    "trx": ("TRX", "ترون"), "ترون": ("TRX", "ترون"),
    "xrp": ("XRP", "ریپل"), "ریپل": ("XRP", "ریپل"),
    "doge": ("DOGE", "دوج‌کوین"), "دوج": ("DOGE", "دوج‌کوین"), "دوج کوین": ("DOGE", "دوج‌کوین"), "دوجکوین": ("DOGE", "دوج‌کوین"),
    "bnb": ("BNB", "بایننس‌کوین"), "بایننس کوین": ("BNB", "بایننس‌کوین"), "بایننس‌کوین": ("BNB", "بایننس‌کوین"),
    "ada": ("ADA", "کاردانو"), "کاردانو": ("ADA", "کاردانو"),
    "dot": ("DOT", "پولکادات"), "پولکادات": ("DOT", "پولکادات"),
    "avax": ("AVAX", "آوالانچ"), "آوالانچ": ("AVAX", "آوالانچ"),
    "shib": ("SHIB", "شیبا"), "شیبا": ("SHIB", "شیبا"),
}

_MARKET_PRICE_ALIASES = {
    "eur": ("EUR", "یورو"),
    "euro": ("EUR", "یورو"),
    "یورو": ("EUR", "یورو"),
    "gold": ("GOLD18", "طلای ۱۸ عیار"),
    "gold18": ("GOLD18", "طلای ۱۸ عیار"),
    "gold 18k": ("GOLD18", "طلای ۱۸ عیار"),
    "18k": ("GOLD18", "طلای ۱۸ عیار"),
    "طلا": ("GOLD18", "طلای ۱۸ عیار"),
    "طلا 18 عیار": ("GOLD18", "طلای ۱۸ عیار"),
    "طلای 18k": ("GOLD18", "طلای ۱۸ عیار"),
    "طلای 18 عیار": ("GOLD18", "طلای ۱۸ عیار"),
    "طلای هجده عیار": ("GOLD18", "طلای ۱۸ عیار"),
    "گرم طلا": ("GOLD18", "طلای ۱۸ عیار"),
}

_CRYPTO_GECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "USDT": "tether",
    "TON": "the-open-network", "TRX": "tron", "XRP": "ripple", "DOGE": "dogecoin",
    "BNB": "binancecoin", "ADA": "cardano", "DOT": "polkadot", "AVAX": "avalanche-2",
    "SHIB": "shiba-inu",
}

# Local logo templates. These are real rendering templates, not a fake remote
# template-id mapping. The supported range is exactly the templates below.
LOGO_TEMPLATES = {
    1: ("classic", "طلایی سلطنتی"), 2: ("neon", "نئون سینت‌ویو"), 3: ("minimal", "مینیمال برند"),
    4: ("badge", "نشان روبان‌دار"), 5: ("shadow", "سایه بلند"), 6: ("gradient", "شیشه‌ای آرورا"),
    7: ("outline", "سایبری"), 8: ("split", "دو رنگ مورب"), 9: ("glow", "طلای مذاب"),
    10: ("terminal", "ترمینال"), 11: ("stamp", "مهر وینتیج"), 12: ("diamond", "الماس لوکس"),
}

def _fa_digits(text):
    return str(text).translate(str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    ))

def _valid_http_url(value: str):
    if not isinstance(value, str):
        return None
    value = value.strip()
    try:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme.casefold() not in {"http", "https"} or not parsed.netloc:
            return None
        return value
    except Exception:
        return None

def _http_json_get(url: str, params=None, timeout=CRYPTO_PROVIDER_TIMEOUT):
    query = urllib.parse.urlencode(params or {}, doseq=True)
    full_url = f"{url}{'&' if '?' in url else '?'}{query}" if query else url
    req = urllib.request.Request(
        full_url,
        headers={"Accept": "application/json", "User-Agent": "HusteRIX-Diamond-Self/3.0"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = int(getattr(response, "status", response.getcode()))
        body = response.read()
        if status < 200 or status >= 300:
            raise urllib.error.HTTPError(full_url, status, "HTTP error", response.headers, None)
        if not body:
            raise ValueError("empty_response")
        try:
            return json.loads(body.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid_json") from exc

def _http_json_post(url: str, payload=None, timeout=CRYPTO_PROVIDER_TIMEOUT):
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "HusteRIX-Diamond-Self/3.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = int(getattr(response, "status", response.getcode()))
        body = response.read()
        if status < 200 or status >= 300:
            raise urllib.error.HTTPError(url, status, "HTTP error", response.headers, None)
        if not body:
            raise ValueError("empty_response")
        try:
            return json.loads(body.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid_json") from exc

def _decimal_or_none(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

def _cmc_price_from_payload(payload, symbol):
    if not isinstance(payload, dict):
        raise ValueError("invalid_json")
    status = payload.get("status") or {}
    if str(status.get("error_code", "0")) != "0":
        raise ValueError(str(status.get("error_message") or "provider_error"))
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("missing_price")
    for item in data:
        if not isinstance(item, dict):
            continue
        if str(item.get("symbol", "")).upper() != symbol.upper():
            continue
        quotes = item.get("quotes")
        if not isinstance(quotes, list):
            continue
        for quote in quotes:
            if isinstance(quote, dict) and str(quote.get("symbol", "")).upper() == "USD":
                price = quote.get("price")
                if price is not None:
                    return str(price), quote.get("last_updated")
    raise ValueError("missing_price")

async def _get_crypto_price_cmc(symbol: str):
    payload = await asyncio.to_thread(
        _http_json_get,
        f"{CMC_PUBLIC_BASE_URL}/v2/simple/price",
        {"symbol": symbol.upper(), "convert": "USD", "skip_invalid": "true"},
        CRYPTO_PROVIDER_TIMEOUT,
    )
    price, updated = _cmc_price_from_payload(payload, symbol)
    return {
        "symbol": symbol.upper(), "toman": None, "usd": _decimal_or_none(price),
        "day_change": None, "updated": updated, "provider": "CoinMarketCap",
    }

async def _get_crypto_price_coingecko(symbol: str):
    coin_id = _CRYPTO_GECKO_IDS.get(symbol.upper())
    if not coin_id:
        raise ValueError("missing_price")
    payload = await asyncio.to_thread(
        _http_json_get,
        f"{COINGECKO_PUBLIC_BASE_URL}/simple/price",
        {"ids": coin_id, "vs_currencies": "usd", "include_last_updated_at": "true"},
        CRYPTO_PROVIDER_TIMEOUT,
    )
    item = payload.get(coin_id) if isinstance(payload, dict) else None
    if not isinstance(item, dict) or "usd" not in item:
        raise ValueError("missing_price")
    return {
        "symbol": symbol.upper(), "toman": None, "usd": _decimal_or_none(item["usd"]),
        "day_change": None, "updated": item.get("last_updated_at"), "provider": "CoinGecko",
    }

def _get_wallex_usdt_toman_sync():
    """Read the top of Wallex's public USDT/Toman order book.

    USDT is used as a practical market proxy for USD, not represented as a
    guaranteed 1:1 fiat-dollar quote. The midpoint is used for conversion;
    top bid and ask are kept for transparent display.
    """
    payload = _http_json_get(
        WALLEX_DEPTH_URL,
        {"symbol": "USDTTMN"},
        CRYPTO_PROVIDER_TIMEOUT,
    )
    result = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(result, dict):
        raise ValueError("missing_wallex_depth")
    asks = result.get("ask")
    bids = result.get("bid")
    if not isinstance(asks, list) or not asks or not isinstance(bids, list) or not bids:
        raise ValueError("empty_wallex_order_book")

    ask_item, bid_item = asks[0], bids[0]
    ask = _decimal_or_none(ask_item.get("price")) if isinstance(ask_item, dict) else None
    bid = _decimal_or_none(bid_item.get("price")) if isinstance(bid_item, dict) else None
    ask_qty = _decimal_or_none(ask_item.get("quantity")) if isinstance(ask_item, dict) else None
    bid_qty = _decimal_or_none(bid_item.get("quantity")) if isinstance(bid_item, dict) else None
    if (
        ask is None or bid is None or ask <= 0 or bid <= 0 or ask < bid
        or ask_qty is None or bid_qty is None or ask_qty <= 0 or bid_qty <= 0
    ):
        raise ValueError("invalid_wallex_order_book")

    mid = (ask + bid) / Decimal("2")
    sampled_at = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    return mid, bid, ask, f"{sampled_at} • Asia/Tehran"


_USD_IRT_RATE_CACHE = {
    "rate": None, "ts": 0.0, "source": None, "updated": None,
    "bid": None, "ask": None, "is_market_proxy": False,
}
USD_IRT_RATE_CACHE_TTL = 30  # seconds

async def _get_usd_irt_rate():
    """Get a current Toman/USD proxy from Wallex, with Bonbast as fallback."""
    now = time.time()
    cached_rate = _USD_IRT_RATE_CACHE["rate"]
    if cached_rate is not None and (now - _USD_IRT_RATE_CACHE["ts"]) < USD_IRT_RATE_CACHE_TTL:
        return cached_rate

    try:
        toman_rate, bid, ask, updated = await asyncio.to_thread(_get_wallex_usdt_toman_sync)
        source = "Wallex • بازار USDT/TMN"
        is_market_proxy = True
    except Exception:
        logging.exception("Wallex USDT/TMN fetch failed; trying Bonbast fallback")
        payload = await asyncio.to_thread(
            _http_json_get,
            f"{BONBAST_MIRROR_URL}/latest",
            None,
            CRYPTO_PROVIDER_TIMEOUT,
        )
        usd = payload.get("usd") if isinstance(payload, dict) else None
        if not isinstance(usd, dict):
            raise ValueError("missing_usd_rate")
        sell = _decimal_or_none(usd.get("sell"))
        buy = _decimal_or_none(usd.get("buy"))
        candidates = [value for value in (sell, buy) if value is not None]
        if not candidates:
            raise ValueError("missing_usd_rate")
        rial_rate = sum(candidates) / Decimal(len(candidates))
        toman_rate = rial_rate / Decimal("10")
        source = "Bonbast • میانگین خرید و فروش (پشتیبان)"
        updated = None
        bid = ask = None
        is_market_proxy = False

    _USD_IRT_RATE_CACHE["rate"] = toman_rate
    _USD_IRT_RATE_CACHE["ts"] = now
    _USD_IRT_RATE_CACHE["source"] = source
    _USD_IRT_RATE_CACHE["updated"] = updated
    _USD_IRT_RATE_CACHE["bid"] = bid
    _USD_IRT_RATE_CACHE["ask"] = ask
    _USD_IRT_RATE_CACHE["is_market_proxy"] = is_market_proxy
    return toman_rate

async def get_crypto_price(symbol: str):
    """Provider layer: try CoinMarketCap, then CoinGecko (in that order) to
    get a USD price — both are public global services reachable from any
    host. Nobitex is intentionally NOT used: it throttles/blocks requests
    from non-Iranian IPs (e.g. Railway), which made it useless here. The
    Toman price is always derived ourselves from the USD price times a
    live free-market USD->Toman rate (see _get_usd_irt_rate)."""
    symbol = str(symbol or "").strip().upper()
    if not symbol:
        raise ValueError("missing_symbol")

    data = None
    last_exc = None
    for provider_fn in (_get_crypto_price_cmc, _get_crypto_price_coingecko):
        try:
            data = await provider_fn(symbol)
            break
        except Exception as exc:
            last_exc = exc
            logging.exception("%s failed for %s", getattr(provider_fn, "__name__", provider_fn), symbol)

    if data is None:
        raise RuntimeError(f"crypto_provider_failed: {type(last_exc).__name__}") from last_exc

    if data.get("toman") is None and data.get("usd") is not None:
        try:
            rate = await _get_usd_irt_rate()
            data["toman"] = data["usd"] * rate
            data["fx_provider"] = _USD_IRT_RATE_CACHE.get("source")
            data["fx_updated"] = _USD_IRT_RATE_CACHE.get("updated")
            data["fx_bid"] = _USD_IRT_RATE_CACHE.get("bid")
            data["fx_ask"] = _USD_IRT_RATE_CACHE.get("ask")
            data["fx_is_market_proxy"] = _USD_IRT_RATE_CACHE.get("is_market_proxy")
        except Exception:
            logging.exception("USD->Toman rate fetch failed for %s", symbol)

    return data

_LOCAL_MARKET_PRICE_CACHE = {}
LOCAL_MARKET_PRICE_CACHE_TTL = 30

async def _get_eur_toman_price():
    """Estimate one euro in Toman using a global EUR/USD cross-rate and
    the bot's live local USD/Toman market proxy."""
    now = time.time()
    cached = _LOCAL_MARKET_PRICE_CACHE.get("EUR")
    if cached and now - cached["ts"] < LOCAL_MARKET_PRICE_CACHE_TTL:
        return dict(cached["data"])

    payload, usd_toman = await asyncio.gather(
        asyncio.to_thread(
            _http_json_get,
            f"{COINGECKO_PUBLIC_BASE_URL}/exchange_rates",
            None,
            CRYPTO_PROVIDER_TIMEOUT,
        ),
        _get_usd_irt_rate(),
    )
    rates = payload.get("rates") if isinstance(payload, dict) else None
    eur_item = rates.get("eur") if isinstance(rates, dict) else None
    usd_item = rates.get("usd") if isinstance(rates, dict) else None
    eur_rate = _decimal_or_none(eur_item.get("value")) if isinstance(eur_item, dict) else None
    usd_rate = _decimal_or_none(usd_item.get("value")) if isinstance(usd_item, dict) else None
    if eur_rate is None or usd_rate is None or eur_rate <= 0 or usd_rate <= 0:
        raise ValueError("missing_eur_usd_rate")

    eur_usd = usd_rate / eur_rate
    data = {
        "symbol": "EUR",
        "card_title": "قیمت یورو",
        "compact_card": True,
        "toman": eur_usd * usd_toman,
        "rial": eur_usd * usd_toman * Decimal("10"),
        "usd": eur_usd,
        "quote_label": "قیمت یورو",
        "day_change": None,
        "updated": datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M"),
        "provider": "CoinGecko • EUR/USD",
        "fx_provider": _USD_IRT_RATE_CACHE.get("source"),
        "fx_bid": _USD_IRT_RATE_CACHE.get("bid"),
        "fx_ask": _USD_IRT_RATE_CACHE.get("ask"),
        "fx_is_market_proxy": _USD_IRT_RATE_CACHE.get("is_market_proxy"),
    }
    _LOCAL_MARKET_PRICE_CACHE["EUR"] = {"ts": now, "data": data}
    return dict(data)

async def _get_gold18_toman_price():
    """Estimate raw 18-karat gold per gram from global spot and the live
    local USD/Toman market proxy; this is not a jewelry retail quote."""
    now = time.time()
    cached = _LOCAL_MARKET_PRICE_CACHE.get("GOLD18")
    if cached and now - cached["ts"] < LOCAL_MARKET_PRICE_CACHE_TTL:
        return dict(cached["data"])

    payload, usd_toman = await asyncio.gather(
        asyncio.to_thread(
            _http_json_get,
            GOLD_SPOT_URL,
            {"currency": "USD", "unit": "gram", "compact": "1"},
            CRYPTO_PROVIDER_TIMEOUT,
        ),
        _get_usd_irt_rate(),
    )
    state = payload.get("data_state") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("stale") is True
        or (isinstance(state, dict) and state.get("status") not in (None, "fresh"))
    ):
        raise ValueError("stale_gold_spot")
    spot_24k_usd_per_gram = _decimal_or_none(payload.get("per_gram_usd"))
    if spot_24k_usd_per_gram is None or spot_24k_usd_per_gram <= 0:
        raise ValueError("missing_gold_spot")

    spot_18k_usd_per_gram = spot_24k_usd_per_gram * Decimal("0.75")
    data = {
        "symbol": "XAU 18K",
        "card_title": "قیمت طلا",
        "compact_card": True,
        "toman": spot_18k_usd_per_gram * usd_toman,
        "rial": spot_18k_usd_per_gram * usd_toman * Decimal("10"),
        "usd": spot_18k_usd_per_gram,
        "quote_label": "قیمت خام هر گرم طلای ۱۸ عیار",
        "day_change": None,
        "updated": payload.get("updated_at") or payload.get("price_as_of"),
        "provider": "XAUS • اونس جهانی طلا",
        "fx_provider": _USD_IRT_RATE_CACHE.get("source"),
        "fx_bid": _USD_IRT_RATE_CACHE.get("bid"),
        "fx_ask": _USD_IRT_RATE_CACHE.get("ask"),
        "fx_is_market_proxy": _USD_IRT_RATE_CACHE.get("is_market_proxy"),
    }
    _LOCAL_MARKET_PRICE_CACHE["GOLD18"] = {"ts": now, "data": data}
    return dict(data)

async def _get_crypto_ohlc_coingecko(symbol: str, days: int = 30):
    """Daily USD price history for the last `days` days, used to draw the
    small price chart. CoinGecko's market_chart endpoint is public,
    keyless, and reachable from any host (unlike Nobitex, which is not
    used anywhere in this bot for that reason)."""
    coin_id = _CRYPTO_GECKO_IDS.get(symbol.upper())
    if not coin_id:
        raise ValueError("unsupported_symbol")
    payload = await asyncio.to_thread(
        _http_json_get,
        f"{COINGECKO_PUBLIC_BASE_URL}/coins/{coin_id}/market_chart",
        {"vs_currency": "usd", "days": str(days), "interval": "daily"},
        CRYPTO_PROVIDER_TIMEOUT,
    )
    prices = payload.get("prices") if isinstance(payload, dict) else None
    if not isinstance(prices, list):
        raise ValueError("ohlc_unavailable")
    points = [
        (int(ts / 1000), float(price)) for ts, price in prices
        if isinstance(price, (int, float))
    ]
    if len(points) < 2:
        raise ValueError("ohlc_empty")
    return "USD", points

async def _get_eur_toman_chart_points(days: int = 30):
    """Build an estimated EUR/Toman daily chart from historical EUR/USD
    rates multiplied by the current local USD/Toman market proxy."""
    end_date = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d")
    start_date = datetime.fromtimestamp(
        time.time() - (days * 86400), tz=ZoneInfo("UTC")
    ).strftime("%Y-%m-%d")
    payload, usd_toman = await asyncio.gather(
        asyncio.to_thread(
            _http_json_get,
            f"{FRANKFURTER_PUBLIC_BASE_URL}/rates",
            {
                "from": start_date,
                "to": end_date,
                "base": "EUR",
                "quotes": "USD",
            },
            CRYPTO_PROVIDER_TIMEOUT,
        ),
        _get_usd_irt_rate(),
    )
    if not isinstance(payload, list):
        raise ValueError("invalid_eur_history")

    points = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        date_text = item.get("date")
        rate = _decimal_or_none(item.get("rate"))
        if not date_text or rate is None or rate <= 0:
            continue
        try:
            timestamp = datetime.strptime(
                str(date_text), "%Y-%m-%d"
            ).replace(tzinfo=ZoneInfo("UTC")).timestamp()
        except (TypeError, ValueError):
            continue
        points.append((int(timestamp), float(rate * usd_toman)))

    points.sort(key=lambda point: point[0])
    if len(points) < 2:
        raise ValueError("eur_history_empty")
    return "TMN", points

async def _get_gold18_toman_chart_points(days: int = 30):
    """Convert XAUS daily XAU/USD history to estimated 18K Toman/gram
    using the current USD/Toman proxy."""
    payload, usd_toman = await asyncio.gather(
        asyncio.to_thread(
            _http_json_get,
            GOLD_HISTORY_URL,
            None,
            CRYPTO_PROVIDER_TIMEOUT,
        ),
        _get_usd_irt_rate(),
    )
    history = payload.get("points") if isinstance(payload, dict) else None
    if not isinstance(history, list):
        raise ValueError("invalid_gold_history")

    cutoff = time.time() - (days * 86400)
    toman_per_usd_per_ounce = (
        usd_toman * Decimal("0.75") / Decimal("31.1034768")
    )
    points = []
    for item in history:
        if not isinstance(item, dict):
            continue
        date_text = item.get("d")
        close = _decimal_or_none(item.get("c"))
        if not date_text or close is None or close <= 0:
            continue
        try:
            timestamp = datetime.strptime(
                str(date_text), "%Y-%m-%d"
            ).replace(tzinfo=ZoneInfo("UTC")).timestamp()
        except (TypeError, ValueError):
            continue
        if timestamp < cutoff:
            continue
        points.append((int(timestamp), float(close * toman_per_usd_per_ounce)))

    points.sort(key=lambda point: point[0])
    if len(points) < 2:
        raise ValueError("gold_history_empty")
    return "TMN", points

def _format_toman(value):
    d = _decimal_or_none(value)
    if d is None:
        return None
    return f"{int(d):,}"

def _format_usd(value):
    d = _decimal_or_none(value)
    if d is None:
        return None
    if d == 0:
        return "0"
    if d >= 1:
        d = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif d >= Decimal("0.0001"):
        d = d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    else:
        d = d.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    text = format(d, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if "." in text:
        int_part, dec_part = text.split(".")
        return f"{int(int_part):,}.{dec_part}"
    return f"{int(text):,}"

def _format_day_change(value):
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return None
    arrow = "🟢 ▲" if pct >= 0 else "🔴 ▼"
    return f"{arrow} {abs(pct):.2f}%"

def _format_crypto_updated(value):
    if not value:
        return "همین حالا"
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
        text = str(value)
        text = re.sub(r"(?<=\d)T(?=\d)", " ", text)
        return text[:-1] + " UTC" if text.endswith("Z") else text
    except Exception:
        return str(value)

def _currency_ui(data, fa_name):
    toman_text = _format_toman(data.get("toman"))
    if toman_text:
        quote_label = html.escape(str(data.get("quote_label", "قیمت تومانی")))
        toman_lines = [f"💰 <b>{quote_label}</b>", f"<b>{toman_text} تومان</b>"]
        rial_value = data.get("rial")
        if rial_value is None:
            rial_value = _decimal_or_none(data.get("toman")) * Decimal("10")
        rial_text = _format_toman(rial_value)
        if rial_text:
            toman_lines.append(f"💴 معادل ریالی: <b>{rial_text} ریال</b>")
        price_block = "<blockquote>" + "\n".join(toman_lines) + "</blockquote>"
    else:
        price_block = "❌ قیمتی دریافت نشد."

    symbol = html.escape(str(data.get("symbol", "")))
    card_title = html.escape(str(data.get("card_title", "نرخ ارز")))
    return (
        f"╭━━━━━━ 💱 <b>{card_title}</b> ━━━━━━╮\n\n"
        f"🪙 <b>{html.escape(fa_name)}</b>  <code>{symbol}</code>\n\n"
        f"{price_block}\n\n"
        "╰━━━━━━ <b>𝐇𝐮𝐬𝐭𝐞𝐑𝐈𝐗</b> ━━━━━━╯"
    )

def _render_crypto_chart_sync(symbol: str, pair_label: str, points, source_label="CoinGecko"):
    """30-day price line chart (dark, HusteRIX-styled). Only Latin/numeric
    text is drawn on the image itself since PIL can't shape Persian glyphs;
    the Persian details live in the caption message sent alongside it."""
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 675
    margin_l, margin_r, margin_t, margin_b = 100, 40, 100, 70
    bg = (15, 15, 22)
    grid_color = (42, 42, 56)
    axis_text_color = (150, 150, 165)

    canvas = Image.new("RGB", (width, height), bg)

    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    reg_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    bold_path = next((x for x in bold_candidates if Path(x).exists()), None)
    reg_path = next((x for x in reg_candidates if Path(x).exists()), None)
    try:
        title_font = ImageFont.truetype(bold_path, 46) if bold_path else ImageFont.load_default()
        label_font = ImageFont.truetype(reg_path, 26) if reg_path else ImageFont.load_default()
        small_font = ImageFont.truetype(reg_path, 22) if reg_path else ImageFont.load_default()
    except Exception:
        title_font = label_font = small_font = ImageFont.load_default()

    values = [p[1] for p in points]
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        vmin -= max(abs(vmin) * 0.01, 1)
        vmax += max(abs(vmax) * 0.01, 1)
    pad = (vmax - vmin) * 0.12
    vmin -= pad
    vmax += pad

    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    def x_for(i):
        return margin_l + (plot_w * i / max(len(points) - 1, 1))

    def y_for(v):
        return margin_t + plot_h - (plot_h * (v - vmin) / (vmax - vmin))

    is_usd = pair_label.upper() in ("USD", "USDT") or pair_label.upper().endswith("USDT")
    draw = ImageDraw.Draw(canvas)
    for i in range(5):
        gy = margin_t + plot_h * i / 4
        draw.line([(margin_l, gy), (width - margin_r, gy)], fill=grid_color, width=1)
        gv = vmax - (vmax - vmin) * i / 4
        label = _format_usd(gv) if is_usd else _format_toman(gv)
        draw.text((14, gy - 10), str(label or ""), font=small_font, fill=axis_text_color)

    trend_up = values[-1] >= values[0]
    line_color = (56, 214, 132) if trend_up else (235, 76, 96)
    fill_color = (56, 214, 132, 40) if trend_up else (235, 76, 96, 40)
    coords = [(x_for(i), y_for(v)) for i, v in enumerate(values)]

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    poly = coords + [(coords[-1][0], margin_t + plot_h), (coords[0][0], margin_t + plot_h)]
    odraw.polygon(poly, fill=fill_color)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    draw.line(coords, fill=line_color, width=5, joint="curve")
    draw.ellipse(
        [coords[-1][0] - 7, coords[-1][1] - 7, coords[-1][0] + 7, coords[-1][1] + 7],
        fill=line_color,
    )

    unit = "USD" if is_usd else ("TMN" if pair_label.upper() == "TMN" else "IRT")
    change_pct = ((values[-1] - values[0]) / values[0] * 100) if values[0] else 0.0
    arrow = "▲" if trend_up else "▼"

    draw.text((margin_l, 22), symbol.upper(), font=title_font, fill=(235, 235, 240))
    draw.text(
        (margin_l, 76),
        f"{arrow} {change_pct:+.2f}%  •  30D  •  {unit}",
        font=label_font,
        fill=line_color,
    )
    draw.text(
        (margin_l, height - 42),
        f"HusteRIX \u2022 {source_label}",
        font=small_font,
        fill=axis_text_color,
    )

    output = BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()

async def _self_currency_command(event, uid, text):
    cleaned_text = text.strip()
    m = re.fullmatch(r"قیمت\s+(.+)", cleaned_text, flags=re.S | re.I)
    is_rate_command = cleaned_text.casefold() in {"نرخ ارز", "قیمت دلار", "قیمت usd"}
    if not m and not is_rate_command:
        return False
    raw = _fa_digits(m.group(1).strip()).casefold() if m else "usd"
    is_usd = raw in {"usd", "دلار", "دلار آمریکا", "دلار امریکا", "نرخ دلار"}
    if is_usd:
        symbol, fa_name = "USD≈USDT/TMN", "شاخص دلار آزاد (بر پایه تتر)"
    elif raw in _MARKET_PRICE_ALIASES:
        symbol, fa_name = _MARKET_PRICE_ALIASES[raw]
    elif raw in _CRYPTO_ALIASES:
        symbol, fa_name = _CRYPTO_ALIASES[raw]
    else:
        await event.edit(
            premium_ui_text("❌ <b>ارز یا دارایی شناخته نشد.</b>\n\n"
            "مثال:\n<code>.نرخ ارز</code>\n<code>.قیمت دلار</code>\n"
            "<code>.قیمت یورو</code>\n<code>.قیمت طلا</code>\n"
            "<code>.قیمت BTC</code>\n<code>.قیمت SOL</code>\n"
            "<code>.قیمت ETH</code>\n<code>.قیمت USDT</code>"),
            parse_mode="html",
        )
        return True
    with contextlib.suppress(Exception):
        await event.edit(
            premium_ui_text(f"💱 <b>در حال دریافت نرخ {html.escape(fa_name)}...</b>"),
            parse_mode="html",
        )
    try:
        if is_usd:
            toman_rate = await _get_usd_irt_rate()
            data = {
                "symbol": "USD≈USDT/TMN",
                "toman": toman_rate,
                "rial": toman_rate * Decimal("10"),
                "usd": None,
                "day_change": None,
                "updated": _USD_IRT_RATE_CACHE.get("updated"),
                "provider": _USD_IRT_RATE_CACHE.get("source") or "Wallex • بازار USDT/TMN",
                "fx_provider": _USD_IRT_RATE_CACHE.get("source"),
                "fx_bid": _USD_IRT_RATE_CACHE.get("bid"),
                "fx_ask": _USD_IRT_RATE_CACHE.get("ask"),
                "fx_is_market_proxy": _USD_IRT_RATE_CACHE.get("is_market_proxy"),
            }
        elif symbol == "EUR":
            data = await _get_eur_toman_price()
        elif symbol == "GOLD18":
            data = await _get_gold18_toman_price()
        else:
            data = await get_crypto_price(symbol)
    except urllib.error.HTTPError as exc:
        await event.edit(premium_ui_text(f"❌ <b>سرویس نرخ ارز خطا داد؛ HTTP {exc.code}.</b>"), parse_mode="html")
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        await event.edit(premium_ui_text("❌ <b>اتصال به سرویس نرخ ارز برقرار نشد.</b>"), parse_mode="html")
        return True
    except ValueError:
        await event.edit(premium_ui_text("❌ <b>پاسخ سرویس نرخ ارز معتبر نبود یا قیمت پیدا نشد.</b>"), parse_mode="html")
        return True
    except Exception:
        await event.edit(premium_ui_text("❌ <b>دریافت نرخ ارز ناموفق بود؛ دوباره تلاش کن.</b>"), parse_mode="html")
        return True

    caption = premium_ui_text(_currency_ui(data, fa_name))
    chart_bytes = None
    if symbol in _CRYPTO_GECKO_IDS:
        with contextlib.suppress(Exception):
            pair_label, points = await _get_crypto_ohlc_coingecko(symbol)
            chart_bytes = await asyncio.to_thread(_render_crypto_chart_sync, symbol, pair_label, points)
    elif symbol == "EUR":
        with contextlib.suppress(Exception):
            pair_label, points = await _get_eur_toman_chart_points()
            chart_bytes = await asyncio.to_thread(
                _render_crypto_chart_sync, "EUR", pair_label, points, "Frankfurter"
            )
    elif symbol == "GOLD18":
        with contextlib.suppress(Exception):
            pair_label, points = await _get_gold18_toman_chart_points()
            chart_bytes = await asyncio.to_thread(
                _render_crypto_chart_sync, "GOLD 18K", pair_label, points, "XAUS"
            )

    if chart_bytes:
        try:
            await send_generated_image(event, chart_bytes, caption, f"{symbol.lower()}_chart.png")
            with contextlib.suppress(Exception):
                await event.delete()
        except Exception:
            await event.edit(caption, parse_mode="html")
    else:
        await event.edit(caption, parse_mode="html")
    return True

# ============================================================
# PRO LOGO ENGINE
# 12 hand-built templates rendered locally with Pillow: metallic gradients,
# multi-layer glow, long shadows, glass cards, emblems, reflections, grain
# and vignette. Rendered at 1.5x and downsampled for clean anti-aliasing.
# Optional subtitle:  .لوگو 12 HusteRIX | Premium Store
# Fonts: put the .ttf files in a «fonts» folder next to this script
# (falls back to system fonts, then DejaVu).
# ============================================================
import math
import os
_LOGO_OUT_W, _LOGO_OUT_H = 1600, 1000
_LOGO_SS = 1.5
_LOGO_RTL_RE = re.compile(r"[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]")
_LOGO_FONT_DIRS = [
    Path(__file__).resolve().parent / "fonts",
    Path.home() / ".fonts",
    Path("/usr/local/share/fonts"),
    Path("/usr/share/fonts"),
]
_LOGO_FONT_FILES = {
    "cinzel": ("Cinzel[wght].ttf", "Cinzel-Black.ttf", "Cinzel-Bold.ttf"),
    "audiowide": ("Audiowide-Regular.ttf",),
    "montserrat": ("Montserrat[wght].ttf", "Montserrat-ExtraBold.ttf", "Montserrat-Bold.ttf"),
    "bebas": ("BebasNeue-Regular.ttf",),
    "anton": ("Anton-Regular.ttf",),
    "poppins": ("Poppins-Black.ttf", "Poppins-ExtraBold.ttf", "Poppins-Bold.ttf"),
    "orbitron": ("Orbitron[wght].ttf", "Orbitron-Black.ttf", "Orbitron-Bold.ttf"),
    "playfair": ("PlayfairDisplay[wght].ttf", "PlayfairDisplay-Black.ttf", "PlayfairDisplay-Bold.ttf"),
    "jetbrains": ("JetBrainsMono[wght].ttf", "JetBrainsMono-ExtraBold.ttf", "JetBrainsMono-Bold.ttf"),
    "blackops": ("BlackOpsOne-Regular.ttf",),
    "vazir": ("Vazirmatn[wght].ttf", "Vazirmatn-Black.ttf", "Vazirmatn-Bold.ttf"),
    "fallback": ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"),
}
_LOGO_FONT_PATHS = {}


_LOGO_FONT_INDEX = None


def _logo_font_path(key):
    """Exact filename lookup (no glob: names like «Cinzel[wght].ttf» contain
    brackets). The font folders are indexed once and cached."""
    global _LOGO_FONT_INDEX
    if key in _LOGO_FONT_PATHS:
        return _LOGO_FONT_PATHS[key]
    if _LOGO_FONT_INDEX is None:
        wanted = {n for names in _LOGO_FONT_FILES.values() for n in names}
        _LOGO_FONT_INDEX = {}
        # Fonts dropped straight next to bot.py (repo root) — top level only.
        with contextlib.suppress(Exception):
            here = Path(__file__).resolve().parent
            for fname in os.listdir(here):
                if fname in wanted:
                    _LOGO_FONT_INDEX[fname] = here / fname
        for base in _LOGO_FONT_DIRS:
            if not base.exists():
                continue
            for root, _dirs, files in os.walk(base):
                for fname in files:
                    if fname in wanted and fname not in _LOGO_FONT_INDEX:
                        _LOGO_FONT_INDEX[fname] = Path(root) / fname
    found = next((_LOGO_FONT_INDEX[n] for n in _LOGO_FONT_FILES.get(key, ()) if n in _LOGO_FONT_INDEX), None)
    _LOGO_FONT_PATHS[key] = found
    return found


def _logo_font(key, size, weight=None):
    from PIL import ImageFont
    size = max(8, int(size))
    path = _logo_font_path(key) or _logo_font_path("fallback")
    if not path:
        try:
            return ImageFont.load_default(size)
        except Exception:
            return ImageFont.load_default()
    try:
        font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
    except Exception:
        font = ImageFont.truetype(str(path), size)
    if weight:
        with contextlib.suppress(Exception):
            axes = font.get_variation_axes()
            font.set_variation_by_axes([
                max(a.get("minimum", weight), min(a.get("maximum", weight), weight))
                if str(a.get("name", b"")).lower().find("weight") >= 0 or i == 0 else a.get("default", 0)
                for i, a in enumerate(axes)
            ])
    return font


def _logo_shape_rtl(text):
    """Only needed when Pillow has no libraqm: fall back to arabic_reshaper."""
    from PIL import features
    if not _LOGO_RTL_RE.search(text) or features.check("raqm"):
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _logo_text_masks(text, font, tracking=0, stroke=0):
    """Returns (fill_mask, outer_mask) of identical size, tightly cropped.
    outer_mask = glyphs thickened by `stroke` (used for outlines)."""
    from PIL import Image, ImageDraw
    pad = stroke + 6
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    per_char = bool(tracking) and not _LOGO_RTL_RE.search(text) and len(text) > 1
    if per_char:
        widths = [font.getlength(ch) for ch in text]
        l, t, r, b = probe.textbbox((0, 0), text, font=font, stroke_width=stroke)
        w = int(sum(widths) + tracking * (len(text) - 1) + pad * 2 + abs(l) + 4)
        h = int(b - min(t, 0) + pad * 2)
        fill = Image.new("L", (w, h), 0)
        outer = Image.new("L", (w, h), 0)
        df, do = ImageDraw.Draw(fill), ImageDraw.Draw(outer)
        x, y = pad - min(l, 0), pad - min(t, 0)
        for ch, cw in zip(text, widths):
            df.text((x, y), ch, font=font, fill=255)
            do.text((x, y), ch, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
            x += cw + tracking
    else:
        l, t, r, b = probe.textbbox((0, 0), text, font=font, stroke_width=stroke)
        w, h = int(r - l + pad * 2), int(b - t + pad * 2)
        fill = Image.new("L", (w, h), 0)
        outer = Image.new("L", (w, h), 0)
        ImageDraw.Draw(fill).text((pad - l, pad - t), text, font=font, fill=255)
        ImageDraw.Draw(outer).text((pad - l, pad - t), text, font=font, fill=255,
                                   stroke_width=stroke, stroke_fill=255)
    box = outer.getbbox() or (0, 0, outer.width, outer.height)
    return fill.crop(box), outer.crop(box)


def _logo_fit(text, key, weight, max_w, max_h, tracking=0.0, stroke=0.0):
    size = int(max_h * 1.25)
    best = None
    for _ in range(8):
        font = _logo_font(key, size, weight)
        fm, om = _logo_text_masks(text, font, int(size * tracking), int(size * stroke))
        scale = min(max_w / max(1, om.width), max_h / max(1, om.height))
        best = (font, fm, om, size)
        if 0.94 <= scale <= 1.0:
            break
        size = max(10, int(size * scale * 0.985))
    font, fm, om, size = best
    while (om.width > max_w or om.height > max_h) and size > 10:
        size = int(size * 0.93)
        font = _logo_font(key, size, weight)
        fm, om = _logo_text_masks(text, font, int(size * tracking), int(size * stroke))
    return fm, om, size


def _logo_ramp(gray, stops):
    """Map an L image through colour stops [(pos 0..1, (r,g,b[,a])), ...] -> RGBA."""
    from PIL import Image
    stops = [(p, tuple(c) + ((255,) if len(c) == 3 else ())) for p, c in stops]
    luts = [[], [], [], []]
    for i in range(256):
        t = i / 255
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if t <= p1 or (p1 == stops[-1][0]):
                k = 0 if p1 == p0 else min(1, max(0, (t - p0) / (p1 - p0)))
                col = [int(c0[j] + (c1[j] - c0[j]) * k) for j in range(4)]
                break
        else:
            col = list(stops[-1][1])
        if t < stops[0][0]:
            col = list(stops[0][1])
        for j in range(4):
            luts[j].append(col[j])
    return Image.merge("RGBA", [gray.point(l) for l in luts])


def _logo_linear(size, stops, angle=90):
    from PIL import Image
    w, h = size
    d = int(math.hypot(w, h)) + 4
    g = Image.linear_gradient("L").resize((d, d), Image.BILINEAR).rotate(90 - angle, resample=Image.BICUBIC)
    l, t = (d - w) // 2, (d - h) // 2
    return _logo_ramp(g.crop((l, t, l + w, t + h)), stops)


def _logo_radial(size, stops, center=None, radius=None):
    from PIL import Image
    w, h = size
    cx, cy = center or (w / 2, h / 2)
    r = int(radius or math.hypot(w, h) / 2)
    g = Image.new("L", (w, h), 255)
    g.paste(Image.radial_gradient("L").resize((r * 2, r * 2), Image.BILINEAR), (int(cx - r), int(cy - r)))
    return _logo_ramp(g, stops)


def _logo_place(canvas, layer, x, y):
    from PIL import Image
    full = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    full.paste(layer, (int(x), int(y)))
    canvas.alpha_composite(full)


def _logo_fill(mask, paint):
    """paint: RGB tuple or RGBA image the size of mask."""
    from PIL import Image, ImageChops
    if isinstance(paint, tuple):
        layer = Image.new("RGBA", mask.size, paint[:3] + (255,))
        alpha = mask if len(paint) == 3 else mask.point(lambda v, a=paint[3]: v * a // 255)
    else:
        layer = paint.copy()
        alpha = ImageChops.multiply(layer.getchannel("A"), mask)
    layer.putalpha(alpha)
    return layer


def _logo_glow(canvas, mask, x, y, color, radius, strength=1.0):
    from PIL import Image, ImageFilter
    pad = int(radius * 3) + 2
    m = Image.new("L", (mask.width + pad * 2, mask.height + pad * 2), 0)
    m.paste(mask, (pad, pad))
    m = m.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        m = m.point(lambda v: min(255, int(v * strength)))
    _logo_place(canvas, _logo_fill(m, tuple(color)), x - pad, y - pad)


def _logo_finish(canvas, rng, grain=10, vignette=120):
    from PIL import Image
    w, h = canvas.size
    if vignette:
        v = _logo_radial((w, h), [(0, (0, 0, 0, 0)), (0.55, (0, 0, 0, 0)), (1, (0, 0, 0, vignette))],
                         radius=int(math.hypot(w, h) / 2))
        canvas.alpha_composite(v)
    if grain:
        n = Image.effect_noise((w // 2, h // 2), 48).resize((w, h))
        layer = Image.merge("RGBA", (n, n, n, Image.new("L", (w, h), grain)))
        canvas.alpha_composite(layer)
    return canvas


def _logo_sparkle(draw, x, y, s, color):
    k = s * 0.16
    draw.polygon([(x, y - s), (x + k, y - k), (x + s, y), (x + k, y + k),
                  (x, y + s), (x - k, y + k), (x - s, y), (x - k, y - k)], fill=color)


def _logo_blobs(size, blobs, blur):
    from PIL import Image, ImageDraw, ImageFilter
    w, h = size
    small = Image.new("RGBA", (w // 8, h // 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(small)
    for cx, cy, r, col in blobs:
        d.ellipse(((cx - r) * w / 8, (cy - r) * h / 8, (cx + r) * w / 8, (cy + r) * h / 8), fill=col)
    small = small.filter(ImageFilter.GaussianBlur(blur))
    return small.resize((w, h), Image.BICUBIC)


def _logo_render_sync(template_id: int, text_value: str):
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    import random as _rnd

    template = LOGO_TEMPLATES[template_id][0]
    raw = text_value.replace("\n", " ").strip()
    title, _, subtitle = raw.partition("|")
    title, subtitle = _logo_shape_rtl(title.strip() or "HTX"), _logo_shape_rtl(subtitle.strip())
    rtl = bool(_LOGO_RTL_RE.search(title))
    sub_rtl = bool(_LOGO_RTL_RE.search(subtitle))
    rng = _rnd.Random(f"{template_id}:{raw}")

    W, H = int(_LOGO_OUT_W * _LOGO_SS), int(_LOGO_OUT_H * _LOGO_SS)
    u = W / 1600
    cx, cy = W // 2, H // 2

    def tfont(key):  # Persian text always uses Vazirmatn Black
        return ("vazir", 900) if rtl else key

    def sfont(key):
        return ("vazir", 700) if sub_rtl else key

    def fit_title(key, weight, max_w, max_h, tracking=0.0, stroke=0.0):
        k, wgt = tfont((key, weight)) if not rtl else ("vazir", 900)
        return _logo_fit(title, k, wgt, max_w, max_h, 0 if rtl else tracking, stroke)

    def fit_sub(key, weight, max_w, max_h, tracking=0.25):
        if not subtitle:
            return None
        k, wgt = ("vazir", 700) if sub_rtl else (key, weight)
        text = subtitle if sub_rtl else subtitle.upper()
        return _logo_fit(text, k, wgt, max_w, max_h * (1.6 if sub_rtl else 1.0), 0 if sub_rtl else tracking)[0]

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    if template == "classic":  # Royal gold
        canvas.alpha_composite(_logo_radial((W, H), [(0, (30, 38, 66)), (0.7, (10, 13, 26)), (1, (4, 5, 12))]))
        gold = [(0, (255, 240, 185)), (0.42, (226, 178, 72)), (0.52, (150, 98, 26)), (0.7, (214, 160, 60)), (1, (255, 226, 140))]
        d = ImageDraw.Draw(canvas)
        for inset, wd in ((70 * u, int(5 * u)), (92 * u, int(2 * u))):
            d.rectangle((inset, inset, W - inset, H - inset), outline=(205, 160, 70), width=wd)
        for px, py in ((81 * u, 81 * u), (W - 81 * u, 81 * u), (81 * u, H - 81 * u), (W - 81 * u, H - 81 * u)):
            s = 18 * u
            d.polygon([(px, py - s), (px + s, py), (px, py + s), (px - s, py)], fill=(230, 190, 95))
        fm, om, _ = fit_title("cinzel", 900, W * 0.72, H * 0.26)
        tx, ty = cx - fm.width // 2, int(cy - fm.height * 0.62)
        _logo_glow(canvas, fm, tx + int(8 * u), ty + int(12 * u), (0, 0, 0), 14 * u, 1.4)
        _logo_glow(canvas, fm, tx, ty, (255, 190, 80), 40 * u, 0.35)
        _logo_place(canvas, _logo_fill(fm, _logo_linear(fm.size, gold, 90)), tx, ty)
        ly = ty + fm.height + 60 * u
        d = ImageDraw.Draw(canvas)
        d.line((cx - 330 * u, ly, cx - 30 * u, ly), fill=(205, 160, 70), width=int(3 * u))
        d.line((cx + 30 * u, ly, cx + 330 * u, ly), fill=(205, 160, 70), width=int(3 * u))
        s = 13 * u
        d.polygon([(cx, ly - s), (cx + s, ly), (cx, ly + s), (cx - s, ly)], fill=(240, 200, 110))
        sm = fit_sub("montserrat", 600, W * 0.6, 44 * u, 0.42)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (232, 200, 130)), cx - sm.width // 2, ly + 45 * u)
        _logo_finish(canvas, rng, grain=9, vignette=150)

    elif template == "neon":  # Synthwave neon
        canvas.alpha_composite(_logo_linear((W, H), [(0, (8, 4, 24)), (0.6, (28, 6, 48)), (1, (60, 8, 70))], 90))
        grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(grid)
        hy = int(H * 0.66)
        for i in range(1, 14):
            y = hy + (H - hy) * (i / 13) ** 1.8
            g.line((0, y, W, y), fill=(255, 60, 200, 90), width=max(1, int(2 * u)))
        for i in range(-16, 17):
            g.line((cx + i * 40 * u, hy, cx + i * 260 * u, H), fill=(255, 60, 200, 80), width=max(1, int(2 * u)))
        grid.putalpha(ImageChops.multiply(grid.getchannel("A"), _logo_linear((W, H), [(0, (0, 0, 0)), (0.62, (0, 0, 0)), (1, (255, 255, 255))], 90).getchannel("R")))
        canvas.alpha_composite(grid)
        canvas.alpha_composite(_logo_radial((W, H), [(0, (255, 60, 180, 90)), (1, (0, 0, 0, 0))], (cx, hy), int(700 * u)))
        fm, om, size = fit_title("audiowide", None, W * 0.78, H * 0.25, stroke=0.035)
        tx, ty = cx - om.width // 2, int(H * 0.42 - om.height / 2)
        ring = ImageChops.subtract(om, fm)
        _logo_glow(canvas, om, tx, ty, (255, 40, 200), 55 * u, 1.3)
        _logo_glow(canvas, om, tx, ty, (255, 90, 230), 16 * u, 2.2)
        _logo_place(canvas, _logo_fill(ring, (255, 170, 240)), tx, ty)
        _logo_place(canvas, _logo_fill(fm, (255, 245, 255)), tx, ty)
        sm = fit_sub("montserrat", 700, W * 0.6, 46 * u, 0.45)
        if sm:
            sx, sy = cx - sm.width // 2, ty + om.height + 60 * u
            _logo_glow(canvas, sm, sx, sy, (0, 230, 255), 14 * u, 2.0)
            _logo_place(canvas, _logo_fill(sm, (210, 255, 255)), sx, sy)
        _logo_finish(canvas, rng, grain=8, vignette=140)

    elif template == "minimal":  # Mark + wordmark
        canvas.alpha_composite(Image.new("RGBA", (W, H), (246, 244, 239, 255)))
        mark = int(H * 0.25)
        fm, om, _ = fit_title("montserrat", 800, W * 0.58, H * 0.17, tracking=0.04)
        sm = fit_sub("montserrat", 500, W * 0.5, 34 * u, 0.35)
        block_h = max(mark, fm.height + (sm.height + 40 * u if sm else 0))
        total_w = mark + 70 * u + fm.width
        mx, my = int(cx - total_w / 2), int(cy - mark / 2)
        sh = Image.new("L", (mark, mark), 0)
        ImageDraw.Draw(sh).rounded_rectangle((0, 0, mark - 1, mark - 1), radius=int(mark * 0.26), fill=255)
        _logo_glow(canvas, sh, mx, my + int(18 * u), (0, 0, 0, 90), 22 * u, 1.0)
        _logo_place(canvas, _logo_fill(sh, _logo_linear((mark, mark), [(0, (255, 98, 64)), (1, (230, 40, 90))], 45)), mx, my)
        initial = title.strip()[:1].upper()
        if rtl:
            initial += "\u200d"  # joined (initial) form, so «ه» doesn't read like the digit ۵
        im = _logo_fit(initial, "vazir" if rtl else "montserrat", 900, mark * 0.6, mark * 0.52)[0]
        _logo_place(canvas, _logo_fill(im, (255, 255, 255)), mx + (mark - im.width) // 2, my + (mark - im.height) // 2)
        wx = mx + mark + 70 * u
        wy = int(cy - (fm.height + (sm.height + 36 * u if sm else 0)) / 2)
        _logo_place(canvas, _logo_fill(fm, (22, 22, 28)), wx, wy)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (120, 118, 128)), wx + 4 * u, wy + fm.height + 36 * u)
        _logo_finish(canvas, rng, grain=6, vignette=0)

    elif template == "badge":  # Emblem with ribbon
        canvas.alpha_composite(_logo_radial((W, H), [(0, (22, 58, 46)), (1, (4, 14, 11))]))
        R = int(H * 0.40)
        gold = [(0, (255, 232, 160)), (0.5, (190, 140, 50)), (1, (255, 215, 120))]
        disc = Image.new("L", (R * 2, R * 2), 0)
        ImageDraw.Draw(disc).ellipse((0, 0, R * 2 - 1, R * 2 - 1), fill=255)
        _logo_glow(canvas, disc, cx - R, cy - R + int(20 * u), (0, 0, 0), 30 * u, 1.2)
        _logo_place(canvas, _logo_fill(disc, _logo_linear(disc.size, gold, 60)), cx - R, cy - R)
        inner = Image.new("L", (R * 2, R * 2), 0)
        di = ImageDraw.Draw(inner)
        e = int(R * 0.09)
        di.ellipse((e, e, R * 2 - e, R * 2 - e), fill=255)
        _logo_place(canvas, _logo_fill(inner, _logo_radial(inner.size, [(0, (26, 74, 58)), (1, (10, 34, 27))])), cx - R, cy - R)
        d = ImageDraw.Draw(canvas)
        r2 = R - e - 22 * u
        d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(214, 172, 86), width=int(3 * u))
        for i in range(72):
            a = i / 72 * math.tau
            px, py = cx + math.cos(a) * (r2 - 20 * u), cy + math.sin(a) * (r2 - 20 * u)
            d.ellipse((px - 3 * u, py - 3 * u, px + 3 * u, py + 3 * u), fill=(214, 172, 86))
        for k, off in enumerate((-110, 0, 110)):
            _logo_sparkle(d, cx + off * u, cy - R * 0.52 - (12 * u if off == 0 else 0), (30 if off == 0 else 22) * u, (240, 205, 120))
        rh = int(H * 0.19)
        rw = int(R * 2.5)
        rx0, ry0 = cx - rw // 2, cy - rh // 2
        notch = int(rh * 0.35)
        for side in (-1, 1):
            ex = cx + side * rw // 2
            tail = [(ex, ry0 + 30 * u), (ex + side * 150 * u, ry0 + 30 * u), (ex + side * (150 * u - notch), ry0 + 30 * u + rh / 2),
                    (ex + side * 150 * u, ry0 + 30 * u + rh), (ex, ry0 + 30 * u + rh)]
            d.polygon(tail, fill=(120, 18, 30))
        rib = Image.new("L", (rw, rh), 255)
        _logo_glow(canvas, rib, rx0, ry0 + int(10 * u), (0, 0, 0), 16 * u, 1.0)
        _logo_place(canvas, _logo_fill(rib, _logo_linear((rw, rh), [(0, (200, 40, 52)), (1, (140, 20, 34))], 90)), rx0, ry0)
        d = ImageDraw.Draw(canvas)
        d.rectangle((rx0, ry0 + 10 * u, rx0 + rw, ry0 + 14 * u), fill=(240, 200, 110))
        d.rectangle((rx0, ry0 + rh - 14 * u, rx0 + rw, ry0 + rh - 10 * u), fill=(240, 200, 110))
        fm, om, _ = fit_title("bebas", None, rw * 0.86, rh * 0.62, tracking=0.06)
        _logo_glow(canvas, fm, cx - fm.width // 2 + int(4 * u), cy - fm.height // 2 + int(6 * u), (60, 0, 10), 6 * u, 1.3)
        _logo_place(canvas, _logo_fill(fm, _logo_linear(fm.size, [(0, (255, 250, 230)), (1, (245, 215, 150))], 90)), cx - fm.width // 2, cy - fm.height // 2)
        sm = fit_sub("montserrat", 700, R * 1.2, 34 * u, 0.35)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (236, 200, 120)), cx - sm.width // 2, cy + R * 0.42)
        _logo_finish(canvas, rng, grain=8, vignette=130)

    elif template == "shadow":  # Flat long shadow
        canvas.alpha_composite(_logo_linear((W, H), [(0, (255, 138, 60)), (1, (240, 52, 110))], 35))
        fm, om, _ = fit_title("anton", None, W * 0.74, H * 0.36, tracking=0.02)
        tx, ty = cx - fm.width // 2, int(cy - fm.height * 0.62)
        L = int(520 * u)
        shm = Image.new("L", (fm.width + L, fm.height + L), 0)
        step = max(1, int(2 * u))
        for i in range(0, L, step):
            shm.paste(255, (i, i), fm)
        fade = _logo_linear(shm.size, [(0, (255, 255, 255)), (0.75, (0, 0, 0))], 45).getchannel("R")
        shm = ImageChops.multiply(shm, fade)
        _logo_place(canvas, _logo_fill(shm, (120, 10, 40, 150)), tx, ty)
        _logo_place(canvas, _logo_fill(fm, (255, 255, 255)), tx, ty)
        sm = fit_sub("montserrat", 800, W * 0.55, 40 * u, 0.4)
        if sm:
            pw, ph = sm.width + 90 * u, sm.height + 50 * u
            px, py = cx - pw / 2, ty + fm.height + 70 * u
            ImageDraw.Draw(canvas).rounded_rectangle((px, py, px + pw, py + ph), radius=int(ph / 2), fill=(255, 255, 255))
            _logo_place(canvas, _logo_fill(sm, (235, 60, 95)), cx - sm.width // 2, py + (ph - sm.height) / 2)
        _logo_finish(canvas, rng, grain=7, vignette=70)

    elif template == "gradient":  # Aurora glass card
        canvas.alpha_composite(Image.new("RGBA", (W, H), (12, 10, 30, 255)))
        canvas.alpha_composite(_logo_blobs((W, H), [
            (2.0, 2.2, 2.2, (120, 60, 255, 255)), (6.2, 1.6, 2.0, (255, 70, 170, 255)),
            (5.4, 6.4, 2.3, (255, 150, 60, 230)), (1.4, 6.6, 1.9, (40, 180, 255, 240)),
            (4.0, 4.0, 1.4, (190, 90, 255, 200))], 22))
        fm, om, _ = fit_title("poppins", None, W * 0.66, H * 0.24)
        sm = fit_sub("montserrat", 600, W * 0.5, 36 * u, 0.38)
        cw = int(max(fm.width, sm.width if sm else 0) + 220 * u)
        ch = int(fm.height + (sm.height + 50 * u if sm else 0) + 200 * u)
        card = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(card).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=int(60 * u), fill=255)
        kx, ky = cx - cw // 2, cy - ch // 2
        _logo_glow(canvas, card, kx, ky + int(30 * u), (0, 0, 0), 40 * u, 0.8)
        blurred = canvas.crop((kx, ky, kx + cw, ky + ch)).filter(ImageFilter.GaussianBlur(30 * u))
        blurred.putalpha(card)
        _logo_place(canvas, blurred, kx, ky)
        _logo_place(canvas, _logo_fill(card, (255, 255, 255, 34)), kx, ky)
        ImageDraw.Draw(canvas).rounded_rectangle((kx, ky, kx + cw, ky + ch), radius=int(60 * u), outline=(255, 255, 255, 110), width=int(3 * u))
        tx, ty = cx - fm.width // 2, ky + int(100 * u)
        _logo_glow(canvas, fm, tx, ty + int(10 * u), (20, 0, 60), 18 * u, 0.9)
        _logo_place(canvas, _logo_fill(fm, _logo_linear(fm.size, [(0, (255, 255, 255)), (1, (225, 215, 255))], 90)), tx, ty)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (255, 255, 255, 215)), cx - sm.width // 2, ty + fm.height + 50 * u)
        _logo_finish(canvas, rng, grain=10, vignette=90)

    elif template == "outline":  # Cyber HUD outline
        canvas.alpha_composite(_logo_radial((W, H), [(0, (16, 22, 34)), (1, (4, 6, 10))]))
        d = ImageDraw.Draw(canvas)
        for i in range(-H, W, int(36 * u)):
            d.line((i, 0, i + H, H), fill=(255, 255, 255, 8), width=1)
        fm, om, size = fit_title("orbitron", 900, W * 0.76, H * 0.24, tracking=0.05, stroke=0.035)
        ring = ImageChops.subtract(om, fm)
        tx, ty = cx - om.width // 2, int(cy - om.height * 0.6)
        for dx, col in ((-14, (255, 40, 120, 110)), (14, (0, 220, 255, 110))):
            _logo_place(canvas, _logo_fill(ring, col), tx + dx * u, ty)
        grad = _logo_linear(om.size, [(0, (0, 240, 255)), (0.5, (140, 110, 255)), (1, (255, 60, 200))], 0)
        _logo_glow(canvas, ring, tx, ty, (80, 160, 255), 18 * u, 1.3)
        _logo_place(canvas, _logo_fill(fm, (10, 14, 22, 235)), tx, ty)
        _logo_place(canvas, _logo_fill(ring, grad), tx, ty)
        m, bl = 110 * u, 90 * u
        d = ImageDraw.Draw(canvas)
        for (x0, y0, sx, sy) in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
            d.line((x0, y0, x0 + sx * bl, y0), fill=(0, 230, 255), width=int(5 * u))
            d.line((x0, y0, x0, y0 + sy * bl), fill=(0, 230, 255), width=int(5 * u))
        sm = fit_sub("jetbrains", 700, W * 0.55, 38 * u, 0.3)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (120, 230, 255)), cx - sm.width // 2, ty + om.height + 70 * u)
        _logo_finish(canvas, rng, grain=8, vignette=140)

    elif template == "split":  # Diagonal duotone
        A, B = (18, 22, 38), (255, 200, 0)
        canvas.alpha_composite(Image.new("RGBA", (W, H), A + (255,)))
        right = Image.new("L", (W, H), 0)
        ImageDraw.Draw(right).polygon([(W * 0.56, 0), (W, 0), (W, H), (W * 0.44, H)], fill=255)
        _logo_place(canvas, _logo_fill(right, B), 0, 0)
        fm, om, _ = fit_title("anton", None, W * 0.8, H * 0.38, tracking=0.03)
        tx, ty = cx - fm.width // 2, int(cy - fm.height * 0.6)

        def duo(mask, x, y):
            full = Image.new("L", (W, H), 0)
            full.paste(mask, (int(x), int(y)))
            _logo_place(canvas, _logo_fill(ImageChops.multiply(full, ImageChops.invert(right)), B), 0, 0)
            _logo_place(canvas, _logo_fill(ImageChops.multiply(full, right), A), 0, 0)

        duo(fm, tx, ty)
        sm = fit_sub("montserrat", 800, W * 0.6, 40 * u, 0.5)
        if sm:
            duo(sm, cx - sm.width // 2, ty + fm.height + 60 * u)
        _logo_finish(canvas, rng, grain=7, vignette=60)

    elif template == "glow":  # Molten gold + reflection
        canvas.alpha_composite(_logo_radial((W, H), [(0, (70, 24, 4)), (0.6, (18, 6, 2)), (1, (4, 2, 1))], (cx, H * 0.72), int(H)))
        emb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        e = ImageDraw.Draw(emb)
        for _ in range(140):
            x, y, r = rng.uniform(0, W), rng.uniform(H * 0.1, H), rng.uniform(1.5, 6) * u
            e.ellipse((x - r, y - r, x + r, y + r), fill=(255, rng.randint(120, 200), 40, rng.randint(60, 200)))
        canvas.alpha_composite(emb.filter(ImageFilter.GaussianBlur(1.5 * u)))
        fm, om, _ = fit_title("playfair", 900, W * 0.76, H * 0.27)
        tx, ty = cx - fm.width // 2, int(H * 0.42 - fm.height / 2)
        fire = [(0, (255, 252, 225)), (0.45, (255, 200, 80)), (0.8, (240, 110, 20)), (1, (190, 60, 10))]
        _logo_glow(canvas, fm, tx, ty, (255, 120, 20), 60 * u, 0.9)
        _logo_glow(canvas, fm, tx, ty, (255, 190, 80), 14 * u, 1.2)
        _logo_place(canvas, _logo_fill(fm, _logo_linear(fm.size, fire, 90)), tx, ty)
        refl = _logo_fill(fm.transpose(Image.FLIP_TOP_BOTTOM), _logo_linear(fm.size, fire[::-1], 90))
        refl.putalpha(ImageChops.multiply(refl.getchannel("A"), _logo_linear(fm.size, [(0, (90, 90, 90)), (0.6, (0, 0, 0))], 90).getchannel("R")))
        _logo_place(canvas, refl.filter(ImageFilter.GaussianBlur(2 * u)), tx, ty + fm.height + 14 * u)
        sm = fit_sub("montserrat", 600, W * 0.55, 38 * u, 0.45)
        if sm:
            _logo_place(canvas, _logo_fill(sm, (255, 214, 150)), cx - sm.width // 2, H * 0.84)
        _logo_finish(canvas, rng, grain=9, vignette=150)

    elif template == "terminal":  # Hacker terminal window
        canvas.alpha_composite(_logo_linear((W, H), [(0, (22, 26, 38)), (1, (8, 10, 16))], 70))
        ww, wh = int(W * 0.8), int(H * 0.66)
        wx, wy = cx - ww // 2, cy - wh // 2
        win = Image.new("L", (ww, wh), 0)
        ImageDraw.Draw(win).rounded_rectangle((0, 0, ww - 1, wh - 1), radius=int(28 * u), fill=255)
        _logo_glow(canvas, win, wx, wy + int(30 * u), (0, 0, 0), 40 * u, 1.2)
        _logo_place(canvas, _logo_fill(win, (24, 27, 36)), wx, wy)
        bar = int(74 * u)
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle((wx, wy, wx + ww, wy + bar), radius=int(28 * u), fill=(40, 44, 58))
        d.rectangle((wx, wy + bar - 28 * u, wx + ww, wy + bar), fill=(40, 44, 58))
        for i, col in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            bx = wx + 50 * u + i * 44 * u
            d.ellipse((bx - 13 * u, wy + bar / 2 - 13 * u, bx + 13 * u, wy + bar / 2 + 13 * u), fill=col)
        tb = _logo_fit("~/brand — zsh", "jetbrains", 500, ww * 0.4, 26 * u)[0]
        _logo_place(canvas, _logo_fill(tb, (150, 155, 175)), cx - tb.width // 2, wy + (bar - tb.height) / 2)
        pm = _logo_fit("$ ./logo --render", "jetbrains", 600, ww * 0.6, 34 * u)[0]
        _logo_place(canvas, _logo_fill(pm, (120, 130, 150)), wx + 70 * u, wy + bar + 60 * u)
        fm, om, size = fit_title("jetbrains", 800, ww * 0.74, wh * 0.28)
        tx, ty = wx + int(70 * u), int(wy + bar + (wh - bar) / 2 - fm.height / 2 + 10 * u)
        _logo_glow(canvas, fm, tx, ty, (60, 255, 120), 22 * u, 1.1)
        _logo_place(canvas, _logo_fill(fm, (90, 255, 140)), tx, ty)
        d = ImageDraw.Draw(canvas)
        cxr = tx + fm.width + 26 * u
        d.rectangle((cxr, ty, cxr + fm.height * 0.5, ty + fm.height), fill=(90, 255, 140))
        if subtitle:
            sm = _logo_fit(("// " + subtitle) if not sub_rtl else subtitle, "vazir" if sub_rtl else "jetbrains", 500, ww * 0.8, 36 * u)[0]
            _logo_place(canvas, _logo_fill(sm, (110, 120, 140)), wx + 70 * u, ty + fm.height + 60 * u)
        scan = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
        s = ImageDraw.Draw(scan)
        for y in range(0, wh, max(2, int(5 * u))):
            s.line((0, y, ww, y), fill=(0, 0, 0, 40))
        scan.putalpha(ImageChops.multiply(scan.getchannel("A"), win))
        _logo_place(canvas, scan, wx, wy)
        _logo_finish(canvas, rng, grain=7, vignette=120)

    elif template == "stamp":  # Distressed rubber stamp
        canvas.alpha_composite(_logo_radial((W, H), [(0, (240, 233, 214)), (1, (214, 202, 176))]))
        sw, shh = int(W * 0.74), int(H * 0.56)
        st = Image.new("L", (sw, shh), 0)
        d = ImageDraw.Draw(st)
        d.rounded_rectangle((0, 0, sw - 1, shh - 1), radius=int(30 * u), outline=255, width=int(16 * u))
        d.rounded_rectangle((34 * u, 34 * u, sw - 34 * u, shh - 34 * u), radius=int(18 * u), outline=255, width=int(5 * u))
        fm, om, _ = fit_title("blackops", None, sw * 0.8, shh * 0.42, tracking=0.03)
        fy = int(shh * 0.44 - fm.height / 2)
        st.paste(255, ((sw - fm.width) // 2, fy), fm)
        ly = fy + fm.height + 40 * u
        d.line((80 * u, ly, sw - 80 * u, ly), fill=255, width=int(5 * u))
        sub = subtitle or "★ ★ ★ ★ ★"
        sm = _logo_fit(sub if sub_rtl or not subtitle else sub.upper(), "vazir" if sub_rtl else ("montserrat" if subtitle else "fallback"), 800, sw * 0.7, 46 * u, 0 if sub_rtl else 0.3)[0]
        st.paste(255, ((sw - sm.width) // 2, int(ly + 30 * u)), sm)
        wear = Image.effect_noise((sw // 3, shh // 3), 90).resize((sw, shh)).filter(ImageFilter.GaussianBlur(1.2 * u))
        wear = wear.point(lambda v: 0 if v < 70 else (255 if v > 110 else (v - 70) * 6))
        st = ImageChops.multiply(st, wear)
        layer = _logo_fill(st, (184, 28, 40, 230)).rotate(-7, resample=Image.BICUBIC, expand=True)
        _logo_place(canvas, layer, cx - layer.width // 2, cy - layer.height // 2)
        _logo_finish(canvas, rng, grain=16, vignette=90)

    else:  # diamond — luxury chrome
        canvas.alpha_composite(_logo_radial((W, H), [(0, (34, 34, 42)), (0.7, (8, 8, 12)), (1, (0, 0, 0))]))
        gy, gs = int(H * 0.25), int(H * 0.13)
        gem = [(cx - gs, gy), (cx - gs * 0.55, gy - gs * 0.55), (cx + gs * 0.55, gy - gs * 0.55), (cx + gs, gy), (cx, gy + gs * 1.1)]
        facets = [
            ([(cx - gs, gy), (cx - gs * 0.55, gy - gs * 0.55), (cx - gs * 0.2, gy)], (200, 225, 255)),
            ([(cx - gs * 0.55, gy - gs * 0.55), (cx + gs * 0.55, gy - gs * 0.55), (cx, gy)], (245, 250, 255)),
            ([(cx + gs, gy), (cx + gs * 0.55, gy - gs * 0.55), (cx + gs * 0.2, gy)], (150, 180, 220)),
            ([(cx - gs, gy), (cx, gy + gs * 1.1), (cx - gs * 0.2, gy)], (120, 160, 210)),
            ([(cx - gs * 0.2, gy), (cx + gs * 0.2, gy), (cx, gy + gs * 1.1)], (210, 230, 255)),
            ([(cx + gs, gy), (cx, gy + gs * 1.1), (cx + gs * 0.2, gy)], (80, 110, 160)),
            ([(cx - gs * 0.2, gy), (cx - gs * 0.55, gy - gs * 0.55), (cx, gy)], (170, 200, 240)),
            ([(cx + gs * 0.2, gy), (cx + gs * 0.55, gy - gs * 0.55), (cx, gy)], (230, 240, 255)),
        ]
        gm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(gm).polygon(gem, fill=255)
        _logo_glow(canvas, gm.crop(gm.getbbox()), int(cx - gs), int(gy - gs * 0.55), (140, 190, 255), 40 * u, 0.9)
        d = ImageDraw.Draw(canvas)
        for poly, col in facets:
            d.polygon(poly, fill=col)
        d.line(gem + [gem[0]], fill=(255, 255, 255), width=int(3 * u))
        chrome = [(0, (255, 255, 255)), (0.42, (178, 192, 212)), (0.5, (70, 78, 96)), (0.62, (205, 216, 232)), (1, (250, 252, 255))]
        fm, om, _ = fit_title("cinzel", 900, W * 0.76, H * 0.22, tracking=0.03, stroke=0.012)
        tx, ty = cx - om.width // 2, int(H * 0.55 - om.height / 2)
        _logo_glow(canvas, om, tx, ty + int(10 * u), (0, 0, 0), 12 * u, 1.3)
        _logo_place(canvas, _logo_fill(ImageChops.subtract(om, fm), (255, 255, 255, 180)), tx, ty)
        _logo_place(canvas, _logo_fill(fm, _logo_linear(fm.size, chrome, 90)), tx + (om.width - fm.width) // 2, ty + (om.height - fm.height) // 2)
        d = ImageDraw.Draw(canvas)
        for _ in range(9):
            x = rng.uniform(tx, tx + om.width)
            y = rng.uniform(ty - 20 * u, ty + om.height * 0.5)
            _logo_sparkle(d, x, y, rng.uniform(10, 26) * u, (255, 255, 255, 230))
        _logo_sparkle(d, cx + gs * 0.6, gy - gs * 0.5, 34 * u, (255, 255, 255))
        ly = ty + om.height + 60 * u
        sm = fit_sub("montserrat", 500, W * 0.55, 36 * u, 0.55)
        half = (sm.width / 2 + 50 * u) if sm else 20 * u
        d.line((cx - half - 240 * u, ly + 18 * u, cx - half, ly + 18 * u), fill=(170, 180, 200), width=int(2 * u))
        d.line((cx + half, ly + 18 * u, cx + half + 240 * u, ly + 18 * u), fill=(170, 180, 200), width=int(2 * u))
        if sm:
            _logo_place(canvas, _logo_fill(sm, (205, 212, 226)), cx - sm.width // 2, ly + 18 * u - sm.height / 2)
        _logo_finish(canvas, rng, grain=8, vignette=160)

    final = canvas.convert("RGB").resize((_LOGO_OUT_W, _LOGO_OUT_H), Image.LANCZOS)
    output = BytesIO()
    final.save(output, format="JPEG", quality=95, subsampling=0, optimize=True)
    return output.getvalue()

async def generate_logo(template_id: int, text: str):
    if template_id not in LOGO_TEMPLATES:
        raise ValueError("invalid_logo_template")
    if not text.strip():
        raise ValueError("empty_logo_text")
    return await asyncio.to_thread(_logo_render_sync, int(template_id), text.strip())

async def send_generated_image(event, media, caption, filename="generated.jpg"):
    """Shared Telegram media layer for generated bytes."""
    from io import BytesIO
    if isinstance(media, (bytes, bytearray)):
        stream = BytesIO(media)
        stream.name = filename
        await event.client.send_file(event.chat_id, stream, caption=caption, parse_mode="html")
        return True
    if isinstance(media, (str, Path)):
        await event.client.send_file(event.chat_id, str(media), caption=caption, parse_mode="html")
        return True
    if _valid_http_url(media):
        await event.client.send_file(event.chat_id, media, caption=caption, parse_mode="html")
        return True
    raise ValueError("unsupported_media")

LOGO_TITLE_MAX = 30
LOGO_SUBTITLE_MAX = 40
_LOGO_URL_RE = re.compile(r"(https?://|www\.|\.com\b|\.exe\b|[\\/<>{}\[\]`])", re.I)


def _logo_quote(text):
    return f"<blockquote>{text}</blockquote>"


async def _logo_fail(event, reason="دوباره امتحان کن."):
    with contextlib.suppress(Exception):
        await event.edit(
            _logo_quote(f"❌ <b>خطای ساخت لوگو | HTX</b>\n{reason}"),
            parse_mode="html",
        )


async def _self_logo_command(event, uid, text):
    m = re.fullmatch(r"لوگو\s+([0-9۰-۹]{1,3})\s+(.+)", text.strip(), flags=re.S | re.I)
    if not m:
        return False
    logo_id = int(_fa_digits(m.group(1)))
    logo_text = m.group(2).strip()
    if logo_id not in LOGO_TEMPLATES:
        await _logo_fail(event, f"شماره قالب باید بین <b>1 تا {len(LOGO_TEMPLATES)}</b> باشد.")
        return True

    # Reject junk input (pasted logs, links, multi-line text) before rendering.
    title, _, subtitle = logo_text.partition("|")
    title, subtitle = title.strip(), subtitle.strip()
    if "\n" in logo_text or not title:
        await _logo_fail(event, "متن لوگو باید یک خط باشد.\nمثال: <code>.لوگو 7 HusteRIX</code>")
        return True
    if _LOGO_URL_RE.search(logo_text):
        await _logo_fail(event, "لینک و کاراکترهای خاص مجاز نیست؛ فقط اسم برند را بنویس.")
        return True
    if len(title) > LOGO_TITLE_MAX or len(subtitle) > LOGO_SUBTITLE_MAX:
        await _logo_fail(
            event,
            f"متن خیلی طولانی است (حداکثر {LOGO_TITLE_MAX} حرف، زیرعنوان {LOGO_SUBTITLE_MAX} حرف).",
        )
        return True

    with contextlib.suppress(Exception):
        await event.edit(_logo_quote("⏳ <b>در حال ساخت لوگو | HTX</b>"), parse_mode="html")
    try:
        media = await asyncio.wait_for(generate_logo(logo_id, logo_text), timeout=45)
        sub_line = f"\n✦ <b>زیرعنوان:</b> {html.escape(subtitle)}" if subtitle else ""
        caption = _logo_quote(
            "🎨 <b>لوگو ساخته شد | HTX</b>\n"
            f"✦ <b>متن:</b> {html.escape(title)}{sub_line}\n"
            f"✦ <b>طرح:</b> #{logo_id} • {LOGO_TEMPLATES[logo_id][1]}"
        )
        await send_generated_image(event, media, caption, f"logo_{logo_id}.jpg")
    except ImportError:
        await _logo_fail(event, "کتابخانه Pillow روی سرور نصب نیست.")
        return True
    except Exception as exc:
        print(f"[LOGO {uid}] template={logo_id} failed: {type(exc).__name__}: {exc!r}")
        await _logo_fail(event)
        return True
    with contextlib.suppress(Exception):
        await event.delete()
    return True


async def _fake_hack_prank(event, uid):
    """Purely fictional entertainment sequence; no real access or scanning occurs."""
    if not event.is_reply:
        with contextlib.suppress(Exception):
            await event.edit(
                premium_ui_text("🎭 <b>حالت هک نمایشی</b>\n\n"
                "روی پیام کاربر ریپلای کن و فقط <code>.هک</code> بفرست."),
                parse_mode="html",
            )
        return

    replied = await event.get_reply_message()
    if not replied:
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text("❌ این دستور باید روی پیام یک کاربر ریپلای شود."), parse_mode="html")
        return

    chat_id = event.chat_id
    if chat_id is None:
        return

    # The command itself disappears.  A fresh message is created as a reply to
    # the target and then edited in place, so the target relationship is visible.
    with contextlib.suppress(Exception):
        await event.delete()

    stages = [
        "INITIALIZING SECURE SESSION",
        "ROUTING TRAFFIC THROUGH 7 NODES",
        "BYPASSING FIREWALL LAYER 01/04",
        "BYPASSING FIREWALL LAYER 02/04",
        "ENUMERATING PROTECTED TABLES",
        "DECRYPTING INDEX MANIFEST",
        "MOUNTING ARCHIVE VOLUME",
        "EXTRACTING RECORD SEGMENTS",
        "VERIFYING CHECKSUMS",
        "PACKING ARCHIVE",
        "FINALIZING TRANSFER",
    ]

    progress = None
    try:
        progress = await event.client.send_message(
            chat_id,
            "🛰️ <b>SECURE ACCESS INITIALIZING…</b>",
            parse_mode="html",
            reply_to=int(replied.id),
        )
    except Exception:
        return

    started = time.monotonic()
    steps = 15
    for i in range(steps):
        percent = min(99, int((i + 1) * 99 / steps))
        filled = round(16 * percent / 100)
        bar = "█" * filled + "░" * (16 - filled)
        stage = stages[min(i, len(stages) - 1)]
        elapsed = time.monotonic() - started
        remaining = max(0.0, steps - elapsed)
        text = (
            "🛰️ <b>REMOTE ACCESS PROTOCOL</b>\n\n"
            f"<code>{bar}</code> <b>{percent}%</b>\n\n"
            f"<code>[{stage}]</code>\n"
            f"<code>NODE: {i + 1:02d}/15   ETA: {remaining:04.1f}s</code>"
        )
        with contextlib.suppress(Exception):
            await progress.edit(premium_ui_text(text), parse_mode="html")
        await asyncio.sleep(1)

    size_gb = round(random.uniform(18.0, 39.0), 2)
    final_text = (
        "🟢 <b>ACCESS PROTOCOL COMPLETE</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✓ PERIMETER BYPASSED\n"
        "✓ SECURITY LAYERS OVERRIDDEN\n"
        "✓ DATABASE INDEX MOUNTED\n"
        "✓ PROTECTED RECORDS ENUMERATED\n"
        "✓ ARCHIVE INTEGRITY VERIFIED\n"
        "✓ ENCRYPTED PACKAGE CREATED\n"
        "✓ TRANSFER CHANNEL CLOSED\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>STATUS:</b> <code>ACCESS GRANTED</code>\n"
        f"<b>ARCHIVE:</b> <code>global_records_{size_gb:.2f}GB.enc</code>\n"
        f"<b>SIZE:</b> <code>{size_gb:.2f} GB</code>\n"
        "<b>INTEGRITY:</b> <code>SHA-256 VERIFIED</code>\n"
        "<b>TRANSFER:</b> <code>COMPLETE</code>"
    )
    with contextlib.suppress(Exception):
        await progress.edit(premium_ui_text(final_text), parse_mode="html")


async def _delete_all_profile_photos(client):
    try:
        photos = await client(functions.photos.GetUserPhotosRequest(
            user_id=await client.get_input_entity("me"),
            offset=0,
            max_id=0,
            limit=20,
        ))
        ids = []
        for photo in getattr(photos, "photos", []) or []:
            if isinstance(photo, types.Photo):
                ids.append(types.InputPhoto(
                    id=photo.id,
                    access_hash=photo.access_hash,
                    file_reference=photo.file_reference,
                ))
        if ids:
            await client(functions.photos.DeletePhotosRequest(id=ids))
    except Exception as exc:
        print(f"[PROFILE] delete photos failed: {exc}")


async def _update_profile_birthday(client, birthday):
    try:
        from telethon.tl import functions as tl_functions
        if not hasattr(tl_functions.account, "UpdateBirthdayRequest"):
            return
        req_cls = tl_functions.account.UpdateBirthdayRequest
        if birthday:
            bday = types.Birthday(
                day=int(getattr(birthday, "day", 1)),
                month=int(getattr(birthday, "month", 1)),
                year=int(getattr(birthday, "year", 0) or 0),
            )
        else:
            # Telegram uses an empty birthday object to clear the date.
            bday = types.Birthday(day=1, month=1, year=0)
        await client(req_cls(birthday=bday))
    except Exception as exc:
        print(f"[PROFILE] birthday update skipped: {exc}")


async def _profile_copy(event, uid):
    if not event.is_reply:
        await event.edit(premium_ui_text("❌ روی پیام همان کاربر ریپلای کن و «.کپی پروفایل» را بفرست."), parse_mode="html")
        return
    replied = await event.get_reply_message()
    if not replied or not replied.sender_id:
        await event.edit(premium_ui_text("❌ کاربر هدف پیدا نشد."), parse_mode="html")
        return
    client = event.client
    try:
        source = await client.get_entity(int(replied.sender_id))
        me = await client.get_me()

        original = {
            "first_name": me.first_name or "",
            "last_name": me.last_name or "",
            "about": getattr(me, "about", None) or "",
            "birthday": None,
            "photo_path": None,
        }
        bday = getattr(me, "birthday", None)
        if bday:
            original["birthday"] = {
                "day": int(getattr(bday, "day", 1)),
                "month": int(getattr(bday, "month", 1)),
                "year": int(getattr(bday, "year", 0) or 0),
            }

        profile_dir = BASE_DIR / "profile_copy" / str(uid)
        profile_dir.mkdir(parents=True, exist_ok=True)
        if getattr(me, "photo", None):
            original_photo = await client.download_profile_photo(me, file=str(profile_dir / "original.jpg"))
            if original_photo:
                original["photo_path"] = original_photo

        self_set(uid, "profile_copy_original", json.dumps(original, ensure_ascii=False))

        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(
            first_name=(getattr(source, "first_name", None) or "")[:64],
            last_name=(getattr(source, "last_name", None) or "")[:64],
            about=(getattr(source, "about", None) or "")[:70],
        ))

        source_birthday = getattr(source, "birthday", None)
        if source_birthday:
            await _update_profile_birthday(client, source_birthday)
        else:
            await _update_profile_birthday(client, None)

        if getattr(source, "photo", None):
            photo_path = await client.download_profile_photo(source, file=str(profile_dir / "source.jpg"))
            if photo_path:
                uploaded = await client.upload_file(photo_path)
                await client(functions.photos.UploadProfilePhotoRequest(file=uploaded))
                with contextlib.suppress(Exception):
                    os.remove(photo_path)
        else:
            await _delete_all_profile_photos(client)

        await event.edit(premium_ui_text("✅ پروفایل کپی شد. آیدی/یوزرنیم دست‌نخورده ماند."), parse_mode="html")
    except Exception as exc:
        print(f"[PROFILE] copy failed: {exc}")
        await event.edit(premium_ui_text("❌ کپی پروفایل انجام نشد؛ اطلاعات اصلی دست‌نخورده ماند."), parse_mode="html")


async def _profile_copy_restore(event, uid):
    raw = self_get(uid, "profile_copy_original", "")
    if not raw:
        await event.edit(premium_ui_text("❌ پروفایل قبلی برای بازگردانی ذخیره نشده است."), parse_mode="html")
        return
    try:
        original = json.loads(raw)
        client = event.client
        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(
            first_name=str(original.get("first_name") or "")[:64],
            last_name=str(original.get("last_name") or "")[:64],
            about=str(original.get("about") or "")[:70],
        ))
        bday = original.get("birthday")
        if bday:
            await _update_profile_birthday(client, types.Birthday(
                day=int(bday.get("day", 1)), month=int(bday.get("month", 1)), year=int(bday.get("year", 0) or 0)
            ))
        else:
            await _update_profile_birthday(client, None)

        await _delete_all_profile_photos(client)
        photo_path = original.get("photo_path")
        if photo_path and Path(photo_path).exists():
            uploaded = await client.upload_file(photo_path)
            await client(functions.photos.UploadProfilePhotoRequest(file=uploaded))
        self_set(uid, "profile_copy_original", "")
        await event.edit(premium_ui_text("✅ پروفایل به حالت قبل برگردانده شد."), parse_mode="html")
    except Exception as exc:
        print(f"[PROFILE] restore failed: {exc}")
        await event.edit(premium_ui_text("❌ بازگردانی پروفایل انجام نشد."), parse_mode="html")


# ============================================================
# EXTRA SELF FEATURES: SPAM / FIRST COMMENT / SECRETARY / GROUP / TAG
# ============================================================

GLOBAL_BAN_KEY = "global_ban_list"
FIRST_COMMENT_CONFIGS_KEY = "first_comment_configs_v2"
SECRETARY_REPLY_KEY = "secretary_reply"
SECRETARY_ENABLED_KEY = "secretary_enabled"
SECRETARY_INTERVAL_KEY = "secretary_interval"


def _secretary_reply(uid):
    """Load the configured secretary response safely from per-user settings."""
    try:
        raw = self_get(uid, SECRETARY_REPLY_KEY, "")
        if not raw:
            return None
        if isinstance(raw, dict):
            data = raw
        else:
            data = json.loads(raw)
        if not isinstance(data, dict):
            return None
        kind = str(data.get("kind") or "text")
        if kind == "media":
            path = str(data.get("path") or "")
            if not path or not Path(path).exists():
                print(f"[SECRETARY {uid}] configured media is missing: {path!r}")
                return None
            return {
                "kind": "media",
                "path": path,
                "caption": str(data.get("caption") or "")[:4096],
            }
        text = str(data.get("text") or data.get("caption") or "").strip()
        return {"kind": "text", "text": text, "caption": text} if text else None
    except Exception as exc:
        print(f"[SECRETARY {uid}] load failed: {type(exc).__name__}: {exc}")
        return None


def _save_secretary_reply(uid, data):
    """Persist the secretary response as JSON without losing media metadata."""
    if not isinstance(data, dict):
        raise ValueError("secretary reply must be a dict")
    clean = {
        "kind": "media" if data.get("kind") == "media" else "text",
        "text": str(data.get("text") or ""),
        "path": str(data.get("path") or "") if data.get("path") else None,
        "caption": str(data.get("caption") or ""),
    }
    self_set(uid, SECRETARY_REPLY_KEY, json.dumps(clean, ensure_ascii=False))
    print(f"[SECRETARY {uid}] reply saved: kind={clean['kind']}, has_text={bool(clean['text'])}, has_media={bool(clean['path'])}")

def _json_setting(uid, key, default):
    try:
        value = json.loads(self_get(uid, key, json.dumps(default, ensure_ascii=False)))
        return value if isinstance(value, type(default)) else default
    except Exception:
        return default

def _global_ban_list(uid):
    return {int(x) for x in _json_setting(uid, GLOBAL_BAN_KEY, []) if str(x).lstrip("-").isdigit()}

def _save_global_ban_list(uid, values):
    self_set(uid, GLOBAL_BAN_KEY, json.dumps(sorted({int(x) for x in values})))


# ============================================================
# "لیست فضول‌ها" — reply-based guesswork, NOT real profile-view data.
# Telegram never exposes who actually viewed a profile. What we track here
# is: anyone who replies to the account owner inside a shared group is added
# to this list, as a (guessed) sign they may have looked at the profile.
# The list resets automatically every day at 00:00 Asia/Tehran.
# ============================================================
SNOOPERS_LIST_KEY = "snoopers_list_v1"
SNOOPERS_RESET_DATE_KEY = "snoopers_reset_date"
SNOOPERS_MAX_ENTRIES = 200


def _snoopers_maybe_reset(uid):
    """Clear the list once the Tehran calendar date has changed since the
    last reset, so the list effectively resets every night at 00:00 Tehran
    time without needing a separate scheduler."""
    today = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d")
    last = self_get(uid, SNOOPERS_RESET_DATE_KEY, "")
    if last != today:
        self_set(uid, SNOOPERS_LIST_KEY, json.dumps([], ensure_ascii=False))
        self_set(uid, SNOOPERS_RESET_DATE_KEY, today)


def _snoopers_list(uid):
    _snoopers_maybe_reset(uid)
    raw = _json_setting(uid, SNOOPERS_LIST_KEY, [])
    return raw if isinstance(raw, list) else []


def _format_snooper_display(sender, sender_id: int) -> str:
    first = getattr(sender, "first_name", "") or "" if sender else ""
    last = getattr(sender, "last_name", "") or "" if sender else ""
    name = f"{first} {last}".strip() or "کاربر"
    username = getattr(sender, "username", None) if sender else None
    tail = f"@{username}" if username else str(sender_id)
    return f"{name} | {tail}"


def _snoopers_add(uid, sender_id: int, display: str):
    _snoopers_maybe_reset(uid)
    raw = _json_setting(uid, SNOOPERS_LIST_KEY, [])
    items = raw if isinstance(raw, list) else []
    # De-duplicate by id; a fresh reply just bumps the entry to the end.
    items = [x for x in items if not (isinstance(x, dict) and int(x.get("id", 0) or 0) == int(sender_id))]
    items.append({"id": int(sender_id), "display": display, "ts": int(time.time())})
    items = items[-SNOOPERS_MAX_ENTRIES:]
    self_set(uid, SNOOPERS_LIST_KEY, json.dumps(items, ensure_ascii=False))

def _first_comment_configs(uid):
    raw = _json_setting(uid, FIRST_COMMENT_CONFIGS_KEY, [])
    out=[]
    for x in raw:
        if not isinstance(x, dict): continue
        try: cid=int(x.get("id"))
        except (TypeError,ValueError): continue
        if cid<=0: continue
        x=dict(x); x["id"]=cid; x["text"]=str(x.get("text") or "")[:4096]; x["enabled"]=bool(x.get("enabled",True))
        try: x["discussion_id"]=int(x["discussion_id"]) if x.get("discussion_id") is not None else None
        except (TypeError,ValueError): x["discussion_id"]=None
        out.append(x)
    return out

def _save_first_comment_configs(uid, values):
    seen=set(); out=[]
    for x in values:
        if not isinstance(x,dict): continue
        try: cid=int(x.get("id"))
        except (TypeError,ValueError): continue
        if cid<=0 or cid in seen: continue
        seen.add(cid); out.append(x)
    self_set(uid, FIRST_COMMENT_CONFIGS_KEY, json.dumps(out, ensure_ascii=False))

def _first_comment_config(uid, channel_id):
    try: cid=int(channel_id)
    except (TypeError,ValueError): return None
    return next((x for x in _first_comment_configs(uid) if int(x["id"])==cid), None)

def _upsert_first_comment_config(uid, item):
    cid=int(item["id"]); _save_first_comment_configs(uid,[x for x in _first_comment_configs(uid) if int(x["id"])!=cid]+[item])

def _remove_first_comment_config(uid, channel_id):
    try: cid=int(channel_id)
    except (TypeError,ValueError): return False
    old=_first_comment_configs(uid); new=[x for x in old if int(x["id"])!=cid]
    if len(old)==len(new): return False
    _save_first_comment_configs(uid,new); _first_comment_ui_target.pop(int(uid),None); return True

def _set_comment_target(uid, channel_id): _first_comment_ui_target[int(uid)]=int(channel_id)
def _comment_target(uid): return _first_comment_ui_target.get(int(uid))
def _clear_comment_target(uid): _first_comment_ui_target.pop(int(uid),None)


async def _is_group_admin(client, chat_id, uid):
    try:
        if not chat_id:
            return False
        perms = await client.get_permissions(chat_id, uid)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


async def _resolve_user(client, raw, reply_message=None):
    raw = (raw or "").strip()
    if reply_message and reply_message.sender_id:
        return await client.get_entity(int(reply_message.sender_id))
    if raw.startswith("@"):
        raw = raw[1:]
    if raw.lstrip("-").isdigit():
        return await client.get_entity(int(raw))
    if raw:
        return await client.get_entity(raw)
    return None


async def _spam_replied(event, uid, count):
    if not event.is_reply:
        return "❌ این دستور باید روی پیام موردنظر ریپلای شود."
    if count < 1 or count > 1000:
        return "❌ تعداد تکرار باید بین ۱ تا ۱۰۰۰ باشد."
    replied = await event.get_reply_message()
    if not replied:
        return "❌ پیام ریپلای‌شده پیدا نشد."
    if uid in _spam_tasks and not _spam_tasks[uid].done():
        return "⏳ یک اسپم در حال اجراست."

    chat_id = event.chat_id
    async def worker():
        try:
            # Re-send content using the SELF account. Never use the bot client.
            text = replied.raw_text or ""
            if getattr(replied, "media", None):
                path = None
                try:
                    path = await replied.download_media(file=str(BASE_DIR / "tmp_spam" / str(uid)))
                    if path:
                        for _ in range(count):
                            await _tg_call_with_flood_retry(
                                lambda p=path: event.client.send_file(chat_id, p, caption=text[:4096]),
                                label="spam send",
                                max_retries=5,
                            )
                    else:
                        raise RuntimeError("media_download_failed")
                finally:
                    if path:
                        with contextlib.suppress(Exception):
                            Path(path).unlink(missing_ok=True)
            else:
                for _ in range(count):
                    await _tg_call_with_flood_retry(
                        lambda: event.client.send_message(chat_id, text),
                        label="spam send",
                        max_retries=5,
                    )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"[SPAM {uid}] failed: {exc}")

    task = asyncio.create_task(worker())
    _spam_tasks[uid] = task
    with contextlib.suppress(Exception):
        await event.delete()
    return f"✅ اسپم {count:,} تکرار با اکانت SELF شروع شد."


async def _maybe_first_comment(event, uid):
    configs={int(x["id"]):x for x in _first_comment_configs(uid) if x.get("enabled") and str(x.get("text") or "").strip()}
    if not configs: return
    client=event.client; msg=event.message
    chat=None
    with contextlib.suppress(Exception): chat=await event.get_chat()
    chat_id=getattr(chat,"id",None)
    is_broadcast=isinstance(chat,types.Channel) and bool(getattr(chat,"broadcast",False)) and not bool(getattr(chat,"megagroup",False))
    is_discussion=isinstance(chat,types.Channel) and bool(getattr(chat,"megagroup",False))
    fwd=getattr(msg,"fwd_from",None); forward=getattr(msg,"forward",None)
    source=None
    for obj in (fwd,forward):
        for peer in (getattr(obj,"from_id",None),getattr(obj,"saved_from_peer",None)):
            val=getattr(peer,"channel_id",None)
            if val is not None:
                source=int(val); break
        if source is None:
            val=getattr(obj,"channel_id",None)
            if val is not None: source=int(val)
        if source is not None: break
    peer_channel=getattr(getattr(msg,"peer_id",None),"channel_id",None)
    if source is None and is_broadcast and peer_channel is not None and int(peer_channel) in configs: source=int(peer_channel)
    if source is None and is_broadcast and chat_id is not None and int(chat_id) in configs: source=int(chat_id)
    if source is None or source not in configs: return
    cfg=configs[source]; original=None
    for obj in (fwd,forward):
        val=getattr(obj,"channel_post",None)
        if val is not None:
            original=int(val); break
    if original is None and is_broadcast: original=int(msg.id)
    did=cfg.get("discussion_id")
    try: did=int(did) if did is not None else None
    except (TypeError,ValueError): did=None
    try:
        channel=await client.get_entity(source)
        if not did:
            full=await client(functions.channels.GetFullChannelRequest(channel=channel)); did=getattr(getattr(full,"full_chat",None),"linked_chat_id",None)
            if did:
                cfg["discussion_id"]=int(did); _upsert_first_comment_config(uid,cfg)
    except Exception as exc:
        print(f"[COMMENT {uid}] resolve source failed: {type(exc).__name__}: {exc}"); return
    if not did: return
    try: discussion=await client.get_entity(int(did))
    except Exception as exc: print(f"[COMMENT {uid}] discussion failed: {exc}"); return
    reply_to=None
    if is_discussion and chat_id is not None and int(chat_id)==int(getattr(discussion,"id",0)) and (fwd is not None or forward is not None): reply_to=int(msg.id)
    if reply_to is None and original is not None:
        for delay in (0,0.8,1.5,2.5,4.0):
            if delay: await asyncio.sleep(delay)
            try:
                result=await client(functions.messages.GetDiscussionMessageRequest(peer=channel,msg_id=int(original)))
                messages=getattr(result,"messages",None) or []
                candidates=[m for m in messages if getattr(getattr(m,"peer_id",None),"channel_id",None)==int(getattr(discussion,"id",0))]
                if not candidates: candidates=[m for m in messages if int(getattr(m,"id",0) or 0)!=int(original)]
                if candidates: reply_to=int(candidates[0].id); break
            except Exception as exc: print(f"[COMMENT {uid}] lookup failed: {type(exc).__name__}: {exc}")
    if reply_to is None and is_discussion and chat_id is not None and int(chat_id)==int(getattr(discussion,"id",0)): reply_to=int(msg.id)
    if reply_to is None: return
    text=str(cfg.get("text") or "").strip()[:4096]; key=(int(source),int(reply_to),text)
    if key in _first_comment_sent_cache: return
    async def send():
        return await client(SendMessageRequest(peer=discussion,message=text,random_id=random.getrandbits(64),reply_to=types.InputReplyToMessage(reply_to_msg_id=int(reply_to))))
    try:
        sent=await _tg_call_with_flood_retry(send,label="first comment",max_retries=5); _first_comment_sent_cache.add(key)
        if len(_first_comment_sent_cache)>5000: _first_comment_sent_cache.clear()
        print(f"[COMMENT {uid}] sent channel={source} reply_to={reply_to} message={getattr(sent,'id',None)}")
    except Exception as exc: print(f"[COMMENT {uid}] send failed: {type(exc).__name__}: {exc}")


# Some mobile keyboards (notably iOS) auto-insert an invisible bidi mark
# right after a leading "." when it's immediately followed by RTL text —
# exactly the shape of our dot-prefixed Persian commands (".بن", ".سیک",
# ".لیست فضول ها"). That invisible character breaks a naive exact-string
# match even though the command looks completely normal on screen. Strip
# these before comparing so the command still matches.
_INVISIBLE_MARKS_RE = re.compile(
    "[\u200b\u200c\u200d\u200e\u200f\u202a\u202b\u202c\u202d\u202e"
    "\u2066\u2067\u2068\u2069\ufeff]"
)


def _strip_invisible_marks(value: str) -> str:
    return _INVISIBLE_MARKS_RE.sub("", value or "")


async def _handle_group_command(event, uid, text):
    low = _strip_invisible_marks(text).casefold().strip()
    client = event.client

    # Global ban enforcement runs for every incoming message elsewhere too.
    if low in {"پین", "پین + ریپلای"}:
        if not event.is_group or not event.is_reply:
            await event.edit(premium_ui_text("❌ داخل گروه روی پیام موردنظر ریپلای کن."), parse_mode="html")
            return True
        if not await _is_group_admin(client, event.chat_id, uid):
            await event.edit(premium_ui_text("❌ فقط ادمین گروه می‌تواند پین کند."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        try:
            await client.pin_message(event.chat_id, replied.id, notify=False)
            await event.edit(premium_ui_text("📌 پیام با موفقیت سنجاق شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ پین انجام نشد: {html.escape(str(exc))}"), parse_mode="html")
        return True

    if low in {"حذف پین", "حذف پین + ریپلای"}:
        if not event.is_group or not event.is_reply:
            await event.edit(premium_ui_text("❌ داخل گروه روی پیام موردنظر ریپلای کن."), parse_mode="html")
            return True
        if not await _is_group_admin(client, event.chat_id, uid):
            await event.edit(premium_ui_text("❌ فقط ادمین گروه می‌تواند پین را حذف کند."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        try:
            await client.unpin_message(event.chat_id, message=replied.id)
            await event.edit(premium_ui_text("📌 سنجاق پیام حذف شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ حذف پین انجام نشد: {html.escape(str(exc))}"), parse_mode="html")
        return True

    if low in {"بن", "سیک", "بن + ریپلای", "سیک + ریپلای"}:
        if not event.is_group or not event.is_reply:
            await event.edit(premium_ui_text("❌ این دستور را داخل گروه و با ریپلای روی کاربر استفاده کن."), parse_mode="html")
            return True
        if not await _is_group_admin(client, event.chat_id, uid):
            await event.edit(premium_ui_text("❌ فقط ادمین گروه می‌تواند بن کند."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        target = int(replied.sender_id) if replied and replied.sender_id else 0
        if not target or target == uid:
            await event.edit(premium_ui_text("❌ کاربر هدف معتبر نیست."), parse_mode="html")
            return True
        try:
            await client.edit_permissions(event.chat_id, target, view_messages=False, send_messages=False)
            await event.edit(premium_ui_text(f"🚫 کاربر `{target}` از گروه بن شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ بن انجام نشد: {html.escape(str(exc))}"), parse_mode="html")
        return True

    if low in {"آن بن", "ان بن", "آن‌بن", "ان‌بن", "آن بن + ریپلای"}:
        if not event.is_group or not event.is_reply:
            await event.edit(premium_ui_text("❌ داخل گروه روی کاربر ریپلای کن."), parse_mode="html")
            return True
        if not await _is_group_admin(client, event.chat_id, uid):
            await event.edit(premium_ui_text("❌ فقط ادمین گروه می‌تواند آن‌بن کند."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        target = int(replied.sender_id) if replied and replied.sender_id else 0
        try:
            await client.edit_permissions(event.chat_id, target, view_messages=True, send_messages=True)
            await event.edit(premium_ui_text(f"✅ کاربر `{target}` آن‌بن شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ آن‌بن انجام نشد: {html.escape(str(exc))}"), parse_mode="html")
        return True

    m = re.fullmatch(r"بن سراسری(?:\s+(.+))?", text, flags=re.S | re.I)
    if m:
        raw = (m.group(1) or "").strip()
        if not raw and not event.is_reply:
            await event.edit(premium_ui_text("❌ آیدی یا یوزرنیم را بده یا روی پیام کاربر ریپلای کن."), parse_mode="html")
            return True
        try:
            replied = await event.get_reply_message() if event.is_reply else None
            target = await _resolve_user(client, raw, replied)
            target_id = int(target.id)
            bans = _global_ban_list(uid)
            bans.add(target_id)
            _save_global_ban_list(uid, bans)
            if event.is_group and await _is_group_admin(client, event.chat_id, uid) and target_id != uid:
                with contextlib.suppress(Exception):
                    await client.edit_permissions(event.chat_id, target_id, view_messages=False, send_messages=False)
            await event.edit(premium_ui_text(f"🚫 کاربر `{target_id}` به لیست بن سراسری اضافه شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ ثبت بن سراسری ناموفق بود: {html.escape(str(exc))}"), parse_mode="html")
        return True

    m = re.fullmatch(r"حذف بن سراسری(?:\s+(.+))?", text, flags=re.S | re.I)
    if m:
        raw = (m.group(1) or "").strip()
        try:
            replied = await event.get_reply_message() if event.is_reply else None
            target = await _resolve_user(client, raw, replied)
            target_id = int(target.id)
            bans = _global_ban_list(uid)
            if target_id not in bans:
                await event.edit(premium_ui_text("❌ این کاربر در لیست بن سراسری نیست."), parse_mode="html")
                return True
            bans.discard(target_id)
            _save_global_ban_list(uid, bans)
            await event.edit(premium_ui_text(f"✅ کاربر `{target_id}` از لیست بن سراسری حذف شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ حذف بن سراسری ناموفق بود: {html.escape(str(exc))}"), parse_mode="html")
        return True

    if low == "لیست بن سراسری":
        bans = sorted(_global_ban_list(uid))
        if not bans:
            await event.edit(premium_ui_text("🚫 لیست بن سراسری خالی است."), parse_mode="html")
        else:
            await event.edit(premium_ui_text("🚫 <b>لیست بن سراسری</b>\n\n" + "\n".join(f"{i}. <code>{x}</code>" for i, x in enumerate(bans, 1))), parse_mode="html")
        return True

    tag_match = re.fullmatch(r"تگ(?:\s+([0-9۰-۹]+))?", _fa_digits(text))
    if tag_match or low == "همه":
        if not event.is_group:
            await event.edit(premium_ui_text("❌ تگ اعضا فقط داخل گروه قابل استفاده است."), parse_mode="html")
            return True
        count = None if low == "همه" else int(tag_match.group(1) or 0)
        if count is not None and not 1 <= count <= 1000:
            await event.edit(premium_ui_text("❌ تعداد تگ باید بین ۱ تا ۱۰۰۰ باشد."), parse_mode="html")
            return True
        replied = await event.get_reply_message() if event.is_reply else None
        members = []
        async for member in client.iter_participants(event.chat_id):
            if getattr(member, "bot", False) or int(member.id) == int(uid):
                continue
            members.append(member)
            if count is not None and len(members) >= count:
                break
        with contextlib.suppress(Exception):
            await event.delete()
        if not members:
            await client.send_message(event.chat_id, "❌ عضوی برای تگ پیدا نشد.")
            return True
        for start in range(0, len(members), 15):
            chunk = members[start:start + 15]
            lines = []
            for member in chunk:
                name = html.escape((getattr(member, "first_name", None) or getattr(member, "username", None) or "کاربر").strip())
                lines.append(f'<a href="tg://user?id={int(member.id)}">{name}</a>')
            kwargs = {"parse_mode": "html"}
            if replied:
                kwargs["reply_to"] = replied.id
            await client.send_message(event.chat_id, "\n".join(lines), **kwargs)
        return True

    return False


async def _handle_first_comment_command(event, uid, text):
    low=text.casefold().strip()
    if low in {"تنظیم کامنت","تنظیم کامنت + ریپلای","تنظیم کامنت ریپلای"}:
        if not event.is_reply: await event.edit(premium_ui_text("❌ روی پیام متنی موردنظر ریپلای کن."), parse_mode="html"); return True
        cid=_comment_target(uid); cfg=_first_comment_config(uid,cid) if cid else None
        if not cfg: await event.edit(premium_ui_text("❌ ابتدا از پنل «💬 کامنت اول» یک کانال را انتخاب کن."), parse_mode="html"); return True
        replied=await event.get_reply_message()
        if not replied or not (replied.raw_text or "").strip(): await event.edit(premium_ui_text("❌ پیام ریپلای‌شده باید متنی باشد."), parse_mode="html"); return True
        cfg["text"]=replied.raw_text.strip()[:4096]; cfg["enabled"]=True; _upsert_first_comment_config(uid,cfg)
        await event.edit(premium_ui_text(f"✅ <b>متن کامنت ذخیره شد.</b>\n\n📢 {html.escape(str(cfg.get('title') or 'کانال'))}\n🟢 فعال شد."),parse_mode="html"); return True
    m = re.fullmatch(r"حذف کامنت اول\s+(.+)", text, flags=re.S)
    if m:
        raw=m.group(1).strip()
        if not raw: await event.edit(premium_ui_text("❌ آیدی یا یوزرنیم کانال را وارد کن."), parse_mode="html"); return True
        try:
            ent=await event.client.get_entity(raw); ok=_remove_first_comment_config(uid,int(ent.id)); await event.edit(premium_ui_text("✅ تنظیمات کامنت کانال حذف شد." if ok else "❌ این کانال تنظیم نشده بود."), parse_mode="html")
        except Exception as exc: await event.edit(premium_ui_text(f"❌ حذف انجام نشد: {html.escape(str(exc))}"), parse_mode="html")
        return True
    if low=="لیست کامنت":
        cfgs=_first_comment_configs(uid)
        if not cfgs: await event.edit(premium_ui_text("💬 لیست کامنت اول خالی است."), parse_mode="html"); return True
        lines=["💬 <b>لیست کامنت اول</b>",""]
        for i,cfg in enumerate(cfgs,1):
            st="🟢 فعال" if cfg.get("enabled") and cfg.get("text") else ("🟡 بدون متن" if cfg.get("enabled") else "🔴 خاموش")
            lines.append(f"{i}. 📢 <b>{html.escape(str(cfg.get('title') or cfg.get('id')))}</b> • {st}")
        await event.edit(premium_ui_text("\n".join(lines)),parse_mode="html"); return True
    if low=="پاکسازی لیست کامنت":
        _save_first_comment_configs(uid,[]); _clear_comment_target(uid); await event.edit(premium_ui_text("✅ تمام تنظیمات کامنت اول پاک شد."), parse_mode="html"); return True
    m = re.fullmatch(r"تنظیم کامنت اول\s+(.+)", text, flags=re.S)
    if m:
        raw=m.group(1).strip()
        if not raw: await event.edit(premium_ui_text("❌ آیدی یا یوزرنیم کانال را وارد کن."), parse_mode="html"); return True
        try:
            ent=await event.client.get_entity(raw)
            full=await event.client(functions.channels.GetFullChannelRequest(channel=ent)); did=getattr(getattr(full,"full_chat",None),"linked_chat_id",None)
            if not did: await event.edit(premium_ui_text("❌ این کانال Discussion متصل ندارد."), parse_mode="html"); return True
            d=await event.client.get_entity(int(did)); old=_first_comment_config(uid,int(ent.id)) or {}
            item={"id":int(ent.id),"access_hash":getattr(ent,"access_hash",None),"title":getattr(ent,"title","کانال"),"username":getattr(ent,"username",None),"discussion_id":int(did),"discussion_access_hash":getattr(d,"access_hash",None),"text":str(old.get("text") or ""),"enabled":True}
            _upsert_first_comment_config(uid,item); _set_comment_target(uid,int(ent.id)); await event.edit(premium_ui_text("✅ کانال ثبت شد. حالا روی پیام متن ریپلای کن و «.تنظیم کامنت» بفرست."), parse_mode="html")
        except Exception as exc: await event.edit(premium_ui_text(f"❌ ثبت کانال ناموفق بود: {html.escape(str(exc))}"), parse_mode="html")
        return True
    return False


async def _send_self_reaction(client, chat_id, msg_id, emoji, *, label="reaction"):
    """Send a reaction using a resolved InputPeer and a couple of safe emoji forms."""
    if not client or chat_id is None or not msg_id:
        raise ValueError("missing reaction peer/message")
    peer = await client.get_input_entity(chat_id)
    candidates = [str(emoji or "❤")]
    # Try both heart representations; Telegram's accepted reaction string can
    # differ by variation selector depending on the client/API representation.
    if candidates[0] == "❤️":
        candidates.append("❤")
    elif candidates[0] == "❤":
        candidates.append("❤️")
    last_exc = None
    for candidate in dict.fromkeys(candidates):
        try:
            result = await _tg_call_with_flood_retry(
                lambda c=candidate: client(SendReactionRequest(
                    peer=peer,
                    msg_id=int(msg_id),
                    reaction=[ReactionEmoji(emoticon=c)],
                )),
                label=f"{label} {candidate!r}",
                max_retries=3,
            )
            print(f"[REACTION] success chat={chat_id} msg={msg_id} emoji={candidate!r}")
            return result
        except Exception as exc:
            last_exc = exc
            print(f"[REACTION] attempt failed chat={chat_id} msg={msg_id} emoji={candidate!r}: {type(exc).__name__}: {exc}")
    raise last_exc


async def _handle_secretary_command(event, uid, text):
    low = text.casefold().strip()
    if low == "منشی روشن":
        if not _secretary_reply(uid):
            await event.edit(premium_ui_text("❌ ابتدا با «.تنظیم منشی» پاسخ منشی را تنظیم کن."), parse_mode="html")
            return True
        self_set(uid, SECRETARY_ENABLED_KEY, "on")
        await event.edit(premium_ui_text("🤵 منشی روشن شد. فقط در پیوی فعال است."), parse_mode="html")
        return True
    if low == "منشی خاموش":
        self_set(uid, SECRETARY_ENABLED_KEY, "off")
        await event.edit(premium_ui_text("🤵 منشی خاموش شد."), parse_mode="html")
        return True
    m = re.fullmatch(r"تنظیم زمان منشی\s+([0-9۰-۹]+)", _fa_digits(text))
    if m:
        minutes = int(m.group(1))
        if not 5 <= minutes <= 60:
            await event.edit(premium_ui_text("❌ زمان منشی باید بین ۵ تا ۶۰ دقیقه باشد."), parse_mode="html")
            return True
        self_set(uid, SECRETARY_INTERVAL_KEY, str(minutes))
        await event.edit(premium_ui_text(f"✅ فاصله پاسخ منشی روی {minutes} دقیقه تنظیم شد."), parse_mode="html")
        return True
    if low in {"تنظیم منشی", "تنظیم منشی + ریپلای", "تنظیم منشی ریپلای"}:
        if not event.is_reply:
            await event.edit(premium_ui_text("❌ روی پیام متنی یا مدیای موردنظر ریپلای کن."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        if not replied:
            await event.edit(premium_ui_text("❌ پیام پیدا نشد."), parse_mode="html")
            return True
        data = {"kind": "text", "text": replied.raw_text or "", "path": None, "caption": replied.raw_text or ""}
        if getattr(replied, "media", None):
            try:
                media_dir = BASE_DIR / "secretary_media" / str(uid)
                media_dir.mkdir(parents=True, exist_ok=True)
                path = await replied.download_media(file=str(media_dir / "reply"))
                if path:
                    data["kind"] = "media"
                    data["path"] = str(path)
            except Exception as exc:
                await event.edit(premium_ui_text(f"❌ ذخیره مدیا ناموفق بود: {html.escape(str(exc))}"), parse_mode="html")
                return True
        _save_secretary_reply(uid, data)
        await event.edit(premium_ui_text("✅ پاسخ منشی ذخیره شد. برای فعال‌سازی: «.منشی روشن»"), parse_mode="html")
        return True
    return False


# ============================================================
# PREMIUM EMOJI REGISTRATION (ثبت/حذف ایموجی)
# ============================================================

def _extract_custom_emoji(msg):
    """Return (document_id, fallback_glyph) for the first custom-emoji entity
    found on a Telethon message, or None if it has none.

    Uses telethon.utils add/del_surrogate so entity offsets (UTF-16 code
    units) line up correctly with the slice, matching how Telethon itself
    resolves entity text.
    """
    if not msg:
        return None
    entities = getattr(msg, "entities", None) or []
    custom = next((e for e in entities if isinstance(e, types.MessageEntityCustomEmoji)), None)
    if not custom:
        return None
    raw = msg.raw_text or msg.text or ""
    wide = utils.add_surrogate(raw)
    glyph = utils.del_surrogate(wide[custom.offset: custom.offset + custom.length])
    try:
        return int(custom.document_id), glyph
    except (TypeError, ValueError):
        return None


def _strip_premium_emoji_command_prefix(remainder):
    return re.sub(r"^\.?\s*(?:ثبت|حذف)\s*ایموجی\s*", "", remainder).strip()


_PREMIUM_EMOJI_CMD_PREFIXES = ("ثبت ایموجی", "ثبت‌ایموجی", "حذف ایموجی", "حذف‌ایموجی")
_PREMIUM_EMOJI_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def _looks_like_premium_emoji_command(stripped: str) -> bool:
    """Guard against false positives when the trigger words merely appear at
    the start of a normal sentence (e.g. "ثبت ایموجی کن دیگه" said to a
    friend). A real command only ever has a numeric id, brackets, or an
    emoji/nothing after the trigger words — never ordinary letters. If the
    remainder contains any letter character (in any script), treat the whole
    message as regular conversation and don't intercept it."""
    prefix = next((p for p in _PREMIUM_EMOJI_CMD_PREFIXES if stripped.startswith(p)), None)
    if prefix is None:
        return False
    remainder = stripped[len(prefix):]
    if _PREMIUM_EMOJI_LETTER_RE.search(remainder):
        return False
    return True


async def _handle_premium_emoji_command(event, uid, text):
    """«ثبت ایموجی» / «حذف ایموجی» — only usable inside the user's own
    Saved Messages. The resulting mapping is then applied automatically to
    every outgoing message in self_handle_outgoing's tail."""
    stripped = text.strip()
    if stripped.casefold() == "لیست پرمیوم":
        try:
            last_exc = None
            for attempt in range(3):
                try:
                    await _send_self_premium_list(event)
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    print(
                        f"[PREMIUM LIST] attempt={attempt + 1} failed: "
                        f"{type(exc).__name__}: {exc!r}"
                    )
                    if attempt < 2:
                        await asyncio.sleep(0.08)
            if last_exc is not None:
                raise last_exc
            with contextlib.suppress(Exception):
                await event.delete()
        except Exception as exc:
            print(f"[PREMIUM LIST] failed: {exc}")
            with contextlib.suppress(Exception):
                await event.edit(
                    premium_ui_text("❌ لیست پرمیوم ارسال نشد."),
                    parse_mode="html",
                )
        return True

    if not _looks_like_premium_emoji_command(stripped):
        return False

    # Registration/removal only make sense in Saved Messages: that is where
    # the mapping is defined for the whole account.
    if not (event.is_private and event.chat_id == uid):
        await event.edit(
            premium_ui_text("❌ ثبت و حذف ایموجی پریمیوم فقط داخل Saved Messages خودت انجام می‌شود."),
            parse_mode="html",
        )
        return True

    is_register = stripped.startswith("ثبت")

    if is_register:
        # Explicit registration format:
        # ثبت ایموجی [PREMIUM_EMOJI_ID] [NORMAL_EMOJI]
        # Also accept the same format without brackets. This path is useful
        # when the user already knows the Telegram custom-emoji document ID.
        explicit = re.match(
            r"^ثبت\s*ایموجی\s*(?:\[\s*(\d{5,25})\s*\]|(\d{5,25}))\s*"
            r"(?:\[\s*(.+?)\s*\]|(.+?))\s*$",
            stripped,
            flags=re.DOTALL,
        )
        if explicit:
            emoji_id = int(explicit.group(1) or explicit.group(2))
            normal_emoji = (explicit.group(3) or explicit.group(4) or "").strip()
            # Avoid accidentally registering another command as an emoji.
            if normal_emoji.lower().startswith(("ثبت ایموجی", "حذف ایموجی")):
                normal_emoji = ""
            premium_glyph = normal_emoji
        else:
            own = _extract_custom_emoji(event.message)
            if own:
                emoji_id, premium_glyph = own
                entities = event.message.entities or []
                ent = next(e for e in entities if isinstance(e, types.MessageEntityCustomEmoji))
                wide = utils.add_surrogate(event.raw_text or "")
                remainder_wide = wide[:ent.offset] + wide[ent.offset + ent.length:]
                normal_emoji = _strip_premium_emoji_command_prefix(utils.del_surrogate(remainder_wide))
            elif event.is_reply:
                replied = await event.get_reply_message()
                found = _extract_custom_emoji(replied)
                if not found:
                    await event.edit(
                        premium_ui_text("❌ پیام ریپلای‌شده ایموجی پریمیوم ندارد."),
                        parse_mode="html",
                    )
                    return True
                emoji_id, premium_glyph = found
                normal_emoji = _strip_premium_emoji_command_prefix(stripped)
            else:
                await event.edit(
                    premium_ui_text(
                        "❌ فرمت درست:\n"
                        "<code>.ثبت ایموجی [آیدی ایموجی پریمیوم] [ایموجی عادی]</code>\n\n"
                        "مثال: <code>.ثبت ایموجی [5368324176734567890] [🔥]</code>\n\n"
                        "یا روی پیام دارای ایموجی پریمیوم ریپلای کن و بنویس: <code>.ثبت ایموجی 🔥</code>"
                    ),
                    parse_mode="html",
                )
                return True
        if not normal_emoji:
            await event.edit(
                premium_ui_text("❌ ایموجی عادی مقصد را هم بعد از ایموجی پریمیوم بنویس."),
                parse_mode="html",
            )
            return True

        mapping = self_premium_emoji_map(uid)
        mapping[normal_emoji] = [emoji_id, premium_glyph or normal_emoji]
        self_save_premium_emoji_map(uid, mapping)
        await event.edit(
            premium_ui_text(
                f"✅ ثبت شد.\nاز این پس هر پیامی که {html.escape(normal_emoji)} داشته باشد، "
                "به‌صورت خودکار با ایموجی پریمیوم ویرایش می‌شود."
            ),
            parse_mode="html",
        )
        return True

    # حذف ایموجی
    mapping = self_premium_emoji_map(uid)
    arg = _strip_premium_emoji_command_prefix(stripped)
    target_key = None

    own = _extract_custom_emoji(event.message)
    ref_id = own[0] if own else None
    if ref_id is None and event.is_reply:
        replied = await event.get_reply_message()
        found = _extract_custom_emoji(replied)
        if found:
            ref_id = found[0]

    if ref_id is not None:
        for key, val in mapping.items():
            if isinstance(val, list) and val and int(val[0]) == int(ref_id):
                target_key = key
                break
    if target_key is None and arg in mapping:
        target_key = arg

    if target_key is None:
        await event.edit(
            premium_ui_text("❌ این ایموجی در لیست ثبت‌شده‌ها پیدا نشد."),
            parse_mode="html",
        )
        return True

    mapping.pop(target_key, None)
    self_save_premium_emoji_map(uid, mapping)
    await event.edit(premium_ui_text("✅ ثبت این ایموجی حذف شد."), parse_mode="html")
    return True


_SNOOPERS_COMMAND_RE = re.compile(r"^\s*لیست\s*فضول\s*ها$")


async def _handle_snoopers_command(event, uid, text):
    """«.لیست فضول ها» — edits the command message itself into the guessed
    reply-based list. Not real Telegram profile-view data; see the guide
    text (buttons menu) for the disclaimer — the delivered list itself stays
    plain: just the header and the names, nothing else.

    Deliberately built without premium_ui_text()/custom-emoji entities: a
    non-premium SELF account can fail to *edit* a message into containing a
    <tg-emoji> entity (Telegram accepts it fine on a fresh send, but rejects
    it on edit), which was silently swallowing this whole feature in Saved
    Messages. Plain header + plain names sidesteps that entirely."""
    norm = _strip_invisible_marks(text).strip()
    if not _SNOOPERS_COMMAND_RE.match(norm):
        return False

    items = _snoopers_list(uid)
    chat_id = event.chat_id
    client = event.client

    # Bots must always end their username in "bot"/"Bot" (Telegram enforces
    # this), so this also retroactively purges any bot entries that slipped
    # into the stored list before the incoming-message filter existed.
    def _is_bot_entry(x):
        display = str(x.get("display", "")) if isinstance(x, dict) else ""
        tail = display.rsplit("|", 1)[-1].strip()
        return tail.startswith("@") and tail[1:].lower().endswith("bot")

    clean_items = [x for x in items if isinstance(x, dict) and not _is_bot_entry(x)]
    if len(clean_items) != len(items):
        self_set(uid, SNOOPERS_LIST_KEY, json.dumps(clean_items, ensure_ascii=False))
    items = clean_items

    if not items:
        body = "🕵️ <b>لیست فضول‌ها</b>\n\nفعلاً کسی به لیست اضافه نشده."
    else:
        lines = [
            f"{i}. {html.escape(str(x.get('display', '')))}"
            for i, x in enumerate(items, 1)
            if isinstance(x, dict)
        ]
        body = "🕵️ <b>لیست فضول‌ها</b>\n\n" + "\n".join(lines)

    try:
        await event.edit(body, parse_mode="html")
    except MessageNotModifiedError:
        pass
    except Exception as exc:
        print(f"[SNOOPERS {uid}] edit failed: {type(exc).__name__}: {exc}")
        # Editing can fail for reasons unrelated to the content (message too
        # old, edit window expired, etc). Fall back to deleting the command
        # and sending a fresh message so the user still gets the list.
        with contextlib.suppress(Exception):
            await event.delete()
        try:
            await client.send_message(chat_id, body, parse_mode="html")
        except Exception as exc2:
            print(f"[SNOOPERS {uid}] fallback send also failed: {type(exc2).__name__}: {exc2}")
            try:
                await client.send_message(uid, body, parse_mode="html")
            except Exception as exc3:
                print(f"[SNOOPERS {uid}] fallback send to Saved Messages also failed: {type(exc3).__name__}: {exc3}")
    return True


def _apply_premium_emoji_substitution(text, mapping):
    """Replace every registered plain emoji in text with its <tg-emoji> tag.
    Longest keys first so multi-character keys win over single-char substrings."""
    if not text or not mapping:
        return text
    for normal_emoji in sorted(mapping.keys(), key=len, reverse=True):
        entry = mapping.get(normal_emoji)
        if not isinstance(entry, list) or len(entry) < 2 or not normal_emoji:
            continue
        try:
            emoji_id = int(entry[0])
        except (TypeError, ValueError):
            continue
        if normal_emoji in text:
            glyph = entry[1] or normal_emoji
            text = text.replace(normal_emoji, f'<tg-emoji emoji-id="{emoji_id}">{glyph}</tg-emoji>')
    return text


# ============================================================
# «.ویس متن» — TEXT TO VOICE (sent as a real Telegram voice message)
# ============================================================
# .ویس سلام خوبی؟          -> female voice (default)
# .ویس زن سلام خوبی؟       -> female voice
# .ویس مرد سلام خوبی؟      -> male voice
# .ویس  (reply on a text)  -> the replied text is spoken
# Engine: Microsoft Edge neural voices (pip install edge-tts), then
# ffmpeg -> OGG/Opus + real waveform so Telegram shows it as a native voice.

TTS_VOICES = {
    ("fa", "female"): "fa-IR-DilaraNeural",
    ("fa", "male"): "fa-IR-FaridNeural",
    ("en", "female"): "en-US-AriaNeural",
    ("en", "male"): "en-US-GuyNeural",
}
TTS_MAX_CHARS = int(os.getenv("TTS_MAX_CHARS", "1500"))
TTS_TIMEOUT_SECONDS = float(os.getenv("TTS_TIMEOUT_SECONDS", "60"))
TTS_RATE = os.getenv("TTS_RATE", "+0%")
TTS_PITCH = os.getenv("TTS_PITCH", "+0Hz")
_tts_locks = {}

# Exact «.ویس …» commands that belong to other features and must never be spoken.
_TTS_RESERVED = {"روشن", "خاموش", "به mp3", "به ام پی تری"}

_TTS_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U0000200D\U000020E3]+"
)
_TTS_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def _tts_parse(text):
    """«ویس …» -> (gender, body) or None when it is not a TTS command.
    body may be "" (then the replied message text is used)."""
    raw = (text or "").strip()
    m = re.match(r"^ویس(?=\s|$)(.*)$", raw, re.DOTALL)
    if not m:
        return None
    body = m.group(1).strip()
    if body.casefold() in _TTS_RESERVED:
        return None
    gender = "female"
    g = re.match(r"^(زن|زنانه|دختر|مرد|مردانه|پسر)(?=\s|$)(.*)$", body, re.DOTALL)
    if g:
        gender = "male" if g.group(1) in {"مرد", "مردانه", "پسر"} else "female"
        body = g.group(2).strip()
    return gender, body


def _tts_clean(text):
    text = _TTS_URL_RE.sub(" ", str(text or ""))
    text = _TTS_EMOJI_RE.sub(" ", text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text


def _tts_lang(text):
    fa = len(re.findall(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    return "en" if en and not fa else "fa"


_EDGE_TTS_INSTALL_LOCK = None
_EDGE_TTS_INSTALL_FAILED_AT = 0.0
EDGE_TTS_AUTO_INSTALL = os.getenv("EDGE_TTS_AUTO_INSTALL", "1") != "0"


def _edge_tts_importable():
    import importlib
    importlib.invalidate_caches()
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        sys.modules.pop("edge_tts", None)
        return False


async def _ensure_edge_tts(force=False):
    """Import edge-tts; if missing, pip-install it into THIS python once.
    Safe to call concurrently. Returns True when edge_tts is importable."""
    global _EDGE_TTS_INSTALL_LOCK, _EDGE_TTS_INSTALL_FAILED_AT
    if _edge_tts_importable():
        return True
    if not EDGE_TTS_AUTO_INSTALL:
        return False
    if _EDGE_TTS_INSTALL_LOCK is None:
        _EDGE_TTS_INSTALL_LOCK = asyncio.Lock()
    async with _EDGE_TTS_INSTALL_LOCK:
        if _edge_tts_importable():
            return True
        # After a failure, retry at most every 5 minutes instead of on every command.
        if not force and time.time() - _EDGE_TTS_INSTALL_FAILED_AT < 300:
            return False
        base = [sys.executable, "-m", "pip", "install", "-U", "--disable-pip-version-check", "-q", "edge-tts"]
        attempts = [base, base + ["--user"], base + ["--break-system-packages"],
                    base + ["--user", "--break-system-packages"]]
        for cmd in attempts:
            extra = " ".join(cmd[len(base):]) or "default"
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                _, err = await asyncio.wait_for(proc.communicate(), timeout=300)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[TTS] edge-tts install error ({extra}): {exc}")
                continue
            if proc.returncode == 0:
                if "--user" in cmd:
                    import site
                    with contextlib.suppress(Exception):
                        user_site = site.getusersitepackages()
                        if user_site and user_site not in sys.path:
                            sys.path.append(user_site)
                if _edge_tts_importable():
                    print("[TTS] edge-tts installed automatically ✅")
                    return True
            else:
                print(f"[TTS] pip failed ({extra}): " + err.decode("utf-8", "ignore").strip()[-300:])
        _EDGE_TTS_INSTALL_FAILED_AT = time.time()
        print("[TTS] edge-tts auto-install failed; install manually: pip install -U edge-tts")
        return False


async def _tts_synthesize(text, voice, out_path):
    if not await _ensure_edge_tts():
        raise RuntimeError("tts_not_installed")
    import edge_tts

    last_exc = None
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=TTS_RATE, pitch=TTS_PITCH)
            await asyncio.wait_for(communicate.save(str(out_path)), timeout=TTS_TIMEOUT_SECONDS)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 512:
                return
            last_exc = RuntimeError("empty_audio")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            last_exc = exc
        await asyncio.sleep(1.0 + attempt)
    raise RuntimeError(f"tts_failed: {type(last_exc).__name__}: {last_exc}")


async def _tts_to_opus(src, dst):
    proc = await asyncio.create_subprocess_exec(
        _media_binary_path("ffmpeg"), "-y", "-v", "error", "-i", str(src),
        "-vn", "-map_metadata", "-1", "-ac", "1", "-ar", "48000",
        "-c:a", "libopus", "-b:a", "48k", "-application", "voip", str(dst),
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
    )
    _, err = await asyncio.wait_for(proc.communicate(), timeout=120)
    if proc.returncode != 0 or not Path(dst).exists():
        raise RuntimeError("opus_failed: " + err.decode("utf-8", "ignore")[-300:])


async def _tts_waveform(path, samples=100):
    """5-bit Telegram waveform (100 bars) from the real audio peaks."""
    try:
        proc = await asyncio.create_subprocess_exec(
            _media_binary_path("ffmpeg"), "-v", "error", "-i", str(path),
            "-ac", "1", "-ar", "8000", "-f", "s16le", "-",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        )
        pcm, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        import array
        data = array.array("h")
        data.frombytes(pcm[: len(pcm) // 2 * 2])
        if not data:
            return None
        step = max(1, len(data) // samples)
        peaks = [max((abs(v) for v in data[i:i + step]), default=0) for i in range(0, step * samples, step)]
        top = max(peaks) or 1
        bars = bytes(min(31, int(p * 31 / top)) for p in peaks[:samples])
        return utils.encode_waveform(bars)
    except Exception:
        return None


async def _self_tts_command(event, uid, gender, body):
    uid = int(uid)

    async def say(msg):
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(msg), parse_mode="html")

    reply_to = event.reply_to_msg_id if event.is_reply else None
    text = body
    if not text:
        replied = await event.get_reply_message() if event.is_reply else None
        text = (getattr(replied, "raw_text", None) or "") if replied else ""
        if not text.strip():
            await say(
                "🗣 <b>تبدیل متن به ویس</b>\n\n"
                "<code>.ویس متن</code> ← صدای زن\n"
                "<code>.ویس مرد متن</code> ← صدای مرد\n"
                "یا روی یک پیام متنی ریپلای کن و فقط <code>.ویس</code> بفرست."
            )
            return

    text = _tts_clean(text)
    if not re.search(r"\w", text):
        await say("❌ متن قابل خواندن نیست؛ فقط ایموجی یا لینک نفرست.")
        return
    if len(text) > TTS_MAX_CHARS:
        await say(f"❌ متن خیلی طولانیه؛ حداکثر {TTS_MAX_CHARS} کاراکتر.")
        return

    lock = _tts_locks.setdefault(uid, asyncio.Lock())
    if lock.locked():
        await say("⏳ ویس قبلی هنوز در حال ساخته؛ چند لحظه صبر کن.")
        return

    async with lock:
        voice = TTS_VOICES[(_tts_lang(text), gender)]
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"htx_tts_{uid}_"))
        mp3_path = tmp_dir / "tts.mp3"
        ogg_path = tmp_dir / "voice.ogg"
        with contextlib.suppress(Exception):
            await event.edit("🎙", parse_mode=None)
        try:
            async with event.client.action(event.chat_id, "record-audio"):
                await _tts_synthesize(text, voice, mp3_path)

                has_ffmpeg = await _media_binary_exists("ffmpeg")
                send_path, mime = mp3_path, "audio/mpeg"
                if has_ffmpeg:
                    await _tts_to_opus(mp3_path, ogg_path)
                    send_path, mime = ogg_path, "audio/ogg"

                duration = 1
                with contextlib.suppress(Exception):
                    duration = max(1, int(round(await _ffprobe_duration(send_path))))
                waveform = await _tts_waveform(send_path) if has_ffmpeg else None

            attr = types.DocumentAttributeAudio(duration=duration, voice=True, waveform=waveform)
            await event.client.send_file(
                event.chat_id,
                str(send_path),
                voice_note=True,
                mime_type=mime,
                attributes=[attr],
                reply_to=reply_to,
            )
            with contextlib.suppress(Exception):
                await event.delete()
        except FloodWaitError as exc:
            await say(f"⏳ تلگرام محدودیت زد؛ {int(exc.seconds)} ثانیه دیگه دوباره امتحان کن.")
        except Exception as exc:
            print(f"[SELF {uid}] TTS failed: {exc}")
            msg = str(exc)
            if "tts_not_installed" in msg:
                await say("❌ نصب خودکار موتور ویس انجام نشد (اینترنت یا دسترسی pip سرور رو چک کن)؛ دستی بزن: <code>pip install -U edge-tts</code>")
            elif "tts_failed" in msg:
                await say("❌ سرویس ساخت صدا جواب نداد؛ اینترنت سرور رو چک کن و دوباره بفرست.")
            elif "VOICE_MESSAGES_FORBIDDEN" in msg or "VoiceMessagesForbidden" in msg:
                await say("❌ این کاربر دریافت ویس رو بسته.")
            elif "CHAT_SEND_VOICES_FORBIDDEN" in msg or "ChatSendVoicesForbidden" in msg:
                await say("❌ ارسال ویس توی این چت ممنوعه.")
            else:
                await say("❌ ساخت ویس ناموفق بود؛ دوباره تلاش کن.")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


async def _self_run_commands(event, uid, orig, text, low):
    """Run every SELF text command.

    Commands are only recognised when the message starts with a dot
    («.پینگ», «.ویس به mp3», …). `orig` is the full dotted message,
    `text` is the same message without the leading dot, `low` its
    casefolded form. Returns True when a command handled the message.
    """
    # «.e 50+25» — calculator (page 4 of the panel).
    if await _self_calc_command(event, uid, text):
        return True

    for command, platform in (("ph", "ph"), ("xvid", "xvid"), ("xnxx", "xnxx")):
        m = re.fullmatch(rf"{command}\s+(\S.*)", text.strip(), re.DOTALL | re.IGNORECASE)
        if m:
            await _self_download_command(event, uid, m.group(1), expected_platform=platform)
            return True

    # «.اینستا <لینک>» — Instagram downloader.
    # A bare «.دانلود» stays the reply-to-message saver below.
    m = re.fullmatch(r"اینستا\s+(\S.*)", text.strip(), re.DOTALL)
    if m:
        await _self_download_command(event, uid, m.group(1))
        return True

    # «.اسم» / «.بیو» / «.محتوا» parse the dotted form themselves.
    if await _handle_htx_profile_command(event, uid, orig):
        return True

    # «.تنظیم دشمن» / «.افزودن فحش …» / «.لیست دوستان» … and «.ویدیو مسیج».
    if await _handle_htx_fe_command(event, uid, orig):
        return True
    if await _handle_htx_video_note_command(event, uid, orig):
        return True

    if await _handle_mozy_command(event, uid, text):
        return True
    if await _handle_miowy_command(event, uid, text):
        return True
    if await _self_currency_command(event, uid, text):
        return True
    if await _self_logo_command(event, uid, text):
        return True

    if await _handle_first_comment_command(event, uid, text):
        return True
    if await _handle_secretary_command(event, uid, text):
        return True
    if await _handle_group_command(event, uid, text):
        return True
    if await _handle_premium_emoji_command(event, uid, text):
        return True
    if await _handle_snoopers_command(event, uid, text):
        return True

    if low == "اسکرین":
        await _self_screenshot_command(event, uid)
        return True

    m = re.fullmatch(r"حذف\s+(\d+)", _fa_digits(text))
    if m:
        await _self_delete_command(event, uid, int(m.group(1)))
        return True

    if low == "آیدی":
        await _self_id_info_command(event, uid)
        return True

    if low == "موجودی":
        await event.edit(_htx_balance_text(uid), parse_mode="html")
        return True

    m = re.fullmatch(r"انتقال\s+(\d+)", _fa_digits(text))
    if m:
        await _self_transfer_command(event, uid, int(m.group(1)))
        return True

    m = re.fullmatch(r"تکرار\s+([0-9۰-۹]+)", _fa_digits(text))
    if m:
        count = int(m.group(1))
        await event.edit(premium_ui_text(await _spam_replied(event, uid, count)), parse_mode="html")
        return True

    if low == "کپی پروفایل":
        await _profile_copy(event, uid)
        return True

    if low == "حذف کپی پروفایل":
        await _profile_copy_restore(event, uid)
        return True

    if low in _UNZIP_COMMANDS:
        result = await _self_unzip_reply(event, uid)
        if result != "__DONE__":
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text(result), parse_mode="html")
        return True

    if low == "دانلود":
        await event.edit(premium_ui_text(await _self_save_replied_message(event, uid)), parse_mode="html")
        return True

    media_operation = _media_conversion_command(text)
    if media_operation:
        if uid in media_convert_state:
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text("⏳ یک تبدیل رسانه‌ای همین حالا در حال انجام است."), parse_mode="html")
            return True
        result = await _self_media_convert(event, uid, media_operation)
        if result == "__SUCCESS__":
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text("✅ تبدیل با موفقیت انجام شد."), parse_mode="html")
        else:
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text(result), parse_mode="html")
        return True

    # «.ویس متن» / «.ویس مرد متن» / reply + «.ویس» — text to voice.
    tts = _tts_parse(text)
    if tts:
        await _self_tts_command(event, uid, *tts)
        return True

    if re.fullmatch(r"متن(?:\s*(?:\+\s*)?ریپ(?:ل|لی)|\s*\+\s*ریپ(?:ل|لی))?", low):
        # Reply to a voice/audio and transcribe it locally (real progress bar).
        if uid in stt_state:
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text("⏳ یک تبدیل ویس‌به‌متن همین حالا در حال انجامه."), parse_mode="html")
            return True
        try:
            result = await _self_transcribe_reply(event, uid)
        except Exception as exc:
            stt_state.pop(uid, None)
            print(f"[SELF {uid}] STT command failed: {type(exc).__name__}: {exc}")
            result = "❌ تبدیل ویس به متن با خطا متوقف شد؛ دوباره تلاش کن."
        await _stt_deliver(event, uid, result)
        return True

    if low == "دریافت الماس":
        if not event.is_group:
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text(f"{premium_emoji('restrict')} این قابلیت فقط درون گروه‌ها فعاله."), parse_mode="html")
            return True
        
        await resolve_official_group_id()
        if OFFICIAL_GROUP_ID is not None and int(event.chat_id) == int(OFFICIAL_GROUP_ID):
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text(f"{premium_emoji('restrict')} <b>این قابلیت فقط برای گروه‌های دیگر فعاله.</b>"), parse_mode="html")
            return True
        
        try:
            result = await _handle_daily_diamond_claim(event, uid)
            if result:
                await event.edit(premium_ui_text(result), parse_mode="html")
        except Exception as exc:
            print(f"[DAILY DIAMOND] claim failed: {exc}")
        return True

    if low in {"ocr", "او سی آر"}:
        try:
            result = await _self_ocr_reply(event, uid)
        except Exception as exc:
            print(f"[SELF {uid}] OCR command failed: {type(exc).__name__}: {exc}")
            result = "❌ OCR انجام نشد؛ دوباره تلاش کن."
        await _stt_deliver(event, uid, result)
        return True

    group_match = re.fullmatch(r"ساخت\s+گروه\s+(.+)", text, flags=re.S)
    if group_match:
        await event.edit(premium_ui_text(await _self_create_chat_or_channel(event, uid, "گروه", group_match.group(1))), parse_mode="html")
        return True

    channel_match = re.fullmatch(r"ساخت\s+چنل\s+(.+)", text, flags=re.S)
    if channel_match:
        await event.edit(premium_ui_text(await _self_create_chat_or_channel(event, uid, "چنل", channel_match.group(1))), parse_mode="html")
        return True

    dice_match = re.fullmatch(r"تاس\s+([1-6۱-۶])", text)
    if dice_match:
        chat_id = event.chat_id
        target_raw = dice_match.group(1)
        target = int(target_raw.translate(str.maketrans("۱۲۳۴۵۶", "123456")))

        with contextlib.suppress(Exception):
            await event.delete()

        ok = await _self_roll_guaranteed_value(event, uid, target)
        if not ok:
            await event.client.send_message(
                chat_id,
                f"❌ تلگرام اجازه تولید تاس {target} را نداد."
            )
        return True

    if low == "هک":
        await _fake_hack_prank(event, uid)
        return True

    if low == "پنل":
        # Instant feedback, but fired as a background task instead of
        # awaited here -- its own round trip no longer sits on the
        # critical path before the real inline flow even starts. It gets
        # superseded by event.delete() below once the real card lands, or
        # by the error edit if the flow fails.
        asyncio.create_task(_htx_panel_placeholder_edit(event))
        try:
            # The self account invokes the bot's inline mode and inserts the
            # result into this chat. The bot does NOT need to be a member here.
            last_exc = None
            for attempt in range(3):
                try:
                    await send_self_inline_result(event, "پنل")
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    if attempt < 2:
                        await asyncio.sleep(0.35)
            if last_exc is not None:
                raise last_exc
            await asyncio.sleep(HTX_PANEL_CMD_DELETE_DELAY)
            with contextlib.suppress(Exception):
                await event.delete()
        except Exception:
            print(f"[SELF {uid}] inline panel failed after 3 attempts")
            with contextlib.suppress(Exception):
                await event.edit(premium_ui_text("❌ پنل شیشه‌ای ارسال نشد. حالت Inline ربات را در BotFather فعال کنید."), parse_mode="html")
        return True

    if low == "تست ایموجی":
        # PoC trigger only — sends the button from the "تست ایموجی" inline
        # result above. It does not carry any premium emoji itself; that is
        # only added afterwards by editing this same message via the bot
        # (see the "poc_apply_premium_emoji" callback).
        try:
            last_exc = None
            for attempt in range(3):
                try:
                    await send_self_inline_result(event, "تست ایموجی")
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    if attempt < 2:
                        await asyncio.sleep(0.35)
            if last_exc is not None:
                raise last_exc
            with contextlib.suppress(Exception):
                await event.delete()
        except Exception:
            print(f"[SELF {uid}] inline emoji test failed after 3 attempts")
            with contextlib.suppress(Exception):
                await event.edit(
                    premium_ui_text("❌ پیام تست ارسال نشد. حالت Inline ربات را در BotFather فعال کنید."),
                    parse_mode="html",
                )
        return True

    if low in {"استیکر", "تبدیل عکس به استیکر", "عکس به استیکر"}:
        result = await _self_image_to_sticker(event, uid, keep_reply=False)
        with contextlib.suppress(Exception):
            await event.delete()
        if result.startswith("❌"):
            await event.client.send_message(event.chat_id, result)
        return True

    if low in {"استیکر + ریپلای", "استیکر ریپلای"}:
        result = await _self_image_to_sticker(event, uid, keep_reply=True)
        with contextlib.suppress(Exception):
            await event.delete()
        if result.startswith("❌"):
            await event.client.send_message(event.chat_id, result)
        return True

    if low in {"عکس", "تبدیل استیکر به عکس", "استیکر به عکس"}:
        result = await _self_sticker_to_photo(event, uid, keep_reply=False)
        with contextlib.suppress(Exception):
            await event.delete()
        if result.startswith("❌"):
            await event.client.send_message(event.chat_id, result)
        return True

    if low in {"عکس + ریپلای", "عکس ریپلای", "استیکر به عکس + ریپلای"}:
        result = await _self_sticker_to_photo(event, uid, keep_reply=True)
        with contextlib.suppress(Exception):
            await event.delete()
        if result.startswith("❌"):
            await event.client.send_message(event.chat_id, result)
        return True

    if low in {"تنظیم بنر فور", "تنظیم بنر کپی"}:
        if not event.is_reply:
            await event.edit(premium_ui_text("❌ روی پیام بنر ریپلای کن."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        if not replied:
            await event.edit(premium_ui_text("❌ پیام بنر پیدا نشد."), parse_mode="html")
            return True
        # In the main group only: «دریافت الماس» can't be registered as a banner.
        await resolve_official_group_id()
        if (
            OFFICIAL_GROUP_ID is not None
            and int(event.chat_id) == int(OFFICIAL_GROUP_ID)
            and _banner_is_claim_word({"text": replied.raw_text})
        ):
            await event.edit(premium_ui_text("❌ کلمه «دریافت الماس» داخل گپ اصلی به‌عنوان بنر ثبت نمی‌شود."), parse_mode="html")
            return True
        banners = self_banners(uid)
        banner_id = _next_banner_id(banners)
        mode = "forward" if low.endswith("فور") else "copy"
        banner = {
            "id": banner_id,
            "mode": mode,
            "source_chat_id": int(event.chat_id),
            "source_msg_id": int(replied.id),
            "text": replied.raw_text or "",
            "media_path": None,
            "interval": 60,
            "targets": [],
            "enabled": True,
            "last_sent": 0,
        }
        if mode == "copy" and getattr(replied, "media", None):
            if not getattr(replied, "photo", None):
                await event.edit(premium_ui_text("❌ برای بنر کپی فقط عکس مجاز است."), parse_mode="html")
                return True
            media_dir = _banner_media_dir(uid)
            media_path = await replied.download_media(file=str(media_dir / f"{banner_id}"))
            if media_path:
                banner["media_path"] = str(media_path)
        banners.append(banner)
        self_save_banners(uid, banners)
        await event.edit(premium_ui_text(f"✅ بنر #{banner_id} با حالت «{'فوروارد' if mode == 'forward' else 'کپی'}» ثبت شد."), parse_mode="html")
        return True

    m = re.fullmatch(r"حذف بنر\s+(\d+)", _fa_digits(text))
    if m:
        bid = int(m.group(1))
        banners = self_banners(uid)
        new = [b for b in banners if int(b.get("id", 0)) != bid]
        if len(new) == len(banners):
            await event.edit(premium_ui_text("❌ بنر موردنظر پیدا نشد."), parse_mode="html")
            return True
        old_b = _banner_by_id(uid, bid)
        if old_b and old_b.get("media_path"):
            with contextlib.suppress(Exception):
                Path(old_b["media_path"]).unlink(missing_ok=True)
        self_save_banners(uid, new)
        await event.edit(premium_ui_text(f"✅ بنر #{bid} حذف شد."), parse_mode="html")
        return True

    if low == "پاکسازی لیست بنر ها":
        for b in self_banners(uid):
            if b.get("media_path"):
                with contextlib.suppress(Exception):
                    Path(b["media_path"]).unlink(missing_ok=True)
        self_save_banners(uid, [])
        await event.edit(premium_ui_text("✅ لیست تمام بنرها پاک شد."), parse_mode="html")
        return True

    m = re.fullmatch(r"تنظیم عدد بنر\s+(\d+)\s+(\d+)\s+دقیقه", _fa_digits(text))
    if m:
        bid, minutes = int(m.group(1)), int(m.group(2))
        banners = self_banners(uid)
        banner = _banner_from_list(banners, bid)
        if not banner or minutes < 1:
            await event.edit(premium_ui_text("❌ بنر یا زمان نامعتبر است."), parse_mode="html")
            return True
        banner["interval"] = minutes
        self_save_banners(uid, banners)
        sent = failed = 0
        if self_get(uid, "banner_auto", "off") == "on" and banner.get("targets"):
            client = _get_tabchi_client(uid)
            if client:
                sent, failed = await _banner_dispatch_configured_now(client, uid, banner)
                self_save_banners(uid, banners)
        extra = f"\n📨 ارسال فوری: {sent} مقصد" if sent else ""
        if failed:
            extra += f"\n⚠️ ناموفق: {failed} مقصد"
        await event.edit(premium_ui_text(f"✅ فاصله ارسال بنر #{bid} روی {minutes} دقیقه تنظیم شد.{extra}"), parse_mode="html")
        return True

    m = re.fullmatch(r"تنظیم گپ هدف بنر\s+(\d+)", _fa_digits(text))
    if m:
        bid = int(m.group(1))
        banners = self_banners(uid)
        banner = _banner_from_list(banners, bid)
        if not banner or event.chat_id is None or not event.is_group:
            await event.edit(premium_ui_text("❌ این دستور را داخل گروه هدف اجرا کن."), parse_mode="html")
            return True
        chat_id = int(event.chat_id)
        targets = {int(x) for x in banner.get("targets", []) if int(x) != 0}
        targets.add(chat_id)
        banner["targets"] = sorted(targets)
        self_save_banners(uid, banners)
        sent = failed = 0
        if self_get(uid, "banner_auto", "off") == "on":
            client = _get_tabchi_client(uid)
            if client:
                sent, failed = await _banner_dispatch_configured_now(client, uid, banner)
                self_save_banners(uid, banners)
        extra = f"\n📨 ارسال فوری: {sent} مقصد" if sent else ""
        if failed:
            extra += f"\n⚠️ ناموفق: {failed} مقصد"
        await event.edit(premium_ui_text(f"✅ این گپ به مقصدهای بنر #{bid} اضافه شد.\n🎯 تعداد مقصدها: {len(banner['targets'])}{extra}"), parse_mode="html")
        return True

    m = re.fullmatch(r"حذف گپ هدف بنر\s+(\d+)", _fa_digits(text))
    if m:
        bid = int(m.group(1))
        banners = self_banners(uid)
        banner = _banner_from_list(banners, bid)
        if not banner or event.chat_id is None or not event.is_group:
            await event.edit(premium_ui_text("❌ این دستور را داخل گروه هدف اجرا کن."), parse_mode="html")
            return True
        chat_id = int(event.chat_id)
        banner["targets"] = [int(x) for x in banner.get("targets", []) if int(x) not in {0, chat_id}]
        self_save_banners(uid, banners)
        await event.edit(premium_ui_text(f"✅ این گپ از مقصدهای بنر #{bid} حذف شد.\n🎯 تعداد مقصدها: {len(banner['targets'])}"), parse_mode="html")
        return True

    m = re.fullmatch(r"تنظیم هدف بنر\s+(\d+)\s+تمام گپ ها", _fa_digits(text))
    if m:
        bid = int(m.group(1))
        banners = self_banners(uid)
        banner = _banner_from_list(banners, bid)
        if not banner:
            await event.edit(premium_ui_text("❌ بنر موردنظر پیدا نشد."), parse_mode="html")
            return True
        client = _get_tabchi_client(uid)
        if not client:
            await event.edit(premium_ui_text("❌ سلف فعال نیست."), parse_mode="html")
            return True
        targets = set()
        async for dialog in client.iter_dialogs():
            entity = getattr(dialog, "entity", None)
            if getattr(dialog, "is_group", False) and not getattr(entity, "broadcast", False):
                try:
                    targets.add(int(dialog.id))
                except (TypeError, ValueError):
                    pass
        banner["targets"] = sorted(x for x in targets if x != 0)
        self_save_banners(uid, banners)
        sent = failed = 0
        if self_get(uid, "banner_auto", "off") == "on" and banner["targets"]:
            client = _get_tabchi_client(uid)
            if client:
                sent, failed = await _banner_dispatch_configured_now(client, uid, banner)
                self_save_banners(uid, banners)
        extra = f"\n📨 ارسال فوری: {sent} مقصد" if sent else ""
        if failed:
            extra += f"\n⚠️ ناموفق: {failed} مقصد"
        await event.edit(premium_ui_text(f"✅ بنر #{bid} برای {len(banner['targets'])} گپ تنظیم شد.{extra}"), parse_mode="html")
        return True

    m = re.fullmatch(r"فور بنر در\s+(\d+)\s+پیوی اخیر", _fa_digits(text))
    if m:
        bid, count = int(m.group(1)), int(m.group(2))
        banner = _banner_by_id(uid, bid)
        if not banner or count < 1:
            await event.edit(premium_ui_text("❌ بنر یا تعداد نامعتبر است."), parse_mode="html")
            return True
        client = _get_tabchi_client(uid)
        if not client:
            await event.edit(premium_ui_text("❌ سلف فعال نیست."), parse_mode="html")
            return True
        targets = await _banner_recent_pv(client, count)
        sent, failed = await _banner_dispatch_now(client, uid, banner, targets)
        await event.edit(premium_ui_text(f"✅ بنر #{bid} به {sent} پیوی اخیر ارسال شد.\n❌ ناموفق: {failed}"), parse_mode="html")
        return True

    if low == "وضعیت تبچی":
        status = "روشن ✅" if self_get(uid, "banner_auto", "off") == "on" else "خاموش ❌"
        banners = self_banners(uid)
        await event.edit(
            premium_ui_text(f"📢 <b>وضعیت تبچی</b>\n\n"
            f"🔘 ارسال خودکار بنرها: {status}\n"
            f"📦 تعداد بنرهای ثبت‌شده: {len(banners)}")
        , parse_mode="html")
        return True

    if low == "لیست بنر هام":
        banners = self_banners(uid)
        if not banners:
            await event.edit(premium_ui_text("📢 <b>لیست بنرها خالی است.</b>"), parse_mode="html")
            return True
        body = ["📢 <b>بنرهای فعال</b>\n"]
        for b in banners:
            body.append(
                f"\n<b>#{b['id']}</b> • {'فوروارد' if b.get('mode') == 'forward' else 'کپی'}"
                f" • هر {int(b.get('interval', 60))} دقیقه • مقصد: {len(b.get('targets', []))}"
            )
        await event.edit(premium_ui_text("".join(body)), parse_mode="html")
        return True

    switches = {
        "بولد روشن": ("bold", "on"), "بولد خاموش": ("bold", "off"),
        "فونت فارسی روشن": ("persian_font", "on"), "فونت فارسی خاموش": ("persian_font", "off"),
        "مترجم روشن": ("translate", "on"), "مترجم خاموش": ("translate", "off"),
        "تبچی روشن": ("banner_auto", "on"), "تبچی خاموش": ("banner_auto", "off"),
        "پاسخ خودکار روشن": ("auto_reply", "on"), "پاسخ خودکار خاموش": ("auto_reply", "off"),
        "سین روشن": ("auto_read", "on"), "سین خاموش": ("auto_read", "off"),
        "تایپینگ روشن": ("typing", "on"), "تایپینگ خاموش": ("typing", "off"),
        "حالت بازی روشن": ("game_mode", "on"), "حالت بازی خاموش": ("game_mode", "off"),
        "ویس روشن": ("action_voice", "on"), "ویس خاموش": ("action_voice", "off"),
        "ویدیو گرد روشن": ("action_round", "on"), "ویدیو گرد خاموش": ("action_round", "off"),
        "ویدیو روشن": ("action_video", "on"), "ویدیو خاموش": ("action_video", "off"),
        "عکس روشن": ("action_photo", "on"), "عکس خاموش": ("action_photo", "off"),
        "سند روشن": ("action_document", "on"), "سند خاموش": ("action_document", "off"),
        "استیکر روشن": ("action_sticker", "on"), "استیکر خاموش": ("action_sticker", "off"),
        "همیشه آنلاین روشن": ("always_online", "on"), "همیشه آنلاین خاموش": ("always_online", "off"),
        "ساعت روشن": ("time_name", "on"), "ساعت خاموش": ("time_name", "off"),
        "تایمردار روشن": ("timer_saver", "on"), "تایمردار خاموش": ("timer_saver", "off"),
        "اسنپ شات گپ روشن": ("snap_group", "on"), "اسنپ شات گپ خاموش": ("snap_group", "off"),
        "اسنپ شات پیوی روشن": ("snap_private", "on"), "اسنپ شات پیوی خاموش": ("snap_private", "off"),
    }
    if low in switches:
        key, val = switches[low]
        if key == "banner_auto" and val == "on":
            client = _get_tabchi_client(uid)
            if not client:
                await event.edit(premium_ui_text("❌ سلف فعال نیست."), parse_mode="html")
                return True
            self_set(uid, key, val)
            sent, failed = await _banner_dispatch_all_configured(client, uid)
            status = f"روشن ✅\n📨 ارسال فوری: {sent} مقصد"
            if failed:
                status += f"\n⚠️ ناموفق: {failed}"
        else:
            self_set(uid, key, val)
            status = "روشن" if val == "on" else "خاموش"
            if key == "time_name":
                # on -> write the clock now, off -> remove it from the name.
                await apply_clock_toggle(uid, "name")
            if key == "snap_private" and val == "on":
                # Re-read the real history: messages may have arrived while it was off.
                for _k in [k for k in _snapshot_seeded if k[0] == int(uid)]:
                    _snapshot_seeded.discard(_k)
                _snap_client = self_clients.get(int(uid))
                if _snap_client:
                    _start_snapshot_seed(_snap_client, uid)

        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(f"✅ {text}\nوضعیت: {status}"), parse_mode="html")
        return True

    m = re.fullmatch(r"پاسخ خودکار جدید\s+(.+)", text, flags=re.S)
    if m:
        keyword = m.group(1).strip().casefold()
        if not keyword:
            await event.edit(premium_ui_text("❌ بعد از «.پاسخ خودکار جدید» کلمه را بنویس."), parse_mode="html")
            return True
        mapping = self_auto_reply_map(uid)
        mapping[keyword] = mapping.get(keyword, "")
        self_save_auto_reply_map(uid, mapping)
        await event.edit(premium_ui_text(f"✅ کلمه «{html.escape(keyword)}» برای پاسخ خودکار ثبت شد."), parse_mode="html")
        return True

    m = re.fullmatch(r"ذخیره پاسخ خودکار\s+(.+)", text, flags=re.S)
    if m:
        if not event.is_reply:
            await event.edit(premium_ui_text("❌ این دستور باید روی پیام پاسخ ریپلای شود."), parse_mode="html")
            return True
        keyword = m.group(1).strip().casefold()
        replied = await event.get_reply_message()
        if not keyword or not replied or not (replied.raw_text or "").strip():
            await event.edit(premium_ui_text("❌ کلمه را مشخص کن و روی پیام متنی موردنظر ریپلای کن."), parse_mode="html")
            return True
        mapping = self_auto_reply_map(uid)
        if keyword not in mapping:
            mapping[keyword] = ""
        mapping[keyword] = replied.raw_text.strip()
        self_save_auto_reply_map(uid, mapping)
        await event.edit(premium_ui_text(f"✅ پاسخ خودکار برای «{html.escape(keyword)}» ذخیره شد."), parse_mode="html")
        return True

    m = re.fullmatch(r"حذف پاسخ خودکار\s+(.+)", text, flags=re.S)
    if m:
        keyword = m.group(1).strip().casefold()
        mapping = self_auto_reply_map(uid)
        if not keyword or keyword not in mapping:
            await event.edit(premium_ui_text("❌ این کلمه در لیست پاسخ خودکار وجود ندارد."), parse_mode="html")
            return True
        mapping.pop(keyword, None)
        self_save_auto_reply_map(uid, mapping)
        await event.edit(premium_ui_text(f"✅ پاسخ خودکار «{html.escape(keyword)}» حذف شد."), parse_mode="html")
        return True

    if low == "لیست پاسخ خودکار":
        mapping = self_auto_reply_map(uid)
        if not mapping:
            await event.edit(premium_ui_text("💬 <b>لیست پاسخ خودکار خالی است.</b>"), parse_mode="html")
            return True
        body = ["💬 <b>لیست پاسخ خودکار</b>\n"]
        for i, (keyword, reply) in enumerate(mapping.items(), 1):
            body.append(f"\n{i}. <code>{html.escape(keyword)}</code> → {html.escape(reply[:120]) if reply else '❌ بدون پاسخ'}")
        await event.edit(premium_ui_text("".join(body)), parse_mode="html")
        return True

    if low == "پینگ":
        with contextlib.suppress(Exception):
            await event.edit(_ping_text(), parse_mode="html")
        return True

    m = re.fullmatch(r"فونت ساعت\s+(.+)", text, flags=re.S)
    if m:
        alias = m.group(1).strip().casefold()
        value = SELF_FONT_ALIASES.get(alias)
        if value in SELF_CLOCK_FONTS:
            self_set(uid, "clock_font", value)
            await event.edit(premium_ui_text(self_font_preview(uid, "clock")), parse_mode="html")
            return True

    m = re.fullmatch(r"فونت انگلیسی\s+(.+)", text, flags=re.S)
    if m:
        alias = m.group(1).strip().casefold()
        value = SELF_ENGLISH_FONT_ALIASES.get(alias, alias)
        if value not in SELF_ENGLISH_FONTS:
            await event.edit(premium_ui_text("❌ فونت نامعتبر است.\n" + " / ".join(SELF_ENGLISH_FONT_ALIASES)), parse_mode="html")
            return True
        self_set(uid, "english_font", value)
        await event.edit(premium_ui_text(self_font_preview(uid, "english")), parse_mode="html")
        return True

    reaction_match = re.fullmatch(r"ریاکشن\s+(\S+)", text)
    if reaction_match:
        emoji = reaction_match.group(1).strip()
        # Natural-language phrases such as «ریاکشن بزن» are not commands.
        # Keep Telegram as the authority for the actual supported emoji set.
        if any(ch.isalnum() for ch in emoji):
            return True
        # Telegram's supported reaction set changes over time.  Never keep a
        # small hard-coded whitelist here.  Accept the complete user-supplied
        # emoji sequence and let Telegram validate whether it is a reaction.
        emoji = re.sub(r"\s+", "", emoji)
        if not emoji or len(emoji) > 32:
            await event.edit(premium_ui_text("❌ ایموجی ریاکشن نامعتبر است. مثال: .ریاکشن 🔥"), parse_mode="html")
            return True
        if not event.is_reply:
            await event.edit(premium_ui_text("❌ روی پیام کاربر ریپلای کن و سپس «.ریاکشن 🔥» را بفرست."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        if not replied or not replied.sender_id:
            await event.edit(premium_ui_text("❌ کاربر پیدا نشد."), parse_mode="html")
            return True
        target = int(replied.sender_id)
        targets = self_reaction_targets(uid)
        targets.add(target)
        self_save_reaction_targets(uid, targets)
        # Telegram's canonical heart reaction is often U+2764 (❤), while
        # users commonly paste U+2764 U+FE0F (❤️). Keep the exact accepted
        # representation instead of converting ❤ into the variation-selector form.
        normalized_emoji = emoji
        try:
            await _send_self_reaction(event.client, event.chat_id, int(replied.id), normalized_emoji, label="reaction test")
            self_set_reaction(uid, target, normalized_emoji)
        except Exception as exc:
            # Keep the configuration only if Telegram accepts the reaction.
            # Otherwise roll it back so a bad emoji cannot poison future jobs.
            self_remove_reaction(uid, target)
            await event.edit(
                premium_ui_text("❌ این ایموجی در ریاکشن‌های قابل‌استفاده تلگرام نیست یا "
                f"تلگرام آن را نپذیرفت: {html.escape(str(exc))}")
            , parse_mode="html")
            return True

        await event.edit(
            premium_ui_text(f"✅ ریاکشن {normalized_emoji} برای کاربر `{target}` فعال شد.")
        , parse_mode="html")
        return True

    if low in {"حذف ریاکشن", "ریاکشن خاموش", "حذف ریاکشن ❤️", "حذف ریاکشن + ریپلای"}:
        if not event.is_reply:
            await event.edit(premium_ui_text("❌ روی پیام همان کاربر ریپلای کن."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        if replied and replied.sender_id:
            target = int(replied.sender_id)
            targets = self_reaction_targets(uid)
            targets.discard(target)
            self_save_reaction_targets(uid, targets)
            self_remove_reaction(uid, target)
            await event.edit(premium_ui_text("✅ ریاکشن خودکار این کاربر حذف شد."), parse_mode="html")
        return True

    if low in {"قفل چت", "قفل چت + ریپلای"}:
        if not event.is_private or not event.is_reply:
            await event.edit(premium_ui_text("❌ در پیوی، روی پیام همان کاربر ریپلای کن و «.قفل چت» را بفرست."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        target = int(replied.sender_id) if replied and replied.sender_id else 0
        if not target or target == uid:
            await event.edit(premium_ui_text("❌ کاربر هدف پیدا نشد."), parse_mode="html")
            return True
        targets = self_chat_lock_targets(uid)
        targets.add(target)
        self_save_chat_lock_targets(uid, targets)
        await event.edit(premium_ui_text(f"🔒 قفل چت برای `{target}` فعال شد. پیام‌های بعدی این کاربر دوطرفه پاک می‌شوند."), parse_mode="html")
        return True

    if low in {"بازکردن قفل چت", "باز کردن قفل چت", "قفل چت خاموش", "قفل چت خاموش + ریپلای"}:
        if not event.is_private or not event.is_reply:
            await event.edit(premium_ui_text("❌ در پیوی روی پیام همان کاربر ریپلای کن."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        target = int(replied.sender_id) if replied and replied.sender_id else 0
        targets = self_chat_lock_targets(uid)
        targets.discard(target)
        self_save_chat_lock_targets(uid, targets)
        await event.edit(premium_ui_text(f"🔓 قفل چت برای `{target}` خاموش شد."), parse_mode="html")
        return True

    if low == "قفل چت همگانی":
        self_set(uid, "chat_lock_global", "on")
        await event.edit(premium_ui_text("🔒 قفل چت همگانی فعال شد. پیام‌های هرکسی که در پیوی برای شما ارسال شود، دوطرفه پاک می‌شود."), parse_mode="html")
        return True

    if low in {"بازکردن قفل چت همگانی", "باز کردن قفل چت همگانی", "قفل چت همگانی خاموش"}:
        self_set(uid, "chat_lock_global", "off")
        await event.edit(premium_ui_text("🔓 قفل چت همگانی خاموش شد."), parse_mode="html")
        return True

    if low in {"بلاک + ریپلای", "بلاک ریپلای", "بلاک"} and event.is_reply:
        if not (event.is_group or event.is_channel):
            await event.edit(premium_ui_text("❌ این دستور برای گروه/سوپرگروه است."), parse_mode="html")
            return True
        replied = await event.get_reply_message()
        target = int(replied.sender_id) if replied and replied.sender_id else 0
        if not target or target == uid:
            await event.edit(premium_ui_text("❌ کاربر هدف پیدا نشد."), parse_mode="html")
            return True
        try:
            await _tg_call_with_flood_retry(
                lambda: event.client(functions.contacts.BlockRequest(id=target)),
                label="block user",
            )
            await event.edit(premium_ui_text(f"🚫 کاربر `{target}` بلاک شد."), parse_mode="html")
        except Exception as exc:
            await event.edit(premium_ui_text(f"❌ بلاک انجام نشد: {exc}"), parse_mode="html")
        return True

    return False


async def self_handle_outgoing(event, uid):
    text = (event.raw_text or "").strip()
    low = text.casefold()
    if not text:
        return

    # «.اسکرین»: the replied message is forwarded to @QuotLyBot. If its text
    # starts with «.» the forwarded copy must never be re-run as a command.
    if event.chat_id in _QUOTLY_BOT_IDS and getattr(event.message, "fwd_from", None):
        return

    # «.دانلود»: the link sent to the downloader bot is never a command and
    # must not go through translate / fonts / saved-content shortcuts.
    if event.chat_id in _DL_BOT_IDS:
        return

    # Messages relayed through the bot's inline mode (the "." premium-emoji
    # placeholder, the panel refresh, etc.) come back through this same
    # outgoing handler as a fresh self-sent message. The premium relay's
    # button is already pressed synchronously inside
    # _send_self_premium_inline_and_click() before that call even returns,
    # so this handler only needs to make sure it never re-parses that
    # synthetic message as a command. `via_bot_id` is the normal marker for
    # this, but SendInlineBotResultRequest uses hide_via=True so Telegram can
    # omit it — the bare "." placeholder text is the fallback marker.
    if getattr(event.message, "via_bot_id", None) or text == ".":
        return

    # Every command needs a leading dot («.دستور»). Plain messages never run
    # a command any more; they only go through the saved-content shortcuts
    # and the text transformations below.
    if text.startswith("."):
        cmd = text[1:].strip()
        if cmd and await _self_run_commands(event, uid, text, cmd, cmd.casefold()):
            return

    # Saved «.محتوا» shortcuts run after every built-in command, so a built-in
    # command always wins over a shortcut with the same text.
    if await _htx_apply_content(event, uid, text):
        return

    if text.startswith(("/", ".")):
        return

    transformed = text
    changed = False
    if self_get(uid, "translate") == "on":
        translated = await self_translate(event.client, transformed)
        if translated:
            transformed = translated
            changed = True
    if self_get(uid, "persian_font") == "on":
        transformed = self_stretch(transformed)
        changed = True
    if self_get(uid, "english_font", "normal") != "normal":
        transformed = self_transform_english(transformed, uid)
        changed = True

    premium_map = self_premium_emoji_map(uid)
    if premium_map and any(k and k in transformed for k in premium_map) and len(transformed) <= 250:
        # A non-premium self account cannot make a custom-emoji entity stick
        # by editing its own message directly — Telegram strips it. Route the
        # message through the bot's inline mode instead (same trick already
        # used for «پنل»/«راهنما»): the bot is exempt from the Premium
        # requirement, so it can attach the tg-emoji entity, and the result
        # still shows up as this account's own message (with a "via @bot" tag).
        #
        # The inline message is sent exactly ONCE and the source message is
        # deleted right after the send (inside the helper). Only failures that
        # happen BEFORE the send are retried; once the relay message exists, a
        # failed press is retried inside the helper and never re-sends.
        relay_exc = None
        source_gone = False
        try:
            for attempt in range(3):
                try:
                    source_gone = await _send_self_premium_inline_and_click(event, transformed)
                    relay_exc = None
                    break
                except _PremiumRelayPostSendError as exc:
                    relay_exc = exc
                    print(
                        f"[PREMIUM AUTO CLICK] attempt={attempt + 1} failed AFTER send "
                        f"(no re-send): {exc}"
                    )
                    break
                except Exception as exc:
                    relay_exc = exc
                    print(
                        f"[PREMIUM AUTO CLICK] attempt={attempt + 1} failed before send: "
                        f"{type(exc).__name__}: {exc!r}"
                    )
                    if attempt < 2:
                        await asyncio.sleep(0.08)
        except Exception as exc:
            relay_exc = exc

        if relay_exc is None:
            if not source_gone:
                with contextlib.suppress(Exception):
                    await event.delete()
            return

        print(f"[SELF {uid}] premium emoji relay failed: {relay_exc}")
        if getattr(relay_exc, "source_deleted", False):
            # The source message is already gone: deliver the plain text as a
            # fresh message so the user's text is never lost.
            with contextlib.suppress(Exception):
                await event.client.send_message(
                    event.peer_id,
                    transformed,
                    reply_to=getattr(event.message, "reply_to_msg_id", None),
                    parse_mode=None,
                )
            return
        # Otherwise fall through: still deliver the message in plain form
        # below instead of leaving the user's text stuck/unedited.

    if self_format_active(uid):
        await event.edit(premium_ui_text(self_apply_format(uid, transformed)), parse_mode="html")
        return
    if changed:
        await event.edit(premium_ui_text(transformed), parse_mode="html")


# ============================================================
# SELF INCOMING / PRESENCE
# ============================================================

def _cache_private_message(uid, message):
    """Keep only incoming private messages for deleted-message archiving."""
    chat_id = getattr(message, "chat_id", None)
    message_id = getattr(message, "id", None)
    sender_id = getattr(message, "sender_id", None)
    # Never cache the owner's own messages. This prevents self-deletions from
    # ever becoming archive candidates.
    if not chat_id or not message_id or not sender_id or int(sender_id) == int(uid):
        return
    key = (int(uid), int(chat_id))
    bucket = _deleted_message_cache.setdefault(key, [])
    # Replace an already-cached copy (edited message / history seed) instead
    # of duplicating it, then keep the bucket ordered by message id.
    for i, old in enumerate(bucket):
        if getattr(old, "id", None) == message_id:
            bucket[i] = message
            break
    else:
        bucket.append(message)
    bucket.sort(key=lambda m: getattr(m, "id", 0))
    _deleted_message_index[(int(uid), int(message_id))] = int(chat_id)
    if len(bucket) > HTX_SNAPSHOT_CACHE_SIZE:
        stale = bucket[:-HTX_SNAPSHOT_CACHE_SIZE]
        del bucket[:-HTX_SNAPSHOT_CACHE_SIZE]
        for old in stale:
            old_id = getattr(old, "id", None)
            if old_id is not None:
                _deleted_message_index.pop((int(uid), int(old_id)), None)


async def _seed_private_chat_snapshot(client, uid, chat_id):
    """Back-fill one private chat's snapshot cache from the server history.

    The live cache only knows messages that arrived while the bot was running
    with «اسنپ شات پیوی» on. Anything older (an hour ago, before a redeploy,
    before the toggle) was never cached, so it could not be archived when the
    chat was cleared. Here the last incoming messages are read from Telegram
    itself, so the cache holds up to HTX_SNAPSHOT_CACHE_SIZE recent incoming
    messages and a message deleted from anywhere in that range is recoverable.
    """
    key = (int(uid), int(chat_id))
    if key in _snapshot_seeded:
        return
    _snapshot_seeded.add(key)
    try:
        found = []
        async for msg in client.iter_messages(chat_id, limit=HTX_SNAPSHOT_CACHE_SIZE * 2):
            sender_id = getattr(msg, "sender_id", None)
            if getattr(msg, "out", False) or not sender_id or int(sender_id) == int(uid):
                continue
            found.append(msg)
            if len(found) >= HTX_SNAPSHOT_CACHE_SIZE:
                break
        for msg in reversed(found):
            _cache_private_message(uid, msg)
    except Exception as exc:
        _snapshot_seeded.discard(key)  # allow a retry on the next incoming message
        print(f"[SELF {uid}] snapshot seed failed for chat {chat_id}: {type(exc).__name__}: {exc}")


async def _seed_private_snapshots(client, uid):
    """Back-fill the most recent private dialogs (run at start-up and when
    «اسنپ شات پیوی» is switched on)."""
    try:
        async for dialog in client.iter_dialogs(limit=HTX_SNAPSHOT_SEED_DIALOGS):
            if self_get(uid, "snap_private", "off") != "on":
                return
            entity = getattr(dialog, "entity", None)
            if not getattr(dialog, "is_user", False) or entity is None:
                continue
            if getattr(entity, "bot", False) or getattr(entity, "deleted", False):
                continue
            if int(getattr(entity, "id", 0) or 0) == int(uid):
                continue
            await _seed_private_chat_snapshot(client, uid, int(entity.id))
            await asyncio.sleep(0.6)  # stay far away from flood limits
    except Exception as exc:
        print(f"[SELF {uid}] snapshot seeding stopped: {type(exc).__name__}: {exc}")


def _start_snapshot_seed(client, uid, chat_id=None):
    """Fire-and-forget seeding task (kept referenced so it is not garbage collected)."""
    coro = (_seed_private_chat_snapshot(client, uid, chat_id) if chat_id
            else _seed_private_snapshots(client, uid))
    task = asyncio.create_task(coro)
    _snapshot_seed_tasks.add(task)
    task.add_done_callback(_snapshot_seed_tasks.discard)


def _cache_group_reply(uid, message):
    """«اسنپ شات گپ»: remember a reply message's text/sender/chat just long
    enough to recover it if the reply itself gets deleted. Non-reply group
    messages are never passed in here at all."""
    message_id = getattr(message, "id", None)
    chat_id = getattr(message, "chat_id", None)
    sender_id = getattr(message, "sender_id", None)
    if not message_id or not chat_id or not sender_id:
        return
    key = (int(uid), int(message_id))
    _snap_group_cache[key] = message
    order = _snap_group_order.setdefault(int(uid), [])
    order.append(int(message_id))
    if len(order) > HTX_SNAP_GROUP_CACHE_SIZE:
        stale = order[:-HTX_SNAP_GROUP_CACHE_SIZE]
        del order[:-HTX_SNAP_GROUP_CACHE_SIZE]
        for old_id in stale:
            _snap_group_cache.pop((int(uid), int(old_id)), None)


async def _archive_snap_group_reply(client, uid, message):
    """«اسنپ شات گپ»: send a deleted group reply to Saved Messages — its
    text (or media), followed by «👤 user | 💬 group» (username when the
    person/group has one, numeric id otherwise)."""
    sender_id = getattr(message, "sender_id", None)
    chat_id = getattr(message, "chat_id", None)
    try:
        user_field = str(sender_id)
        with contextlib.suppress(Exception):
            sender = await client.get_entity(sender_id)
            username = getattr(sender, "username", None)
            if username:
                user_field = f"@{username}"
        group_field = str(chat_id)
        with contextlib.suppress(Exception):
            chat = await client.get_entity(chat_id)
            chat_username = getattr(chat, "username", None)
            if chat_username:
                group_field = f"@{chat_username}"
        footer = f"👤 {user_field} | 💬 {group_field}"
        body = (message.raw_text or "").strip()
        caption = f"{body}\n\n{footer}" if body else footer
        if getattr(message, "media", None):
            path = await message.download_media()
            if path:
                try:
                    await client.send_file("me", path, caption=caption[:1024])
                finally:
                    with contextlib.suppress(Exception):
                        os.remove(path)
                return
        await client.send_message("me", caption)
    except Exception as exc:
        print(f"[SELF {uid}] snap-group archive failed: {exc}")


async def _archive_messages_to_saved(client, uid, messages):
    """Copy archived messages to Saved Messages and always keep author identity visible."""
    saved = 0
    seen = set()
    for msg in sorted(messages, key=lambda m: getattr(m, "id", 0)):
        msg_id = getattr(msg, "id", None)
        if msg_id in seen:
            continue
        seen.add(msg_id)

        sender_id = getattr(msg, "sender_id", None)
        # Only the other human participant's private messages may be archived.
        # Bot messages are intentionally excluded from the deletion snapshot.
        if not sender_id or int(sender_id) == int(uid):
            continue
        try:
            sender = await client.get_entity(int(sender_id))
            if getattr(sender, "bot", False):
                continue
            username = getattr(sender, "username", None)
            first_name = getattr(sender, "first_name", None) or "کاربر"
            sender_label = f"@{username}" if username else f"{first_name} | ID: {int(sender_id)}"
        except Exception:
            sender_label = f"ID: {int(sender_id)}"
        author_footer = f"👤 نویسنده: {sender_label}"

        # Deliberately copy instead of forwarding.  This keeps Saved Messages
        # clean while the explicit author footer guarantees attribution even
        # when Telegram cannot create a forward for a deleted message.
        try:
            body = (msg.raw_text or "").strip()
            caption = f"{body}\n\n{author_footer}" if body else author_footer
            if getattr(msg, "media", None):
                path = await msg.download_media()
                if path:
                    try:
                        await client.send_file("me", path, caption=caption)
                    finally:
                        with contextlib.suppress(Exception):
                            os.remove(path)
                    saved += 1
            elif body:
                await client.send_message("me", caption)
                saved += 1
        except Exception as exc:
            print(f"[SELF {uid}] deleted-chat archive {msg_id or '?'}: {exc}")
    return saved


async def _archive_last_snapshot_before_delete(client, uid, chat_id, deleted_ids=None):
    """Archive deleted messages (at most HTX_DELETE_SNAPSHOT_SIZE per deletion,
    taken from wherever in the chat they were); when the whole chat is gone,
    archive the last HTX_DELETE_SNAPSHOT_SIZE
    only when the whole private history is gone."""
    try:
        deleted_ids = {int(x) for x in (deleted_ids or [])}
        cached = list(_deleted_message_cache.get((int(uid), int(chat_id)), []))
        deleted_messages = [m for m in cached if getattr(m, "id", 0) in deleted_ids]

        # MessageDeleted does not reliably expose whether the user chose
        # "delete entire chat".  The most reliable post-delete signal is that
        # no message remains in the private dialog.  Only in that case do we
        # take the full snapshot. A normal message deletion archives
        # only the message(s) actually deleted and never unrelated messages.
        remaining = None
        query_ok = False
        try:
            query_ok = True
            async for _ in client.iter_messages(chat_id, limit=1):
                remaining = True
                break
        except Exception as exc:
            query_ok = False
            print(f"[SELF {uid}] deleted-chat remaining-message check failed: {exc}")
        # Telegram may still report the last message for a moment right after
        # a chat is cleared — look once more before deciding it is not empty.
        if query_ok and remaining is True:
            await asyncio.sleep(1.5)
            remaining = None
            with contextlib.suppress(Exception):
                async for _ in client.iter_messages(chat_id, limit=1):
                    remaining = True
                    break
        whole_chat_cleared = query_ok and remaining is not True

        if whole_chat_cleared and cached:
            to_archive = sorted(cached, key=lambda m: getattr(m, "id", 0))[-HTX_DELETE_SNAPSHOT_SIZE:]
        else:
            # Whichever messages were deleted — even 200 messages up — up to
            # HTX_DELETE_SNAPSHOT_SIZE of them are archived (newest first pick).
            to_archive = sorted(deleted_messages, key=lambda m: getattr(m, "id", 0))[-HTX_DELETE_SNAPSHOT_SIZE:]

        # A cleared chat can arrive as several deletion events; never save a
        # message twice.
        fresh = []
        for m in to_archive:
            mid = (int(uid), int(getattr(m, "id", 0) or 0))
            if mid in _snapshot_archived:
                continue
            _snapshot_archived.add(mid)
            fresh.append(m)
        if len(_snapshot_archived) > 5000:
            _snapshot_archived.clear()
        # Handled messages leave the cache, so a later deletion picks the next
        # ones instead of the same messages again.
        gone = {int(getattr(m, "id", 0) or 0) for m in (cached if whole_chat_cleared else deleted_messages)}
        bucket = _deleted_message_cache.get((int(uid), int(chat_id)))
        if bucket is not None:
            bucket[:] = [m for m in bucket if int(getattr(m, "id", 0) or 0) not in gone]
        for mid_ in gone:
            _deleted_message_index.pop((int(uid), mid_), None)
        if not fresh:
            return 0
        return await _archive_messages_to_saved(client, uid, fresh)
    except Exception as exc:
        print(f"[SELF {uid}] deleted-chat archive failed: {exc}")
        return 0

async def self_handle_incoming(event, uid):
    client = event.client

    sender_id = int(event.sender_id) if event.sender_id else 0
    # «.اسکرین»: whatever @QuotLyBot sends is handled only by that command —
    # no secretary / auto-reply / archive / read-receipt side effects.
    if sender_id and sender_id in _QUOTLY_BOT_IDS:
        return
    # «.دانلود»: the downloader bot's answers are handled only by that command.
    # Anything it sends while no download is running (a late answer after a
    # timeout) is deleted on the spot so it never shows up in the chat list.
    if sender_id and sender_id in _DL_BOT_IDS:
        if int(uid) not in _dl_active:
            _dl_sweep_later(event.client, sender_id)
        return
    print(f"[SELF {uid}] incoming: chat={event.chat_id} sender={sender_id} private={event.is_private} msg={event.id} text={(event.raw_text or '')[:80]!r}")
    if event.is_private and sender_id and sender_id != int(uid):
        if self_get(uid, "snap_private", "off") == "on":
            _cache_private_message(uid, event.message)
            # First message seen from this chat since start-up: pull its real
            # recent history so older messages are covered too.
            if (int(uid), int(event.chat_id)) not in _snapshot_seeded:
                _start_snapshot_seed(client, uid, int(event.chat_id))
        await _self_capture_timer_media(event, uid)

    # «اسنپ شات گپ»: only reply messages are worth caching — everything
    # else is left alone, per _cache_group_reply's own docstring.
    if event.is_group and event.is_reply and sender_id and sender_id != int(uid) and self_get(uid, "snap_group", "off") == "on":
        _cache_group_reply(uid, event.message)

    # "لیست فضول‌ها": anyone who replies to the account owner — in ANY chat
    # the self account is present in (group, private, or channel comments) —
    # gets logged as a (guessed) profile-visit candidate.
    if event.is_reply and sender_id and sender_id != int(uid):
        with contextlib.suppress(Exception):
            replied = await event.get_reply_message()
            if replied and replied.sender_id and int(replied.sender_id) == int(uid):
                sender = await event.get_sender()
                if not getattr(sender, "bot", False):
                    _snoopers_add(uid, sender_id, _format_snooper_display(sender, sender_id))
    if (event.is_group or event.is_channel) and sender_id and sender_id in _global_ban_list(uid) and sender_id != int(uid):
        with contextlib.suppress(Exception):
            if event.is_group:
                await client.edit_permissions(event.chat_id, sender_id, view_messages=False, send_messages=False)
        return

    if event.is_private and sender_id and sender_id != int(uid) and (
        sender_id in self_chat_lock_targets(uid) or self_get(uid, "chat_lock_global", "off") == "on"
        or _self_content_lock_hit(uid, event.message)
    ):
        # Delete this incoming message for both sides when Telegram allows revoke.
        with contextlib.suppress(Exception):
            await _tg_call_with_flood_retry(
                lambda: client.delete_messages(event.chat_id, event.id, revoke=True),
                label="chat lock incoming delete",
            )
        return

    if self_get(uid, "auto_read", "off") == "on":
        with contextlib.suppress(Exception):
            await client.send_read_acknowledge(event.chat_id, max_id=event.id)

    if event.sender_id and int(event.sender_id) in self_reaction_targets(uid):
        target_sender = int(event.sender_id)
        emoji = self_reaction_map(uid).get(target_sender, "❤️")
        try:
            await _send_self_reaction(client, event.chat_id, int(event.id), emoji, label="automatic reaction")
        except Exception as exc:
            # A reaction can become unavailable after it was configured.
            # Disable only that broken mapping instead of breaking all
            # incoming-message processing.
            print(
                f"[REACTION {uid}] emoji {emoji!r} failed for {target_sender}: {exc}"
            )
            self_remove_reaction(uid, target_sender)
            self_save_reaction_targets(
                uid,
                self_reaction_targets(uid) - {target_sender},
            )

    # دوست و دشمن: a registered user gets an instant random reply to every
    # message; that reply replaces the secretary / auto-reply for that user.
    if await _htx_fe_incoming(event, uid):
        return

    if event.is_private and self_get(uid, SECRETARY_ENABLED_KEY, "off") == "on" and event.sender_id and int(event.sender_id) != int(uid):
        sender = int(event.sender_id)
        key = (int(uid), sender)
        now = time.time()
        interval = max(5, min(60, int(self_get(uid, SECRETARY_INTERVAL_KEY, "5") or 5))) * 60
        last = float(_secretary_reply_cache.get(key, 0) or 0)
        if now - last >= interval:
            reply = _secretary_reply(uid)
            print(f"[SECRETARY {uid}] trigger sender={sender} enabled=on interval={interval // 60}m has_reply={bool(reply)}")
            if reply:
                try:
                    if reply.get("kind") == "media" and reply.get("path") and Path(reply["path"]).exists():
                        await client.send_file(event.chat_id, reply["path"], caption=(reply.get("caption") or "")[:4096])
                    else:
                        await client.send_message(event.chat_id, reply.get("text") or reply.get("caption") or "")
                    _secretary_reply_cache[key] = now
                except Exception as exc:
                    print(f"[SECRETARY {uid}] reply failed: {exc}")

    if event.is_private and self_get(uid, "auto_reply", "off") == "on" and event.sender_id and int(event.sender_id) != int(uid):
        incoming_text = (event.raw_text or "").strip().casefold()
        replies = self_auto_reply_map(uid)
        if incoming_text in replies and replies.get(incoming_text):
            cache_key = (int(uid), int(event.sender_id), incoming_text)
            if cache_key not in _self_reply_cache:
                _self_reply_cache.add(cache_key)
                with contextlib.suppress(Exception):
                    await event.respond(replies[incoming_text])
                asyncio.create_task(_clear_self_reply_cache(cache_key))

async def _self_capture_timer_media(event, uid):
    """«تایمردار»: when a self-destructing (timer) photo or video message
    arrives, silently mirror it into Saved Messages before it can expire.
    No message is sent back into the original chat and nothing is printed
    to the console either way — a failure here is simply swallowed so it
    never disrupts the rest of incoming-message handling."""
    if self_get(uid, "timer_saver", "off") != "on":
        return
    media = getattr(event.message, "media", None)
    if not media or not getattr(media, "ttl_seconds", None):
        return
    try:
        data = await event.client.download_media(event.message, file=bytes)
        if not data:
            return
        import mimetypes
        from io import BytesIO
        filename = "photo.jpg"
        if isinstance(media, types.MessageMediaDocument):
            mime = getattr(getattr(media, "document", None), "mime_type", "") or ""
            ext = mimetypes.guess_extension(mime) or (".mp4" if mime.startswith("video") else ".bin")
            filename = ("video" if mime.startswith("video") else "file") + ext
        buf = BytesIO(data)
        buf.name = filename
        await event.client.send_file("me", buf, force_document=False)
    except Exception:
        pass


async def _clear_self_reply_cache(key):
    await asyncio.sleep(60)
    _self_reply_cache.discard(key)

# «⚡ اکشن آنلاین» — the chat-activity status shown at the top of the other
# side's chat ("Recording voice...", "Sending photo...", etc). Checked in
# this fixed order every loop tick; every toggle that's on gets its turn.
_ACTION_ORDER = (
    "typing", "action_voice", "action_round", "action_video",
    "action_photo", "action_document", "action_sticker", "game_mode",
)
_ALWAYS_ONLINE_PING_SECONDS = 50   # keep-alive interval for «همیشه آنلاین»


def _presence_action_instance(key):
    if key == "typing":
        return types.SendMessageTypingAction()
    if key == "action_voice":
        return types.SendMessageRecordAudioAction()
    if key == "action_round":
        return types.SendMessageRecordRoundAction()
    if key == "action_video":
        return types.SendMessageRecordVideoAction()
    if key == "action_photo":
        return types.SendMessageUploadPhotoAction(progress=50)
    if key == "action_document":
        return types.SendMessageUploadDocumentAction(progress=50)
    if key == "action_sticker":
        return types.SendMessageChooseStickerAction()
    if key == "game_mode":
        return types.SendMessageGamePlayAction()
    return None


async def _send_presence(client, entity, action_key):
    try:
        action = _presence_action_instance(action_key)
        if action is None:
            return False
        await client(SetTypingRequest(peer=entity, action=action))
        return True
    except Exception:
        return False


async def _presence_loop(client, uid):
    last_online_ping = 0.0
    while True:
        try:
            active = [k for k in _ACTION_ORDER if self_get(uid, k, "off") == "on"]
            always_online = self_get(uid, "always_online", "off") == "on"

            now = time.time()
            if always_online and now - last_online_ping > _ALWAYS_ONLINE_PING_SECONDS:
                with contextlib.suppress(Exception):
                    await client(functions.account.UpdateStatusRequest(offline=False))
                last_online_ping = now

            if not active:
                await asyncio.sleep(2)
                continue
            async for dialog in client.iter_dialogs():
                entity = getattr(dialog, "entity", None)
                if not entity or getattr(entity, "bot", False) or getattr(entity, "id", None) == uid:
                    continue
                for action_key in active:
                    await _send_presence(client, entity, action_key)
                    await asyncio.sleep(0.05)
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"[SELF {uid}] presence loop: {exc}")
            await asyncio.sleep(3)

# ============================================================
# MOZY AUTOMATION
# ============================================================

MOZY_CONFIG_KEY = "mozy_configs_v2"
MOZY_FEATURES = ("banana", "spin", "monkey")
MOZY_COMMANDS = {
    "banana": "موز",
    "spin": "اسپین",
    "monkey": "میمون",
}
MOZY_DISPLAY = {
    "banana": "🍌 موز خودکار",
    "spin": "🎰 اسپین خودکار",
    "monkey": "🐒 درآمد میمون",
}
MOZY_DEFAULT_INTERVALS = {
    "banana": 185,   # 3 minutes + 5 seconds
    "spin": 21605,   # 6 hours + 5 seconds
    "monkey": 43205, # 12 hours + 5 seconds
}
MOZY_MONKEY_BUTTON = "برداشت همه"
MOZY_MONKEY_RESPONSE_WAIT = 30.0
MOZY_BANANA_WORDS = ("موز", "مظ")
MOZY_BANANA_RANDOM_CHANCE = 0.35   # chance a turn breaks the strict alternation
_mozy_banana_last = {}             # (uid, chat_id) -> last word sent
MOZY_RESPONSE_WAIT = 20.0
MOZY_POLL_INTERVAL = 0.7
_mozy_running = set()
_mozy_flood_until = {}


def _mozy_default_feature(feature=None):
    return {"enabled": False, "interval": int(MOZY_DEFAULT_INTERVALS.get(feature, 0) or 0), "last_run": 0.0}


def _mozy_configs(uid: int):
    """Load per-user Miowy settings; each chat owns independent feature state."""
    try:
        raw = self_get(uid, MOZY_CONFIG_KEY, "{}")
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            return {}
    except Exception:
        return {}
    out = {}
    changed = False
    for raw_chat, raw_cfg in data.items():
        try:
            chat_id = int(raw_chat)
        except (TypeError, ValueError):
            changed = True
            continue
        if not isinstance(raw_cfg, dict):
            changed = True
            continue
        cfg = {}
        for feature in MOZY_FEATURES:
            item = raw_cfg.get(feature, {})
            if not isinstance(item, dict):
                item = {}
                changed = True
            try:
                interval = max(0, int(item.get("interval", 0) or 0))
            except (TypeError, ValueError):
                interval = 0
                changed = True
            if interval <= 0:
                interval = int(MOZY_DEFAULT_INTERVALS.get(feature, 0) or 0)
            try:
                last_run = float(item.get("last_run", 0) or 0)
            except (TypeError, ValueError):
                last_run = 0.0
                changed = True
            enabled = item.get("enabled", False) not in {False, 0, "0", "off", "false"}
            cfg[feature] = {"enabled": bool(enabled), "interval": interval, "last_run": last_run}
        out[str(chat_id)] = cfg
    if changed:
        _mozy_save_configs(uid, out)
    return out


def _mozy_save_configs(uid: int, configs):
    self_set(uid, MOZY_CONFIG_KEY, json.dumps(configs, ensure_ascii=False, separators=(",", ":")))


def _mozy_chat_config(uid: int, chat_id: int, create=True):
    configs = _mozy_configs(uid)
    key = str(int(chat_id))
    cfg = configs.get(key)
    if cfg is None:
        if not create:
            return None, configs
        cfg = {feature: _mozy_default_feature(feature) for feature in MOZY_FEATURES}
        configs[key] = cfg
    else:
        for feature in MOZY_FEATURES:
            cfg.setdefault(feature, _mozy_default_feature(feature))
    return cfg, configs


def _mozy_set_interval(uid: int, feature: str, minutes: int):
    configs = _mozy_configs(uid)
    for chat_cfg in configs.values():
        chat_cfg.setdefault(feature, _mozy_default_feature(feature))
        # The interval is a user setting, mirrored into existing chat records.
        chat_cfg[feature]["interval"] = int(minutes)
    _mozy_save_configs(uid, configs)
    # Also keep an explicit user-level value so a group activated later inherits it.
    self_set(uid, f"miowy_interval_{feature}", int(minutes))


def _mozy_user_interval(uid: int, feature: str) -> int:
    try:
        return max(0, int(self_get(uid, f"miowy_interval_{feature}", "0") or 0))
    except (TypeError, ValueError):
        return 0


def _mozy_update_feature(uid: int, chat_id: int, feature: str, *, enabled=None, last_run=None):
    cfg, configs = _mozy_chat_config(uid, chat_id, create=True)
    item = cfg[feature]
    if enabled is not None:
        item["enabled"] = bool(enabled)
    if last_run is not None:
        item["last_run"] = float(last_run)
    # A group activated after the PV interval was configured inherits that interval.
    if int(item.get("interval", 0) or 0) <= 0:
        item["interval"] = _mozy_user_interval(uid, feature)
    _mozy_save_configs(uid, configs)
    return item


def _mozy_interval_text(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours} ساعت")
    if minutes:
        parts.append(f"{minutes} دقیقه")
    if secs:
        parts.append(f"{secs} ثانیه")
    return " و ".join(parts) if parts else "تنظیم نشده"


def _mozy_status_text(uid: int, chat_id: int | None = None):
    if chat_id is not None:
        cfg, _ = _mozy_chat_config(uid, chat_id, create=False)
        title = "🍌 <b>وضعیت موزی</b>"
        if not cfg:
            cfg = {feature: _mozy_default_feature(feature) for feature in MOZY_FEATURES}
        lines = [title, "", f"🆔 گپ: <code>{int(chat_id)}</code>"]
        for feature in MOZY_FEATURES:
            item = cfg.get(feature, _mozy_default_feature(feature))
            status = "✅ روشن" if item.get("enabled") else "❌ خاموش"
            interval = int(item.get("interval", 0) or 0)
            lines.append(f"{MOZY_DISPLAY[feature]}: {status}")
            lines.append(f"⏱ زمان: {_mozy_interval_text(interval)}" if interval else "⏱ زمان: تنظیم نشده")
        return "\n".join(lines)

    configs = _mozy_configs(uid)
    if not configs:
        return "🍌 <b>وضعیت موزی</b>\n\nهنوز هیچ گروهی برای موزی تنظیم نشده است."
    lines = ["🍌 <b>وضعیت موزی</b>", ""]
    for raw_chat, cfg in configs.items():
        try:
            chat_id_value = int(raw_chat)
        except (TypeError, ValueError):
            continue
        lines.append(f"🆔 گپ: <code>{chat_id_value}</code>")
        for feature in MOZY_FEATURES:
            item = cfg.get(feature, _mozy_default_feature(feature))
            status = "✅ روشن" if item.get("enabled") else "❌ خاموش"
            interval = int(item.get("interval", 0) or 0)
            lines.append(f"{MOZY_DISPLAY[feature]}: {status} • ⏱ {_mozy_interval_text(interval)}" if interval else f"{MOZY_DISPLAY[feature]}: {status} • ⏱ تنظیم نشده")
        lines.append("")
    return "\n".join(lines).rstrip()


def _mozy_button_score(text: str, feature: str, context: str = "") -> int:
    """Conservative matcher for Miowy reply keyboards."""
    value = (text or "").casefold().strip()
    ctx = (context or "").casefold()
    if not value:
        return 0
    if feature == "banana":
        strong = ("موز", "banana", "🍌")
        supporting = ("گرفتن", "دریافت", "پاداش", "claim", "reward", "get")
    else:
        strong = ("اسپین", "spin", "🎰", "چرخ")
        supporting = ("انجام", "بزن", "دریافت", "claim", "reward", "get")
    score = sum(4 if term in value else 0 for term in strong)
    score += sum(1 for term in supporting if term in value)
    if any(term in ctx for term in strong):
        score += 2
    return score if any(term in value for term in strong) and score >= 3 else 0

def _mozy_iter_buttons(message):
    buttons = getattr(message, "buttons", None) or []
    for row in buttons:
        for button in (row if isinstance(row, (list, tuple)) else [row]):
            yield button


async def _mozy_find_and_click(client, uid: int, chat_id: int, trigger_message_id: int, feature: str):
    """Inspect only messages created after this trigger; never click an old keyboard."""
    deadline = time.monotonic() + MOZY_RESPONSE_WAIT
    seen_ids = set()
    while time.monotonic() < deadline:
        try:
            async for message in client.iter_messages(chat_id, min_id=int(trigger_message_id), limit=20):
                mid = int(getattr(message, "id", 0) or 0)
                if mid <= int(trigger_message_id) or mid in seen_ids:
                    continue
                seen_ids.add(mid)
                buttons = getattr(message, "buttons", None)
                if not buttons:
                    continue
                context = (getattr(message, "raw_text", None) or "")[:2000]
                candidates = []
                for button in _mozy_iter_buttons(message):
                    label = str(getattr(button, "text", "") or "").strip()
                    score = _mozy_button_score(label, feature, context)
                    if score:
                        candidates.append((score, label, button))
                if not candidates:
                    continue
                candidates.sort(key=lambda item: item[0], reverse=True)
                best = candidates[0]
                if len(candidates) > 1 and best[0] == candidates[1][0]:
                    # Equal-confidence candidates are ambiguous; do not click randomly.
                    print(f"[MOZY {uid}] ambiguous buttons in msg={mid}; skipping")
                    continue
                try:
                    await best[2].click()
                    print(f"[MOZY {uid}] clicked feature={feature} chat={chat_id} msg={mid} button={best[1]!r} score={best[0]}")
                    return True
                except FloodWaitError as exc:
                    _mozy_flood_until[(uid, chat_id, feature)] = time.time() + int(exc.seconds)
                    await asyncio.sleep(int(exc.seconds))
                    return False
                except Exception as exc:
                    print(f"[MOZY {uid}] button click failed feature={feature} msg={mid}: {type(exc).__name__}: {exc}")
                    return False
        except FloodWaitError as exc:
            _mozy_flood_until[(uid, chat_id, feature)] = time.time() + int(exc.seconds)
            await asyncio.sleep(int(exc.seconds))
            return False
        except Exception as exc:
            print(f"[MOZY {uid}] response scan failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")
            return False
        await asyncio.sleep(MOZY_POLL_INTERVAL)
    return False


def _mozy_norm_label(text: str) -> str:
    value = str(text or "")
    value = value.replace("\u200c", " ").replace("\u200f", "").replace("\u200e", "")
    value = value.replace("ي", "ی").replace("ك", "ک")
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


async def _mozy_monkey_claim(client, uid: int, chat_id: int, trigger_message_id: int):
    """Click «برداشت همه» ONLY on the bot message that replies to our «میمون»."""
    deadline = time.monotonic() + MOZY_MONKEY_RESPONSE_WAIT
    target = _mozy_norm_label(MOZY_MONKEY_BUTTON)
    me_id = None
    with contextlib.suppress(Exception):
        me_id = int((await client.get_me()).id)
    while time.monotonic() < deadline:
        try:
            async for message in client.iter_messages(chat_id, min_id=int(trigger_message_id), limit=30):
                mid = int(getattr(message, "id", 0) or 0)
                if mid <= int(trigger_message_id):
                    continue
                if me_id is not None and int(getattr(message, "sender_id", 0) or 0) == me_id:
                    continue
                reply_to = getattr(message, "reply_to_msg_id", None)
                if reply_to is None:
                    header = getattr(message, "reply_to", None)
                    reply_to = getattr(header, "reply_to_msg_id", None)
                if int(reply_to or 0) != int(trigger_message_id):
                    continue
                if not getattr(message, "buttons", None):
                    continue
                for button in _mozy_iter_buttons(message):
                    label = str(getattr(button, "text", "") or "")
                    if _mozy_norm_label(label) != target:
                        continue
                    try:
                        await button.click()
                        print(f"[MOZY {uid}] monkey claim clicked chat={chat_id} msg={mid} button={label!r}")
                        return True
                    except FloodWaitError as exc:
                        _mozy_flood_until[(uid, chat_id, "monkey")] = time.time() + int(exc.seconds)
                        await asyncio.sleep(int(exc.seconds))
                        return False
                    except Exception as exc:
                        print(f"[MOZY {uid}] monkey claim click failed msg={mid}: {type(exc).__name__}: {exc}")
                        return False
        except FloodWaitError as exc:
            _mozy_flood_until[(uid, chat_id, "monkey")] = time.time() + int(exc.seconds)
            await asyncio.sleep(int(exc.seconds))
            return False
        except Exception as exc:
            print(f"[MOZY {uid}] monkey scan failed chat={chat_id}: {type(exc).__name__}: {exc}")
            return False
        await asyncio.sleep(MOZY_POLL_INTERVAL)
    print(f"[MOZY {uid}] monkey: no reply with «{MOZY_MONKEY_BUTTON}» found chat={chat_id}")
    return False


def _mozy_banana_next_word(uid: int, chat_id: int) -> str:
    """Mostly alternates موز / مظ / موز / مظ; now and then it is random, so
    repeats like مظ مظ موز or موز موز happen too."""
    key = (int(uid), int(chat_id))
    last = _mozy_banana_last.get(key)
    if last is None:
        word = random.choice(MOZY_BANANA_WORDS)
    elif random.random() < MOZY_BANANA_RANDOM_CHANCE:
        word = random.choice(MOZY_BANANA_WORDS)
    else:
        word = MOZY_BANANA_WORDS[1] if last == MOZY_BANANA_WORDS[0] else MOZY_BANANA_WORDS[0]
    _mozy_banana_last[key] = word
    return word


async def _mozy_execute(client, uid: int, chat_id: int, feature: str):
    key = (int(uid), int(chat_id), feature)
    if key in _mozy_running:
        return False
    flood_until = float(_mozy_flood_until.get(key, 0) or 0)
    if flood_until > time.time():
        return False
    _mozy_running.add(key)
    try:
        command = MOZY_COMMANDS[feature]
        if feature == "banana":
            command = _mozy_banana_next_word(uid, chat_id)
        try:
            trigger = await client.send_message(int(chat_id), command)
        except FloodWaitError as exc:
            _mozy_flood_until[key] = time.time() + int(exc.seconds)
            print(f"[MOZY {uid}] FloodWait on {feature}: sleeping {exc.seconds}s")
            await asyncio.sleep(int(exc.seconds))
            return False
        trigger_id = int(getattr(trigger, "id", 0) or 0)
        if trigger_id <= 0:
            return False
        if feature == "monkey":
            # Even if the claim fails, count this run so «میمون» is not spammed;
            # the next attempt happens after the normal 12-hour interval.
            await _mozy_monkey_claim(client, uid, chat_id, trigger_id)
            return True
        if feature in {"pishi", "fishing"}:
            await _mozy_find_and_click(client, uid, chat_id, trigger_id, feature)
        return True
    except FloodWaitError as exc:
        _mozy_flood_until[key] = time.time() + int(exc.seconds)
        print(f"[MOZY {uid}] FloodWait on {feature}: sleeping {exc.seconds}s")
        await asyncio.sleep(int(exc.seconds))
        return False
    except Exception as exc:
        print(f"[MOZY {uid}] execute failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")
        return False
    finally:
        _mozy_running.discard(key)


async def _mozy_run_and_record(client, uid: int, chat_id: int, feature: str):
    """Run one feature independently and persist its own last_run timestamp."""
    try:
        ok = await _mozy_execute(client, uid, chat_id, feature)
        if not ok:
            return
        configs = _mozy_configs(uid)
        cfg, _ = _mozy_chat_config(uid, chat_id, create=False)
        if not cfg:
            return
        item = cfg.get(feature)
        if not isinstance(item, dict) or not item.get("enabled"):
            return
        item["last_run"] = time.time()
        configs[str(int(chat_id))] = cfg
        _mozy_save_configs(uid, configs)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[MOZY {uid}] task record failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")


async def _mozy_worker_tick(client, uid: int):
    configs = _mozy_configs(uid)
    now = time.time()
    for raw_chat_id, cfg in configs.items():
        try:
            chat_id = int(raw_chat_id)
        except (TypeError, ValueError):
            continue
        for feature in MOZY_FEATURES:
            item = cfg.get(feature, _mozy_default_feature(feature))
            if not item.get("enabled"):
                continue
            interval = max(1, int(item.get("interval", 0) or 0))
            last_run = float(item.get("last_run", 0) or 0)
            if not interval or (last_run and now - last_run < interval):
                continue
            key = (int(uid), chat_id, feature)
            if key in _mozy_running:
                continue
            if float(_mozy_flood_until.get(key, 0) or 0) > now:
                continue
            # Do not await a response scan here. Each group/feature owns its task,
            # so pishi waiting for a Miowy reply cannot delay mew/fishing elsewhere.
            asyncio.create_task(_mozy_run_and_record(client, uid, chat_id, feature))


async def _handle_mozy_command(event, uid: int, text: str):
    normalized = _fa_digits(" ".join(str(text or "").strip().split())).casefold()

    if normalized == "وضعیت موزی":
        await event.edit(premium_ui_text(_mozy_status_text(uid, event.chat_id if event.is_group else None)), parse_mode="html")
        return True

    switches = {
        "موز خودکار روشن": ("banana", True),
        "موز خودکار خاموش": ("banana", False),
        "اسپین خودکار روشن": ("spin", True),
        "اسپین خودکار خاموش": ("spin", False),
        "درآمد میمون روشن": ("monkey", True),
        "درآمد میمون خاموش": ("monkey", False),
    }
    command = switches.get(normalized)
    if command:
        feature, enabled = command
        if not event.is_group:
            await event.edit(premium_ui_text("❌ فعال‌سازی و خاموش‌کردن موزی باید داخل گروه انجام شود."), parse_mode="html")
            return True
        item = _mozy_update_feature(uid, int(event.chat_id), feature, enabled=enabled)
        label = MOZY_DISPLAY[feature]
        status = "روشن ✅" if enabled else "خاموش ❌"
        interval = int(item.get("interval", MOZY_DEFAULT_INTERVALS.get(feature, 0)) or 0)
        interval_text = _mozy_interval_text(interval)
        await event.edit(premium_ui_text(f"{label}: {status}\n⏱ زمان اجرا: {interval_text}"), parse_mode="html")
        return True

    return False



# ============================================================
# MIOWY AUTOMATION
# ============================================================

MIOWY_CONFIG_KEY = "miowy_configs_v2"
MIOWY_FEATURES = ("pishi", "mew", "fishing")
MIOWY_COMMANDS = {
    "pishi": "پیشی",
    "mew": "میو",
    "fishing": "ماهیگیری",
}
MIOWY_DISPLAY = {
    "pishi": "🐱 پیشی خودکار",
    "mew": "😼 میو خودکار",
    "fishing": "🎣 ماهیگیری خودکار",
}
# New Miowy features require an explicit user-set interval before activation.
MIOWY_DEFAULT_INTERVALS = {
    "pishi": 0,
    "mew": 0,
    "fishing": 0,
}
MIOWY_RESPONSE_WAIT = 20.0
MIOWY_POLL_INTERVAL = 0.7
_miowy_running = set()
_miowy_flood_until = {}


def _miowy_default_feature(feature=None):
    return {"enabled": False, "interval": int(MIOWY_DEFAULT_INTERVALS.get(feature, 0) or 0), "last_run": 0.0}


def _miowy_configs(uid: int):
    """Load per-user Miowy settings; each chat owns independent feature state."""
    try:
        raw = self_get(uid, MIOWY_CONFIG_KEY, "{}")
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            return {}
    except Exception:
        return {}
    out = {}
    changed = False
    for raw_chat, raw_cfg in data.items():
        try:
            chat_id = int(raw_chat)
        except (TypeError, ValueError):
            changed = True
            continue
        if not isinstance(raw_cfg, dict):
            changed = True
            continue
        cfg = {}
        for feature in MIOWY_FEATURES:
            item = raw_cfg.get(feature, {})
            if not isinstance(item, dict):
                item = {}
                changed = True
            try:
                interval = max(0, int(item.get("interval", 0) or 0))
            except (TypeError, ValueError):
                interval = 0
                changed = True
            if interval <= 0:
                interval = int(MIOWY_DEFAULT_INTERVALS.get(feature, 0) or 0)
            try:
                last_run = float(item.get("last_run", 0) or 0)
            except (TypeError, ValueError):
                last_run = 0.0
                changed = True
            enabled = item.get("enabled", False) not in {False, 0, "0", "off", "false"}
            cfg[feature] = {"enabled": bool(enabled), "interval": interval, "last_run": last_run}
        out[str(chat_id)] = cfg
    if changed:
        _miowy_save_configs(uid, out)
    return out


def _miowy_save_configs(uid: int, configs):
    self_set(uid, MIOWY_CONFIG_KEY, json.dumps(configs, ensure_ascii=False, separators=(",", ":")))


def _miowy_chat_config(uid: int, chat_id: int, create=True):
    configs = _miowy_configs(uid)
    key = str(int(chat_id))
    cfg = configs.get(key)
    if cfg is None:
        if not create:
            return None, configs
        cfg = {feature: _miowy_default_feature(feature) for feature in MIOWY_FEATURES}
        configs[key] = cfg
    else:
        for feature in MIOWY_FEATURES:
            cfg.setdefault(feature, _miowy_default_feature(feature))
    return cfg, configs


def _miowy_set_interval(uid: int, feature: str, minutes: int):
    seconds = int(minutes) * 60
    configs = _miowy_configs(uid)
    for chat_cfg in configs.values():
        chat_cfg.setdefault(feature, _miowy_default_feature(feature))
        # The interval is stored in seconds and mirrored into existing chat records.
        chat_cfg[feature]["interval"] = seconds
    _miowy_save_configs(uid, configs)
    # Also keep an explicit user-level value in seconds so a group activated later inherits it.
    self_set(uid, f"miowy_interval_{feature}", seconds)


def _miowy_user_interval(uid: int, feature: str) -> int:
    try:
        return max(0, int(self_get(uid, f"miowy_interval_{feature}", "0") or 0))
    except (TypeError, ValueError):
        return 0


def _miowy_update_feature(uid: int, chat_id: int, feature: str, *, enabled=None, last_run=None):
    cfg, configs = _miowy_chat_config(uid, chat_id, create=True)
    item = cfg[feature]
    if enabled is not None:
        item["enabled"] = bool(enabled)
    if last_run is not None:
        item["last_run"] = float(last_run)
    # A group activated after the PV interval was configured inherits that interval.
    if int(item.get("interval", 0) or 0) <= 0:
        item["interval"] = _miowy_user_interval(uid, feature)
    _miowy_save_configs(uid, configs)
    return item


def _miowy_interval_text(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours} ساعت")
    if minutes:
        parts.append(f"{minutes} دقیقه")
    if secs:
        parts.append(f"{secs} ثانیه")
    return " و ".join(parts) if parts else "تنظیم نشده"


def _miowy_status_text(uid: int, chat_id: int | None = None):
    if chat_id is not None:
        cfg, _ = _miowy_chat_config(uid, chat_id, create=False)
        title = "😼 <b>وضعیت میویی</b>"
        if not cfg:
            cfg = {feature: _miowy_default_feature(feature) for feature in MIOWY_FEATURES}
        lines = [title, "", f"🆔 گپ: <code>{int(chat_id)}</code>"]
        for feature in MIOWY_FEATURES:
            item = cfg.get(feature, _miowy_default_feature(feature))
            status = "✅ روشن" if item.get("enabled") else "❌ خاموش"
            interval = int(item.get("interval", 0) or 0)
            lines.append(f"{MIOWY_DISPLAY[feature]}: {status}")
            lines.append(f"⏱ زمان: {_miowy_interval_text(interval)}" if interval else "⏱ زمان: تنظیم نشده")
        return "\n".join(lines)

    configs = _miowy_configs(uid)
    if not configs:
        return "😼 <b>وضعیت میویی</b>\n\nهنوز هیچ گروهی برای میویی تنظیم نشده است."
    lines = ["😼 <b>وضعیت میویی</b>", ""]
    for raw_chat, cfg in configs.items():
        try:
            chat_id_value = int(raw_chat)
        except (TypeError, ValueError):
            continue
        lines.append(f"🆔 گپ: <code>{chat_id_value}</code>")
        for feature in MIOWY_FEATURES:
            item = cfg.get(feature, _miowy_default_feature(feature))
            status = "✅ روشن" if item.get("enabled") else "❌ خاموش"
            interval = int(item.get("interval", 0) or 0)
            lines.append(f"{MIOWY_DISPLAY[feature]}: {status} • ⏱ {_miowy_interval_text(interval)}" if interval else f"{MIOWY_DISPLAY[feature]}: {status} • ⏱ تنظیم نشده")
        lines.append("")
    return "\n".join(lines).rstrip()


def _miowy_button_score(text: str, feature: str, context: str = "") -> int:
    """Conservative matcher for Miowy reward/action buttons."""
    value = (text or "").casefold().strip()
    ctx = (context or "").casefold()
    if not value:
        return 0
    if feature == "pishi":
        strong = ("پیشی", "pishi", "🐱", "میو پوینت")
        supporting = ("گرفتن", "دریافت", "پاداش", "پوینت", "claim", "reward", "get")
    elif feature == "fishing":
        strong = ("ماهی", "ماهیگیری", "fishing", "fish", "🎣")
        supporting = ("گرفتن", "دریافت", "صید", "طعمه", "claim", "reward", "get")
    else:
        return 0
    score = sum(4 if term in value else 0 for term in strong)
    score += sum(1 for term in supporting if term in value)
    if any(term in ctx for term in strong):
        score += 2
    return score if any(term in value for term in strong) and score >= 3 else 0

def _miowy_iter_buttons(message):
    buttons = getattr(message, "buttons", None) or []
    for row in buttons:
        for button in (row if isinstance(row, (list, tuple)) else [row]):
            yield button


async def _miowy_find_and_click(client, uid: int, chat_id: int, trigger_message_id: int, feature: str):
    """Inspect only messages created after this trigger; never click an old keyboard."""
    deadline = time.monotonic() + MIOWY_RESPONSE_WAIT
    seen_ids = set()
    while time.monotonic() < deadline:
        try:
            async for message in client.iter_messages(chat_id, min_id=int(trigger_message_id), limit=20):
                mid = int(getattr(message, "id", 0) or 0)
                if mid <= int(trigger_message_id) or mid in seen_ids:
                    continue
                seen_ids.add(mid)
                buttons = getattr(message, "buttons", None)
                if not buttons:
                    continue
                context = (getattr(message, "raw_text", None) or "")[:2000]
                candidates = []
                for button in _miowy_iter_buttons(message):
                    label = str(getattr(button, "text", "") or "").strip()
                    score = _miowy_button_score(label, feature, context)
                    if score:
                        candidates.append((score, label, button))
                if not candidates:
                    continue
                candidates.sort(key=lambda item: item[0], reverse=True)
                best = candidates[0]
                if len(candidates) > 1 and best[0] == candidates[1][0]:
                    # Equal-confidence candidates are ambiguous; do not click randomly.
                    print(f"[MIOWY {uid}] ambiguous buttons in msg={mid}; skipping")
                    continue
                try:
                    await best[2].click()
                    print(f"[MIOWY {uid}] clicked feature={feature} chat={chat_id} msg={mid} button={best[1]!r} score={best[0]}")
                    return True
                except FloodWaitError as exc:
                    _miowy_flood_until[(uid, chat_id, feature)] = time.time() + int(exc.seconds)
                    await asyncio.sleep(int(exc.seconds))
                    return False
                except Exception as exc:
                    print(f"[MIOWY {uid}] button click failed feature={feature} msg={mid}: {type(exc).__name__}: {exc}")
                    return False
        except FloodWaitError as exc:
            _miowy_flood_until[(uid, chat_id, feature)] = time.time() + int(exc.seconds)
            await asyncio.sleep(int(exc.seconds))
            return False
        except Exception as exc:
            print(f"[MIOWY {uid}] response scan failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")
            return False
        await asyncio.sleep(MIOWY_POLL_INTERVAL)
    return False


async def _miowy_execute(client, uid: int, chat_id: int, feature: str):
    key = (int(uid), int(chat_id), feature)
    if key in _miowy_running:
        return False
    flood_until = float(_miowy_flood_until.get(key, 0) or 0)
    if flood_until > time.time():
        return False
    _miowy_running.add(key)
    try:
        command = MIOWY_COMMANDS[feature]
        try:
            trigger = await client.send_message(int(chat_id), command)
        except FloodWaitError as exc:
            _miowy_flood_until[key] = time.time() + int(exc.seconds)
            print(f"[MIOWY {uid}] FloodWait on {feature}: sleeping {exc.seconds}s")
            await asyncio.sleep(int(exc.seconds))
            return False
        trigger_id = int(getattr(trigger, "id", 0) or 0)
        if trigger_id <= 0:
            return False
        if feature in {"pishi", "fishing"}:
            await _miowy_find_and_click(client, uid, chat_id, trigger_id, feature)
        return True
    except FloodWaitError as exc:
        _miowy_flood_until[key] = time.time() + int(exc.seconds)
        print(f"[MIOWY {uid}] FloodWait on {feature}: sleeping {exc.seconds}s")
        await asyncio.sleep(int(exc.seconds))
        return False
    except Exception as exc:
        print(f"[MIOWY {uid}] execute failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")
        return False
    finally:
        _miowy_running.discard(key)


async def _miowy_run_and_record(client, uid: int, chat_id: int, feature: str):
    """Run one feature independently and persist its own last_run timestamp."""
    try:
        ok = await _miowy_execute(client, uid, chat_id, feature)
        if not ok:
            return
        configs = _miowy_configs(uid)
        cfg, _ = _miowy_chat_config(uid, chat_id, create=False)
        if not cfg:
            return
        item = cfg.get(feature)
        if not isinstance(item, dict) or not item.get("enabled"):
            return
        item["last_run"] = time.time()
        configs[str(int(chat_id))] = cfg
        _miowy_save_configs(uid, configs)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[MIOWY {uid}] task record failed feature={feature} chat={chat_id}: {type(exc).__name__}: {exc}")


async def _miowy_worker_tick(client, uid: int):
    configs = _miowy_configs(uid)
    now = time.time()
    for raw_chat_id, cfg in configs.items():
        try:
            chat_id = int(raw_chat_id)
        except (TypeError, ValueError):
            continue
        for feature in MIOWY_FEATURES:
            item = cfg.get(feature, _miowy_default_feature(feature))
            if not item.get("enabled"):
                continue
            interval = max(1, int(item.get("interval", 0) or 0))
            last_run = float(item.get("last_run", 0) or 0)
            if not interval or (last_run and now - last_run < interval):
                continue
            key = (int(uid), chat_id, feature)
            if key in _miowy_running:
                continue
            if float(_miowy_flood_until.get(key, 0) or 0) > now:
                continue
            # Do not await a response scan here. Each group/feature owns its task,
            # so pishi waiting for a Miowy reply cannot delay mew/fishing elsewhere.
            asyncio.create_task(_miowy_run_and_record(client, uid, chat_id, feature))


async def _handle_miowy_command(event, uid: int, text: str):
    normalized = _fa_digits(" ".join(str(text or "").strip().split())).casefold()

    if normalized == "وضعیت میویی":
        await event.edit(
            premium_ui_text(_miowy_status_text(uid, event.chat_id if event.is_group else None)),
            parse_mode="html",
        )
        return True

    time_match = re.fullmatch(r"تنظیم زمان (پیشی|میو|ماهیگیری) (\d+)", normalized)
    if time_match:
        command_name = time_match.group(1)
        minutes = int(time_match.group(2))
        feature = {"پیشی": "pishi", "میو": "mew", "ماهیگیری": "fishing"}[command_name]
        if minutes <= 0:
            await event.edit(
                premium_ui_text("❌ زمان باید بیشتر از صفر دقیقه باشد."),
                parse_mode="html",
            )
            return True
        _miowy_set_interval(uid, feature, minutes)
        await event.edit(
            premium_ui_text(
                f"{MIOWY_DISPLAY[feature]}\n"
                f"⏱ زمان اجرا: <b>{minutes} دقیقه</b>\n\n"
                "✅ زمان با موفقیت تنظیم شد."
            ),
            parse_mode="html",
        )
        return True

    switches = {
        "پیشی خودکار روشن": ("pishi", True),
        "پیشی خودکار خاموش": ("pishi", False),
        "میو خودکار روشن": ("mew", True),
        "میو خودکار خاموش": ("mew", False),
        "ماهیگیری خودکار روشن": ("fishing", True),
        "ماهیگیری خودکار خاموش": ("fishing", False),
    }
    command = switches.get(normalized)
    if command:
        feature, enabled = command
        if not event.is_group:
            await event.edit(
                premium_ui_text("❌ فعال‌سازی و خاموش‌کردن میویی باید داخل گروه انجام شود."),
                parse_mode="html",
            )
            return True
        if enabled and _miowy_user_interval(uid, feature) <= 0:
            command_word = {"pishi": "پیشی", "mew": "میو", "fishing": "ماهیگیری"}[feature]
            await event.edit(
                premium_ui_text(
                    f"⚠️ قبل از روشن‌کردن {command_word} خودکار، ابتدا باید زمان اجرای {command_word} را تنظیم کنی.\n\n"
                    f"<code>.تنظیم زمان {command_word} 10</code>"
                ),
                parse_mode="html",
            )
            return True
        item = _miowy_update_feature(uid, int(event.chat_id), feature, enabled=enabled)
        label = MIOWY_DISPLAY[feature]
        status = "روشن ✅" if enabled else "خاموش ❌"
        interval = int(item.get("interval", 0) or 0)
        interval_text = _miowy_interval_text(interval)
        await event.edit(
            premium_ui_text(f"{label}: {status}\n⏱ زمان اجرا: {interval_text}"),
            parse_mode="html",
        )
        return True

    return False


# ============================================================
# SELF WORKER
# ============================================================

def time_name_enabled(user_id: int) -> bool:
    return get_setting(user_id, "time_name", "on") == "on"


async def update_time_name(user_id: int, client):
    if not time_name_enabled(user_id):
        return
    try:
        me = await client.get_me()
        if not me:
            return

        first = me.first_name or "کاربر"
        clean = _clean_clock_suffix(first)
        # IMPORTANT: use the selected clock font here.  The previous worker
        # hard-coded ASCII digits, so the panel preview changed but the name
        # always received the default/plain clock.
        new_first = f"{clean[:55]} {self_clock(user_id)}"

        if new_first != first:
            from telethon.tl.functions.account import UpdateProfileRequest
            await client(UpdateProfileRequest(first_name=new_first))
    except Exception as exc:
        print(f"[SELF {user_id}] time-name update skipped: {exc}")


# ---- bio clock ("ساعت بیو") ------------------------------------------------
# Additive: the clock is appended to the bio that is already there as
# "<bio> | <clock>". The clock font is the same "clock_font" the name uses.
_BIO_CLOCK_SUFFIX_RE = re.compile(
    rf"(?:\s*\|\s*|^\s*)[{re.escape(''.join(SELF_CLOCK_FONTS.values()))}]{{1,2}}:"
    rf"[{re.escape(''.join(SELF_CLOCK_FONTS.values()))}]{{2}}\s*$"
)
_BIO_CLOCK_TOO_LONG = set()   # uids whose bio is too long to fit the clock


def _clean_bio_clock_suffix(bio: str) -> str:
    return _BIO_CLOCK_SUFFIX_RE.sub("", bio or "").strip()


def time_bio_enabled(user_id: int) -> bool:
    return get_setting(user_id, "time_bio", "off") == "on"


def _bio_limit(me) -> int:
    return 140 if getattr(me, "premium", False) else 70


async def _get_my_bio(client) -> str:
    full = await client(functions.users.GetFullUserRequest(types.InputUserSelf()))
    return (getattr(full.full_user, "about", "") or "")


async def update_time_bio(user_id: int, client):
    if not time_bio_enabled(user_id):
        _BIO_CLOCK_TOO_LONG.discard(int(user_id))
        return
    try:
        me = await client.get_me()
        if not me:
            return
        current = await _get_my_bio(client)
        base = _clean_bio_clock_suffix(current)
        clock = self_clock(user_id)
        new_bio = f"{base} | {clock}" if base else clock
        if len(new_bio) > _bio_limit(me):
            # Never truncate the user's own bio text; just skip and flag it.
            _BIO_CLOCK_TOO_LONG.add(int(user_id))
            return
        _BIO_CLOCK_TOO_LONG.discard(int(user_id))
        if new_bio != current:
            await client(functions.account.UpdateProfileRequest(about=new_bio))
    except Exception as exc:
        print(f"[SELF {user_id}] time-bio update skipped: {exc}")


async def clear_time_name(user_id: int, client):
    """Turning the name clock off removes the clock text from the name."""
    try:
        me = await client.get_me()
        first = (me.first_name or "") if me else ""
        clean = _clean_clock_suffix(first)
        if clean and clean != first:
            await client(functions.account.UpdateProfileRequest(first_name=clean))
    except Exception as exc:
        print(f"[SELF {user_id}] clear name clock failed: {exc}")


async def clear_time_bio(user_id: int, client):
    """Turning the bio clock off removes " | <clock>" from the bio."""
    _BIO_CLOCK_TOO_LONG.discard(int(user_id))
    try:
        current = await _get_my_bio(client)
        base = _clean_bio_clock_suffix(current)
        if base != current.strip():
            await client(functions.account.UpdateProfileRequest(about=base))
    except Exception as exc:
        print(f"[SELF {user_id}] clear bio clock failed: {exc}")


async def apply_clock_toggle(user_id: int, which: str):
    """Call after time_name / time_bio changed: on -> write the clock now,
    off -> strip the clock from the name / bio right away."""
    client = self_clients.get(int(user_id))
    if not client:
        return
    if which == "name":
        if time_name_enabled(user_id):
            await update_time_name(user_id, client)
        else:
            await clear_time_name(user_id, client)
    else:
        if time_bio_enabled(user_id):
            await update_time_bio(user_id, client)
        else:
            await clear_time_bio(user_id, client)


async def apply_clock_font(user_id: int):
    """Re-render the clock on name and bio after the font changed."""
    client = self_clients.get(int(user_id))
    if not client:
        return
    if time_name_enabled(user_id):
        await update_time_name(user_id, client)
    if time_bio_enabled(user_id):
        await update_time_bio(user_id, client)


async def self_worker(user_id: int, session_string: str, sub_type: int = 0):
    client = TelegramClient(
        StringSession(session_string),
        API_ID,
        API_HASH,
        device_model="Diamond Self",
        system_version="Python",
        app_version="1.0"
    )

    self_clients[user_id] = client
    presence_task = None

    @client.on(events.NewMessage(outgoing=True))
    async def _self_outgoing(event):
        try:
            # Outgoing messages belong to the account owner and must never be
            # placed in the deleted-message archive cache.
            await self_handle_outgoing(event, user_id)
            await _maybe_first_comment(event, user_id)
        except Exception as exc:
            print(f"[SELF {user_id}] outgoing handler error: {exc}")

    @client.on(events.NewMessage(incoming=True))
    async def _self_incoming(event):
        try:
            await self_handle_incoming(event, user_id)
            # FIRST COMMENT must also react to NEW POSTS received by the SELF
            # account in a configured broadcast channel. Previously this feature
            # was called only from the outgoing handler, so a normal channel post
            # was never processed unless SELF itself forwarded it somewhere.
            await _maybe_first_comment(event, user_id)
        except Exception as exc:
            print(f"[SELF {user_id}] incoming handler error: {exc}")

    @client.on(events.MessageDeleted)
    async def _self_deleted(event):
        try:
            deleted_ids = [int(x) for x in (getattr(event, "deleted_ids", None) or [])]
            if not deleted_ids:
                return

            # «اسنپ شات گپ»: matched directly by message id against the reply
            # cache, which already carries its own chat context — independent
            # of the private-chat resolution below, and no event.chat_id needed.
            if self_get(user_id, "snap_group", "off") == "on":
                for message_id in deleted_ids:
                    cached_reply = _snap_group_cache.pop((int(user_id), message_id), None)
                    if cached_reply is not None:
                        await _archive_snap_group_reply(client, user_id, cached_reply)

            # MessageDeleted is not a reliable source of peer/chat_id for normal
            # private chats. Resolve the chat from the short-lived message index
            # populated when NewMessage arrived.
            chats = {}
            for message_id in deleted_ids:
                chat_id = _deleted_message_index.get((int(user_id), message_id))
                if chat_id is not None:
                    chats.setdefault(int(chat_id), []).append(message_id)

            for chat_id, ids in chats.items():
                # Chat-lock intentionally deletes incoming messages and must not
                # archive those messages into Saved Messages.
                if chat_id in self_chat_lock_targets(user_id):
                    continue
                await _archive_last_snapshot_before_delete(client, user_id, chat_id, ids)
        except Exception as exc:
            print(f"[SELF {user_id}] deleted-message handler error: {exc}")

    try:
        await client.connect()

        if not await client.is_user_authorized():
            deactivate_session(user_id)
            print(f"[SELF {user_id}] session is no longer authorized")
            return

        self_workers[user_id] = asyncio.current_task()
        presence_task = asyncio.create_task(_presence_loop(client, user_id))
        print(f"[SELF {user_id}] started")
        if self_get(user_id, "snap_private", "off") == "on":
            _start_snapshot_seed(client, user_id)

        last_clock_value = None

        while True:
            if not get_active_session(user_id):
                break

            balance = get_balance(user_id)
            if balance < 2:
                print(f"[SELF {user_id}] balance ended; stopping")
                deactivate_session(user_id)
                break

            name_clock_on = time_name_enabled(user_id)
            bio_clock_on = time_bio_enabled(user_id)
            clock_value = self_clock(user_id) if (name_clock_on or bio_clock_on) else None
            # Check every second but call Telegram only when the displayed minute changes.
            # This removes the old 15s loop + 30s polling drift while avoiding API spam.
            if clock_value and clock_value != last_clock_value:
                if name_clock_on:
                    await update_time_name(user_id, client)
                if bio_clock_on:
                    await update_time_bio(user_id, client)
                last_clock_value = clock_value

            try:
                await _banner_worker_tick(client, user_id)
            except Exception as exc:
                print(f"[BANNER {user_id}] worker tick error: {type(exc).__name__}: {exc}")

            try:
                await _mozy_worker_tick(client, user_id)
                await _miowy_worker_tick(client, user_id)
            except Exception as exc:
                print(f"[MIOWY {user_id}] worker tick error: {type(exc).__name__}: {exc}")

            # Billing: SELF_HOURLY_COST diamonds/hour, accumulated safely using whole-diamond balance.
            # We charge floor(total_elapsed * SELF_HOURLY_COST), so the average rate is exactly SELF_HOURLY_COST/hour.
            start = get_active_session(user_id)
            if not start:
                break

            start_time = int(start[2])
            elapsed_hours = int((time.time() - start_time) // 3600)
            due_total = (elapsed_hours + 1) * float(SELF_HOURLY_COST)
            charged_total = float(get_setting(user_id, "charged_diamonds", "0") or 0)
            if due_total > charged_total:
                charge = due_total - charged_total
                with connect_db(user_id) as db:
                    db.execute(
                        "UPDATE users SET balance=MAX(balance-?,0) WHERE user_id=?",
                        (charge, user_id)
                    )
                    db.execute(
                        "INSERT OR REPLACE INTO settings(key,value) VALUES('charged_diamonds',?)",
                        (str(due_total),)
                    )
                if get_balance(user_id) <= 0:
                    deactivate_session(user_id)
                    break

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        raise
    except Exception as exc:
        print(f"[SELF {user_id}] worker error: {exc}")
    finally:
        if presence_task:
            presence_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await presence_task
        self_workers.pop(user_id, None)
        self_clients.pop(user_id, None)
        with contextlib.suppress(Exception):
            await client.disconnect()
        print(f"[SELF {user_id}] stopped")


async def start_self_worker(user_id: int, session_string: str, sub_type: int = 0):
    old = self_workers.get(user_id)
    if old and not old.done():
        old.cancel()
        with contextlib.suppress(Exception):
            await old

    task = asyncio.create_task(
        self_worker(user_id, session_string, sub_type)
    )
    self_workers[user_id] = task


async def stop_self_worker(user_id: int):
    task = self_workers.get(user_id)
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task
    deactivate_session(user_id)


async def delete_self_account(user_id: int):
    """«حذف سلف»: the real, destructive teardown -- unlike disable_self
    (which only pauses billing/the worker and keeps the session so
    «روشن کردن» can resume it), this logs the Telegram session out for
    good and wipes it from this account's DB. A fresh «خرید سلف» login is
    required afterwards."""
    task = self_workers.pop(user_id, None)
    if task and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task
    client = self_clients.pop(user_id, None)
    if client:
        try:
            await client.log_out()
        except Exception:
            with contextlib.suppress(Exception):
                await client.disconnect()
    deactivate_session(user_id)
    with contextlib.suppress(Exception):
        init_user_db(user_id)
        with connect_db(user_id) as db:
            db.execute("DELETE FROM self_sessions")


# ============================================================
# LOGIN FLOW
# ============================================================

async def code_timeout(user_id: int):
    await asyncio.sleep(180)
    state = pending.get(user_id)
    if state and state.get("step") in {"code", "password"}:
        client = state.get("client")
        if client:
            with contextlib.suppress(Exception):
                await client.disconnect()
        pending.pop(user_id, None)
        with contextlib.suppress(Exception):
            await bot.send_message(
                user_id,
                premium_ui_text("⏰ زمان ورود تمام شد. دوباره از ابتدا تلاش کنید.")
            , parse_mode="html")


def _login_code_keyboard(uid: int, code: str = ""):
    display = code if code else "•••••"
    return [
        [btn(f"کد فعلی: {display}", _self_cb(uid, "login_code:display"), "primary")],
        [btn("1", _self_cb(uid, "login_code:1"), "primary"), btn("2", _self_cb(uid, "login_code:2"), "primary"), btn("3", _self_cb(uid, "login_code:3"), "primary")],
        [btn("4", _self_cb(uid, "login_code:4"), "primary"), btn("5", _self_cb(uid, "login_code:5"), "primary"), btn("6", _self_cb(uid, "login_code:6"), "primary")],
        [btn("7", _self_cb(uid, "login_code:7"), "primary"), btn("8", _self_cb(uid, "login_code:8"), "primary"), btn("9", _self_cb(uid, "login_code:9"), "primary")],
        [btn("🗑 حذف", _self_cb(uid, "login_code:clear"), "danger"), btn("0", _self_cb(uid, "login_code:0"), "primary"), btn("⌫", _self_cb(uid, "login_code:back"), "danger")],
        [btn("✅ تأیید کد", _self_cb(uid, "login_code:submit"), "success")],
        [btn("❌ انصراف", _self_cb(uid, "login_code:cancel"), "danger", icon=PREMIUM_EMOJI["cross"][0])],
    ]


def _login_code_text(code: str = "", error: str | None = None):
    shown = code if code else "•••••"
    text = (
        "🔐 <b>تأیید کد ورود تلگرام</b>\n\n"
        "کد ۵ رقمی ارسال‌شده از تلگرام را با دکمه‌های زیر وارد کن.\n"
        "برای مثال اگر کد <code>13523</code> است، دکمه‌ها را به ترتیب <b>1 → 3 → 5 → 2 → 3</b> بزن.\n\n"
        f"🔢 کد واردشده: <b>{shown}</b>"
    )
    if error:
        text += f"\n\n❌ <b>{error}</b>\nکد را بررسی کن و دوباره تأیید بزن؛ دکمه‌ها همچنان فعال هستند."
    else:
        text += "\n\n💡 بعد از کامل شدن ۵ رقم، روی «✅ تأیید کد» بزن."
    return text


async def _submit_login_code(event, uid: int):
    state = pending.get(uid)
    if not state or state.get("step") != "code":
        await safe_answer(event, "❌ نشست ورود منقضی شده است.", True)
        return True
    code = str(state.get("entered_code", ""))
    if not re.fullmatch(r"\d{5}", code):
        await safe_callback_edit(event, _login_code_text(code, "کد باید دقیقاً ۵ رقمی باشد."), parse_mode="html", buttons=_login_code_keyboard(uid, code))
        return True
    client = state.get("client")
    if not client:
        pending.pop(uid, None)
        await safe_callback_edit(event, "❌ نشست ورود پیدا نشد. دوباره فعال‌سازی را شروع کنید.", parse_mode="html")
        return True
    try:
        await client.sign_in(phone=state["phone"], code=code, phone_code_hash=state.get("phone_code_hash"))
        # Successful authorization: remove the keyboard from this exact message.
        await safe_callback_edit(event, "✅ <b>کد صحیح بود.</b>\n\n⏳ ورود تأیید شد؛ در حال فعال‌سازی سلف...", parse_mode="html", buttons=None)
        timer = state.get("timer")
        if timer:
            timer.cancel()
        await finish_login(uid)
    except SessionPasswordNeededError:
        state["step"] = "password"
        state["timer"] = asyncio.create_task(code_timeout(uid))
        await safe_callback_edit(event, "🔑 <b>تأیید کد انجام شد.</b>\n\nرمز دو مرحله‌ای تلگرام را ارسال کنید.", parse_mode="html", buttons=None)
    except (PhoneCodeInvalidError, PhoneCodeExpiredError):
        # IMPORTANT: do not remove the keyboard or destroy the pending state.
        await safe_callback_edit(event, _login_code_text(code, "کد اشتباه یا منقضی است."), parse_mode="html", buttons=_login_code_keyboard(uid, code))
        return True
    except Exception as exc:
        print(f"[SELF LOGIN {uid}] code verification failed: {type(exc).__name__}: {exc}")
        await safe_callback_edit(event, _login_code_text(code, "تأیید کد انجام نشد؛ دوباره تلاش کن."), parse_mode="html", buttons=_login_code_keyboard(uid, code))
    return True


async def begin_self_login(user_id: int, event=None):
    # Never start a new login/activation flow when this user already has
    # an active self. The management panel remains available separately.
    if get_active_session(user_id):
        if event:
            await safe_answer(event, "❌ شما یه سلف فعال دارید!", True)
        else:
            await bot.send_message(user_id, premium_ui_text("❌ شما یه سلف فعال دارید!"), parse_mode="html")
        return

    balance = get_balance(user_id)
    if balance < MIN_SELF_BALANCE:
        text = (
            "❌ موجودی شما کافی نیست.\n\n"
            f"💎 موجودی: {_fmt_diamonds(balance)}\n"
            f"💎 حداقل موجودی لازم: {MIN_SELF_BALANCE:,} الماس\n"
            f"💎 هزینه: {SELF_HOURLY_COST:g} الماس در ساعت"
        )
        if event:
            await safe_answer(event, text, True)
        else:
            await bot.send_message(user_id, premium_ui_text(text), parse_mode="html")
        return

    phone = get_phone_number(user_id)
    if not phone:
        if event:
            await safe_answer(event, "❌ ابتدا شماره موبایل خود را ثبت کنید.", True)
        else:
            await bot.send_message(user_id, premium_ui_text("❌ ابتدا با /start شماره موبایل خود را ثبت کنید."), parse_mode="html")
        return

    pending.pop(user_id, None)
    if event:
        await safe_answer(event, "⏳ در حال ارسال کد ورود به شماره ثبت‌شده…")

    client = TelegramClient(StringSession(), API_ID, API_HASH)
    try:
        await client.connect()
        sent = await client.send_code_request(phone)
        pending[user_id] = {
            "step": "code",
            "sub_type": 0,
            "timer": asyncio.create_task(code_timeout(user_id)),
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "entered_code": "",
        }
        await bot.send_message(
            user_id,
            premium_ui_text(_login_code_text()),
            parse_mode="html",
            buttons=_login_code_keyboard(user_id),
        )
    except PhoneNumberInvalidError:
        await bot.send_message(user_id, premium_ui_text("❌ شماره ثبت‌شده معتبر نیست. دوباره شماره خودت را از طریق دکمه اشتراک‌گذاری ثبت کن."), parse_mode="html")
        with contextlib.suppress(Exception):
            await client.disconnect()
    except FloodWaitError as exc:
        await bot.send_message(user_id, premium_ui_text(f"⏳ تلگرام موقتاً محدود کرده است.\nدوباره بعد از {exc.seconds} ثانیه تلاش کن."), parse_mode="html")
        with contextlib.suppress(Exception):
            await client.disconnect()
    except Exception as exc:
        print(f"[SELF LOGIN {user_id}] {exc}")
        await bot.send_message(user_id, premium_ui_text("❌ ارسال کد ورود ناموفق بود. چند لحظه بعد دوباره تلاش کن."), parse_mode="html")
        with contextlib.suppress(Exception):
            await client.disconnect()
        pending.pop(user_id, None)


async def finish_login(user_id: int):
    state = pending.get(user_id)
    if not state or not state.get("client"):
        return

    client = state["client"]
    session_string = client.session.save()

    if not session_string:
        await bot.send_message(user_id, premium_ui_text("❌ ساخت SessionString ناموفق بود."), parse_mode="html")
        return

    # Re-check here as well so a pending login can never activate a second
    # self if another activation/backup restore became active meanwhile.
    if get_active_session(user_id):
        await bot.send_message(user_id, premium_ui_text("❌ شما یه سلف فعال دارید!"), parse_mode="html")
        with contextlib.suppress(Exception):
            await client.disconnect()
        pending.pop(user_id, None)
        return

    # Charge only after successful authorization.
    if get_balance(user_id) < MIN_SELF_BALANCE:
        await bot.send_message(user_id, premium_ui_text("❌ موجودی شما دیگر کافی نیست."), parse_mode="html")
        with contextlib.suppress(Exception):
            await client.disconnect()
        pending.pop(user_id, None)
        return

    # First SELF_HOURLY_COST diamonds are charged immediately when activation succeeds.
    activation_cost = float(SELF_HOURLY_COST)
    change_balance(user_id, -activation_cost)
    save_active_session(user_id, session_string, state.get("sub_type", 0))
    set_setting(user_id, "charged_diamonds", str(activation_cost))

    await start_self_worker(
        user_id,
        session_string,
        state.get("sub_type", 0)
    )

    await bot.send_message(
        user_id,
        premium_ui_text("✅ سلف با موفقیت فعال شد!\n\n"
        f"💎 {SELF_HOURLY_COST:g} الماس همان لحظه فعال‌سازی کسر شد؛ از این پس هر ساعت {SELF_HOURLY_COST:g} الماس کسر می‌شود.")
    , parse_mode="html")

    with contextlib.suppress(Exception):
        await client.disconnect()

    pending.pop(user_id, None)


# ============================================================
# INLINE MODE
# ============================================================

@bot.on(events.InlineQuery)
async def inline_query_handler(event):
    """Return the self panel, or a premium-emoji relay, through Telegram inline mode."""
    raw_query = (event.text or "").strip()
    query = raw_query.casefold()
    print(f"[INLINE QUERY] uid={getattr(event, 'sender_id', '?')} query={query!r}")

    uid = int(event.sender_id)

    if query not in {"پنل", "تست ایموجی", "لیست پرمیوم"}:
        # Premium-emoji relay: only ever built from *this* querying account's
        # own registered mapping (self_premium_emoji_map keys strictly on
        # uid=event.sender_id), so a random outside account gets nothing here
        # unless it has an active self session with its own registered pairs.
        mapping = self_premium_emoji_map(uid)
        if (
            mapping
            and any(k and k in raw_query for k in mapping)
            and not is_banned(uid)
            and has_registered_phone(uid)
            and get_active_session(uid)
        ):
            substituted = _apply_premium_emoji_substitution(raw_query, mapping)
            if self_format_active(uid):
                substituted = self_apply_format(uid, substituted)
            # The premium text can't go in the initial send (see note above
            # self_save_premium_emoji_map) — send the plain fallback plus a
            # button, then apply the real text through a bot-driven edit.
            token = _store_pending_premium_relay(uid, substituted)
            result = event.builder.article(
                title="💎 پیام با ایموجی پریمیوم",
                id=token,
                description=raw_query[:60],
                text=".",
                buttons=[[Button.inline("ㅤ", f"relay:{token}".encode())]],  # invisible label: pressed by SELF in ms
            )
            await event.answer([result], cache_time=0, private=True)
            return

        await event.answer([], cache_time=0, private=True)
        return

    if is_banned(uid):
        result = event.builder.article(
            title="🚫 دسترسی مسدود است",
            description="حساب شما توسط مدیریت مسدود شده است.",
            text="🚫 شما توسط ادمین مسدود شده‌اید."
        )
        await event.answer([result], cache_time=0, private=True)
        return

    if not has_registered_phone(uid):
        result = event.builder.article(
            title="📱 ابتدا شماره را ثبت کنید",
            description="برای استفاده از پنل، ابتدا شماره موبایل خود را ثبت کنید.",
            text="📱 برای استفاده از پنل، ابتدا در گفت‌وگوی ربات /start را بزنید و شماره خود را ثبت کنید."
        )
        await event.answer([result], cache_time=0, private=True)
        return

    if query == "لیست پرمیوم":
        mapping = self_premium_emoji_map(uid)
        if not mapping:
            list_text = "💎 <b>لیست ایموجی‌های پریمیوم</b>\n\n❌ هیچ ایموجی پریمیومی ثبت نشده است."
        else:
            lines = [
                "💎 <b>لیست ایموجی‌های پریمیوم</b>",
                "",
                "✨ ایموجی‌های ثبت‌شده برای جایگزینی خودکار:",
                "",
            ]
            valid_count = 0
            for i, (normal_emoji, entry) in enumerate(mapping.items(), 1):
                if not isinstance(entry, list) or len(entry) < 2:
                    continue
                try:
                    emoji_id = int(entry[0])
                except (TypeError, ValueError):
                    continue
                premium_glyph = str(entry[1] or normal_emoji)
                valid_count += 1
                lines.append(
                    f"{valid_count}. {html.escape(str(normal_emoji))}  ➜  "
                    f"<tg-emoji emoji-id=\"{emoji_id}\">{html.escape(premium_glyph)}</tg-emoji>"
                )
            if valid_count == 0:
                list_text = "💎 <b>لیست ایموجی‌های پریمیوم</b>\n\n❌ هیچ ایموجی معتبر ثبت نشده است."
            else:
                list_text = "\n".join(lines)

        result = event.builder.article(
            title="💎 لیست پرمیوم",
            description="نمایش ایموجی‌های پریمیوم ثبت‌شده",
            text=list_text,
            parse_mode="html",
            buttons=[[Button.inline("🗑 پاکسازی لیست پرمیوم", b"premium_clear")]],
        )
        await event.answer([result], cache_time=0, private=True)
        return

    if query == "تست ایموجی":
        # Proof-of-concept: send a plain "." with a single button. The
        # actual custom emoji is only applied later, by editing this exact
        # inline message via the bot (see the "poc_apply_premium_emoji"
        # callback below) — never by sending it here or by the self client
        # editing its own message. Only the bot-driven edit is exempt from
        # the Premium requirement, so this is the minimal setup needed to
        # test how fast that edit lands after the button is tapped.
        result = event.builder.article(
            title="🧪 تست ایموجی پریمیوم",
            description="یک پیام با دکمه می‌فرستد؛ با زدن دکمه، ایموجی پریمیوم روی همان پیام جا می‌افتد.",
            text=".",
            buttons=[[Button.inline("👆 اعمال ایموجی پریمیوم", b"poc_apply_premium_emoji")]],
        )
        await event.answer([result], cache_time=0, private=True)
        return

    panel_photo = None
    try:
        panel_photo = await _get_self_panel_photo_bytes(uid)
    except Exception as e:
        await _report_panel_bug(uid, "compose/download (_get_self_panel_photo_bytes)", e)
        panel_photo = None

    if panel_photo is not None:
        try:
            result = await event.builder.photo(
                file=panel_photo,
                text=_panel_home_text(),
                parse_mode="html",
                buttons=_panel_home_buttons(uid),
            )
        except Exception as e:
            await _report_panel_bug(uid, "event.builder.photo(...)", e)
            panel_photo = None

    if panel_photo is None:
        # Frame missing, PIL failure, download failure, builder.photo
        # rejecting the upload, etc. — never let "پنل" fail to open;
        # fall back to the plain text panel exactly as it worked
        # before this card was added. The real error was just mirrored
        # to Saved Messages above.
        result = event.builder.article(
            title="⚙️ پنل سلف",
            description="پنل تنظیمات سلف را همین‌جا با Inline باز کن.",
            text=_panel_home_text(),
            parse_mode="html",
            buttons=_panel_home_buttons(uid),
        )
    await event.answer([result], cache_time=0, private=True)



# ============================================================
# MAIN MESSAGE HANDLER
# ============================================================

# ============================================================
# دریافت الماس رایگان هر ۷ دقیقه (بخش گروه)
# ============================================================
_DAILY_DIAMOND_COOLDOWN = 7 * 60  # ۷ دقیقه
_DAILY_DIAMOND_THRESHOLD = 30  # بعد ۳۰ بار
_DAILY_DIAMOND_LOCKOUT = 12 * 3600  # ۱۲ ساعت
_DAILY_DIAMOND_AMOUNT = (1, 5)  # ۱-۵ الماس

_daily_diamond_state = {}  # {uid: {count: int, last_time: time.time, lockout_until: time.time}}


def _get_daily_diamond_state(uid):
    return _daily_diamond_state.get(uid, {"count": 0, "last_time": 0.0, "lockout_until": 0.0})


def _set_daily_diamond_state(uid, count, last_time, lockout_until):
    _daily_diamond_state[uid] = {"count": count, "last_time": last_time, "lockout_until": lockout_until}


async def _handle_daily_diamond_claim(event, uid):
    """«دریافت الماس» is available only in the official group."""
    if not (getattr(event, "is_group", False) or getattr(event, "is_channel", False)):
        return None
    if OFFICIAL_GROUP_ID is None or int(event.chat_id) != int(OFFICIAL_GROUP_ID):
        return None
    
    state = _get_daily_diamond_state(uid)
    now = time.time()
    
    # ۱۲ ساعت بلاک بعد ۳۰ بار
    if state["lockout_until"] > now:
        remaining_secs = int(state["lockout_until"] - now)
        hours = remaining_secs // 3600
        mins = (remaining_secs % 3600) // 60
        time_str = f"{hours} ساعت" if hours > 0 else f"{mins} دقیقه"
        return (
            f"{premium_emoji('daily_clock')} <b>زمان استراحت</b>\n\n"
            f"{time_str} دیگه باقی مونده\n\n"
            f"{htx_wordmark()}"
        )
    
    # ۷ دقیقه cooldown
    elapsed = now - state["last_time"]
    if elapsed < _DAILY_DIAMOND_COOLDOWN:
        remaining_secs = int(_DAILY_DIAMOND_COOLDOWN - elapsed)
        mins = remaining_secs // 60
        secs = remaining_secs % 60
        return (
            f"{premium_emoji('daily_clock')} <b>زمان استراحت</b>\n\n"
            f"{mins}:{secs:02d} دقیقه دیگه باید صبر کنی\n\n"
            f"{htx_wordmark()}"
        )
    
    # بده الماس
    amount = secrets.randbelow(_DAILY_DIAMOND_AMOUNT[1] - _DAILY_DIAMOND_AMOUNT[0] + 1) + _DAILY_DIAMOND_AMOUNT[0]
    change_balance(uid, amount)
    new_balance = get_balance(uid)
    new_count = state["count"] + 1
    
    lockout = now + _DAILY_DIAMOND_LOCKOUT if new_count >= _DAILY_DIAMOND_THRESHOLD else 0.0
    _set_daily_diamond_state(uid, new_count, now, lockout)
    
    return (
        f"{premium_emoji('diamond')} <b>دریافت الماس با موفقیت انجام شد</b>\n\n"
        f"تعداد:\n{premium_number(amount)}\n\n"
        f"{htx_wordmark()}\n\n"
        f"موجودی:\n{premium_number(int(new_balance))}"
    )




# ============================================================
# ربات غیر از گپ رسمی فعالیت نمیکنه
# ============================================================

async def _on_bot_added_to_group(event):
    """Handle only a ChatAction where this bot is among added users."""
    if not (getattr(event, "is_group", False) or getattr(event, "is_channel", False)):
        return False
    if not (getattr(event, "user_added", False) or getattr(event, "user_joined", False)):
        return False

    try:
        me = await event.client.get_me()
        my_id = int(me.id)
        # ChatAction.user_ids are Telegram's marked IDs; for users these are
        # positive, same as get_me().id. get_users() is a fallback if absent.
        affected_ids = {int(x) for x in (getattr(event, "user_ids", None) or [])}
        if not affected_ids:
            users = await event.get_users()
            affected_ids = {int(getattr(x, "id", 0)) for x in (users or [])}
        if my_id not in affected_ids:
            return False

        # Broadcast CHANNELS are exempt: the bot must be able to stay there
        # (premium-emoji publishing, forced-join channels, ...). Only
        # groups/supergroups are restricted to the official group. If the
        # chat type cannot be determined, do not leave.
        chat_obj = None
        try:
            chat_obj = await event.get_chat()
        except Exception:
            chat_obj = None
        if isinstance(chat_obj, types.Channel) and getattr(chat_obj, "broadcast", False):
            print(f"[BOT JOIN] broadcast channel {event.chat_id}: staying")
            return False
        if chat_obj is None and getattr(event, "is_group", None) is not True:
            print(f"[BOT JOIN] chat type unknown for {event.chat_id}: not leaving")
            return False

        await resolve_official_group_id()
        chat_id = int(event.chat_id)
        # Fail closed if we cannot identify the official group. Never eject
        # the bot from a group based on an unresolved target ID.
        if OFFICIAL_GROUP_ID is None:
            print("[BOT JOIN] official group unresolved; refusing automatic leave")
            return False
        if chat_id == int(OFFICIAL_GROUP_ID):
            return False

        official_str = f"@{OFFICIAL_GROUP_USERNAME}" if OFFICIAL_GROUP_USERNAME else str(OFFICIAL_GROUP_ID)
        text = (
            f"{premium_emoji('restrict')} <b>ربات نمیتواند داخل این گروه فعالیت کند!</b>\n\n"
            f"برای استفاده از قابلیت‌های ربات به گروه\n"
            f"<b>{html.escape(official_str)}</b>\n"
            f"مراجعه کنید!\n\n"
            f"{premium_emoji('htx_h')} {premium_emoji('htx_t')} {premium_emoji('htx_x')}"
        )
        try:
            await event.client.send_message(chat_id, premium_ui_text(text), parse_mode="html")
            print(f"[BOT JOIN] warning sent to {chat_id}")
        except Exception as send_exc:
            print(f"[BOT JOIN] warning send failed for {chat_id}: {type(send_exc).__name__}: {send_exc}")

        # Leave independently of message-send success: restrictive chat
        # permissions must not strand the bot in an unsupported group.
        await asyncio.sleep(2)
        from telethon.tl import functions as tl_functions, types as tl_types
        try:
            entity = await event.client.get_input_entity(chat_id)
            await event.client(tl_functions.channels.LeaveChannelRequest(entity))
        except Exception as leave_exc:
            try:
                if chat_id <= 0:
                    raise leave_exc
                await event.client(tl_functions.messages.DeleteChatUserRequest(
                    chat_id=chat_id, user_id=tl_types.InputUserSelf()
                ))
            except Exception as fallback_exc:
                print(f"[BOT JOIN] leave failed for {chat_id}: "
                      f"{type(leave_exc).__name__}: {leave_exc}; fallback: "
                      f"{type(fallback_exc).__name__}: {fallback_exc}")
                return False
        print(f"[BOT JOIN] left non-official group {chat_id}")
        return True
    except Exception as exc:
        print(f"[BOT JOIN] handler failed: {type(exc).__name__}: {exc}")
        return False


@bot.on(events.ChatAction)
async def on_chat_action(event):
    await _on_bot_added_to_group(event)


@bot.on(events.NewMessage)
async def on_message(event):
    user_id = event.sender_id

    if not user_id:
        return

    if event.is_private:
        await private_message(event)
    elif event.is_group or event.is_channel:
        await group_commands(event)


async def process_referral(user_id: int, referrer: int):
    if referrer <= 0 or referrer == user_id:
        return False
    init_user_db(user_id)
    init_user_db(referrer)
    # The referred user can only be assigned once.
    with connect_db(user_id) as db: user_row = db.execute("SELECT invited_by FROM users WHERE user_id=?", (user_id,)).fetchone()
    if user_row and int(user_row[0] or 0) != 0:
        return False
    # Store the relationship in the referrer's database, where referral counts live.
    with connect_db(referrer) as rdb:
        exists = rdb.execute("SELECT 1 FROM referrals WHERE referred_id=?", (user_id,)).fetchone()
        if exists:
            return False
        rdb.execute("INSERT INTO referrals(referrer_id,referred_id,reward_claimed) VALUES(?,?,1)", (referrer, user_id))
        rdb.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (REFERRAL_REWARD, referrer))
    with connect_db(user_id) as udb:
        udb.execute("UPDATE users SET invited_by=? WHERE user_id=?", (referrer, user_id))
    with contextlib.suppress(Exception):
        await bot.send_message(referrer, premium_ui_text(f"🎉 دعوت موفق بود!\n\n💎 {REFERRAL_REWARD:,} الماس به موجودی شما اضافه شد."), parse_mode="html")
    return True


async def private_message(event):
    user_id = event.sender_id
    text = event.raw_text or ""

    init_user_db(user_id)

    if not is_bot_enabled() and user_id not in ADMINS:
        await event.reply(premium_ui_text(BOT_UPDATE_TEXT), parse_mode="html")
        return

    # --------------------------------------------------------
    # START + REFERRAL
    # --------------------------------------------------------
    if text.startswith("/start"):
        if is_banned(user_id):
            await event.reply(premium_ui_text("🚫 شما توسط ادمین مسدود شده‌اید."), parse_mode="html")
            return

        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            with contextlib.suppress(Exception):
                referrer = int(parts[1])
                if referrer != user_id and not has_registered_phone(user_id):
                    set_setting(user_id, "pending_referrer", str(referrer))
                else:
                    await process_referral(user_id, referrer)

        if not await ensure_force_join(user_id):
            return

        if not has_registered_phone(user_id):
            await send_phone_request(user_id)
            return

        await send_main(user_id, user_id)
        return

    # --------------------------------------------------------
    # REQUIRED PHONE REGISTRATION (any country)
    # --------------------------------------------------------
    if event.contact:
        contact = event.contact
        contact_user_id = getattr(contact, "user_id", None)
        phone = normalize_iran_phone(getattr(contact, "phone_number", ""))
        if contact_user_id not in (None, user_id):
            await event.reply(premium_ui_text("❌ فقط شماره خودت را از دکمه اشتراک‌گذاری ارسال کن."), parse_mode="html")
            return
        if not phone:
            await event.reply(premium_ui_text("❌ شماره ارسالی نامعتبر است. دوباره از دکمه اشتراک‌گذاری شماره استفاده کن."), parse_mode="html")
            return
        save_phone_number(user_id, phone)
        pending_referrer = get_setting(user_id, "pending_referrer")
        if pending_referrer:
            with contextlib.suppress(Exception):
                await process_referral(user_id, int(pending_referrer))
            set_setting(user_id, "pending_referrer", "")
        await bot.send_message(user_id, premium_ui_text("✅ شماره شما ثبت شد."), buttons=Button.clear(), parse_mode="html")
        if not await ensure_force_join(user_id):
            return
        await send_main(user_id, user_id)
        return

    # --------------------------------------------------------
    # ADMIN INPUTS: FORCE JOIN / BACKUP
    # --------------------------------------------------------
    state = pending.get(user_id)

    if user_id in ADMINS and state and state.get("step") == "force_join_add":
        raw = (event.raw_text or "").strip()
        try:
            entity = None
            url = ""

            # Private channel/group: forward any message from it to the bot.
            fwd = getattr(event.message, "fwd_from", None)
            fwd_peer = getattr(fwd, "from_id", None) if fwd else None
            if fwd_peer is not None:
                entity = await bot.get_entity(fwd_peer)
                url = ""
                # Generate a direct invite link when the bot has permission.
                with contextlib.suppress(Exception):
                    invite = await bot(functions.messages.ExportChatInviteRequest(peer=entity))
                    url = getattr(invite, "link", None) or ""
            else:
                # Public channel/group: @username or https://t.me/username
                username = raw.split("/")[-1].lstrip("@").strip()
                if not username or " " in username:
                    raise RuntimeError("invalid_username")
                entity = await bot.get_entity("@" + username)
                username_value = getattr(entity, "username", None) or username
                url = f"https://t.me/{username_value}"

            if not isinstance(entity, (types.Channel, types.Chat)):
                raise RuntimeError("not_supported_chat")

            title = getattr(entity, "title", None) or getattr(entity, "username", None) or "گروه/کانال"
            channel = {
                "id": int(entity.id),
                "title": title,
                "username": getattr(entity, "username", None),
                "url": url,
                "private": not bool(getattr(entity, "username", None)),
            }
            channels = [c for c in get_force_join_channels() if int(c.get("id", 0)) != channel["id"]]
            channels.append(channel)
            save_force_join_channels(channels)
            pending.pop(user_id, None)
            link_note = " لینک دعوت خصوصی هم ساخته شد." if channel["private"] and url else ""
            await event.reply(
                premium_ui_text(f"✅ «{channel['title']}» به جوین اجباری اضافه شد.{link_note}"),
                buttons=[[btn("📢 مدیریت جوین اجباری", b"force_join", "primary")]],
            parse_mode="html")
        except Exception as exc:
            print(f"[FORCE JOIN] add failed: {exc}")
            await event.reply(
                premium_ui_text("❌ افزودن انجام نشد. برای کانال خصوصی، یک پیام از همان کانال را فوروارد کن "
                "و مطمئن شو بات داخل کانال/گروه دسترسی لازم برای بررسی عضویت و ساخت لینک دعوت را دارد.")
            , parse_mode="html")
        return

    if user_id in ADMINS and state and state.get("step") == "backup_restore":
        document = getattr(event, "document", None)
        if not document:
            await event.reply(premium_ui_text("❌ فایل ZIP بکاپ را ارسال کن."), parse_mode="html")
            return
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"husterix_backup_upload_{user_id}_"))
        archive_path = tmp_dir / "backup.zip"
        try:
            downloaded = await event.download_media(file=str(archive_path))
            if not downloaded:
                raise RuntimeError("download_failed")
            await asyncio.to_thread(inspect_backup_sync, archive_path)
            await bot.send_message(user_id, premium_ui_text("⏳ بکاپ معتبر است؛ در حال توقف Workerها و بازگردانی اطلاعات..."), parse_mode="html")
            await stop_all_self_workers_for_backup()
            manifest = await asyncio.to_thread(restore_backup_sync, archive_path)
            pending.pop(user_id, None)
            await bot.send_message(
                user_id,
                premium_ui_text("✅ بکاپ با موفقیت بازگردانی شد.\n"
                "⚙️ اطلاعات کاربران، موجودی‌ها، sessionها و تنظیمات برگشتند.\n"
                "🔄 در حال بازیابی Workerهای فعال...")
            , parse_mode="html")
            await restore_workers()
            await send_main(user_id, user_id)
        except Exception as exc:
            print(f"[BACKUP] restore failed: {exc}")
            await bot.send_message(user_id, premium_ui_text("❌ بازگردانی انجام نشد؛ بکاپ فعلی دست‌نخورده باقی ماند."), parse_mode="html")
        finally:
            pending.pop(user_id, None)
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    # --------------------------------------------------------
    # RECEIPT
    # --------------------------------------------------------
    state = pending.get(user_id)
    if state and state.get("step") == "receipt":
        if not (event.photo or event.document):
            await event.reply(premium_ui_text("📸 لطفاً عکس رسید پرداخت را ارسال کنید."), parse_mode="html")
            return

        receipt = None
        try:
            receipt = await event.download_media()
            amount = int(state["amount"])
            diamonds = int(state["diamonds"])

            sender = await event.get_sender()
            username = getattr(sender, "username", None)

            info = (
                "🧾 **رسید پرداخت جدید**\n\n"
                f"🆔 آیدی: `{user_id}`\n"
                f"👤 نام: {getattr(sender, 'first_name', 'کاربر')}\n"
                f"📱 یوزرنیم: @{username if username else 'ندارد'}\n\n"
                f"💎 الماس: {diamonds:,}\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"💳 کارت: {CARD_NUMBER}\n"
                f"👤 صاحب کارت: {CARD_HOLDER}"
            )

            buttons = [
                [
                    btn(
                        "تأیید",
                        f"pay_confirm_{user_id}_{diamonds}".encode(),
                        "success",
                        icon=5260726538302660868
                    ),
                    btn(
                        "رد",
                        f"pay_reject_{user_id}".encode(),
                        "danger",
                        icon=5260342697075416641
                    ),
                ]
            ]

            delivered = 0
            for admin_id in ADMINS:
                try:
                    await bot.send_file(
                        admin_id,
                        receipt,
                        caption=premium_ui_text(info),
                        buttons=buttons
                    , parse_mode="html")
                    delivered += 1
                except Exception as send_exc:
                    print(f"[RECEIPT] local delivery failed for {admin_id}: {send_exc}")
                    with contextlib.suppress(Exception):
                        await bot.send_file(
                            admin_id,
                            event.media,
                            caption=premium_ui_text(info),
                            buttons=buttons
                        , parse_mode="html")
                        delivered += 1
            if delivered:
                await event.reply(
                    premium_ui_text("✅ رسید شما برای مدیریت ارسال شد.\n"
                    "لطفاً منتظر تأیید پرداخت باشید.")
                , parse_mode="html")
                pending.pop(user_id, None)
            else:
                await event.reply(premium_ui_text("❌ ارسال رسید به مدیریت انجام نشد. لطفاً چند لحظه بعد دوباره ارسال کنید."), parse_mode="html")

        except Exception as exc:
            print(f"[RECEIPT] {exc}")
            await event.reply(premium_ui_text("❌ ارسال رسید ناموفق بود."), parse_mode="html")
        finally:
            if receipt and os.path.exists(receipt):
                with contextlib.suppress(Exception):
                    os.remove(receipt)
        return

    # --------------------------------------------------------
    # GIFT CODE REDEMPTION
    # --------------------------------------------------------
    if state and state.get("step") == "gift_redeem":
        code = str(text or "").strip()
        cancel_buttons = [[btn("لغو", b"gift_redeem_cancel", "danger", icon=PREMIUM_EMOJI["cross"][0])]]
        prompt_chat_id = state.get("chat_id", user_id)
        prompt_message_id = state.get("message_id")

        async def update_gift_prompt(message_text):
            if prompt_message_id:
                try:
                    await bot.edit_message(
                        prompt_chat_id,
                        prompt_message_id,
                        premium_ui_text(message_text),
                        buttons=cancel_buttons,
                        parse_mode="html",
                    )
                    return True
                except Exception:
                    logging.exception("gift prompt edit failed for %s", user_id)
            return False

        async with _gift_lock:
            codes = _gift_codes()
            now = time.time()
            match = next((item for item in codes if str(item.get("code", "")).casefold() == code.casefold()), None)
            if not match:
                edited = await update_gift_prompt(
                    "❌ <b>کد هدیه نامعتبر است.</b>\n\n"
                    "کد را دقیق بررسی کن و دوباره ارسال کن.\n\n"
                    "🔹 هنوز منتظر کد هدیه هستم؛ برای خروج روی «لغو» بزن."
                )
                if not edited:
                    await event.reply(
                        premium_ui_text(
                            "❌ <b>کد هدیه نامعتبر است.</b>\n\n"
                            "کد را دقیق بررسی کن و دوباره ارسال کن.\n\n"
                            "برای لغو، دکمه «لغو» را بزن."
                        ),
                        buttons=cancel_buttons,
                        parse_mode="html",
                    )
                return
            if float(match.get("expires_at", 0)) <= now:
                edited = await update_gift_prompt(
                    "⏰ <b>این کد هدیه منقضی شده است.</b>\n\n"
                    "🔹 یک کد هدیه دیگر وارد کن یا روی «لغو» بزن."
                )
                if not edited:
                    await event.reply(
                        premium_ui_text("⏰ <b>این کد هدیه منقضی شده است.</b>\n\nیک کد دیگر وارد کن یا روی «لغو» بزن."),
                        buttons=cancel_buttons,
                        parse_mode="html",
                    )
                return
            used_by = match.setdefault("used_by", [])
            if int(user_id) in used_by:
                await update_gift_prompt(
                    "⚠️ <b>این کد را قبلاً استفاده کرده‌ای.</b>\n\n"
                    "🔹 یک کد دیگر وارد کن یا روی «لغو» بزن."
                )
                return
            reward = int(match.get("reward", 0))
            if reward <= 0:
                await update_gift_prompt(
                    "❌ <b>این کد پاداش معتبری ندارد.</b>\n\n"
                    "🔹 یک کد دیگر وارد کن یا روی «لغو» بزن."
                )
                return
            init_user_db(user_id)
            change_balance(user_id, reward)
            used_by.append(int(user_id))
            _save_gift_codes(codes)
            pending.pop(user_id, None)
            await update_gift_prompt(
                f"🎁 <b>کد هدیه با موفقیت دریافت شد!</b>\n\n"
                f"💎 پاداش شما: <b>{reward:,}</b> الماس\n"
                "✨ الماس‌ها همین حالا به موجودی حسابت اضافه شدند."
            )
        return

    # --------------------------------------------------------
    # SELF LOGIN
    # --------------------------------------------------------
    if state:
        step = state.get("step")

        if step == "phone":
            pending.pop(user_id, None)
            await event.reply(premium_ui_text("📱 شماره را دستی وارد نکن. با /start دکمه «اشتراک‌گذاری شماره» را بزن."), parse_mode="html")
            return

        if step == "code":
            # Keep manual text entry as a backward-compatible fallback. The preferred
            # flow is the inline keypad above; both paths share the same verifier.
            raw_code = text.strip().translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
            code = re.sub(r"[.\s-]", "", raw_code)
            if not re.fullmatch(r"\d{5}", code):
                await event.reply(premium_ui_text("❌ کد باید دقیقاً ۵ رقمی باشد. برای جلوگیری از اشتباه از دکمه‌های پیام کد استفاده کن."), parse_mode="html")
                return
            state["entered_code"] = code
            # Text messages cannot edit the keypad message reliably without its id,
            # so perform the same verification and preserve state on an invalid code.
            client = state.get("client")
            if not client:
                pending.pop(user_id, None)
                await event.reply(premium_ui_text("❌ نشست ورود پیدا نشد. دوباره تلاش کنید."), parse_mode="html")
                return
            try:
                await client.sign_in(phone=state["phone"], code=code, phone_code_hash=state.get("phone_code_hash"))
                timer = state.get("timer")
                if timer:
                    timer.cancel()
                await finish_login(user_id)
            except SessionPasswordNeededError:
                state["step"] = "password"
                state["timer"] = asyncio.create_task(code_timeout(user_id))
                await event.reply(premium_ui_text("🔑 رمز دو مرحله‌ای را ارسال کنید."), parse_mode="html")
            except (PhoneCodeInvalidError, PhoneCodeExpiredError):
                await event.reply(premium_ui_text("❌ کد اشتباه یا منقضی است. پنل کد همچنان فعال است؛ دوباره تأیید کن."), parse_mode="html")
            except Exception as exc:
                print(f"[SELF LOGIN {user_id}] code verification failed: {type(exc).__name__}: {exc}")
                await event.reply(premium_ui_text("❌ تأیید کد انجام نشد؛ دوباره تلاش کن."), parse_mode="html")
            return

        if step == "password":
            client = state.get("client")
            try:
                await client.sign_in(password=text.strip())
                await finish_login(user_id)
            except Exception as exc:
                await event.reply(premium_ui_text(f"❌ رمز صحیح نیست یا ورود ناموفق بود: {exc}"), parse_mode="html")
            return

    await admin_text_flow(event)


async def admin_text_flow(event):
    user_id = event.sender_id
    text = event.raw_text.strip()

    if user_id not in ADMINS:
        return

    state = pending.get(user_id)
    if not state:
        return

    step = state.get("step")

    if step == "gift_create_code":
        if user_id not in ADMINS:
            pending.pop(user_id, None)
            return
        code = str(text or "").strip()
        if not _gift_code_valid(code):
            await event.reply(premium_ui_text("❌ کد نامعتبر است.\n\nکد باید ۳ تا ۴۰ کاراکتر و فقط شامل حروف انگلیسی، عدد، <code>_</code> یا <code>-</code> باشد."), parse_mode="html")
            return
        if any(str(item.get("code", "")).casefold() == code.casefold() for item in _gift_codes()):
            await event.reply(premium_ui_text("⚠️ این کد از قبل وجود دارد؛ یک کد دیگر انتخاب کن."), parse_mode="html")
            return
        state["code"] = code
        state["step"] = "gift_create_reward"
        await event.reply(
            premium_ui_text("🎁 <b>ساخت کد هدیه</b>\n\n🎟 کد: <code>" + html.escape(code) + "</code>\n\n💎 <b>مرحله ۲ از ۳</b>\nتعداد الماس پاداش را به‌صورت عدد وارد کن.\nمثال: <code>100</code>"),
            buttons=[[btn("لغو", b"gift_cancel", "danger", icon=PREMIUM_EMOJI["cross"][0])]],
            parse_mode="html"
        )
        return

    if step == "gift_create_reward":
        if user_id not in ADMINS:
            pending.pop(user_id, None)
            return
        raw = _fa_digits(str(text or "").strip()).replace(",", "").replace("٬", "")
        try:
            reward = int(raw)
            if reward <= 0 or reward > 10_000_000:
                raise ValueError
        except ValueError:
            await event.reply(premium_ui_text("❌ تعداد الماس نامعتبر است. یک عدد صحیح بین ۱ تا ۱۰٬۰۰۰٬۰۰۰ وارد کن."), parse_mode="html")
            return
        state["reward"] = reward
        state["step"] = "gift_create_duration"
        await event.reply(
            premium_ui_text("🎁 <b>ساخت کد هدیه</b>\n\n"
                            f"🎟 کد: <code>{html.escape(state['code'])}</code>\n"
                            f"💎 پاداش: <b>{reward:,}</b> الماس\n\n"
                            "⏳ <b>مرحله ۳ از ۳</b>\n"
                            "مدت اعتبار کد را وارد کن.\n"
                            "مثال‌ها: <code>30 دقیقه</code>، <code>24 ساعت</code>، <code>7 روز</code>"),
            buttons=[[btn("لغو", b"gift_cancel", "danger", icon=PREMIUM_EMOJI["cross"][0])]],
            parse_mode="html"
        )
        return

    if step == "gift_create_duration":
        if user_id not in ADMINS:
            pending.pop(user_id, None)
            return
        seconds = _gift_duration(text)
        if seconds is None:
            await event.reply(premium_ui_text("❌ مدت اعتبار نامعتبر است.\n\nمثال درست: <code>30 دقیقه</code> یا <code>24 ساعت</code> یا <code>7 روز</code>."), parse_mode="html")
            return
        async with _gift_lock:
            codes = _gift_codes()
            code = str(state["code"]).strip()
            if any(str(item.get("code", "")).casefold() == code.casefold() for item in codes):
                pending.pop(user_id, None)
                await event.reply(premium_ui_text("⚠️ این کد در همین لحظه ساخته شده یا قبلاً وجود داشته است."), parse_mode="html")
                return
            expires_at = time.time() + seconds
            codes.append({
                "code": code,
                "reward": int(state["reward"]),
                "expires_at": expires_at,
                "created_at": time.time(),
                "used_by": [],
            })
            _save_gift_codes(codes)
        pending.pop(user_id, None)
        await event.reply(
            premium_ui_text(
                "🎁 <b>کد هدیه با موفقیت ساخته شد!</b>\n\n"
                f"🎟 کد: <code>{html.escape(code)}</code>\n"
                f"💎 پاداش: <b>{int(state['reward']):,}</b> الماس\n"
                f"⏳ انقضا: <b>{html.escape(_gift_format_expiry(expires_at))}</b>\n\n"
                "✨ این کد اکنون آماده استفاده است."
            ),
            parse_mode="html"
        )
        return

    if step == "add_balance_user":
        try:
            target = int(text)
            init_user_db(target)
            state["target_id"] = target
            state["step"] = "add_balance_amount"
            await event.reply(premium_ui_text("💎 مقدار الماس را وارد کنید:"), parse_mode="html")
        except ValueError:
            await event.reply(premium_ui_text("❌ آیدی نامعتبر است."), parse_mode="html")
        return

    if step == "add_balance_amount":
        try:
            amount = int(text)
            if amount <= 0:
                raise ValueError

            target = int(state["target_id"])
            init_user_db(target)
            change_balance(target, amount)

            await event.reply(
                premium_ui_text(f"✅ {amount:,} الماس به `{target}` اضافه شد.")
            , parse_mode="html")
            pending.pop(user_id, None)
        except ValueError:
            await event.reply(premium_ui_text("❌ مقدار نامعتبر است."), parse_mode="html")
        return

    if step == "remove_balance_user":
        try:
            target = int(text)
            init_user_db(target)
            state["target_id"] = target
            state["step"] = "remove_balance_amount"
            await event.reply(premium_ui_text("💎 مقدار الماس را وارد کنید:"), parse_mode="html")
        except ValueError:
            await event.reply(premium_ui_text("❌ آیدی نامعتبر است."), parse_mode="html")
        return

    if step == "remove_balance_amount":
        try:
            amount = int(text)
            if amount <= 0:
                raise ValueError

            target = int(state["target_id"])
            init_user_db(target)
            balance = get_balance(target)
            if amount > balance:
                await event.reply(
                    premium_ui_text(f"❌ موجودی کاربر کافی نیست.\n"
                    f"💎 موجودی فعلی: {_fmt_diamonds(balance)}")
                , parse_mode="html")
                return

            change_balance(target, -amount)

            await event.reply(
                premium_ui_text(f"✅ {amount:,} الماس از `{target}` کسر شد.")
            , parse_mode="html")
            pending.pop(user_id, None)
        except ValueError:
            await event.reply(premium_ui_text("❌ مقدار نامعتبر است."), parse_mode="html")
        return

    if step == "ban_user":
        try:
            target = int(text)
            set_banned(target, True)
            await event.reply(premium_ui_text(f"🚫 کاربر `{target}` مسدود شد."), parse_mode="html")
            pending.pop(user_id, None)
        except ValueError:
            await event.reply(premium_ui_text("❌ آیدی نامعتبر است."), parse_mode="html")


# ============================================================
# GROUP COMMANDS
# ============================================================

async def group_commands(event):
    if not (event.is_group or event.is_channel):
        return

    text = (event.raw_text or "").strip()
    user_id = event.sender_id
    if not user_id:
        return

    # Free diamonds are available ONLY in the official group.
    if text.casefold() == "دریافت الماس":
        await resolve_official_group_id()
        if OFFICIAL_GROUP_ID is None:
            await event.reply(
                premium_ui_text(f"{premium_emoji('restrict')} <b>گروه رسمی شناسایی نشد؛ دریافت الماس فعلاً ممکن نیست.</b>"),
                parse_mode="html",
            )
        elif int(event.chat_id) != int(OFFICIAL_GROUP_ID):
            await event.reply(
                premium_ui_text(f"{premium_emoji('restrict')} <b>دریافت الماس فقط داخل گروه رسمی فعاله.</b>"),
                parse_mode="html",
            )
        else:
            result = await _handle_daily_diamond_claim(event, user_id)
            if result:
                await event.reply(premium_ui_text(result), parse_mode="html")
        return

    # BOT game/balance features are strictly limited to the official group.
    if not await is_official_group_event(event):
        return

    user_id = event.sender_id
    user_id = event.sender_id

    if not user_id:
        return

    if not is_bot_enabled():
        # During updates the official group remains responsive only with the
        # maintenance message; SELF functionality is unaffected.
        if text == "بازی" or text.startswith("بازی ") or text == "موجودی" or text.startswith("انتقال "):
            await event.reply(premium_ui_text(BOT_UPDATE_TEXT), parse_mode="html")
        return

    if text == "موجودی":
        # Always show the balance of the person who typed "موجودی".
        # Replying to another user must never change the target.
        target = user_id
        balance = get_balance(target)
        try:
            target_entity = await bot.get_entity(int(target))
            username = getattr(target_entity, "username", None)
        except Exception:
            username = None
        identity = f"@{username}" if username else str(int(target))
        buttons = [[btn(
            f"{_fmt_diamonds(balance)} الماس",
            f"balance_{target}".encode(),
            "primary",
            icon=PREMIUM_EMOJI["diamond"][0]
        )]]
        await event.reply(
            premium_ui_text(
                f'{premium_emoji("diamond")} **موجودی شما :**'
            ),
            buttons=buttons
        , parse_mode="html")
        return

    game = re.fullmatch(r"بازی\s+(\d+)", text)
    if game:
        amount = int(game.group(1))

        if amount < MIN_GAME:
            await event.reply(
                premium_ui_text(f"❌ حداقل مبلغ بازی {MIN_GAME} الماس است.")
            , parse_mode="html")
            return

        balance = get_balance(user_id)
        if balance < amount:
            await event.reply(
                premium_ui_text(f"❌ موجودی کافی نیست.\n"
                f"💎 موجودی: {_fmt_diamonds(balance)}")
            , parse_mode="html")
            return

        change_balance(user_id, -amount)

        total = amount * 2
        tax = max(1, round(total * GAME_TAX))
        prize = total - tax

        def _build_game_text(use_htx):
            wordmark = htx_wordmark() if use_htx else "𝗛𝗧𝗫"
            return (
                "<b>💎 بازی\n"
                f" ‌{premium_number(_fmt_diamonds_plain(amount))}\n\n"
                f"{premium_emoji('winner')} جایزه برنده:\n"
                f"{premium_number(_fmt_diamonds_plain(prize))}\n"
                f"{premium_emoji("tax")} مالیات:\n"
                f"{premium_number(_fmt_diamonds_plain(tax))}\n\n"
                f"{wordmark}\n"
                "برای شروع بازی، نفر دوم روی پیوستن بزند.</b>"
            )

        buttons = [
            [
                btn(
                    "پیوستن",
                    f"game_join_{amount}_{user_id}".encode(), "success",
                    icon=PREMIUM_EMOJI["transfer_success"][0]
                ),
                btn(
                    "لغو",
                    f"game_cancel_{amount}_{user_id}".encode(), "danger",
                    icon=PREMIUM_EMOJI["loser"][0]
                ),
            ]
        ]

        msg = await _send_game_announcement(event, _build_game_text, buttons, user_id, amount)
        if msg is None:
            return

        key = (event.chat_id, msg.id)
        task = asyncio.create_task(
            game_timeout(event.chat_id, msg.id, user_id, amount)
        )
        active_games[key] = {
            "organizer": user_id,
            "amount": amount,
            "task": task
        }
        return

    rps_start = re.fullmatch(r"سنگ\s+(\d+)", text)
    if rps_start:
        amount = int(rps_start.group(1))

        if amount < MIN_GAME:
            await event.reply(
                premium_ui_text(f"❌ حداقل مبلغ بازی {MIN_GAME} الماس است.")
            , parse_mode="html")
            return

        balance = get_balance(user_id)
        if balance < amount:
            await event.reply(
                premium_ui_text(f"❌ موجودی کافی نیست.\n"
                f"💎 موجودی: {_fmt_diamonds(balance)}")
            , parse_mode="html")
            return

        change_balance(user_id, -amount)

        rps_total = amount * 2
        rps_tax = max(1, round(rps_total * GAME_TAX))
        rps_prize = rps_total - rps_tax

        def _build_rps_text(use_htx):
            wordmark = htx_wordmark() if use_htx else "𝗛𝗧𝗫"
            return (
                f"<b>{premium_glyph('rps_rock')}{premium_glyph('rps_paper')}{premium_glyph('rps_scissors')} سنگ کاغذ قیچی\n"
                f" ‌{premium_number(_fmt_diamonds_plain(amount))}\n\n"
                f"{premium_emoji('winner')} جایزه برنده:\n"
                f"{premium_number(_fmt_diamonds_plain(rps_prize))} {premium_emoji("diamond")}\n"
                f"{premium_emoji("tax")} مالیات:\n"
                f"{premium_number(_fmt_diamonds_plain(rps_tax))} {premium_emoji("diamond")}\n\n"
                "هر کس زودتر به امتیاز ۲ برسد، برنده می‌شود.\n\n"
                f"{wordmark}\n\n"
                "برای شروع بازی، نفر دوم روی پیوستن بزند.</b>"
            )

        rps_buttons = [
            [
                btn(
                    "پیوستن",
                    f"rps_join_{amount}_{user_id}".encode(), "success",
                    icon=PREMIUM_EMOJI["transfer_success"][0]
                ),
                btn(
                    "لغو",
                    f"rps_cancel_{amount}_{user_id}".encode(), "danger",
                    icon=PREMIUM_EMOJI["loser"][0]
                ),
            ]
        ]

        msg = await _send_game_announcement(event, _build_rps_text, rps_buttons, user_id, amount)
        if msg is None:
            return

        key = (event.chat_id, msg.id)
        task = asyncio.create_task(
            rps_join_timeout(event.chat_id, msg.id, user_id, amount)
        )
        active_rps_games[key] = {
            "p1": user_id,
            "p2": None,
            "amount": amount,
            "score": {},
            "choices": {},
            "round": 1,
            "task": task,
            "phase": "waiting_join",
        }
        return

    transfer = re.fullmatch(r"انتقال\s+(\d+)", text)
    if transfer:
        amount = int(transfer.group(1))

        if amount < 1:
            await event.reply(
                premium_ui_text("❌ مبلغ انتقال باید حداقل ۱ الماس باشد.")
            , parse_mode="html")
            return

        if not event.is_reply:
            await event.reply(
                premium_ui_text("❌ روی پیام کاربر ریپلای کنید و سپس دستور «انتقال 500» را بفرستید.")
            , parse_mode="html")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.sender_id:
            await event.reply(premium_ui_text("❌ گیرنده پیدا نشد."), parse_mode="html")
            return

        receiver = reply.sender_id

        if receiver == user_id:
            await event.reply(premium_ui_text("❌ نمی‌توانید به خودتان انتقال دهید."), parse_mode="html")
            return

        try:
            receiver_entity_check = await reply.get_sender()
        except Exception:
            receiver_entity_check = None

        receiver_username_check = (getattr(receiver_entity_check, "username", None) or "")
        if getattr(receiver_entity_check, "bot", False) or receiver_username_check.lower().endswith("bot"):
            await event.reply(
                premium_ui_text(f"{premium_emoji('loser')} انتقال الماس به حساب‌های ربات (Bot) امکان‌پذیر نیست.")
            , parse_mode="html")
            return

        tax = max(1, round(amount * TRANSFER_TAX))
        total = amount + tax

        balance = get_balance(user_id)
        if balance < total:
            await event.reply(
                premium_ui_text(f"{premium_emoji('loser')} موجودی شما کافی نیست\n\n"
                f"مبلغ انتقال:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
                f"کسر کل با مالیات:\n{premium_number(_fmt_diamonds_plain(total))}\n\n"
                f"موجودی شما:\n{premium_number(_fmt_diamonds_plain(balance))}")
            , parse_mode="html")
            return

        # Atomic enough for per-user SQLite databases.
        change_balance(user_id, -total)
        init_user_db(receiver)
        change_balance(receiver, amount)

        async def _display_name(uid):
            try:
                entity = await bot.get_entity(int(uid))
                username = getattr(entity, "username", None)
            except Exception:
                username = None
            return f"@{username}" if username else str(int(uid))

        sender_display = await _display_name(user_id)
        receiver_display = await _display_name(receiver)

        sender_balance_after = get_balance(user_id)
        receiver_balance_after = get_balance(receiver)

        await event.reply(
            premium_ui_text(f"{premium_emoji('transfer_success')} انتقال انجام شد\n\n"
            f"فرستنده: {sender_display}\n"
            f"گیرنده: {receiver_display}\n\n"
            f"مبلغ انتقال:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
            f"مالیات:\n{premium_number(_fmt_diamonds_plain(tax))}\n\n"
            f"کسر کل:\n{premium_number(_fmt_diamonds_plain(total))}\n\n"
            f"موجودی فرستنده:\n{premium_number(_fmt_diamonds_plain(sender_balance_after))}\n\n"
            f"موجودی گیرنده:\n{premium_number(_fmt_diamonds_plain(receiver_balance_after))}")
        , parse_mode="html")

        try:
            receiver_entity = await reply.get_sender()
            await bot.send_message(
                receiver_entity,
                premium_ui_text(
                    f"{premium_emoji('diamond')} انتقال الماس دریافت شد\n\n"
                    f"فرستنده: {sender_display}\n"
                    f"مبلغ:\n{premium_number(_fmt_diamonds_plain(amount))}\n\n"
                    f"موجودی جدید شما:\n{premium_number(_fmt_diamonds_plain(receiver_balance_after))}"
                ),
                parse_mode="html"
            )
        except Exception as exc:
            print(f"[TRANSFER NOTIFY] failed to notify {receiver}: {exc}")
            await event.reply(
                premium_ui_text(
                    "⚠️ الماس منتقل شد اما گیرنده باید ابتدا ربات را در پی‌وی استارت "
                    "(/start) کند تا نوتیفیکیشن دریافت الماس برایش ارسال شود."
                ),
                parse_mode="html"
            )
        return


async def _delete_expired_game_message(chat_id, message_id):
    """An expired / dead game card must disappear completely. Try a real
    delete (twice), and only if Telegram refuses both times fall back to
    stripping the buttons so the card can never be clicked again."""
    for attempt in range(2):
        try:
            await bot.delete_messages(chat_id, message_id)
            return True
        except Exception as exc:
            print(f"[GAME] expired card delete failed ({attempt + 1}/2): {type(exc).__name__}: {exc}")
            await asyncio.sleep(0.6)
    with contextlib.suppress(Exception):
        await bot.edit_message(
            chat_id, message_id,
            premium_ui_text("⏰ این بازی منقضی شد."),
            buttons=None, parse_mode="html",
        )
    return False


async def game_timeout(chat_id, message_id, organizer_id, amount):
    await asyncio.sleep(GAME_TIMEOUT)

    key = (chat_id, message_id)
    game = active_games.pop(key, None)

    if not game:
        return

    change_balance(organizer_id, amount)

    await _delete_expired_game_message(chat_id, message_id)

    with contextlib.suppress(Exception):
        await bot.send_message(
            organizer_id,
            premium_ui_text(f"❌ نبرد به دلیل عدم حضور حریف لغو شد.\n"
            f"💎 {amount} الماس به حساب شما برگشت.")
        , parse_mode="html")


async def rps_join_timeout(chat_id, message_id, organizer_id, amount):
    await asyncio.sleep(GAME_TIMEOUT)

    key = (chat_id, message_id)
    game = active_rps_games.get(key)

    if not game or game.get("phase") != "waiting_join":
        return
    active_rps_games.pop(key, None)

    change_balance(organizer_id, amount)

    await _delete_expired_game_message(chat_id, message_id)

    with contextlib.suppress(Exception):
        await bot.send_message(
            organizer_id,
            premium_ui_text(f"❌ بازی سنگ‌کاغذقیچی به دلیل عدم حضور حریف لغو شد.\n"
            f"💎 {amount} الماس به حساب شما برگشت.")
        , parse_mode="html")


async def rps_round_timeout(chat_id, message_id, round_no):
    # Rule: once joined, the game can't run forever — each player has 30
    # seconds to lock in a move, or they forfeit the match.
    await asyncio.sleep(30)

    key = (chat_id, message_id)
    game = active_rps_games.get(key)

    if not game or game.get("round") != round_no or game.get("phase") != "playing":
        return
    active_rps_games.pop(key, None)

    amount = int(game.get("amount", 0))
    p1 = int(game.get("p1", 0))
    p2 = int(game.get("p2", 0))
    choices = game.get("choices", {})
    p1_moved = p1 in choices
    p2_moved = p2 in choices

    if p1_moved == p2_moved:
        # Neither player moved in time (both moving is already handled
        # before this timer fires) — no fair loser to pick, so cancel and
        # refund both.
        if amount > 0:
            change_balance(p1, amount)
            change_balance(p2, amount)
        await _delete_expired_game_message(chat_id, message_id)
        for _uid in (p1, p2):
            with contextlib.suppress(Exception):
                await bot.send_message(
                    int(_uid),
                    premium_ui_text(f"❌ بازی سنگ‌کاغذقیچی به دلیل عدم انتخاب به‌موقع لغو شد.\n💎 {amount} الماس به حساب شما برگشت."),
                    parse_mode="html",
                )
        return

    # Exactly one player let the 30-second timer run out — they lose the match.
    winner = p1 if p1_moved else p2
    loser = p2 if p1_moved else p1

    total = amount * 2
    tax = max(1, round(total * GAME_TAX))
    prize = total - tax
    change_balance(winner, prize)
    change_balance(7727625618, tax / 2)

    winner_balance = get_balance(winner)
    loser_balance = get_balance(loser)
    winner_name = await user_name(winner)
    loser_name = await user_name(loser)

    diamond_icon = PREMIUM_EMOJI["diamond"][0]
    result_buttons = [
        [
            btn("جایزه برنده", b"game_noop_prize", "success", icon=PREMIUM_EMOJI["winner"][0]),
            btn(f"{prize}", b"game_noop_prize_value", "success", icon=diamond_icon),
        ],
        [
            btn("موجودی برنده", b"game_noop_winner", "primary", icon=diamond_icon),
            btn(f"{_fmt_diamonds_plain(winner_balance)}", b"game_noop_winner_value", "primary", icon=diamond_icon),
        ],
        [
            btn("موجودی بازنده", b"game_noop_loser", "danger", icon=PREMIUM_EMOJI["loser"][0]),
            btn(f"{_fmt_diamonds_plain(loser_balance)}", b"game_noop_loser_value", "danger", icon=diamond_icon),
        ],
    ]
    with contextlib.suppress(Exception):
        await bot.edit_message(
            chat_id, message_id,
            premium_ui_text(
                f"{premium_glyph('rps_clock')} {loser_name}\n"
                f" ظرف ۳۰ ثانیه حرکتش را نزد و بازنده شد!\n\n"
                f"{premium_emoji('winner')} کاربر برنده: {winner_name}\n"
                f"{premium_emoji('loser')} کاربر بازنده: {loser_name}"
            ),
            buttons=result_buttons, parse_mode="html"
        )


# ============================================================
# CALLBACKS
# ============================================================

@bot.on(events.CallbackQuery)
async def callbacks(event):
    data = event.data.decode("utf-8", errors="ignore")
    user_id = event.sender_id

    if data == "poc_apply_premium_emoji":
        inline_message_id = _event_inline_message_id(event)
        if inline_message_id is None:
            await safe_answer(event, "❌ پیام Inline پیدا نشد.", True)
            return
        try:
            await safe_answer(event, "💎 اعمال شد")
        except Exception:
            pass
        await _edit_panel_message(
            text=premium_ui_text(f"✅ اعمال شد: {premium_emoji('diamond')}"),
            buttons=None,
            inline_message_id=inline_message_id,
        )
        return

    if data == "premium_clear":
        if user_id is None:
            await safe_answer(event, "❌ کاربر شناسایی نشد.", True)
            return

        # Clear the persistent mapping first, then edit the exact inline
        # message through the same callback-edit path that is already used by
        # the working premium relay.  This avoids relying on a separately
        # reconstructed inline-message identity.
        self_save_premium_emoji_map(int(user_id), {})
        await safe_answer(event, "🗑 لیست پرمیوم پاک شد.")

        try:
            await safe_callback_edit(
                event,
                "🗑 <b>لیست پرمیوم پاک شد</b>\n\n"
                "تمام ایموجی‌های پریمیوم ثبت‌شده حذف شدند. 💎\n\n"
                "برای ثبت دوباره، از «.ثبت ایموجی» استفاده کن.",
                buttons=None,
            )
        except Exception as exc:
            print(f"[PREMIUM LIST] clear edit failed: {type(exc).__name__}: {exc!r}")
        return

    if data.startswith("relay:"):
        token = data.split(":", 1)[1].strip()
        uid = int(user_id or 0)

        # The auto-click by SELF always targets a fresh *inline* message.
        # Without this explicit inline_message_id, event.edit() has to guess
        # the message identity from the callback query alone — that guess is
        # what was silently failing (the edit landed on nothing, or on the
        # wrong message, so the button never visibly "opened"/applied).
        # Resolve it explicitly first, exactly like the pre-update build did.
        inline_message_id = _event_inline_message_id(event)
        if inline_message_id is None:
            await safe_answer(event, "❌ این دکمه فقط روی پیام Inline کار می‌کند.", True)
            return

        entry = _get_pending_premium_relay(uid, token)
        if not entry:
            await safe_answer(
                event,
                "❌ این پیام منقضی شده؛ دوباره ایموجی را ارسال کن.",
                True,
            )
            return

        substituted = entry.get("text")
        if not isinstance(substituted, str) or not substituted:
            _PREMIUM_RELAY_PENDING.pop(token, None)
            await safe_answer(event, "❌ متن ایموجی پریمیوم پیدا نشد.", True)
            return

        # Exactly the pre-update sequence: answer first, then edit this
        # exact inline message (already carries the real tg-emoji HTML, so
        # it is sent through as-is — no premium_ui_text() re-wrap here).
        # Edit FIRST (that is what removes the button on screen) and answer
        # the callback in parallel, instead of waiting a round trip for it.
        answer_task = asyncio.create_task(safe_answer(event))
        try:
            await safe_callback_edit(
                event,
                substituted,
                parse_mode="html",
                buttons=None,
            )
            print(f"[PREMIUM RELAY BOT] applied uid={uid} token={token}")
        except Exception as exc:
            print(
                f"[PREMIUM RELAY BOT] edit failed uid={uid} token={token}: "
                f"{type(exc).__name__}: {exc!r}"
            )
        _PREMIUM_RELAY_PENDING.pop(token, None)
        with contextlib.suppress(Exception):
            await answer_task
        return

    # Admin can always enter the management panel and switch update mode.
    if data == "bot_toggle":
        if user_id not in ADMINS:
            await safe_answer(event, "❌ دسترسی ندارید.", True)
            return
        new_state = not is_bot_enabled()
        set_bot_enabled(new_state)
        if not new_state:
            await cancel_all_active_games_for_update()
        status = "روشن ✅" if new_state else "خاموش ❌"
        await safe_answer(event, f"ربات {status}")
        buttons = [
            [btn("الماس", b"admin_gems", "success", icon=PREMIUM_EMOJI["diamond"][0])],
            [btn("کد هدیه", b"admin_gift", "primary", icon=PREMIUM_EMOJI["gift"][0]), btn("آمار کاربران", b"admin_stats", "primary", icon=PREMIUM_EMOJI["profile"][0])],
            [btn("جوین اجباری", b"force_join", "success", icon=PREMIUM_EMOJI["megaphone"][0])],
            [btn("مسدودی", b"admin_block", "danger", icon=PREMIUM_EMOJI["danger"][0]), btn("Backups", b"backups", "primary", icon=PREMIUM_EMOJI["order"][0])],
            [btn("روشن کردن بات" if not new_state else "خاموش کردن بات", b"bot_toggle", "success" if not new_state else "danger", icon=PREMIUM_EMOJI["green"][0] if not new_state else PREMIUM_EMOJI["red"][0])],
            [btn("بازگشت", b"user_account", "danger", icon=PREMIUM_EMOJI["self_back"][0])],
        ]
        await edit_or_send(event, "🛠 **مدیریت**\n\n" + f"🤖 وضعیت بات: **{status}**\n\nیک گزینه را انتخاب کنید:", buttons)
        return

    # Gift-code flow is a real input screen. Create a dedicated prompt message
    # immediately and keep its message id in pending, so every submitted code
    # updates this exact prompt instead of creating an endless chain of replies.
    if data == "gift_redeem":
        gift_text = premium_ui_text("🎁 <b>کد هدیه را وارد کن:</b>\n\nکد هدیه خود را همین‌جا ارسال کن.")
        gift_buttons = [[btn("لغو", b"gift_redeem_cancel", "danger", icon=PREMIUM_EMOJI["cross"][0])]]
        pending[user_id] = {
            "step": "gift_redeem",
            "chat_id": user_id,
            "message_id": getattr(event, "message_id", None),
        }
        await safe_answer(event)
        try:
            await event.edit(gift_text, buttons=gift_buttons, parse_mode="html")
        except Exception:
            logging.exception("gift redeem prompt edit failed for %s", user_id)
            pending.pop(user_id, None)
            with contextlib.suppress(Exception):
                await bot.send_message(user_id, gift_text, buttons=gift_buttons, parse_mode="html")
        return

    if data == "gift_redeem_cancel":
        pending.pop(user_id, None)
        await safe_answer(event)
        try:
            await event.edit(
                "**به سلـف‌ساز 𝗛𝘂𝘀𝘁𝗲𝗥𝗜𝗫 𝗗𝗶𝗺𝗼𝗻𝗱 𝗦𝗲𝗹𝗳 خوش آمدید! 💎**\n\n"
                "برای ساخت سلـف‌ربات، خرید الماس یا دریافت پاداش زیرمجـموعه‌گیری، لطفاً یکی از گزینه‌های منوی زیر را انتخاب کنید:",
                buttons=main_buttons(user_id),
            )
        except Exception:
            await send_main(user_id, user_id)
        return

    # Game/balance callback buttons are valid only inside the official group.
    if data.startswith(("game_join_", "game_cancel_", "game_noop_", "balance_", "rps_")):
        if not await is_official_group_event(event):
            await safe_answer(event, "❌ این قابلیت فقط در گپ رسمی ربات فعال است.", True)
            return
        if not is_bot_enabled():
            await safe_answer(event, BOT_UPDATE_TEXT, True)
            return

    if data == "fj_check":
        # Verify FIRST.  Never delete/skip the force-join gate while any
        # required channel is still missing. notify=False: the "عضو شدم"
        # tap should only pop the error alert, never re-edit the message
        # underneath it (that redundant edit was re-rendering the dirty
        # \n text and visibly breaking the message style).
        if not await ensure_force_join(user_id, event, notify=False):
            await safe_answer(event, "❌ هنوز در همه کانال‌ها عضو نشده‌اید.", True)
            return

        await safe_answer(event, "✅ عضویت تأیید شد.")
        with contextlib.suppress(Exception):
            await event.delete()
        if not has_registered_phone(user_id):
            await send_phone_request(user_id)
        else:
            await send_main(user_id, user_id)
        return

    if data.startswith("sp:") and data.endswith(":premium_clear_panel"):
        # Keep the premium clear callback isolated from the large SELF panel
        # dispatcher.  This avoids unrelated panel branches swallowing the tap.
        try:
            parts = data.split(":")
            uid = int(parts[1])
        except (ValueError, IndexError):
            await safe_answer(event, "❌ پنل نامعتبر است.", True)
            return
        if user_id != uid:
            await safe_answer(event, "❌ این پنل متعلق به شما نیست.", True)
            return
        self_save_premium_emoji_map(uid, {})
        await safe_answer(event, "🗑 لیست پرمیوم پاک شد.")
        await _panel_show_premium_emoji(event, uid)
        return

    # Premium Emoji has a dedicated callback path. Do this before the
    # generic SELF dispatcher so this screen can never be swallowed by another
    # panel branch.
    if data.startswith(f"sp:{int(user_id)}:premium_emoji_open"):
        await safe_answer(event)
        await _panel_show_premium_emoji(event, int(user_id))
        return

    if data.startswith("sp:"):
        # Login-code keypad callbacks use the same SELF callback namespace.
        if data.startswith(f"sp:{int(user_id)}:login_code:"):
            action = data.split(":", 3)[3]
            state = pending.get(user_id)
            if not state or state.get("step") != "code":
                await safe_answer(event, "❌ نشست ورود منقضی شده است.", True)
                return
            code = str(state.get("entered_code", ""))
            if action.isdigit() and len(action) == 1:
                if len(code) < 5:
                    code += action
                    state["entered_code"] = code
                    await safe_callback_edit(event, _login_code_text(code), parse_mode="html", buttons=_login_code_keyboard(user_id, code))
                else:
                    await safe_answer(event, "❌ کد ۵ رقمی کامل شده؛ تأییدش کن.", True)
                return
            if action == "clear":
                state["entered_code"] = ""
                await safe_callback_edit(event, _login_code_text(), parse_mode="html", buttons=_login_code_keyboard(user_id))
                return
            if action == "back":
                state["entered_code"] = code[:-1]
                await safe_callback_edit(event, _login_code_text(state["entered_code"]), parse_mode="html", buttons=_login_code_keyboard(user_id, state["entered_code"]))
                return
            if action == "display":
                await safe_answer(event, f"کد فعلی: {code or 'خالی'}")
                return
            if action == "submit":
                await _submit_login_code(event, user_id)
                return
            if action == "cancel":
                state = pending.pop(user_id, None)
                if state:
                    timer = state.get("timer")
                    if timer:
                        timer.cancel()
                    client = state.get("client")
                    if client:
                        with contextlib.suppress(Exception):
                            await client.disconnect()
                await safe_callback_edit(
                    event,
                    "**به سلـف‌ساز 𝗛𝘂𝘀𝘁𝗲𝗥𝗜𝗫 𝗗𝗶𝗺𝗼𝗻𝗱 𝗦𝗲𝗹𝗳 خوش آمدید! 💎**\n\n"
                    "برای ساخت سلـف‌ربات، خرید الماس یا دریافت پاداش زیرمجـموعه‌گـیری، لطـفاً یکی از گزینـه‌های منوی زیر را انتـخاب کنـید:",
                    buttons=main_buttons(user_id),
                )
                return
        await handle_self_panel_callback(event)
        return

    if data.startswith("game_noop_"):
        await safe_answer(event)
        return

    if data == "user_account":
        await safe_answer(event)
        try:
            if is_banned(user_id):
                await safe_callback_edit(event, "🚫 <b>شما مسدود هستید.</b>", parse_mode="html", buttons=[[btn("بازگشت", b"back", "primary")]], icon=PREMIUM_EMOJI["self_back"][0])
                return
            init_user_db(user_id)
            balance = get_balance(user_id)
            session = get_active_session(user_id)
            if session:
                elapsed = max(0, int(time.time()) - int(session[2] or 0))
                days = elapsed // 86400
                hours = (elapsed % 86400) // 3600
                self_status = "فعال"
                duration = f"{days} روز و {hours} ساعت"
            else:
                self_status = "غیرفعال"
                duration = "—"
            balance_value_toman = balance * DIAMOND_PRICE_TOMAN
            text = (
                "👤 <b>حساب کاربری</b>\n\n"
                f"🆔 آیدی: <code>{user_id}</code>\n"
                f"💎 موجودی: <code>{html.escape(_fmt_diamonds(balance))}</code> الماس\n"
                f"💰 ارزش موجودی: <code>{balance_value_toman:,.0f}</code> تومان\n"
                f"{premium_emoji('self_status')} وضعیت: {html.escape(self_status)} ❌\n"
                f"⏱ مدت فعالیت: <code>{html.escape(duration)}</code>"
            )
            buttons = user_account_buttons(user_id)
            await edit_or_send(event, text, buttons)
        except Exception:
            logging.exception("user_account callback failed for %s", user_id)
            with contextlib.suppress(Exception):
                await bot.send_message(user_id, premium_ui_text("👤 <b>حساب کاربری</b>\n\n❌ دریافت اطلاعات حساب با خطا مواجه شد. دوباره تلاش کن."), buttons=[[btn("بازگشت", b"back", "primary")]], parse_mode="html", icon=PREMIUM_EMOJI["self_back"][0])
        return

    if not has_registered_phone(user_id):
        await safe_answer(event, "📱 ابتدا شماره موبایل خود را ثبت کنید.", True)
        with contextlib.suppress(Exception):
            await send_phone_request(user_id)
        return

    if not await ensure_force_join(user_id, event):
        return

    if data == "buy_self":
        await begin_self_login(user_id, event)
        return

    if data == "manage_self":
        await show_manage_self(event)
        return

    if data == "refresh_self":
        session = get_active_session(user_id)
        if not session:
            await safe_answer(event, "❌ سلف فعالی پیدا نشد.", True)
            return
        try:
            await safe_answer(event, "⏳ در حال بروزرسانی سلف...")
            await start_self_worker(user_id, session[0], int(session[1]))
            await event.edit(
                premium_ui_text("✅ **سلف با موفقیت بروزرسانی شد.**\n\n"
                "🔐 Session قبلی حفظ شد و Worker دوباره اجرا شد."),
                buttons=[[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
            , parse_mode="html")
        except Exception as exc:
            print(f"[SELF {user_id}] refresh failed: {exc}")
            await safe_answer(event, "❌ بروزرسانی سلف ناموفق بود.", True)
        return

    if data == "toggle_time":
        current = get_setting(user_id, "time_name", "on")
        new = "off" if current == "on" else "on"
        set_setting(user_id, "time_name", new)

        await safe_answer(
            event,
            f"🕐 ساعت کنار نام: {'فعال ✅' if new == 'on' else 'غیرفعال ❌'}"
        )
        await apply_clock_toggle(user_id, "name")
        await show_manage_self(event)
        return

    if data == "disable_self":
        await stop_self_worker(user_id)
        await safe_answer(event)
        await bot.send_message(user_id, premium_ui_text("✅ سلف خاموش شد."), parse_mode="html")
        return

    if data == "enable_self":
        result = reactivate_last_session(user_id)
        if not result:
            await safe_answer(event, "❌ سشنی برای روشن کردن پیدا نشد. ابتدا سلف بسازید.", True)
            return
        session_string, sub_type = result
        try:
            await safe_answer(event, "⏳ در حال روشن کردن سلف...")
            await start_self_worker(user_id, session_string, sub_type)
        except Exception as exc:
            print(f"[SELF {user_id}] enable failed: {exc}")
            await safe_answer(event, "❌ روشن کردن سلف ناموفق بود.", True)
            return
        await bot.send_message(user_id, premium_ui_text("✅ سلف با موفقیت روشن شد\nبرای دیدن دستورات بنویس .پنل"), parse_mode="html")
        return

    if data == "delete_self":
        await delete_self_account(user_id)
        await safe_answer(event, "🗑 سلف حذف شد.")
        await show_manage_self(event)
        return

    if data == "back":
        text = f"{premium_emoji('htx_crown')} <b>پنل اصلی Self 𝑯𝑻𝑿</b>"
        buttons = main_buttons(user_id)
        try:
            # Same photo the whole menu already lives on -- editing the
            # caption in place instead of delete+resend avoids the
            # flash/reflow every "back" tap used to cause.
            await event.edit(premium_ui_text(text), buttons=buttons, parse_mode="html")
        except Exception:
            with contextlib.suppress(Exception):
                await event.delete()
            await send_main(user_id, user_id, text)
        return

    if data == "referral_system":
        init_user_db(user_id)
        with connect_db(user_id) as db:
            count = db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id=?",
                (user_id,)
            ).fetchone()[0]

        me = await bot.get_me()
        link = f"https://t.me/{me.username}?start={user_id}"

        text = (
            "👥 **زیرمجموعه‌گیری**\n\n"
            f"🎁 پاداش هر دعوت: {REFERRAL_REWARD:,} الماس\n"
            f"📊 تعداد دعوت‌ها: {count:,}\n\n"
            f"🔗 لینک دعوت:\n`{link}`"
        )
        await edit_or_send(
            event,
            text,
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data == "buy_balance":
        purchase_state[user_id] = "0"
        await show_buy_balance(event)
        return

    if data.startswith("num_"):
        value = data[4:]
        current = str(purchase_state.get(user_id, "0"))

        if value == "00":
            if current != "0":
                current += "00"
        else:
            current = value if current == "0" else current + value

        if len(current) > 10:
            await safe_answer(event, "❌ مقدار بیش از حد بزرگ است.", True)
            return

        current = current.lstrip("0") or "0"
        purchase_state[user_id] = current
        await show_buy_balance(event)
        return

    if data == "clear_amount":
        purchase_state[user_id] = "0"
        await show_buy_balance(event)
        return

    if data == "confirm_amount":
        try:
            diamonds = int(purchase_state.get(user_id, "0"))
        except ValueError:
            diamonds = 0

        if diamonds < MIN_DIAMOND_PURCHASE:
            await safe_answer(event, f"❌ حداقل خرید {MIN_DIAMOND_PURCHASE:,} الماس است.", True)
            return

        amount = diamonds * DIAMOND_PRICE_TOMAN

        purchase_state[user_id] = {
            "diamonds": diamonds,
            "amount": amount
        }

        text = (
            "💳 **فاکتور خرید**\n\n"
            f"💎 تعداد الماس: {diamonds:,}\n"
            f"💰 مبلغ: {amount:,} تومان\n\n"
            f"💳 شماره کارت:\n`{CARD_NUMBER}`\n"
            f"👤 صاحب کارت: {CARD_HOLDER}\n\n"
            "پس از پرداخت، روی دکمه پرداخت بزنید و عکس رسید را ارسال کنید."
        )

        buttons = [
            [btn("پرداخت و ارسال رسید", b"proceed_payment", "success", icon=5258205968025525531)],
            [btn("لغو", b"cancel_payment", "danger", icon=PREMIUM_EMOJI["cross"][0])]
        ]
        await edit_or_send(event, text, buttons)
        return

    if data == "proceed_payment":
        state = purchase_state.get(user_id)
        if not isinstance(state, dict):
            await safe_answer(event, "❌ فاکتور پیدا نشد.", True)
            return

        purchase_state.pop(user_id, None)
        pending[user_id] = {
            "step": "receipt",
            "diamonds": state["diamonds"],
            "amount": state["amount"]
        }

        await edit_or_send(
            event,
            f"📸 مبلغ `{state['amount']:,}` تومان را پرداخت کنید و سپس عکس رسید را ارسال کنید.\n\n"
            f"💎 معادل: {state['diamonds']:,} الماس\n"
            f"💳 کارت: `{CARD_NUMBER}`\n"
            f"👤 صاحب کارت: {CARD_HOLDER}"
        )
        return

    if data == "cancel_payment":
        purchase_state.pop(user_id, None)
        await edit_or_send(
            event,
            "❌ خرید لغو شد.",
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data.startswith("balance_"):
        target = int(data.split("_", 1)[1])
        balance = get_balance(target)
        await safe_answer(event, f"💎 موجودی: {_fmt_diamonds(balance)} الماس")
        return

    # --------------------------------------------------------
    # GAME JOIN
    # --------------------------------------------------------
    if data.startswith("game_join_"):
        parts = data.split("_")
        if len(parts) != 4:
            await safe_answer(event, "❌ اطلاعات بازی نامعتبر است.", True)
            return

        amount = int(parts[2])
        organizer = int(parts[3])
        joiner = user_id
        key = (event.chat_id, event.message_id)

        if amount < MIN_GAME:
            await safe_answer(
                event,
                f"❌ حداقل مبلغ بازی {MIN_GAME} الماس است.",
                True
            )
            return

        if joiner == organizer:
            await safe_answer(event, "❌ برگزارکننده نمی‌تواند وارد بازی خودش شود.", True)
            return

        game = active_games.get(key)
        if not game:
            await safe_answer(event, "❌ این بازی منقضی شده است.", True)
            asyncio.create_task(_delete_expired_game_message(event.chat_id, event.message_id))
            return

        # Lock before the reveal delay so the same game cannot be joined twice.
        if game.get("resolving"):
            await safe_answer(event, "⏳ در حال انتخاب برنده ...", True)
            return
        game["resolving"] = True

        if get_balance(joiner) < amount:
            game.pop("resolving", None)
            await safe_answer(event, "❌ موجودی کافی ندارید.", True)
            return

        change_balance(joiner, -amount)

        total = amount * 2
        tax = max(1, round(total * GAME_TAX))
        prize = total - tax

        # Exactly 50/50: one unbiased random bit chooses either player.
        winner = organizer if secrets.randbelow(2) == 0 else joiner
        loser = joiner if winner == organizer else organizer

        # Keep the existing game message; only replace it during the 3-second reveal.
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(f"{premium_emoji('game_waiting')} درحال انتخاب برنده ..."), buttons=None, parse_mode="html")

        await asyncio.sleep(3)

        if not is_bot_enabled():
            # Update mode may have been enabled during the 3-second reveal.
            # The organizer is refunded by cancel_all_active_games_for_update();
            # refund the joiner here because this callback already deducted it.
            change_balance(joiner, amount)
            return

        change_balance(winner, prize)
        game_tax_admin_share = tax / 2
        change_balance(7727625618, game_tax_admin_share)

        winner_balance = get_balance(winner)
        loser_balance = get_balance(loser)
        winner_name = await user_name(winner)
        loser_name = await user_name(loser)

        active_games.pop(key, None)
        game["task"].cancel()

        # Result layout matches the reference UI: label + value in two columns.
        diamond_icon = PREMIUM_EMOJI["diamond"][0]
        game_result_buttons = [
            [
                btn("جایزه برنده", b"game_noop_prize", "success", icon=PREMIUM_EMOJI["winner"][0]),
                btn(f"{prize}", b"game_noop_prize_value", "success", icon=diamond_icon),
            ],
            [
                btn("موجودی برنده", b"game_noop_winner", "primary", icon=diamond_icon),
                btn(f"{_fmt_diamonds_plain(winner_balance)}", b"game_noop_winner_value", "primary", icon=diamond_icon),
            ],
            [
                btn("موجودی بازنده", b"game_noop_loser", "danger", icon=PREMIUM_EMOJI["loser"][0]),
                btn(f"{_fmt_diamonds_plain(loser_balance)}", b"game_noop_loser_value", "danger", icon=diamond_icon),
            ],
        ]
        await bot.edit_message(
            event.chat_id,
            event.message_id,
            premium_ui_text(
                f"{premium_emoji("winner")} نتیجه بازی مشخص شد\n\n"
                f"{premium_emoji("winner")} کاربر برنده: {winner_name}\n"
                f"{premium_emoji("loser")} کاربر بازنده: {loser_name}"
            ),
            buttons=game_result_buttons,
            parse_mode="html",
        )

        await safe_answer(event, "✅ بازی به پایان رسید.")
        return


    # --------------------------------------------------------
    # GAME CANCEL
    # --------------------------------------------------------
    if data.startswith("game_cancel_"):
        parts = data.split("_")
        if len(parts) != 4:
            return

        amount = int(parts[2])
        organizer = int(parts[3])
        key = (event.chat_id, event.message_id)

        if user_id != organizer:
            await safe_answer(
                event,
                "❌ فقط برگزارکننده می‌تواند بازی را لغو کند.",
                True
            )
            return

        game = active_games.pop(key, None)
        if not game:
            await safe_answer(event, "❌ بازی قبلاً پایان یافته.", True)
            return

        game["task"].cancel()
        change_balance(organizer, amount)

        cancel_text = f"<b>{premium_emoji('loser')} بازی توسط سازنده لغو شد</b>"
        with contextlib.suppress(Exception):
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(cancel_text),
                buttons=None, parse_mode="html"
            )

        await safe_answer(event, "✅ بازی لغو شد.")
        return

    # --------------------------------------------------------
    # RPS (rock-paper-scissors) — JOIN
    # --------------------------------------------------------
    if data.startswith("rps_join_"):
        parts = data.split("_")
        if len(parts) != 4:
            await safe_answer(event, "❌ اطلاعات بازی نامعتبر است.", True)
            return

        amount = int(parts[2])
        organizer = int(parts[3])
        joiner = user_id
        key = (event.chat_id, event.message_id)

        if joiner == organizer:
            await safe_answer(event, "❌ برگزارکننده نمی‌تواند وارد بازی خودش شود.", True)
            return

        game = active_rps_games.get(key)
        if not game or game.get("phase") != "waiting_join":
            await safe_answer(event, "❌ این بازی منقضی شده یا قبلاً شروع شده است.", True)
            asyncio.create_task(_delete_expired_game_message(event.chat_id, event.message_id))
            return

        if get_balance(joiner) < amount:
            await safe_answer(event, "❌ موجودی کافی ندارید.", True)
            return

        change_balance(joiner, -amount)

        old_task = game.get("task")
        if old_task:
            old_task.cancel()

        game["p2"] = joiner
        game["phase"] = "playing"
        game["score"] = {organizer: 0, joiner: 0}
        game["choices"] = {}
        game["round"] = 1
        game["task"] = asyncio.create_task(rps_round_timeout(event.chat_id, event.message_id, 1))

        p1_name = await user_name(organizer)
        p2_name = await user_name(joiner)

        rock_text, rock_icon = btn_icon_label("rps_rock", "سنگ")
        paper_text, paper_icon = btn_icon_label("rps_paper", "کاغذ")
        scissors_text, scissors_icon = btn_icon_label("rps_scissors", "قیچی")
        move_buttons = [[
            btn(rock_text, b"rps_move_rock", "primary", icon=rock_icon),
            btn(paper_text, b"rps_move_paper", "primary", icon=paper_icon),
            btn(scissors_text, b"rps_move_scissors", "primary", icon=scissors_icon),
        ]]

        await bot.edit_message(
            event.chat_id, event.message_id,
            premium_ui_text(
                f"<b>{premium_glyph('rps_rock')}{premium_glyph('rps_paper')}{premium_glyph('rps_scissors')} سنگ کاغذ قیچی — دور ۱\n\n"
                f"{premium_glyph('rps_user')} {p1_name}: 0 امتیاز\n"
                f"{premium_glyph('rps_user')} {p2_name}: 0 امتیاز\n\n"
                "حرکت خود را با دکمه‌های پایین انتخاب کنید (فقط برای بازیکنان این بازی):</b>"
            ),
            buttons=move_buttons, parse_mode="html"
        )
        await safe_answer(event, "✅ به بازی پیوستید.")
        return

    # --------------------------------------------------------
    # RPS — CANCEL (only before the opponent joins)
    # --------------------------------------------------------
    if data.startswith("rps_cancel_"):
        parts = data.split("_")
        if len(parts) != 4:
            return

        amount = int(parts[2])
        organizer = int(parts[3])
        key = (event.chat_id, event.message_id)

        if user_id != organizer:
            await safe_answer(event, "❌ فقط برگزارکننده می‌تواند بازی را لغو کند.", True)
            return

        game = active_rps_games.get(key)
        if not game or game.get("phase") != "waiting_join":
            await safe_answer(event, "❌ بازی شروع شده و دیگر قابل لغو نیست.", True)
            return

        active_rps_games.pop(key, None)
        task = game.get("task")
        if task:
            task.cancel()
        change_balance(organizer, amount)

        cancel_text_rps = (
            f"<b>{premium_glyph('rps_rock')}{premium_glyph('rps_paper')}{premium_glyph('rps_scissors')} سنگ کاغذ قیچی\n"
            f" ‌{premium_number(_fmt_diamonds_plain(amount))}\n\n"
            f"{premium_emoji('loser')} بازی توسط سازنده لغو شد</b>"
        )
        with contextlib.suppress(Exception):
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(cancel_text_rps),
                buttons=None, parse_mode="html"
            )

        await safe_answer(event, "✅ بازی لغو شد.")
        return

    # --------------------------------------------------------
    # RPS — MOVE (rock / paper / scissors)
    # --------------------------------------------------------
    if data.startswith("rps_move_"):
        choice = data[len("rps_move_"):]
        if choice not in ("rock", "paper", "scissors"):
            return

        key = (event.chat_id, event.message_id)
        game = active_rps_games.get(key)

        if not game or game.get("phase") != "playing":
            await safe_answer(event, "❌ این بازی منقضی شده است.", True)
            asyncio.create_task(_delete_expired_game_message(event.chat_id, event.message_id))
            return

        p1 = int(game["p1"])
        p2 = int(game["p2"])
        if user_id not in (p1, p2):
            await safe_answer(event, "❌ شما در این بازی نیستید.", True)
            return

        choices = game["choices"]
        if user_id in choices:
            await safe_answer(event, "⏳ قبلاً انتخاب کردید، منتظر حریف بمانید.", True)
            return

        choices[user_id] = choice
        rps_choice_fa = {"rock": "سنگ", "paper": "کاغذ", "scissors": "قیچی"}.get(choice, choice)
        await safe_answer(event, f"✅ انتخاب شما: {rps_choice_fa} ثبت شد.")

        if len(choices) < 2:
            return

        # Both players have chosen — cancel this round's timeout and reveal.
        task = game.get("task")
        if task:
            task.cancel()

        amount = int(game["amount"])
        p1_choice = choices[p1]
        p2_choice = choices[p2]
        p1_name = await user_name(p1)
        p2_name = await user_name(p2)

        with contextlib.suppress(Exception):
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(
                    f"{premium_emoji('game_waiting')} هر دو نفر انتخاب کردند ...\n\n"
                    "درحال آشکارسازی انتخاب‌ها ..."
                ),
                buttons=None, parse_mode="html"
            )

        await asyncio.sleep(2)

        if not is_bot_enabled() or active_rps_games.get(key) is not game:
            # Update mode may have kicked in during the reveal delay; the
            # refund in that case is handled by cancel_all_active_games_for_update().
            return

        # Only now — after the suspense delay — are the moves actually shown.
        with contextlib.suppress(Exception):
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(
                    f"{premium_emoji('game_waiting')} انتخاب‌ها آشکار شد!\n\n"
                    f"{premium_glyph('rps_user')} {p1_name}: {premium_glyph('rps_' + p1_choice)}\n"
                    f"{premium_glyph('rps_user')} {p2_name}: {premium_glyph('rps_' + p2_choice)}"
                ),
                buttons=None, parse_mode="html"
            )

        await asyncio.sleep(1.2)

        if not is_bot_enabled() or active_rps_games.get(key) is not game:
            return

        beats = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        if p1_choice == p2_choice:
            round_winner = None
        elif beats[p1_choice] == p2_choice:
            round_winner = p1
        else:
            round_winner = p2

        if round_winner is None:
            # Tie: replay the same round.
            game["choices"] = {}
            new_round_task = asyncio.create_task(
                rps_round_timeout(event.chat_id, event.message_id, game["round"])
            )
            game["task"] = new_round_task

            rock_text, rock_icon = btn_icon_label("rps_rock", "سنگ")
            paper_text, paper_icon = btn_icon_label("rps_paper", "کاغذ")
            scissors_text, scissors_icon = btn_icon_label("rps_scissors", "قیچی")
            move_buttons = [[
                btn(rock_text, b"rps_move_rock", "primary", icon=rock_icon),
                btn(paper_text, b"rps_move_paper", "primary", icon=paper_icon),
                btn(scissors_text, b"rps_move_scissors", "primary", icon=scissors_icon),
            ]]

            score = game["score"]
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(
                    f"{premium_glyph('rps_tie')} این دور مساوی شد! دوباره انتخاب کنید.\n\n"
                    f"{premium_glyph('rps_user')} {p1_name}: {score.get(p1, 0)} امتیاز\n"
                    f"{premium_glyph('rps_user')} {p2_name}: {score.get(p2, 0)} امتیاز"
                ),
                buttons=move_buttons, parse_mode="html"
            )
            return

        # Someone won this round.
        loser = p2 if round_winner == p1 else p1
        game["score"][round_winner] = game["score"].get(round_winner, 0) + 1
        game["choices"] = {}

        if game["score"][round_winner] < 2:
            # Match continues — next round.
            game["round"] += 1
            new_round_task = asyncio.create_task(
                rps_round_timeout(event.chat_id, event.message_id, game["round"])
            )
            game["task"] = new_round_task

            rock_text, rock_icon = btn_icon_label("rps_rock", "سنگ")
            paper_text, paper_icon = btn_icon_label("rps_paper", "کاغذ")
            scissors_text, scissors_icon = btn_icon_label("rps_scissors", "قیچی")
            move_buttons = [[
                btn(rock_text, b"rps_move_rock", "primary", icon=rock_icon),
                btn(paper_text, b"rps_move_paper", "primary", icon=paper_icon),
                btn(scissors_text, b"rps_move_scissors", "primary", icon=scissors_icon),
            ]]

            score = game["score"]
            round_winner_name = p1_name if round_winner == p1 else p2_name
            await bot.edit_message(
                event.chat_id, event.message_id,
                premium_ui_text(
                    f"{premium_emoji('winner')} برنده این دور: {round_winner_name}\n\n"
                    f"{premium_glyph('rps_rock')}{premium_glyph('rps_paper')}{premium_glyph('rps_scissors')} دور {game['round']}\n\n"
                    f"{premium_glyph('rps_user')} {p1_name}: {score.get(p1, 0)} امتیاز\n"
                    f"{premium_glyph('rps_user')} {p2_name}: {score.get(p2, 0)} امتیاز"
                ),
                buttons=move_buttons, parse_mode="html"
            )
            return

        # Match finished — pay out, exactly like the dice game payout.
        active_rps_games.pop(key, None)

        total = amount * 2
        tax = max(1, round(total * GAME_TAX))
        prize = total - tax
        change_balance(round_winner, prize)
        change_balance(7727625618, tax / 2)

        winner_balance = get_balance(round_winner)
        loser_balance = get_balance(loser)
        winner_name = p1_name if round_winner == p1 else p2_name
        loser_name = p2_name if round_winner == p1 else p1_name

        diamond_icon = PREMIUM_EMOJI["diamond"][0]
        result_buttons = [
            [
                btn("جایزه برنده", b"game_noop_prize", "success", icon=PREMIUM_EMOJI["winner"][0]),
                btn(f"{prize}", b"game_noop_prize_value", "success", icon=diamond_icon),
            ],
            [
                btn("موجودی برنده", b"game_noop_winner", "primary", icon=diamond_icon),
                btn(f"{_fmt_diamonds_plain(winner_balance)}", b"game_noop_winner_value", "primary", icon=diamond_icon),
            ],
            [
                btn("موجودی بازنده", b"game_noop_loser", "danger", icon=PREMIUM_EMOJI["loser"][0]),
                btn(f"{_fmt_diamonds_plain(loser_balance)}", b"game_noop_loser_value", "danger", icon=diamond_icon),
            ],
        ]
        await bot.edit_message(
            event.chat_id, event.message_id,
            premium_ui_text(
                f"{premium_emoji('winner')} نتیجه بازی سنگ‌کاغذقیچی مشخص شد (۲-{game['score'].get(loser, 0)})\n\n"
                f"{premium_emoji('winner')} کاربر برنده: {winner_name}\n"
                f"{premium_emoji('loser')} کاربر بازنده: {loser_name}"
            ),
            buttons=result_buttons, parse_mode="html"
        )
        return
    if data == "admin_panel":
        if user_id not in ADMINS:
            await safe_answer(event, "❌ دسترسی ندارید.", True)
            return

        buttons = [
            [btn("الماس", b"admin_gems", "success", icon=PREMIUM_EMOJI["diamond"][0])],
            [btn("کد هدیه", b"admin_gift", "primary", icon=PREMIUM_EMOJI["gift"][0]), btn("آمار کاربران", b"admin_stats", "primary", icon=PREMIUM_EMOJI["profile"][0])],
            [btn("جوین اجباری", b"force_join", "success", icon=PREMIUM_EMOJI["megaphone"][0])],
            [btn("مسدودی", b"admin_block", "danger", icon=PREMIUM_EMOJI["danger"][0]), btn("Backups", b"backups", "primary", icon=PREMIUM_EMOJI["order"][0])],
            [btn("روشن کردن بات" if not is_bot_enabled() else "خاموش کردن بات", b"bot_toggle", "success" if not is_bot_enabled() else "danger", icon=PREMIUM_EMOJI["green"][0] if not is_bot_enabled() else PREMIUM_EMOJI["red"][0])],
            [btn("بازگشت", b"user_account", "danger", icon=PREMIUM_EMOJI["self_back"][0])],
        ]
        await edit_or_send(event, "🛠 **مدیریت**\n\nیک گزینه را انتخاب کنید:", buttons)
        return

    if data == "admin_gems":
        if user_id not in ADMINS:
            return
        pending.pop(user_id, None)
        await edit_or_send(
            event,
            "💎 <b>مدیریت الماس</b>\n\nیک گزینه را انتخاب کنید:",
            [
                [
                    btn("اضافه", b"add_balance", "success", icon=PREMIUM_EMOJI["diamond"][0]),
                    btn("کاهش", b"remove_balance", "danger", icon=PREMIUM_EMOJI["danger"][0]),
                ],
                [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])],
            ],
        )
        return

    if data == "admin_gift":
        if user_id not in ADMINS:
            return
        pending.pop(user_id, None)
        await edit_or_send(event, _gift_admin_menu_text(), _gift_admin_menu_buttons())
        return

    if data == "admin_block":
        if user_id not in ADMINS:
            return
        pending.pop(user_id, None)
        await edit_or_send(
            event,
            "🚫 <b>مدیریت مسدودی</b>\n\nیک گزینه را انتخاب کنید:",
            [
                [
                    btn("مسدود", b"ban_user", "danger", icon=PREMIUM_EMOJI["danger"][0]),
                    btn("رفع مسدودی", b"unban_user", "success", icon=PREMIUM_EMOJI["check"][0]),
                ],
                [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])],
            ],
        )
        return

    if data == "gift_create":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "gift_create_code"}
        await edit_or_send(
            event,
            "🎁 <b>ساخت کد هدیه</b>\n\n"
            "🎟 <b>مرحله ۱ از ۳</b>\n"
            "کد هدیه را ارسال کن.\n\n"
            "مثال: <code>GIFT2026</code>\n"
            "فقط حروف انگلیسی، عدد، <code>_</code> و <code>-</code> مجاز است.",
            [[btn("لغو", b"gift_cancel", "danger", icon=PREMIUM_EMOJI["cross"][0])]]
        )
        return

    if data == "gift_cancel":
        if user_id not in ADMINS:
            return
        pending.pop(user_id, None)
        await edit_or_send(event, _gift_admin_menu_text(), _gift_admin_menu_buttons())
        return

    if data == "gift_manage":
        if user_id not in ADMINS:
            return
        codes = _gift_codes()
        active = _gift_active_codes()
        rows = []
        for idx, item in enumerate(codes):
            if float(item.get("expires_at", 0)) <= time.time() or int(item.get("reward", 0)) <= 0:
                continue
            rows.append([btn(f"🎁 {item['code']} • 💎 {item['reward']:,}", f"gift_info:{idx}", "primary", icon=PREMIUM_EMOJI["gift"][0])])
        if not rows:
            body = "🎁 <b>کدهای جاری</b>\n\n❕ در حال حاضر هیچ کد فعالی وجود ندارد."
        else:
            body = f"🎁 <b>کدهای جاری</b>\n\n🟢 تعداد فعال: <b>{len(active):,}</b>\n\nبرای مشاهده جزئیات یا حذف هر کد، روی آن بزن."
        rows.append([btn("ساخت کد هدیه", b"gift_create", "success", icon=PREMIUM_EMOJI["gift"][0])])
        rows.append([btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])])
        await edit_or_send(event, body, rows)
        return

    if data.startswith("gift_info:"):
        if user_id not in ADMINS:
            return
        try:
            idx = int(data.split(":", 1)[1])
            codes = _gift_codes()
            item = codes[idx]
        except (ValueError, IndexError):
            await safe_answer(event, "❌ کد هدیه پیدا نشد.", True)
            return
        if float(item.get("expires_at", 0)) <= time.time():
            await safe_answer(event, "⏰ این کد منقضی شده است.", True)
        used = len(item.get("used_by", []))
        body = (
            "🎁 <b>جزئیات کد هدیه</b>\n\n"
            f"🎟 کد: <code>{html.escape(item['code'])}</code>\n"
            f"💎 پاداش: <b>{int(item['reward']):,}</b> الماس\n"
            f"⏰ انقضا: <b>{html.escape(_gift_format_expiry(item['expires_at']))}</b>\n"
            f"👥 استفاده‌شده: <b>{used:,}</b> نفر"
        )
        await edit_or_send(
            event, body,
            [
                [btn("🗑 حذف کد", f"gift_delete:{idx}", "danger", icon=PREMIUM_EMOJI["cross"][0])],
                [btn("بازگشت", b"gift_manage", "primary", icon=PREMIUM_EMOJI["self_back"][0])],
            ]
        )
        return

    if data.startswith("gift_delete:"):
        if user_id not in ADMINS:
            return
        try:
            idx = int(data.split(":", 1)[1])
            codes = _gift_codes()
            item = codes.pop(idx)
        except (ValueError, IndexError):
            await safe_answer(event, "❌ کد هدیه پیدا نشد.", True)
            return
        _save_gift_codes(codes)
        await safe_answer(event, "✅ کد حذف شد.")
        await edit_or_send(event, _gift_admin_menu_text(), _gift_admin_menu_buttons())
        return

    if data == "fj_add_cancel":
        if user_id not in ADMINS:
            return
        pending.pop(user_id, None)
        await edit_or_send(
            event,
            "📢 **جوین اجباری**\n\n"
            "کانال‌های فعال با رنگ بنفش نمایش داده می‌شوند.\n"
            "برای افزودن، لینک عمومی کانال مثل `@channel` یا `https://t.me/channel` را بفرست.",
            [
                [btn("افزودن کانال", b"fj_add", "success", icon=5780899429204631677),
                 btn("حذف همه", b"fj_clear", "danger", icon=5258130763148172425)],
                [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])]
            ]
        )
        return

    if data == "force_join":
        if user_id not in ADMINS:
            return
        channels = get_force_join_channels()
        rows = []
        for c in channels:
            rows.append([
                btn(f"📢 {c.get('title', c.get('username', 'کانال'))}", f"fj_info:{c.get('id')}", "primary")
            ])
        rows.append([btn("افزودن کانال", b"fj_add", "success", icon=5780899429204631677), btn("حذف همه", b"fj_clear", "danger", icon=5258130763148172425)])
        rows.append([btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])])
        await edit_or_send(
            event,
            "📢 **جوین اجباری**\n\n"
            "کانال‌های فعال با رنگ بنفش نمایش داده می‌شوند.\n"
            "برای افزودن، لینک عمومی کانال مثل `@channel` یا `https://t.me/channel` را بفرست.",
            rows
        )
        return

    if data == "fj_add":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "force_join_add"}
        await safe_callback_edit(event, "📢 <b>افزودن کانال</b>\n\nلینک عمومی کانال را ارسال کن؛ مثلاً:\n<code>@channel</code>\nیا\n<code>https://t.me/channel</code>\n\nبرای کانال/گروه خصوصی، یک پیام از همان‌جا را فوروارد کن.", parse_mode="html", buttons=[[btn("بازگشت", b"force_join", "danger", icon=PREMIUM_EMOJI["self_back"][0])]])
        return

    if data.startswith("fj_info:"):
        if user_id not in ADMINS:
            return
        try:
            cid = int(data.split(":", 1)[1])
        except ValueError:
            await safe_answer(event, "❌ کانال نامعتبر است.", True)
            return
        channel = next((c for c in get_force_join_channels() if int(c.get("id", 0)) == cid), None)
        if not channel:
            await safe_answer(event, "❌ کانال پیدا نشد.", True)
            return
        title = html.escape(str(channel.get("title") or "کانال"))
        username = str(channel.get("username") or "")
        url = _channel_url(channel)
        kind = "خصوصی" if channel.get("private") else "عمومی"
        text = (
            f"📢 <b>اطلاعات جوین اجباری</b>\n\n"
            f"🏷 نام: <b>{title}</b>\n"
            f"🔐 نوع: <b>{kind}</b>\n"
            f"🆔 آیدی: <code>{int(channel.get('id', 0))}</code>\n"
            f"🔗 لینک: <code>{html.escape(url or 'ندارد')}</code>"
        )
        await event.edit(
            premium_ui_text(text),
            parse_mode="html",
            buttons=[
                [btn("حذف جوین اجباری", f"fj_remove:{cid}", "danger", icon=5258130763148172425)],
                [btn("بازگشت", b"force_join", "primary", icon=PREMIUM_EMOJI["self_back"][0])],
            ],
        )
        return

    if data.startswith("fj_remove:"):
        if user_id not in ADMINS:
            return
        cid = int(data.split(":", 1)[1])
        channels = [c for c in get_force_join_channels() if int(c.get("id", 0)) != cid]
        save_force_join_channels(channels)
        await safe_answer(event, "✅ کانال حذف شد.")
        await event.edit(premium_ui_text("📢 **جوین اجباری**"), buttons=[
            [btn("افزودن کانال", b"fj_add", "success", icon=5780899429204631677), btn("حذف همه", b"fj_clear", "danger", icon=5258130763148172425)],
            [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])]
        ], parse_mode="html")
        return

    if data == "fj_clear":
        if user_id not in ADMINS:
            return
        save_force_join_channels([])
        await safe_answer(event, "✅ همه جوین‌های اجباری حذف شدند.")
        await edit_or_send(event, "📢 **جوین اجباری**\n\nهیچ کانالی تنظیم نشده است.", [
            [btn("افزودن کانال", b"fj_add", "success", icon=5780899429204631677)],
            [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])]
        ])
        return

    if data == "backups":
        if user_id not in ADMINS:
            return
        await edit_or_send(
            event,
            "💾 **Backups**\n\n"
            "بکاپ شامل database_users، موجودی کاربران، وضعیت سلف، sessionها، تنظیمات و جوین اجباری است.",
            [
                [btn("بکاپ‌گیری", b"backup_create", "success"), btn("بارگزاری بکاپ", b"backup_restore", "primary")],
                [btn("بازگشت", b"admin_panel", "danger", icon=PREMIUM_EMOJI["self_back"][0])]
            ]
        )
        return

    if data == "backup_create":
        if user_id not in ADMINS:
            return
        await safe_answer(event, "⏳ در حال ساخت بکاپ...")
        try:
            path = await asyncio.to_thread(create_backup_sync)
            await bot.send_file(user_id, str(path), caption=premium_ui_text("💾 بکاپ کامل ربات آماده است."), parse_mode="html")
            with contextlib.suppress(Exception):
                path.unlink()
            await event.edit(premium_ui_text("✅ بکاپ کامل با موفقیت ارسال شد."), buttons=[[btn("Backups", b"backups", "danger")]], parse_mode="html")
        except Exception as exc:
            print(f"[BACKUP] create failed: {exc}")
            await event.edit(premium_ui_text("❌ ساخت بکاپ ناموفق بود."), buttons=[[btn("Backups", b"backups", "danger")]], parse_mode="html")
        return

    if data == "backup_restore":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "backup_restore"}
        await edit_or_send(
            event,
            "🟣 **بارگزاری بکاپ**\n\nفایل ZIP بکاپ را همین‌جا ارسال کن.\n"
            "قبل از بازگردانی، Workerهای سلف متوقف و بعد از اتمام دوباره بازیابی می‌شوند.",
            [[btn("لغو", b"backups", "danger")]]
        )
        return

    if data == "admin_stats":
        if user_id not in ADMINS:
            return
        count = len(list(DATA_DIR.glob("user_*.db")))
        active = len(all_active_sessions())
        total_diamonds = total_diamonds_in_circulation()
        await edit_or_send(
            event,
            f"📊 **آمار مدیریت**\n\n👥 کاربران ثبت‌شده: `{count}`\n⚙️ سلف‌های فعال: `{active}`\n📢 جوین‌های اجباری: `{len(get_force_join_channels())}`\n💎 کل الماس‌های در گردش: `{_fmt_diamonds(total_diamonds)}`",
            [[btn("🔙 مدیریت", b"admin_panel", "danger")]]
        )
        return

    if data == "add_balance":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "add_balance_user"}
        await edit_or_send(
            event,
            "➕ آیدی عددی کاربر را ارسال کنید:",
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data == "remove_balance":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "remove_balance_user"}
        await edit_or_send(
            event,
            "➖ آیدی عددی کاربر را ارسال کنید:",
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data == "ban_user":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "ban_user"}
        await edit_or_send(
            event,
            "🚫 آیدی عددی کاربر را ارسال کنید:",
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data == "unban_user":
        if user_id not in ADMINS:
            return
        pending[user_id] = {"step": "unban_user"}
        await edit_or_send(
            event,
            "🔓 آیدی عددی کاربر را ارسال کنید:",
            [[btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]]
        )
        return

    if data.startswith("pay_confirm_"):
        if user_id not in ADMINS:
            return

        parts = data.split("_")
        target = int(parts[2])
        diamonds = int(parts[3])

        init_user_db(target)
        change_balance(target, diamonds)

        purchase_state.pop(target, None)

        with contextlib.suppress(Exception):
            await bot.send_message(
                target,
                premium_ui_text(f"✅ پرداخت شما تأیید شد.\n"
                f"💎 {diamonds:,} الماس به حساب شما اضافه شد.\n\n"
                "🔄 منوی اصلی شما خودکار بروزرسانی شد.")
            , parse_mode="html")
            # Behave like /start after approval so the user immediately gets
            # the normal main buttons without having to send /start manually.
            await send_main(target, target)

        await safe_answer(event, "✅ پرداخت تأیید شد و منوی کاربر بروزرسانی شد.")
        with contextlib.suppress(Exception):
            await event.edit(
                premium_ui_text(f"✅ پرداخت کاربر `{target}` تأیید شد.\n"
                f"💎 {diamonds:,} الماس اضافه شد.")
            , parse_mode="html")
        return

    if data.startswith("pay_reject_"):
        if user_id not in ADMINS:
            return

        target = int(data.split("_")[2])

        with contextlib.suppress(Exception):
            await bot.send_message(
                target,
                premium_ui_text("❌ پرداخت شما رد شد.\nلطفاً با پشتیبانی تماس بگیرید.")
            , parse_mode="html")

        await safe_answer(event, "❌ پرداخت رد شد.")
        with contextlib.suppress(Exception):
            await event.edit(premium_ui_text(f"❌ پرداخت کاربر `{target}` رد شد."), parse_mode="html")
        return


async def show_manage_self(event):
    user_id = event.sender_id
    last = get_last_session(user_id)

    if not last:
        text = f"{premium_emoji('self_manage')} <b>مدیریت سلف</b>\n\nهنوز سلفی نساخته‌اید."
        buttons = [
            [btn("فعال‌سازی سلف", b"buy_self", "success", icon=PREMIUM_EMOJI["diamond"][0])],
            [btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]
        ]
    else:
        text = f"{premium_emoji('self_manage')} <b>مدیریت سلف</b>"
        buttons = [
            [
                btn("روشن کردن", b"enable_self", "primary", icon=PREMIUM_EMOJI["self_on"][0]),
                btn("خاموش کردن", b"disable_self", "primary", icon=PREMIUM_EMOJI["self_off"][0]),
            ],
            [btn("حذف سلف", b"delete_self", "danger", icon=PREMIUM_EMOJI["loser"][0])],
            [btn("بازگشت", b"back", "danger", icon=PREMIUM_EMOJI["self_back"][0])]
        ]

    await edit_or_send(event, text, buttons)


async def show_buy_balance(event):
    user_id = event.sender_id
    value = str(purchase_state.get(user_id, "0"))

    try:
        diamonds = int(value)
    except ValueError:
        diamonds = 0

    amount = diamonds * DIAMOND_PRICE_TOMAN

    buttons = [
        [
            btn("1", b"num_1", "primary"),
            btn("2", b"num_2", "primary"),
            btn("3", b"num_3", "primary"),
        ],
        [
            btn("4", b"num_4", "primary"),
            btn("5", b"num_5", "primary"),
            btn("6", b"num_6", "primary"),
        ],
        [
            btn("7", b"num_7", "primary"),
            btn("8", b"num_8", "primary"),
            btn("9", b"num_9", "primary"),
        ],
        [
            btn("تأیید", b"confirm_amount", "success", icon=5260726538302660868),
            btn("0", b"num_0", "primary"),
            btn("حذف", b"clear_amount", "danger", icon=5258130763148172425),
        ],
        [btn("بازگشت", b"back", "primary", icon=PREMIUM_EMOJI["self_back"][0])]
    ]

    text = (
        "💳 **خرید موجودی**\n\n"
        f"💎 تعداد الماس: {diamonds:,}\n"
        f"💰 مبلغ: {amount:,} تومان\n\n"
        f"📌 حداقل خرید: {MIN_DIAMOND_PURCHASE:,} الماس\n"
        f"💵 {MIN_DIAMOND_PURCHASE:,} الماس = {MIN_DIAMOND_PURCHASE * DIAMOND_PRICE_TOMAN:,} تومان\n\n"
        "تعداد الماس را انتخاب کنید:"
    )

    await edit_or_send(event, text, buttons)


# ============================================================
# ADMIN COMMANDS
# ============================================================

@bot.on(events.NewMessage(pattern=r"^/panel$"))
async def panel(event):
    if not event.is_private:
        return
    if event.sender_id not in ADMINS:
        await event.reply(premium_ui_text("❌ شما دسترسی ندارید."), parse_mode="html")
        return
    buttons = [[btn("🛠 پنل مدیریت", b"admin_panel", "primary")]]
    await event.reply(premium_ui_text("🛠 برای ورود به پنل مدیریت:"), buttons=buttons, parse_mode="html")

@bot.on(events.NewMessage(pattern=r"^/fix_half$"))
async def fix_half(event):
    if not event.is_private:
        return
    if event.sender_id not in ADMINS:
        await event.reply(premium_ui_text("❌ شما دسترسی ندارید."), parse_mode="html")
        return

    fixed = 0
    checked = 0
    for db_file in sorted(DATA_DIR.glob("user_*.db")):
        checked += 1
        try:
            conn = sqlite3.connect(db_file, timeout=30)
            try:
                row = conn.execute("SELECT balance FROM users LIMIT 1").fetchone()
                if not row:
                    continue
                balance = float(row[0])
                if abs((balance - int(balance)) - 0.5) < 1e-6:
                    conn.execute("UPDATE users SET balance = ?", (balance - 0.5,))
                    conn.commit()
                    fixed += 1
            finally:
                conn.close()
        except Exception as exc:
            print(f"[FIX_HALF] {db_file.name}: {exc}")

    await event.reply(
        premium_ui_text(f"✅ پاکسازی انجام شد.\n"
        f"🔎 بررسی‌شده: {checked}\n"
        f"💎 اصلاح‌شده: {fixed}")
    , parse_mode="html")


@bot.on(events.NewMessage(pattern=r"^/sioh\s+(\d+)\s+(\d+)$"))
async def sioh(event):
    user_id = event.sender_id
    amount = int(event.pattern_match.group(1))
    target = int(event.pattern_match.group(2))

    if amount <= 0:
        await event.reply(premium_ui_text("❌ مقدار باید بیشتر از صفر باشد."), parse_mode="html")
        return

    if user_id == target:
        await event.reply(premium_ui_text("❌ نمی‌توانید به خودتان انتقال دهید."), parse_mode="html")
        return

    if get_balance(user_id) < amount:
        await event.reply(premium_ui_text("❌ موجودی کافی نیست."), parse_mode="html")
        return

    init_user_db(target)
    change_balance(user_id, -amount)
    change_balance(target, amount)

    await event.reply(
        premium_ui_text(f"✅ انتقال انجام شد.\n"
        f"💎 {amount:,} الماس به `{target}` منتقل شد.")
    , parse_mode="html")


# ============================================================
# STARTUP / SHUTDOWN
# ============================================================

async def restore_workers():
    restored = 0

    for user_id, session_string, sub_type in all_active_sessions():
        try:
            if get_balance(user_id) <= 0:
                deactivate_session(user_id)
                continue

            await start_self_worker(
                user_id,
                session_string,
                sub_type
            )
            restored += 1
        except Exception as exc:
            print(f"[RESTORE {user_id}] {exc}")

    print(f"[RESTORE] {restored} self worker(s) restored.")


async def main():
    for admin in ADMINS:
        init_user_db(admin)

    print("=" * 55)
    print("🤖 Diamond Bot is starting...")
    print(f"👤 Admins: {ADMINS}")
    print("📁 Database:", DATA_DIR)
    print("=" * 55)

    # FloodWait-safe login: instead of crashing (Railway would restart the
    # container and hit ImportBotAuthorization again, making the ban longer),
    # wait out Telegram's cooldown and retry in-process.
    while True:
        try:
            await bot.start(bot_token=BOT_TOKEN)
            break
        except FloodWaitError as exc:
            wait = int(getattr(exc, "seconds", 60)) + 5
            print(f"⏳ Bot login FloodWait: waiting {wait}s before retrying (do NOT redeploy)")
            await asyncio.sleep(wait)

    me = await bot.get_me()
    print(f"✅ Bot: @{me.username if me else 'unknown'}")
    await resolve_official_group_id()

    # «.ویس متن»: install edge-tts in the background so startup never waits on pip.
    _tts_install_task = asyncio.create_task(_ensure_edge_tts(force=True))
    _tts_install_task.add_done_callback(lambda t: t.cancelled() or t.exception())
    # OCR: fetch the accurate tessdata_best models (fas+eng) in the background.
    _ocr_dl_task = asyncio.create_task(_ocr_ensure_best_models(force=True))
    _ocr_dl_task.add_done_callback(lambda t: t.cancelled() or t.exception())

    await asyncio.to_thread(disable_non_photo_banners_sync)

    await restore_workers()

    print("🚀 Bot is running.")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
