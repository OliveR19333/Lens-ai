#!/usr/bin/env python3
"""
collect_instagram.py — Official Instagram Graph API hashtag collector.
Zero scraping, zero ban risk. Uses the hashtag search endpoints available
to any IG Business account via a Meta developer app.

Per account per rolling 7 days: 30 unique hashtags MAX (Meta-enforced).
This script tracks usage in hashtag_budget.json and refuses to exceed it.

Env:
    IG_ACCESS_TOKEN   long-lived Page access token from your Meta app
Usage:
    python collect_instagram.py            # collects all verticals
    python collect_instagram.py --flex pooltrends2026   # spend a flex slot
Output:
    data/ig_YYYY-MM-DD.json
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta
from pathlib import Path

BASE = 'https://graph.facebook.com/v21.0'
ROOT = Path(__file__).parent
DATA = ROOT / 'data'; DATA.mkdir(exist_ok=True)
BUDGET_FILE = ROOT / 'hashtag_budget.json'

def api(path, **params):
    params['access_token'] = os.environ['IG_ACCESS_TOKEN']
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def budget():
    b = json.load(open(BUDGET_FILE)) if BUDGET_FILE.exists() else {}
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    return {acct: {tag: ts for tag, ts in tags.items() if ts > cutoff}
            for acct, tags in b.items()}

def collect_account(label, acct, bud):
    ig_id = acct['ig_user_id']
    if 'PUT_IG' in ig_id:
        print(f"  ! {label}: set ig_user_id in config.json — skipping"); return []
    used = bud.setdefault(label, {})
    results = []
    tags = [t for v in acct['verticals'].values() for t in v]
    for tag in tags:
        if tag not in used and len(used) >= 30:
            print(f"  ! {label}: 30-tag weekly budget hit, skipping remaining"); break
        try:
            # 1. hashtag name → hashtag ID
            found = api('ig_hashtag_search', user_id=ig_id, q=tag)['data']
            if not found: continue
            hid = found[0]['id']
            used[tag] = datetime.now().isoformat()
            # 2. top media for that hashtag
            media = api(f'{hid}/top_media', user_id=ig_id,
                        fields='caption,like_count,comments_count,media_type,permalink,timestamp',
                        limit=15)['data']
            for m in media:
                m['hashtag'] = tag
                m['account'] = label
            results.extend(media)
            print(f"  ✓ #{tag}: {len(media)} top posts")
            time.sleep(1)
        except Exception as e:
            print(f"  ! #{tag}: {e}")
    return results

def main():
    cfg = json.load(open(ROOT / 'config.json'))
    bud = budget()
    all_media = []
    for key in ('account_1_build_side', 'account_2_media_market_side'):
        print(f"[{key}]")
        all_media += collect_account(key, cfg[key], bud)
    json.dump(bud, open(BUDGET_FILE, 'w'), indent=2)
    out = DATA / f"ig_{datetime.now():%Y-%m-%d}.json"
    json.dump(all_media, open(out, 'w'), indent=2)
    print(f"{len(all_media)} posts → {out}")

if __name__ == '__main__':
    main()
