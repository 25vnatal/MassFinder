"""Build parishes.json for the Parish Finder app from parish_data.xlsx.

Usage:  python build_json.py parish_data.xlsx parishes.json
Needs:  pip install openpyxl

The script stops with a list of problems if it finds bad days, times or parish_ids.
"""
import json, re, sys, datetime
from openpyxl import load_workbook

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def rows(ws):
    it = ws.iter_rows(values_only=True)
    header = [h for h in next(it)]
    for r in it:
        d = {h: ('' if v is None else str(v).strip()) for h, v in zip(header, r) if h}
        if any(d.values()):
            yield d


def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None


def split(v, sep=r'[;,]'):
    return [x.strip() for x in re.split(sep, v) if x.strip()] if v else []


def main(src, dst):
    wb = load_workbook(src, data_only=True)
    parishes, problems, ids = [], [], set()

    for p in rows(wb['Parishes']):
        pid = p.get('parish_id', '')
        if not pid:
            problems.append(f"Parishes: row for '{p.get('name')}' has no parish_id"); continue
        if pid in ids:
            problems.append(f'Parishes: duplicate parish_id {pid}')
        ids.add(pid)
        lat, lng = num(p.get('latitude')), num(p.get('longitude'))
        if (lat is None) != (lng is None) or (lat is not None and not (6 <= lat <= 37 and 68 <= lng <= 98)):
            problems.append(f'Parishes: {pid} has an incomplete or out-of-India location ({lat}, {lng})')
            lat = lng = None
        parishes.append({
            'id': pid,
            'name': p.get('name', ''),
            'patron': p.get('patron') or None,
            'feast_day': p.get('feast_day') or None,
            'diocese': {'code': p.get('diocese_code', ''), 'name': p.get('diocese', '')},
            'deanery': p.get('deanery') or None,
            'rite': p.get('rite') or 'Latin',
            'address': {
                'line': p.get('address', ''),
                'locality': p.get('locality') or None,
                'city': p.get('city') or None,
                'district': p.get('district') or None,
                'state': p.get('state') or None,
                'pincode': (p.get('pincode') or '').replace('.0', '') or None,
            },
            'geo': {'lat': lat, 'lng': lng,
                    'status': p.get('geo_status') or 'approximate',
                    'precision': p.get('geo_precision') or None} if lat is not None else
                   {'lat': None, 'lng': None, 'status': 'pending', 'precision': None},
            'contact': {
                'phones': split(p.get('phone', ''), r';'),
                'email': p.get('email') or None,
                'website': p.get('website') or None,
            },
            'established': num(p.get('year_established')),
            'catholics': num(p.get('catholics')) or p.get('catholics') or None,
            'languages': split(p.get('languages', '')),
            'masses': [],
        })

    by_id = {p['id']: p for p in parishes}
    for m in rows(wb['Masses']):
        pid, mid = m.get('parish_id', ''), m.get('mass_id', '')
        if not pid and not mid:
            continue
        where = f'Masses: {mid or "(no mass_id)"}'
        if pid not in ids:
            problems.append(f'{where} points to unknown parish_id "{pid}"'); continue
        day, t = m.get('day', '').title(), m.get('time', '')
        if re.fullmatch(r'\d{1,2}:\d{2}:\d{2}', t):
            t = t[:5]  # Excel turned it into a time value
        if day not in DAYS:
            problems.append(f'{where} has day "{day}"')
        if not re.fullmatch(r'([01]?\d|2[0-3]):[0-5]\d', t):
            problems.append(f'{where} has time "{t}" (use 24-hour HH:MM)')
        if pid not in by_id:
            continue  # parish marked inactive
        by_id[pid]['masses'].append({
            'id': mid,
            'day': day,
            'time': t.zfill(5),
            'type': m.get('type') or 'Mass',
            'languages': split(m.get('language', '')),
            'venue': m.get('venue') or None,
            'recurrence': m.get('recurrence') or 'Weekly',
            'notes': m.get('notes') or None,
        })

    for p in parishes:
        p['masses'].sort(key=lambda x: (DAYS.index(x['day']) if x['day'] in DAYS else 9, x['time']))
        langs = {l for x in p['masses'] for l in x['languages']} | set(p['languages'])
        p['languages'] = sorted(langs)

    if problems:
        print(f'{len(problems)} problem(s) found. Fix these in the workbook and run again:')
        for x in problems:
            print('  -', x)
        sys.exit(1)

    dioceses = {}
    for p in parishes:
        d = dioceses.setdefault(p['diocese']['code'], {**p['diocese'], 'rite': p['rite'], 'parish_count': 0})
        d['parish_count'] += 1

    out = {
        'meta': {
            'schema_version': 1,
            'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
            'parish_count': len(parishes),
            'mass_count': sum(len(p['masses']) for p in parishes),
            'with_location': sum(p['geo']['lat'] is not None for p in parishes),
            'with_masses': sum(bool(p['masses']) for p in parishes),
        },
        'dioceses': sorted(dioceses.values(), key=lambda d: d['name']),
        'parishes': parishes,
    }
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out['meta'], indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'parish_data.xlsx',
         sys.argv[2] if len(sys.argv) > 2 else 'parishes.json')
