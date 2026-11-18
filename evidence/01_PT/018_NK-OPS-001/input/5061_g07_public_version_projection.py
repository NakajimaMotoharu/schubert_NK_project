"""Build a bounded G07 projection from fixed tracked Git blobs only."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys

ROOT = Path.cwd()
SAFE_PREFIXES = (b'documents/', b'evidence/01_PT/018_NK-OPS-001/', b'src/', b'tools/quality/')
HELD = {'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
BASE = 'a59658c630ec319c50675f3e98e39735c1ac0243'
HEAD = 'de715616216bd3ccc42f3dd38e7388b71eac7d63'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    work = Path(sys.argv[1])
    assert work.is_absolute() and work.is_dir() and not any(work.iterdir())
    history = git('rev-list', '--reverse', BASE + '..' + HEAD).decode().splitlines()
    assert history and history[-1] == HEAD
    by_blob_path = {}
    for rev in history:
        changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', '--diff-filter=ACM', '-z', rev)
        for path_raw in changed.split(b'\0'):
            if not path_raw:
                continue
            path = path_raw.decode()
            assert path_raw.startswith(SAFE_PREFIXES) and Path(path).name not in HELD
            entry = git('ls-tree', '-z', rev, '--', path)
            meta, name = entry.removesuffix(b'\0').split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            assert kind == 'blob' and mode in ('100644', '100755') and name == path_raw
            by_blob_path.setdefault((path, blob), rev)
    projection = work / 'text'
    binaries = work / 'binary'
    projection.mkdir()
    binaries.mkdir()
    rows = []
    for (path, blob), rev in sorted(by_blob_path.items()):
        raw = git('cat-file', 'blob', blob)
        candidate = raw
        name = Path(path).name
        packed = Path(path).suffix == '.gz'
        if packed:
            candidate = gzip.decompress(raw)
            name = name.removesuffix('.gz')
        assert len(candidate) < 32 * 1024 * 1024
        try:
            candidate.decode('utf-8')
            text = b'\0' not in candidate
        except UnicodeDecodeError:
            text = False
        index = (projection if text else binaries) / f'{len(rows)+1:04}' / name
        index.parent.mkdir()
        index.write_bytes(candidate)
        rows.append({'path': path, 'blob': blob, 'firstCommit': rev, 'rawSha256': sha(raw),
                     'decodedSha256': sha(candidate), 'prefix': str(index.relative_to(work)),
                     'text': text, 'losslessGzipExpanded': packed})
    manifest = {'createdAtUTC': datetime.now(timezone.utc).isoformat(), 'from': BASE, 'to': HEAD,
                'commits': history, 'versions': rows, 'notTrackedFilesRead': 0}
    (work / 'projection.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(len(history), len(rows), sum(x['text'] for x in rows), sum(x['losslessGzipExpanded'] for x in rows))


if __name__ == '__main__':
    main()
