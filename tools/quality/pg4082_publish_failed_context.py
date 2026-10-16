"""Publish safe failed-parent/profile input metadata; raw journal, FD tables and DB stay private."""
import datetime
import hashlib
import json
import os
from pathlib import Path
from pg1446_current_cold_stage import W

ROOT = Path(__file__).resolve().parents[2]
SLOTS = ['pg4068-peer-read-profile-v1', 'pg4070-failed-root-resource-read-v1',
         'pg4072-failed-parent-pid1-read-v1', 'pg4076-failed-done-parent-read-v1',
         'pg4080-failed-ordinary-full-capture-v1']


def main():
    os.umask(0o022); out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4082-failed-done-context-v1'; out.mkdir()
    files = {}
    for slot in SLOTS:
        raw = (W / slot / 'manifest.safe.json').read_bytes(); data = json.loads(raw)
        if data['actualExit'] != 0 or data['source'] != '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e':
            raise ValueError('actual same-source read results required')
        # These result contracts contain only counters, fixed systemd identity and digests.
        # No observed.private.json, journal MESSAGE, FD map, DB row or credential is read here.
        result = dict(data['result'])
        for k in ['compileCommand', 'profileCommand']: result.pop(k, None)
        p = out / (slot + '.json'); p.write_text(json.dumps({'actualExit': 0, 'source': data['source'],
            'payloadSha256': data['payloadSha256'], 'originalManifestSha256': hashlib.sha256(raw).hexdigest(),
            'result': result}, ensure_ascii=False, indent=2) + '\n'); files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = {'source': data['source'], 'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'files': files, 'parentNormal': False, 'recoveryAuthorityIssued': False,
                'stopIssued': False, 'formalAccepted': False, 'productionPtAdded': 0}
    p = out / 'manifest.json'; p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'readResults': len(files)}))


if __name__ == '__main__': main()
