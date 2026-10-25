import copy
from datetime import datetime, timedelta, timezone
from email.message import Message
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError

SPEC = importlib.util.spec_from_file_location('update_energy_data', Path(__file__).resolve().parents[1]/'scripts/update_energy_data.py')
energy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(energy)
NOW = datetime(2026, 10, 25, 17, 0, tzinfo=timezone.utc)
T = int(NOW.timestamp())


def fixture():
    power = {'unix_seconds': [T-900, T], 'production_types': [
        {'name': n, 'data': [v, v]} for n, v in [('Solar', 1000), ('Wind onshore', 2000), ('Renewable share of generation', 75)]], 'deprecated': False}
    flows = {'unix_seconds': [T-900, T], 'countries': [{'name': 'France', 'data': [2, -1]}], 'deprecated': False}
    price = {'unix_seconds': [T, T+86400], 'price': [50, -10], 'unit': 'EUR / MWh', 'license_info': 'CC BY 4.0 from Bundesnetzagentur | SMARD.de', 'deprecated': False}
    return {'power': power, 'flows': flows, 'price': price, 'tomorrow': energy.split_tomorrow(price, NOW.astimezone(energy.BERLIN).date()), 'fetched_at': NOW.isoformat()}


class EnergyDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'data.json'
        self.old = fixture()
        self.path.write_text(json.dumps(self.old))

    def fetcher(self, url):
        kind = 'power' if '/public_power?' in url else 'flows' if '/cbpf?' in url else 'price'
        return copy.deepcopy(self.old[kind])

    def test_successful_refresh_preserves_units_and_negative_prices(self):
        result = energy.update(self.path, NOW, self.fetcher)
        self.assertFalse(result['fetch_errors'])
        self.assertEqual(result['tomorrow']['price'], [-10])
        self.assertEqual(set(result['updated_at']), {'power', 'flows', 'price'})
        self.assertEqual(json.loads(self.path.read_text()), result)

    def test_outage_keeps_last_valid_snapshot(self):
        def offline(url):
            raise OSError('offline')
        result = energy.update(self.path, NOW+timedelta(hours=1), offline)
        for key in energy.ENDPOINTS:
            self.assertEqual(result[key], self.old[key])
        self.assertEqual(result['fetched_at'], self.old['fetched_at'])
        self.assertEqual(len(result['fetch_errors']), 3)

    def test_partial_outage_only_replaces_successful_endpoints(self):
        def partial(url):
            if '/cbpf?' in url:
                raise OSError('offline')
            return self.fetcher(url)
        result = energy.update(self.path, NOW, partial)
        self.assertEqual(result['flows'], self.old['flows'])
        self.assertEqual(set(result['fetch_errors']), {'flows'})
        self.assertEqual(set(result['updated_at']), {'power', 'price'})

    def test_rate_limit_persists_pause_for_next_run(self):
        calls = []
        def limited(url):
            calls.append(url)
            headers = Message()
            headers['Retry-After'] = '7200'
            raise HTTPError(url, 429, 'limited', headers, None)
        energy.update(self.path, NOW, limited)
        result = energy.update(self.path, NOW+timedelta(minutes=30), limited)
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(result['fetch_errors']), 3)

    def test_invalid_license_and_units_are_rejected(self):
        for change in [{'unit':'ct/kWh'}, {'license_info':'private use only'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                energy.validate({**self.old['price'], **change}, 'price')

    def test_null_is_missing_not_zero_and_bad_values_are_rejected(self):
        candidate = copy.deepcopy(self.old['price'])
        candidate['price'][0] = None
        self.assertIsNone(energy.validate(candidate, 'price')['price'][0])
        for value in [float('nan'), float('inf'), '1', True]:
            candidate['price'][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                energy.validate(candidate, 'price')

    def test_mismatched_and_duplicate_timestamps_are_rejected(self):
        for changes in [{'price':[1]}, {'unix_seconds':[T,T]}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                energy.validate({**self.old['price'], **changes}, 'price')

    def test_older_response_does_not_overwrite_newer_data(self):
        def older(url):
            value = self.fetcher(url)
            value['unix_seconds'] = [t-86400 for t in value['unix_seconds']]
            return value
        result = energy.update(self.path, NOW, older)
        self.assertEqual(result['price'], self.old['price'])
        self.assertEqual(len(result['fetch_errors']), 3)

    def test_failed_initial_refresh_leaves_no_partial_file(self):
        self.path.unlink()
        def offline(url):
            raise OSError('offline')
        with self.assertRaises(ValueError):
            energy.update(self.path, NOW, offline)
        self.assertFalse(self.path.exists())

    def test_tomorrow_uses_berlin_calendar_across_dst(self):
        # 25 October has 25 hours. Date selection must not be now + 24 hours.
        start = int(datetime(2026,10,25,tzinfo=energy.BERLIN).timestamp())
        prices = {**self.old['price'], 'unix_seconds':[start+i*900 for i in range(196)], 'price':[1]*196}
        result = energy.split_tomorrow(prices, datetime(2026,10,24).date())
        self.assertEqual(len(result['price']), 100)


if __name__ == '__main__':
    unittest.main()
