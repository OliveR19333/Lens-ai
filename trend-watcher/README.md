# TNC TREND WATCHER
Weekly trend intelligence across TNC's revenue verticals. Official APIs only — zero scraping, zero account risk.

## What it does
- **collect_instagram.py** — Instagram Graph API hashtag search (top posts + engagement) across two IG Business accounts = 60 hashtags/week. Tracks the Meta-enforced 30-tag rolling budget per account in hashtag_budget.json and refuses to overspend it.
- **collect_gtrends.py** — Google Trends (pytrends) for Tennessee buying-intent: search interest, 4-week momentum, rising queries per vertical.
- **make_digest.py** — Claude API turns raw signals into the Monday operator digest: rising/fading per vertical, one concrete post idea each, demand reads, Builder Brief fodder, and flex-slot hashtag suggestions for next week.

## Setup (after the FB Pages + IG Business accounts are linked)
1. developers.facebook.com → create app → add Instagram Graph API product
2. Connect both IG accounts; generate a long-lived access token
3. Find each account's IG User ID (Graph Explorer: me/accounts → page → instagram_business_account) and drop them into config.json
4. `pip install pytrends anthropic`
5. Env: IG_ACCESS_TOKEN, ANTHROPIC_API_KEY (+ SMTP_* / FROM_EMAIL if emailing)
6. Edit digest recipients in config.json

## Run weekly (cron on the VPS, Sunday night)
    0 21 * * 0  cd /app && python collect_instagram.py && python collect_gtrends.py && python make_digest.py --email

## Notes
- Hashtag budget: 30/account/rolling-7-days, enforced by Meta and by this code. Locked lists in config.json + 3 flex slots each. Querying a tag spends it for the week even if you delete it after.
- TikTok Creative Center publishes trend data publicly but has no official API — check it manually monthly, or we add a collector later if it earns it.
- Digest doubles as Builder Brief source material — the "Builder Brief Fodder" section is written for direct expansion into newsletter items.
