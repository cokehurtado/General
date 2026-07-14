# ⛳ Golf Club Second-Hand Tracker

Tracks the used market for a specific dream bag and tells you when to pounce:

| Club | Spec | Retail (new) | Reference used price* |
|---|---|---|---|
| **TaylorMade P770 irons** | stiff shaft, RH | ~$1,399 | $1,000 |
| **TaylorMade Qi4D driver** | stiff shaft, RH | $649.99 | $520 |
| **TaylorMade Qi4D 3 wood** | stiff shaft, RH | $379.99 | $300 |

\* Editable in [`config.json`](config.json) — tune these as the market moves.
The Qi4D line launched in January 2026, so used supply is thin and prices
should keep dropping through the season; that's exactly what the history
chart is for.

## What it does

- **Collects** used & refurbished listings from the **official eBay Browse API**
  (price + shipping = true cost), twice a day via GitHub Actions or on demand.
- **Filters out the junk**: left-handed, ladies/senior/regular flex, single
  irons, heads only, shaft-only, headcovers, and lookalike models (P790, Qi10,
  Qi35, 5-woods…). Listings that don't state a flex are kept but tagged `flex?`
  so you can check them manually.
- **Scores every listing** against a reference price (the lower of the current
  market median and your configured baseline):
  - 🟢 **Great deal** — ≥15% below reference
  - 🟢 **Good price** — 5–15% below
  - ⚪ **Fair price** — within ±5%
  - 🟠 **Above market** — >5% over
- **Tracks history** (min / p25 / median per day) and flags listings it has
  never seen before with a **NEW** badge — fresh underpriced listings are where
  the bargains are.
- **Dashboard** with best-price tiles, a 90-day price trend chart (light & dark
  mode), and sortable listing tables linking straight to eBay.

## Setup (one time, ~5 minutes)

1. **Get free eBay API keys**: sign up at
   [developer.ebay.com](https://developer.ebay.com), create an application, and
   copy the **production** keyset — the *App ID* is your client id, the
   *Cert ID* is your client secret. (The free tier allows 5,000 calls/day;
   this tracker uses ~6/day.)
2. **For automatic tracking** — add the keys as repository secrets
   (`Settings → Secrets and variables → Actions`):
   - `EBAY_CLIENT_ID`
   - `EBAY_CLIENT_SECRET`

   The [workflow](../.github/workflows/golf-club-tracker.yml) then runs twice a
   day and commits fresh data. You can also trigger it manually from the
   Actions tab (*Golf Club Tracker → Run workflow*).
3. **For local runs**:

   ```bash
   export EBAY_CLIENT_ID="your-app-id"
   export EBAY_CLIENT_SECRET="your-cert-id"
   python3 golf-club-tracker/tracker.py
   ```

   No Python dependencies — standard library only.

## Viewing the dashboard

From the repo root (uses the existing zero-dependency server):

```bash
npm start
# → open http://localhost:8080/golf-club-tracker/
```

or `python3 -m http.server 8080` and open the same path. (Opening
`index.html` via `file://` won't work — the dashboard fetches JSON.)

Want a preview before wiring up API keys?

```bash
python3 golf-club-tracker/tracker.py --demo
```

generates clearly-labeled simulated data so you can see the dashboard working.
The first real run overwrites it.

## Tuning

Everything lives in [`config.json`](config.json):

- `referenceUsedPrice` — what *you* consider a fair used price; deal ratings are
  relative to this (or the live market median, whichever is lower).
- `priceRange` — hard bounds that pre-filter obvious accessories/scams.
- `acceptFlex` — default `["stiff", "unknown"]`; set to `["stiff"]` to hide
  listings that don't state a flex.
- `excludeKeywords` / `extraExcludeKeywords` — title words that disqualify a
  listing.
- `dexterity` — set to `"right"` (default) to drop left-handed listings.

## Files

```
golf-club-tracker/
  config.json        what to track + filters + reference prices
  tracker.py         collector: eBay Browse API → filtered, scored JSON
  index.html         dashboard
  assets/            dashboard styles + logic (no dependencies)
  data/latest.json   current scored snapshot (committed by the workflow)
  data/history.jsonl daily min/p25/median per club
  data/seen.json     first-seen dates (powers the NEW badge)
```

## Buying tips baked into the data

- **Total cost** = price + shipping; sorting and scoring always use the total.
- **Auctions** are tagged — a low "current price" on an auction isn't a deal yet.
- Watch the **NEW badge + Great deal combo**: well-priced listings of in-demand
  clubs (especially the Qi4D) tend to sell within hours.
- The P770 has several generations (2020/2023/2024 — the year tag is extracted
  from the title). The 2024 model holds ~$1,000+ used; a 2023 set in good shape
  around $750–850 is strong value if you don't need the latest.
