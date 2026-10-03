#!/usr/bin/env python3
"""Build a public artifact, releasing approved content only at its timestamp."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
from zoneinfo import ZoneInfo
from build_articles import build

ROOT = Path(__file__).resolve().parents[1]
# Only web content belongs in the deployment, never scripts or release sources.
DIRECTORIES = ('assets', 'aktuelles', 'urbar')
ROOT_SUFFIXES = {'.html', '.xml', '.txt', '.svg', '.png', '.ico'}

def assemble(root, destination, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Build time must include a timezone')
    if destination.exists():
        raise ValueError('Output directory must not already exist')
    destination.mkdir(parents=True)
    for path in root.iterdir():
        if path.is_file() and (path.suffix in ROOT_SUFFIXES or path.name == 'CNAME'):
            shutil.copy2(path, destination / path.name)
    for name in DIRECTORIES:
        shutil.copytree(root / name, destination / name)
    released = []
    for manifest in sorted((root / '_scheduled').glob('*/release.json')):
        release = json.loads(manifest.read_text())
        due = datetime.fromisoformat(release['publish_at'])
        if due.tzinfo is None:
            raise ValueError('Release time must include a timezone')
        if now < due:
            continue
        files = manifest.parent / 'files'
        if not (files / release['article']).is_file():
            raise ValueError('Missing release article')
        for source in sorted(files.rglob('*')):
            if source.is_symlink():
                raise ValueError('Release symlinks are not allowed')
            if source.is_file():
                relative = source.relative_to(files)
                if relative.parts[0] not in DIRECTORIES:
                    raise ValueError('Release outside public directories')
                target = destination / relative
                if target.exists() and target.read_bytes() != source.read_bytes():
                    raise ValueError('Release would overwrite existing content: ' + str(relative))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        released.append(release['article'])
    build(destination, today=now.astimezone(ZoneInfo('Europe/Berlin')).date())
    (destination / '.nojekyll').touch()
    return released

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    # Preview only. Production workflow never sets this option.
    parser.add_argument('--preview-at', type=datetime.fromisoformat)
    args = parser.parse_args()
    print('Released:', assemble(ROOT, args.output.resolve(), args.preview_at))
