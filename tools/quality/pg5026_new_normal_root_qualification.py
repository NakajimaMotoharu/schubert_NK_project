"""Freeze exact Root/observer/preflight host inputs before the single new start."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check, checkPath
import pg5022_new_normal_root_once as entry
import pg5024_new_normal_live_binding as binding

NAMES = ['pg5016_new_current_readonly.py', 'pg5018_new_current_same_peer_observer.py',
         'pg5020_current_query_oracle_preflight.py', 'pg5022_new_normal_root_once.py',
         'pg5024_new_normal_live_binding.py', 'pg5026_new_normal_root_qualification.py',
         'pg5026_new_normal_root_test.py', 'pg5014_ssc304_publication_post.py',
         'pg4996_resume_connection.py']


def main():
    os.umask(0o077)
    out = entry.W / entry.QUALIFICATION
    out.mkdir(mode=0o700)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    names = ['pg5026_new_normal_root_test', 'pg4220_same_peer_current_observer_test',
             'pg4216_same_peer_observer_manager_test']
    with (out / 'tests.private.log').open('xb') as log:
        result = subprocess.run(['python3', '-B', '-m', 'unittest', *names], stdout=log, stderr=log)
    if result.returncode:
        raise ValueError('selected independent Root tests failed; no start')
    files = entry.observer.files()
    hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in files.items()}
    raw = entry.payload(hashes)
    emitted = {**files, 'fresh-once.py': raw,
               'live.py': 'SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n' + binding.body()}
    findings = sum(check(v, '<' + n + '>') for n, v in emitted.items())
    paths = [Path('tools/quality') / n for n in NAMES]
    findings += sum(checkPath(str(p)) for p in paths)
    if findings:
        raise ValueError('all host/emitted static0 required')
    value = {'actualExit': 0, 'source': entry.SOURCE, 'files': hashes,
             'freshOnceSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'hostSourceHashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'staticFindings': 0, 'startedUTC': started,
             'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'formalAccepted': False, 'productionPtAdded': 0, 'rootStartIssued': False}
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps({k: v for k, v in value.items() if k != 'hostSourceHashes'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
