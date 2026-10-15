"""Independently qualify original Protocol85 XML/input/member hashes, no rerun."""
import ast
import hashlib
import json
import os

from lan_server import run
import pg3270_header_protocol_independent as previous
from pg3274_header_group_full_six import SOURCE, W


def server():
    raw = previous.SERVER.replace('PG3266-v1', 'PG3298-v1').replace('PG3248', 'PG3274').replace('PG3270-independent-header-v1', 'PG3300-independent-directional-v1')
    raw = raw.replace("d['tests']==84", "d['tests']==85").replace("'tests':84", "'tests':85").replace("'originalWrapperExit':1", "'originalWrapperExit':0")
    marker = "require(len(cases)==len(set(cases))==d['tests']==85)"
    if raw.count(marker) != 1:
        raise ValueError('one independently enumerated case boundary required')
    raw = raw.replace(marker, marker + "\nrequire(('dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest','allNamedTypesHaveIndependentDirectionalFieldMeaning')in cases)")
    compile('INPUT={}\n' + raw, '<independent Protocol85>', 'exec')
    return raw


def main():
    original = W / 'pg3298-directional-protocol-regression-v1'
    receipt = json.loads((original / 'manifest.safe.json').read_bytes()); payload = (original / 'regression.private.py').read_bytes()
    inputs = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    if receipt['actualExit'] != 0 or hashlib.sha256(payload).hexdigest() != receipt['payloadSha256'] or receipt['testSource'] != inputs['head']:
        raise ValueError('original completed0 immutable source and payload required')
    data = {'source': SOURCE, 'testSource': inputs['head'], 'payloadSha256': receipt['payloadSha256'],
            'archiveSha256': inputs['archiveSha256'], 'manifestSha256': receipt['result']['serverManifestSha256']}
    raw = 'INPUT=' + repr(data) + '\n' + server(); compile(raw, '<Protocol85 independent qualification>', 'exec')
    os.umask(0o077); out = W / 'pg3300-directional-protocol-qualified-v1'; out.mkdir(mode=0o700)
    (out / 'qualifier.private.py').write_text(raw)
    code, output = run("python3 -B - <<'INDEPENDENT'\n" + raw + '\nINDEPENDENT', timeout=90)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit': code, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0:
        value.update(json.loads(next(line for line in output.splitlines() if line.startswith('{'))))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if code == 0:
        print(json.dumps({k: value['result'][k] for k in ['tests', 'suites', 'mainClasses', 'coverage', 'staticIssues', 'originalWrapperExit', 'actualMavenExit']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
