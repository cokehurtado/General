#!/usr/bin/env python3
"""
Golf Club Second-Hand Tracker — data collector.

Searches eBay (official Browse API) for the tracked clubs, filters listings
to the wanted spec (stiff shaft, right-handed, full sets / correct loft),
scores each listing against a reference price, and writes:

  data/latest.json    current scored snapshot per club (read by the dashboard)
  data/history.jsonl  one line per club per run: min / p25 / median / count
  data/seen.json      first-seen date per eBay item id (powers "NEW" badges)

Credentials (free at https://developer.ebay.com — a "keyset" for the
production environment):

  export EBAY_CLIENT_ID="your-app-id"
  export EBAY_CLIENT_SECRET="your-cert-id"

Usage:
  python3 tracker.py            # fetch live data from eBay
  python3 tracker.py --demo     # generate clearly-labeled demo data instead
"""

import base64
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
OAUTH_SCOPE = "https://api.ebay.com/oauth/api_scope"


# ---------------------------------------------------------------- utilities

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def http_json(url, headers=None, data=None, retries=3):
    """GET/POST returning parsed JSON, with basic exponential backoff."""
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            last_err = RuntimeError(f"HTTP {e.code} from {url}: {body}")
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise last_err
        except urllib.error.URLError as e:
            last_err = RuntimeError(f"Network error for {url}: {e.reason}")
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise last_err
    raise last_err


# ------------------------------------------------------------- eBay client

def get_token():
    client_id = os.environ.get("EBAY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("EBAY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        sys.exit(
            "Missing EBAY_CLIENT_ID / EBAY_CLIENT_SECRET environment variables.\n"
            "Create a free production keyset at https://developer.ebay.com, then:\n"
            '  export EBAY_CLIENT_ID="<App ID>"\n'
            '  export EBAY_CLIENT_SECRET="<Cert ID>"\n'
            "Or run with --demo to generate sample data for the dashboard."
        )
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    body = urllib.parse.urlencode(
        {"grant_type": "client_credentials", "scope": OAUTH_SCOPE}
    ).encode()
    resp = http_json(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=body,
    )
    return resp["access_token"]


def search_ebay(token, marketplace, club, conditions, currency):
    lo, hi = club.get("priceRange", [0, 100000])
    filters = [
        "conditions:{" + "|".join(conditions) + "}",
        f"price:[{lo}..{hi}]",
        f"priceCurrency:{currency}",
    ]
    params = {
        "q": club["query"],
        "limit": "200",
        "filter": ",".join(filters),
        "sort": "price",
    }
    if club.get("categoryIds"):
        params["category_ids"] = ",".join(club["categoryIds"])
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    resp = http_json(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": marketplace,
            "Content-Type": "application/json",
        },
    )
    return resp.get("itemSummaries", [])


# ------------------------------------------------------- listing filtering

FLEX_PATTERNS = [
    ("x-stiff", re.compile(r"\b(x[\s-]?stiff|extra\s+stiff|\bxs\b|\bx\s+flex)\b", re.I)),
    ("stiff", re.compile(r"\bstiff\b|\bs\s+flex\b|\bflex[:\s]+s\b", re.I)),
    ("regular", re.compile(r"\bregular\b|\breg\b|\br\s+flex\b|\bflex[:\s]+r\b", re.I)),
    ("senior", re.compile(r"\bsenior\b|\ba\s+flex\b", re.I)),
    ("ladies", re.compile(r"\bladies\b|\bwomen", re.I)),
]

LEFT_RE = re.compile(r"\bleft[\s-]?hand|\blh\b", re.I)
RIGHT_RE = re.compile(r"\bright[\s-]?hand|\brh\b", re.I)
YEAR_RE = re.compile(r"\b(20(1[89]|2[0-6]))\b|'(2[0-6])\b")

WOOD_PATTERNS = {
    3: re.compile(r"\b3[\s-]?(wood|w\b)|#\s?3\b|\b15(\.0)?\s*(deg|°)|\b13\.5\b|\b16\.5\b", re.I),
    5: re.compile(r"\b5[\s-]?(wood|w\b)|#\s?5\b|\b18(\.0)?\s*(deg|°)", re.I),
    7: re.compile(r"\b7[\s-]?(wood|w\b)|#\s?7\b|\b21(\.0)?\s*(deg|°)", re.I),
}


def classify_flex(title):
    for name, pat in FLEX_PATTERNS:
        if pat.search(title):
            return name
    return "unknown"


def classify_dexterity(title):
    if LEFT_RE.search(title):
        return "left"
    if RIGHT_RE.search(title):
        return "right"
    return "unknown"


def detect_year(title):
    m = YEAR_RE.search(title)
    if not m:
        return None
    return m.group(1) or ("20" + m.group(3))


def wood_number_ok(title, wanted):
    """For fairway woods: keep listings that mention the wanted wood/loft,
    or don't mention any wood number at all (checked manually via tags)."""
    mentions = {n for n, pat in WOOD_PATTERNS.items() if pat.search(title)}
    if not mentions:
        return True, False  # keep, but not confirmed
    return wanted in mentions, wanted in mentions


def passes_filters(title, club, config):
    t = " " + title.lower() + " "
    for kw in config.get("excludeKeywords", []) + club.get("extraExcludeKeywords", []):
        if kw.lower() in t:
            return False
    return True


def normalize_item(item, club, config):
    title = item.get("title", "")
    if not passes_filters(title, club, config):
        return None

    price = float(item.get("price", {}).get("value", 0) or 0)
    if price <= 0:
        return None
    shipping = 0.0
    for opt in item.get("shippingOptions", []) or []:
        cost = opt.get("shippingCost", {})
        if cost.get("value") is not None:
            shipping = float(cost["value"])
            break

    flex = classify_flex(title)
    if flex not in config.get("acceptFlex", ["stiff", "unknown"]):
        return None

    dex = classify_dexterity(title)
    if config.get("dexterity") == "right" and dex == "left":
        return None

    tags = []
    wanted_wood = club.get("woodNumber")
    if wanted_wood:
        ok, confirmed = wood_number_ok(title, wanted_wood)
        if not ok:
            return None
        if confirmed:
            tags.append(f"{wanted_wood}W ✓")
        else:
            tags.append("loft?")

    year = detect_year(title)
    if year:
        tags.append(year)
    if flex == "unknown":
        tags.append("flex?")
    if dex == "unknown":
        tags.append("dex?")

    seller = item.get("seller", {}) or {}
    return {
        "itemId": item.get("itemId", ""),
        "title": title,
        "url": item.get("itemWebUrl", ""),
        "image": (item.get("image", {}) or {}).get("imageUrl", ""),
        "price": round(price, 2),
        "shipping": round(shipping, 2),
        "total": round(price + shipping, 2),
        "condition": item.get("condition", ""),
        "buyingOption": ", ".join(item.get("buyingOptions", []) or []),
        "flex": flex,
        "dexterity": dex,
        "tags": tags,
        "seller": {
            "username": seller.get("username", ""),
            "feedbackPct": seller.get("feedbackPercentage", ""),
            "feedbackScore": seller.get("feedbackScore", 0),
        },
        "endDate": item.get("itemEndDate", ""),
    }


# ---------------------------------------------------------------- scoring

def score_listings(listings, club):
    """Rate each listing against a reference price: the median of the current
    market when there are enough listings, else the configured baseline."""
    totals = sorted(l["total"] for l in listings)
    market_median = round(statistics.median(totals), 2) if totals else None
    reference = club.get("referenceUsedPrice") or club.get("retailPrice")
    if market_median is not None and len(totals) >= 5:
        reference = min(market_median, reference or market_median)

    for l in listings:
        if not reference:
            l["rating"], l["dealPct"] = "fair", 0.0
            continue
        ratio = l["total"] / reference
        l["dealPct"] = round((1 - ratio) * 100, 1)
        if ratio <= 0.85:
            l["rating"] = "great"
        elif ratio <= 0.95:
            l["rating"] = "good"
        elif ratio <= 1.05:
            l["rating"] = "fair"
        else:
            l["rating"] = "high"
    return market_median, reference


def summarize(totals):
    if not totals:
        return {"count": 0, "min": None, "p25": None, "median": None}
    ts = sorted(totals)
    return {
        "count": len(ts),
        "min": round(ts[0], 2),
        "p25": round(ts[max(0, len(ts) // 4)], 2),
        "median": round(statistics.median(ts), 2),
    }


# -------------------------------------------------------------- demo data

DEMO_SHAFTS = {
    "p770-irons": ["KBS Tour Stiff", "Project X LZ 6.0", "Dynamic Gold 105 S300", "Modus 105 Stiff"],
    "qi4d-driver": ["Ventus Blue 6 S", "Diamana T+ 60 Stiff", "Tensei AV Blue 65 S", "HZRDUS Black S"],
    "qi4d-3wood": ["Ventus Blue 7 S", "Diamana T+ 70 Stiff", "Tensei AV Raw Blue 75 S"],
}
DEMO_TITLES = {
    "p770-irons": "TaylorMade P770 {yr} Iron Set 4-PW {shaft} Right Handed",
    "qi4d-driver": "TaylorMade Qi4D Driver 9.0° {shaft} Stiff RH w/ Headcover",
    "qi4d-3wood": "TaylorMade Qi4D 3 Wood 15° {shaft} Stiff Right Hand",
}
DEMO_BASE = {"p770-irons": (1050, 2024), "qi4d-driver": (560, 2026), "qi4d-3wood": (330, 2026)}
DEMO_CONDITIONS = ["Used - Excellent", "Used - Very Good", "Used - Good", "Seller refurbished"]


def make_demo_data(config):
    rng = random.Random(7)
    now = datetime.now(timezone.utc)
    history_lines = []
    clubs_out = []

    for club in config["clubs"]:
        base, yr = DEMO_BASE[club["id"]]
        # 90 days of gently declining daily stats
        for d in range(90, 0, -1):
            day = (now - timedelta(days=d)).strftime("%Y-%m-%d")
            drift = base * (1 + 0.10 * d / 90)  # prices ~10% higher 3 months ago
            noise = rng.uniform(-0.03, 0.03) * drift
            median = drift + noise
            history_lines.append(json.dumps({
                "date": day, "clubId": club["id"],
                "count": rng.randint(6, 28),
                "min": round(median * rng.uniform(0.78, 0.88), 2),
                "p25": round(median * rng.uniform(0.9, 0.96), 2),
                "median": round(median, 2),
            }))

        listings = []
        for i in range(rng.randint(9, 16)):
            shaft = rng.choice(DEMO_SHAFTS[club["id"]])
            price = round(base * rng.uniform(0.8, 1.25), 2)
            ship = rng.choice([0.0, 0.0, 12.95, 19.99, 24.99])
            title = DEMO_TITLES[club["id"]].format(shaft=shaft, yr=yr)
            listings.append({
                "itemId": f"demo-{club['id']}-{i}",
                "title": title,
                "url": "https://www.ebay.com/sch/i.html?_nkw=" + urllib.parse.quote(title),
                "image": "",
                "price": price,
                "shipping": ship,
                "total": round(price + ship, 2),
                "condition": rng.choice(DEMO_CONDITIONS),
                "buyingOption": rng.choice(["FIXED_PRICE", "FIXED_PRICE", "AUCTION"]),
                "flex": "stiff",
                "dexterity": "right",
                "tags": ([str(yr)] if club["id"] == "p770-irons" else []) + (["NEW"] if i < 2 else []),
                "seller": {"username": f"golfer{rng.randint(100, 999)}",
                           "feedbackPct": f"{rng.uniform(97.5, 100):.1f}",
                           "feedbackScore": rng.randint(50, 5000)},
                "endDate": "",
            })
        listings.sort(key=lambda l: l["total"])
        market_median, reference = score_listings(listings, club)
        stats = summarize([l["total"] for l in listings])
        history_lines.append(json.dumps({
            "date": now.strftime("%Y-%m-%d"), "clubId": club["id"], **stats,
        }))
        clubs_out.append({**club_meta(club), "marketMedian": market_median,
                          "reference": reference, "stats": stats, "listings": listings})

    latest = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "demo": True,
        "currency": config.get("currency", "USD"),
        "clubs": clubs_out,
    }
    return latest, history_lines


def club_meta(club):
    return {
        "id": club["id"],
        "label": club["label"],
        "fullName": club["fullName"],
        "retailPrice": club.get("retailPrice"),
        "referenceUsedPrice": club.get("referenceUsedPrice"),
    }


# ------------------------------------------------------------------- main

def main():
    config = load_config()
    demo = "--demo" in sys.argv
    os.makedirs(DATA_DIR, exist_ok=True)
    history_path = os.path.join(DATA_DIR, "history.jsonl")
    seen_path = os.path.join(DATA_DIR, "seen.json")
    latest_path = os.path.join(DATA_DIR, "latest.json")

    if demo:
        latest, history_lines = make_demo_data(config)
        with open(history_path, "w", encoding="utf-8") as f:
            f.write("\n".join(history_lines) + "\n")
        save_json(latest_path, latest)
        print(f"Demo data written to {DATA_DIR} (marked demo=true).")
        return

    token = get_token()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    seen = load_json(seen_path, {})
    clubs_out = []
    history_lines = []

    for club in config["clubs"]:
        raw = search_ebay(token, config["marketplace"], club,
                          config["conditions"], config["currency"])
        listings, ids = [], set()
        for item in raw:
            norm = normalize_item(item, club, config)
            if norm and norm["itemId"] not in ids:
                ids.add(norm["itemId"])
                listings.append(norm)
        listings.sort(key=lambda l: l["total"])

        for l in listings:
            if l["itemId"] not in seen:
                seen[l["itemId"]] = today
                l["tags"].insert(0, "NEW")

        market_median, reference = score_listings(listings, club)
        stats = summarize([l["total"] for l in listings])
        history_lines.append(json.dumps({
            "date": today, "clubId": club["id"], **stats,
        }))
        clubs_out.append({**club_meta(club), "marketMedian": market_median,
                          "reference": reference, "stats": stats, "listings": listings})
        print(f"{club['label']}: {stats['count']} listings"
              + (f", min ${stats['min']}, median ${stats['median']}" if stats["count"] else ""))

    # Append today's stats, replacing any earlier lines from the same day.
    existing = []
    if os.path.exists(history_path):
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if not (rec.get("date") == today):
                    existing.append(line)
    with open(history_path, "w", encoding="utf-8") as f:
        for line in existing + history_lines:
            f.write(line + "\n")

    save_json(seen_path, seen)
    save_json(latest_path, {
        "generatedAt": now.isoformat(timespec="seconds"),
        "demo": False,
        "currency": config.get("currency", "USD"),
        "clubs": clubs_out,
    })
    print(f"Wrote {latest_path}")


if __name__ == "__main__":
    main()
