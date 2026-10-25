#!/usr/bin/env python3
"""Local preview with a shared 30-minute, demand-driven data cache."""
import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

from update_energy_data import update


class Handler(SimpleHTTPRequestHandler):
    refresh_lock = threading.Lock()

    def do_GET(self):
        if urlsplit(self.path).path == '/assets/data/strom-im-blick.json':
            target = Path(self.directory)/'assets/data/strom-im-blick.json'
            try:
                snapshot = json.loads(target.read_text())
                attempted = datetime.fromisoformat(snapshot.get('attempted_at', snapshot['fetched_at']))
                due = (datetime.now(timezone.utc)-attempted).total_seconds() >= 1800
            except (OSError, ValueError, KeyError):
                due = True
            if due and self.refresh_lock.acquire(blocking=False):
                def refresh():
                    try:
                        update(target)
                    except (OSError, ValueError) as error:
                        print('Energy preview refresh failed: ' + type(error).__name__)
                    finally:
                        self.refresh_lock.release()
                threading.Thread(target=refresh, daemon=True).start()
        super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8875)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(args.directory.resolve())))
    print('Preview: http://127.0.0.1:' + str(args.port) + '/energie/strom-im-blick/', flush=True)
    server.serve_forever()
