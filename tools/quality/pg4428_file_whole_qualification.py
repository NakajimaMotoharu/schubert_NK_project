"""Transfer original independent payload bytes, never re-run the whole job."""
import hashlib
import json
import os
from lan_server import copy, run
from pg4420_shared_manager_full import SOURCE, W


def command(path):
    expected = '/home/mini/schubert-nk-pgpt/transfer/PG4428-whole-qualified-v1/qualify.private.py'
    if path != expected:
        raise ValueError('one fixed qualification artifact')
    result = 'python3 -B ' + path
    if len(result.encode()) >= 256:
        raise ValueError('bounded command; no source map in argv')
    return result


def main():
    original = json.loads((W / 'pg4420-shared-manager-six-v1/manifest.safe.json').read_bytes())
    if original['actualExit'] != 0 or original['source'] != SOURCE:
        raise ValueError('genuine original whole first')
    payload = W / 'pg4422-shared-manager-whole-qualified-v1/qualify.private.py'
    raw = payload.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
    from pyflakes.api import check
    if check(raw.decode(), '<original independent payload>'):
        raise ValueError('all original emitted static0')
    os.umask(0o077); out = W / 'pg4428-shared-manager-whole-qualified-v1'; out.mkdir(mode=0o700)
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG4428-whole-qualified-v1'
    status, _ = run('mkdir -m700 ' + destination, timeout=30)
    if status: raise ValueError('new-only payload namespace')
    status, _ = copy(payload, destination + '/', timeout=60)
    if status: raise ValueError('original payload transfer')
    path = destination + '/qualify.private.py'
    status, value = run('sha256sum ' + path, timeout=30)
    if status or value.split()[0] != digest: raise ValueError('exact original transferred bytes')
    (out / 'begin.safe.json').write_text(json.dumps({'source': SOURCE, 'originalPayloadSha256': digest,
        'payloadBytes': len(raw), 'remoteCommand': command(path), 'remoteStarted': False, 'wholeReplay': False}, sort_keys=True))
    status, output = run(command(path), timeout=180)
    (out / 'observer.private.log').write_text(output)
    result = {'actualExit': status, 'source': SOURCE, 'payloadSha256': digest, 'original4422RemoteStarted': False,
              'originalWholeReplayed': False, 'formalAccepted': False}
    if status == 0:
        result['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps({k: v for k, v in result.items() if k != 'result'}))
    if status == 0:
        print(json.dumps({k: result['result'][k] for k in ['tests', 'suites', 'mainClasses', 'staticSixModules', 'unchangedPhysicalClasses', 'global100', 'F03Accepted']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
