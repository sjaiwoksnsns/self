# -*- coding: utf-8 -*-
"""Presentation-only Premium Custom Emoji helpers."""

import re

PREMIUM_EMOJI = {
    "diamond": (5823211806327316872, "💎"),
    "dollar": (6260350833230090640, "$"),
    "phone": (5316653334688446735, "📱"),
    "crown": (6332172315735891342, "👑"),
    "shield": (5900009781539639795, "🛡️"),
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

    "numbers": {
        "0": (5780643711146795718, "0️⃣"),
        "1": (5780843006219264060, "1️⃣"),
        "2": (5780668012071754752, "2️⃣"),
        "3": (5780802667886419287, "3️⃣"),
        "4": (5780747000815296636, "4️⃣"),
        "5": (5780681429549588430, "5️⃣"),
        "6": (5780715303956652173, "6️⃣"),
        "7": (5780648783503171696, "7️⃣"),
        "8": (5780631380295688856, "8️⃣"),
        "9": (5780397579455962736, "9️⃣"),
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
    "☑️": "checkbox", "🎁": "gift", "✈️": "plane", "🙂": "smile",
    "📷": "camera", "➕": "plus", "▶️": "play", "🔼": "up",
    "🔽": "down_shop", "⏳": "clock", "❤": "heart", "📦": "order",
    "😼": "smile", "⚙": "gear", "🔐": "shield", "🕐": "clock",
    "🧹": "cross", "⏱": "clock", "🏓": "play", "🤖": "shield",
    "📚": "info", "🎙": "chat", "🎬": "play", "💡": "star",
    "💳": "dollar", "🛠": "gear", "🖼": "camera", "🤵": "user",
    "💱": "dollar", "🎨": "star", "🎣": "link", "📊": "info",
    "📨": "megaphone", "🔓": "shield", "🆔": "user", "🌐": "link",
    "👁": "user", "🔒": "lock", "🏷": "price", "💰": "dollar",
    "🎲": "diamond", "🐱": "smile", "🔎": "blue", "🔘": "blue",
    "📸": "camera", "🎵": "music", "🎤": "chat", "🔄": "lightning",
    "👥": "user", "🕐": "clock", "🔐": "shield", "🏠": "home",
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
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def premium_number(value):
    raw = str(value)
    return "".join(
        f'<tg-emoji emoji-id="{PREMIUM_EMOJI["numbers"][ch][0]}">'
        f'{PREMIUM_EMOJI["numbers"][ch][1]}</tg-emoji>'
        if ch in PREMIUM_EMOJI["numbers"] else ch
        for ch in raw
    )

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
    """Premium only the final UI text; protect existing tg-emoji/code/pre blocks."""
    if text is None or not isinstance(text, str) or not text:
        return text

    protected = []
    def hold(match):
        token = f"\x00PREMIUM_PROTECTED_{len(protected)}\x00"
        protected.append(match.group(0))
        return token

    # Convert only the small Markdown subset used by the existing UI first.
    # Newly-created <code> blocks are then protected together with pre-existing
    # <code>/<pre>/<tg-emoji> blocks.
    text = _premium_markdown_to_html(text)
    working = _PREMIUM_TAG_RE.sub(hold, text)

    # Longest glyphs first so ❤️/⚠️/🛡️ are processed before ❤/⚙ etc.
    glyph_pattern = re.compile(
        "|".join(re.escape(g) for g in sorted(PREMIUM_GLYPH_MAP, key=len, reverse=True))
    )
    working = glyph_pattern.sub(
        lambda m: premium_emoji(PREMIUM_GLYPH_MAP[m.group(0)]),
        working,
    )

    # Restore protected blocks exactly as they were.
    for idx, original in enumerate(protected):
        working = working.replace(f"\x00PREMIUM_PROTECTED_{idx}\x00", original)

    return working

