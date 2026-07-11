#!/usr/bin/env python3
"""
make_digest.py — Claude API synthesis: raw signals → Monday operator digest.
Answers four questions per vertical: what's rising, what's fading,
what should TNC post this week, what does it signal for demand.

Env:  ANTHROPIC_API_KEY
Requires: pip install anthropic
Usage:
    python make_digest.py            # builds digest from latest data files
    python make_digest.py --email    # also emails it (uses SMTP_* env vars)
Output: digests/digest_YYYY-MM-DD.md
"""
import argparse, glob, json, os, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent
DIGESTS = ROOT / 'digests'; DIGESTS.mkdir(exist_ok=True)

PROMPT = """You are the trend analyst for Teaster's Natural Creations (TNC), an East Tennessee
property company: pools, hardscape, landscape, waterscapes, construction, drone media
(TNC GAS), web design (TNC Digital), and STR/housing-market awareness.

Below is this week's raw signal data:
- INSTAGRAM: top posts per tracked hashtag (engagement = like/comment counts)
- GOOGLE TRENDS: Tennessee search interest with 4-week momentum % and rising queries

<instagram_data>
{ig}
</instagram_data>

<google_trends_data>
{gt}
</google_trends_data>

Write the TNC MONDAY TREND DIGEST in markdown. Rules:
- Only claim what the data shows. If a vertical has thin/no data this week, say so in one line.
- Be an operator, not a reporter: every insight ends in something TNC can DO.
- Keep it tight — this is read on a phone Monday morning.

Structure:
# TNC Trend Digest — {date}
## 🔥 Top Signal of the Week  (the single most actionable thing across all data)
## Per Vertical  (pools/hardscape · landscape/waterscape · drone media · web design · STR/housing · construction)
For each: **Rising:** / **Fading:** / **Post this week:** (one concrete content idea for TNC channels) / **Demand read:** (one sentence)
## 📰 Builder Brief Fodder  (2-3 items worth expanding in the newsletter)
## Flex-Slot Suggestions  (hashtags worth spending next week's flex slots on, based on rising queries)"""

def latest(pattern):
    files = sorted(glob.glob(str(ROOT / 'data' / pattern)))
    return json.load(open(files[-1])) if files else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--email', action='store_true')
    args = ap.parse_args()

    ig, gt = latest('ig_*.json'), latest('gt_*.json')
    if not ig and not gt:
        raise SystemExit('No data files — run the collectors first.')

    # Trim IG data to what matters (caption snippets + engagement) to keep tokens sane
    ig_slim = [{'tag': m.get('hashtag'), 'likes': m.get('like_count'),
                'comments': m.get('comments_count'),
                'caption': (m.get('caption') or '')[:200]} for m in (ig or [])]

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model='claude-sonnet-4-5', max_tokens=3000,
        messages=[{'role': 'user', 'content': PROMPT.format(
            ig=json.dumps(ig_slim)[:60000], gt=json.dumps(gt)[:30000],
            date=f"{datetime.now():%B %d, %Y}")}])
    digest = msg.content[0].text

    out = DIGESTS / f"digest_{datetime.now():%Y-%m-%d}.md"
    out.write_text(digest)
    print(f"→ {out}")

    if args.email:
        cfg = json.load(open(ROOT / 'config.json'))['digest']
        m = MIMEText(digest, 'plain')
        m['Subject'] = f"TNC Trend Digest — {datetime.now():%b %d}"
        m['From'] = os.environ['FROM_EMAIL']
        m['To'] = ', '.join(cfg['recipients'])
        with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ.get('SMTP_PORT', 587))) as s:
            s.starttls(); s.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
            s.send_message(m)
        print(f"emailed → {m['To']}")

if __name__ == '__main__':
    main()
