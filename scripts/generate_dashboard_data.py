
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 baseline 与 products 目录汇总生成 dashboards/data/*.json
- summary.json
- coverage_trend.json
- high_risk_trend.json
- top_risk_products.json
并维护 dashboards/data/history/*.jsonl
"""
import os, json, datetime
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'baseline' / 'security_baseline.yaml'
PRODUCTS = ROOT / 'products'
DATA_DIR = ROOT / 'dashboards' / 'data'
HIST_DIR = DATA_DIR / 'history'


def yload(p: Path):
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.exists() else {}


def list_products():
    if not PRODUCTS.exists(): return []
    return [d for d in PRODUCTS.iterdir() if d.is_dir() and not d.name.startswith('.')]


def count_controls():
    y = yload(BASELINE)
    return len(y.get('controls', []))


def parse_traceability(pd: Path):
    y = yload(pd / 'traceability.yaml')
    items = y.get('items', [])
    met = sum(1 for it in items if str(it.get('status','')).lower()=='met')
    partial = sum(1 for it in items if str(it.get('status','')).lower()=='partial')
    not_met = sum(1 for it in items if str(it.get('status','')).lower()=='not_met')
    exceptions = []
    for it in items:
        ex = it.get('exception')
        if isinstance(ex, dict) and ex.get('expiry'):
            exceptions.append(ex['expiry'])
    open_high = y.get('open_high', 0)
    status = y.get('overall_status') or ('Green' if not_met==0 else 'Yellow' if partial>0 else 'Red')
    return {'met':met,'partial':partial,'not_met':not_met,'exceptions':exceptions,'open_high':open_high,'status':status}


def days_until(s):
    try:
        dt = datetime.date.fromisoformat(s)
        return (dt - datetime.date.today()).days
    except Exception:
        return None


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HIST_DIR.mkdir(parents=True, exist_ok=True)


def write_json(name, data):
    p = DATA_DIR / name
    p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    print('[ok] write', p)


def append_history(name, value):
    p = HIST_DIR / f'{name}.jsonl'
    rec = {'ts': datetime.datetime.utcnow().isoformat(timespec='seconds')+'Z', 'value': value}
    with p.open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False)+'
')


def load_recent(name, limit=6):
    p = HIST_DIR / f'{name}.jsonl'
    if not p.exists(): return []
    lines = p.read_text(encoding='utf-8').splitlines()[-limit:]
    out = []
    for ln in lines:
        try: out.append(json.loads(ln))
        except Exception: pass
    return out


def main():
    ensure_dirs()
    total_ctrl = count_controls()
    prods = list_products()

    total_products = len(prods)
    cov_values = []
    total_high = 0
    expiring = 0
    top = []

    for pd in prods:
        tr = parse_traceability(pd)
        covered = (tr['met']/total_ctrl*100) if total_ctrl else 0
        cov_values.append(covered)
        total_high += int(tr['open_high'] or 0)
        for ex in tr['exceptions']:
            d = days_until(ex)
            if d is not None and d <= 30:
                expiring += 1
        if tr['open_high'] >= 5:
            risk, color = 'High', '#ef4444'
        elif tr['open_high'] > 0:
            risk, color = 'Medium', '#f59e0b'
        else:
            risk, color = 'Low', '#10b981'
        top.append({
            'product': pd.name,
            'risk': risk,
            'risk_color': color,
            'open_high': int(tr['open_high'] or 0),
            'status': tr['status'],
            'coverage': round(covered, 1)
        })

    avg_cov = round(sum(cov_values)/len(cov_values), 0) if cov_values else 0

    write_json('summary.json', {
        'total_products': total_products,
        'baseline_coverage': int(avg_cov),
        'open_high_risk': int(total_high),
        'expiring_exemptions': int(expiring)
    })

    top.sort(key=lambda x: (-x['open_high'], x['coverage']))
    write_json('top_risk_products.json', {'items': top[:10]})

    append_history('coverage', avg_cov)
    append_history('high_risk', total_high)

    def to_xy(hist):
        labels, values = [], []
        for r in hist:
            ts = r['ts']
            try:
                dt = datetime.datetime.fromisoformat(ts.replace('Z',''))
                labels.append(dt.strftime('%m-%d'))
            except Exception:
                labels.append(ts[:10])
            values.append(r['value'])
        return {'labels': labels, 'values': values}

    write_json('coverage_trend.json', to_xy(load_recent('coverage', 6)))
    write_json('high_risk_trend.json', to_xy(load_recent('high_risk', 6)))

if __name__ == '__main__':
    main()
