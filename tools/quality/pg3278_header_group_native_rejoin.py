"""Sealed28/new3701, original negative3694 provenance retained; read-only no VM."""
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from lan_server import run
from pg1446_current_cold_stage import W
import pg3252_cycle_group_native_rejoin as previous
from pg3274_header_group_full_six import SOURCE, validate, rebase


def build(*args):
    raw = rebase(inspect.getsource(previous.build), 'PG3248', 'PG3274', 3697, 3701).replace('PG3252', 'PG3278')
    ns = dict(previous.__dict__)
    exec(compile(raw, '<native28/Header3701 builder fixed provenance>', 'exec'), ns)
    result = ns['build'](*args)
    if check(result, '<complete native28 Header3701 payload>'):
        raise ValueError('complete qualifier namespace required')
    return result


def public_summary(value):
    r = value['result']
    expected = {'actualExit': 0, 'qualifiedFullTests': 3701, 'qualifiedNativeStreams': 28,
                'distinctSessions': 28, 'mainClassesIdentical': 1643,
                'allResourceMetaMembersIdentical': 79, 'productionSource': SOURCE}
    if value['actualExit'] != 0 or any(r[k] != v for k, v in expected.items()):
        raise ValueError('actual fixed3701 native28 complete result required')
    return {'actualExit': value['actualExit'], 'tests': r['qualifiedFullTests'],
            'streams': r['qualifiedNativeStreams'], 'sameMain': r['mainClassesIdentical'],
            'sameResources': r['allResourceMetaMembersIdentical'],
            'remaining': {k: sum(v[k]['missed'] for v in r['moduleCounters'].values())
                          for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
            'manifestSha256': value['manifestSha256'], 'formalAccepted': False}


def main():
    def read(slot):
        result = json.loads((W / slot / 'manifest.safe.json').read_bytes())
        if result['actualExit'] != 0:
            raise ValueError('every original actual authority required')
        return result
    current = read('pg3276-header-group-full-qualified-v1')
    original = read('pg3206-expiry-group-full-qualified-v1')
    capsule_full = read('pg3056-boundary-group-full-qualified-v1')
    capsule = read('pg3188-browser-native-qualified-v1')
    post = read('pg3238-legacy-negative-post-v1')
    compiled = read('pg3214-legacy-fixture-compile-v1')
    validate(current['result']['sourceSnapshot'])
    raw = build(current['result'], original['result'], capsule_full['result'], capsule['manifestSha256'], post['capsuleSha256'], compiled['inputSha256'])
    os.umask(0o077); out = W / 'pg3278-header-group-native-qualified-v1'; out.mkdir(mode=0o700)
    (out / 'payload.private.py').write_text(raw)
    code, output = run("python3 -B - <<'NATIVE28'\n" + raw + '\nNATIVE28', timeout=240)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit': code, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0:
        value.update(json.loads(next(line for line in output.splitlines() if line.startswith('{'))))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(public_summary(value) if code == 0 else {'actualExit': code, 'formalAccepted': False}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
