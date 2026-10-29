"""Refine parish pins in parish_data.xlsx.

Usage:
  python geocode.py parish_data.xlsx --google YOUR_API_KEY   # recommended: exact church pins from Google
  python geocode.py parish_data.xlsx                           # free: OpenStreetMap, only rows with no pin
Needs:  pip install openpyxl   (and an internet connection)

Google mode looks up "<parish name>, <address>" with the Google Geocoding API for
every row that is not already "verified" and replaces the pin when Google finds the
church itself (or a nearby street address). It skips Google answers that are only a
whole town or pincode, or more than 30 km from the current pin, since those are
likely the wrong place. Updated rows get geo_precision = "exact" (or "post_office"
precision is kept) and stay "approximate" until a person checks them.
Google gives a monthly free allowance that easily covers ~600 lookups; you need a
Google Cloud project with the Geocoding API enabled and billing set up.

OpenStreetMap mode only fills rows that have no pin at all (1 request per second).
Progress is saved every 25 rows, so you can stop and re-run safely.
"""
import json, math, sys, time, urllib.parse, urllib.request
from openpyxl import load_workbook

UA = 'ParishConnect-ParishFinder/1.0 (contact: replace-with-your-email@example.com)'
GOOD_GOOGLE_TYPES = {'church', 'place_of_worship', 'establishment', 'point_of_interest', 'premise', 'street_address', 'route'}


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def google(query, key):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.parse.urlencode(
        {'address': query, 'region': 'in', 'components': 'country:IN', 'key': key})
    d = get(url)
    if d.get('status') == 'REQUEST_DENIED':
        sys.exit('Google refused the key: ' + d.get('error_message', ''))
    if not d.get('results'):
        return None
    r = d['results'][0]
    if r.get('partial_match') and not (set(r['types']) & {'church', 'place_of_worship', 'establishment'}):
        return None
    if not (set(r['types']) & GOOD_GOOGLE_TYPES):
        return None
    loc = r['geometry']['location']
    return loc['lat'], loc['lng']


def osm(**params):
    params.update(format='json', limit=1, countrycodes='in')
    time.sleep(1.1)
    hits = get('https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(params))
    return (float(hits[0]['lat']), float(hits[0]['lon'])) if hits else None


def km(a, b):
    return 111 * math.hypot(a[0] - b[0], (a[1] - b[1]) * math.cos(math.radians(a[0])))


def main(path, key=None):
    wb = load_workbook(path)
    ws = wb['Parishes']
    col = {c.value: c.column for c in ws[1]}
    done = 0
    for r in range(2, ws.max_row + 1):
        g = lambda k: str(ws.cell(r, col[k]).value or '').strip()
        if not g('parish_id') or g('geo_status') == 'verified':
            continue
        has_pin = bool(g('latitude'))
        hit = None
        try:
            if key:
                hit = google(f"{g('name')}, {g('address') or g('locality')}, {g('district')}, {g('state')} {g('pincode')}", key)
                if hit and has_pin and km(hit, (float(g('latitude')), float(g('longitude')))) > 30:
                    print(f"{g('parish_id')}: Google answer is far from current pin, kept current. Please check manually.")
                    hit = None
            elif not has_pin:
                for a in (dict(q=f"{g('name')}, {g('address')}, {g('state')}"),
                          dict(q=', '.join(x for x in [g('locality'), g('district'), g('state'), g('pincode')] if x)),
                          dict(postalcode=g('pincode')) if g('pincode') else None):
                    if a and (hit := osm(**a)):
                        break
            else:
                continue
        except Exception as e:
            print('  network error:', e); time.sleep(5)
        if hit:
            ws.cell(r, col['latitude']).value = round(hit[0], 6)
            ws.cell(r, col['longitude']).value = round(hit[1], 6)
            ws.cell(r, col['geo_status']).value = 'approximate'
            ws.cell(r, col['geo_precision']).value = 'exact' if key else 'locality'
        print(f"{g('parish_id')}: {'%.5f, %.5f' % hit if hit else 'no better match'}")
        done += 1
        if done % 25 == 0:
            wb.save(path)
    wb.save(path)
    print('Saved. Open the workbook in Excel so the map links refresh.')


if __name__ == '__main__':
    args = sys.argv[1:]
    key = args[args.index('--google') + 1] if '--google' in args else None
    path = next((a for a in args if a.endswith('.xlsx')), 'parish_data.xlsx')
    main(path, key)
