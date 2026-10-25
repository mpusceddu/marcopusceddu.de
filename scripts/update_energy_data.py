#!/usr/bin/env python3
"""Fetch shared Energy-Charts snapshots; keep last valid data per endpoint."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'assets/data/strom-im-blick.json'
BERLIN = ZoneInfo('Europe/Berlin')
ENDPOINTS = {'power': ('public_power', 'country', 'de'),
             'flows': ('cbpf', 'country', 'de'),
             'price': ('price', 'bzn', 'DE-LU')}


def validate(data, kind):
    """Reject malformed responses before touching the existing snapshot."""
    times = data.get('unix_seconds')
    if not isinstance(times, list) or not times:
        raise ValueError('No timestamps')
    if any(type(t) is not int for t in times) or times != sorted(set(times)):
        raise ValueError('Timestamps must be unique and increasing')
    if data.get('deprecated'):
        raise ValueError('Endpoint is deprecated; review required')
    if kind == 'price':
        unit = data.get('unit', '').replace(' ', '').lower()
        if unit != 'eur/mwh':
            raise ValueError('Unexpected price unit')
        if 'CC BY 4.0' not in data.get('license_info', '') or 'SMARD' not in data.get('license_info', ''):
            raise ValueError('Price license requires review')
        series = [data.get('price')]
    else:
        collection = data.get('production_types' if kind == 'power' else 'countries')
        if not isinstance(collection, list) or not collection:
            raise ValueError('No series')
        names = [s.get('name') for s in collection]
        if any(not isinstance(n, str) for n in names) or len(names) != len(set(names)):
            raise ValueError('Invalid series names')
        if kind == 'power' and not {'Solar', 'Wind onshore', 'Renewable share of generation'}.issubset(names):
            raise ValueError('Required power series missing')
        series = [s.get('data') for s in collection]
    for values in series:
        if not isinstance(values, list) or len(values) != len(times):
            raise ValueError('Mismatched time and value lengths')
        if any(v is not None and (type(v) not in (int, float) or not math.isfinite(v)) for v in values):
            raise ValueError('Invalid numeric value')
    if not any(v is not None for values in series for v in values):
        raise ValueError('No actual values')
    return data


def fetch(url):
    request = Request(url, headers={'User-Agent': 'marcopusceddu.de energy dashboard; cached 30min', 'Accept': 'application/json'})
    with urlopen(request, timeout=25) as response:
        return json.load(response)


def split_tomorrow(price, today):
    tomorrow = (today + timedelta(days=1)).isoformat()
    selected = [i for i, t in enumerate(price['unix_seconds'])
                if datetime.fromtimestamp(t, BERLIN).date().isoformat() == tomorrow]
    return {**price, 'unix_seconds': [price['unix_seconds'][i] for i in selected],
            'price': [price['price'][i] for i in selected]}


def update(target=TARGET, now=None, fetcher=fetch):
    now = now or datetime.now(timezone.utc)
    today = now.astimezone(BERLIN).date()
    stamp = now.isoformat()
    old = json.loads(target.read_text()) if target.exists() else {}
    result = {**old, 'attempted_at': stamp, 'updated_at': dict(old.get('updated_at', {})), 'fetch_errors': {}}
    successes = 0
    for kind, (endpoint, parameter, value) in ENDPOINTS.items():
        end = today + timedelta(days=1) if kind == 'price' else today
        query = urlencode({parameter: value, 'start': (today-timedelta(days=6)).isoformat(), 'end': end.isoformat()})
        try:
            retry_at = result.get('retry_after', {}).get(kind)
            if retry_at and datetime.fromisoformat(retry_at) > now:
                raise ValueError('Upstream requested a longer pause')
            candidate = validate(fetcher('https://api.energy-charts.info/' + endpoint + '?' + query), kind)
            # An upstream regression must not silently discard more recent valid observations.
            previous = old.get(kind, {}).get('unix_seconds', [])
            if previous and candidate['unix_seconds'][-1] < previous[-1]:
                raise ValueError('Response older than saved data')
            result[kind] = candidate
            result['updated_at'][kind] = stamp
            result.get('retry_after', {}).pop(kind, None)
            successes += 1
        except (OSError, ValueError, KeyError, TypeError) as error:
            # Do not retry during this run. Respect Retry-After on rate limiting.
            message = 'Abruf fehlgeschlagen; letzter gültiger Stand bleibt erhalten.'
            if isinstance(error, HTTPError) and error.code == 429:
                message = 'Datenquelle begrenzt Abrufe; erneuter Versuch beim nächsten Lauf.'
                retry = error.headers.get('Retry-After', '')
                if retry.isdigit():
                    result.setdefault('retry_after', {})[kind] = (now+timedelta(seconds=int(retry))).isoformat()
            result['fetch_errors'][kind] = message
            print(kind + ': ' + message)
    if not all(k in result for k in ENDPOINTS):
        raise ValueError('No complete initial snapshot; existing file preserved')
    for key in ENDPOINTS:
        validate(result[key], key)
    result['tomorrow'] = split_tomorrow(result['price'], today)
    if successes:
        result['fetched_at'] = stamp
    target.parent.mkdir(parents=True, exist_ok=True)
    # Replace atomically, so readers never receive half-written JSON.
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent, delete=False) as handle:
        json.dump(result, handle, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        temporary = Path(handle.name)
    temporary.replace(target)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=TARGET)
    args = parser.parse_args()
    state = update(args.output.resolve())
    print('Energy snapshot ready; failed endpoints: ' + str(len(state['fetch_errors'])))
