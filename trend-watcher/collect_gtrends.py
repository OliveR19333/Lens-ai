#!/usr/bin/env python3
"""
collect_gtrends.py — Google Trends demand signals via pytrends (open source).
This is the BUYING-INTENT side of the watcher: what East Tennessee is
searching for, per TNC vertical, with rising-query detection.

Requires: pip install pytrends
Output:   data/gt_YYYY-MM-DD.json
"""
import json, time
from datetime import datetime
from pathlib import Path
from pytrends.request import TrendReq

ROOT = Path(__file__).parent
DATA = ROOT / 'data'; DATA.mkdir(exist_ok=True)

def main():
    cfg = json.load(open(ROOT / 'config.json'))['google_trends']
    py = TrendReq(hl='en-US', tz=300)  # tz 300 = US Eastern
    out = {'collected': datetime.now().isoformat(), 'geo': cfg['geo'], 'batches': []}

    for batch in cfg['keyword_batches']:
        entry = {'keywords': batch, 'interest': {}, 'rising': {}}
        try:
            py.build_payload(batch, geo=cfg['geo'], timeframe='today 3-m')
            df = py.interest_over_time()
            if not df.empty:
                df = df.drop(columns=['isPartial'], errors='ignore')
                # 4-week momentum: recent mean vs prior mean, per keyword
                recent, prior = df.tail(4).mean(), df.iloc[:-4].mean()
                for kw in batch:
                    if kw in df.columns and prior.get(kw, 0) > 0:
                        entry['interest'][kw] = {
                            'current': round(float(recent[kw]), 1),
                            'momentum_pct': round((float(recent[kw]) / float(prior[kw]) - 1) * 100, 1),
                        }
            # Rising related queries = trend-emergence signal
            for kw, rq in (py.related_queries() or {}).items():
                rising = rq.get('rising') if rq else None
                if rising is not None and not rising.empty:
                    entry['rising'][kw] = rising.head(5)[['query', 'value']].to_dict('records')
        except Exception as e:
            entry['error'] = str(e)
        out['batches'].append(entry)
        print(f"  ✓ {batch[0]}...")
        time.sleep(5)  # be polite; Google throttles aggressive clients

    path = DATA / f"gt_{datetime.now():%Y-%m-%d}.json"
    json.dump(out, open(path, 'w'), indent=2)
    print(f"→ {path}")

if __name__ == '__main__':
    main()
