"""Three independently sealed same-a9 activations, no VM operation or new full run.

451/SS355; PT-OPS-3190-001. Every selected stream/session/CRC and resource byte
remains independently qualified. The two inspector checkpoints count once.
"""
import inspect
import json
import pg3058_boundary_group_native_rejoin as previous
from pg1446_current_cold_stage import W
from pg2025_fresh_resume_full_live_seal import constant

SOURCE = previous.SOURCE
SLOT = 'pg3190-browser-three-activation-join-v1'


def expand(raw, digest):
    import re
    if type(digest) is not str or re.fullmatch('[0-9a-f]{64}', digest) is None:
        raise ValueError('actual third qualified capsule SHA required')
    old = "roots=[B/'runs/PG2934-native-v1',B/'runs/PG3030-native-v1'];"
    if raw.count(old) != 1:
        raise ValueError('one exact two-capsule boundary required')
    raw = raw.replace(old, "roots=[B/'runs/PG2934-native-v1',B/'runs/PG3030-native-v1',B/'runs/PG3188-native-v1'];")
    raw = constant(raw, 'MANIFESTS', previous.previous.MANIFESTS + [digest])
    for old, new in [('PG3058', 'PG3190'), ('len(streams)==18', 'len(streams)==27'),
                     ('len(sessions)==18', 'len(sessions)==27'),
                     ("for s in sessions})==18", "for s in sessions})==27"),
                     ("'qualifiedNativeActivations':2", "'qualifiedNativeActivations':3"),
                     ("'qualifiedNativeStreams':18", "'qualifiedNativeStreams':27"),
                     ("'distinctSessions':18", "'distinctSessions':27"),
                     ("require(inputs[0]['libraries']==inputs[1]['libraries'])", "require(inputs[0]['libraries']==inputs[1]['libraries']==inputs[2]['libraries'] and inputs[2]['qualifiedFull']==FULL)")]:
        if old not in raw:
            raise ValueError('closed three-activation source boundary absent: ' + old)
        raw = raw.replace(old, new)
    from pyflakes.api import check
    if check(raw, '<complete three same-a9 activation join>'):
        raise ValueError('whole union namespace required')
    compile(raw, '<sealed 27 independent sessions and all member bytes>', 'exec')
    return raw


def payload():
    proof = json.loads((W / 'pg3188-browser-native-qualified-v1/manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or proof['productionSource'] != SOURCE:
        raise ValueError('actual third native qualification required')
    return expand(previous.payload(), proof['manifestSha256'])


def main():
    base = previous.previous.previous
    raw = inspect.getsource(base.main)
    raw = raw.replace('pg2284-current-signed-native-qualified-v1', 'pg2934-format-fixed-same-native-qualified-v1').replace('pg2384-current-resume-native-qualified-v1', 'pg3030-current-resume-native-qualified-v1').replace("'pg3030-current-resume-native-qualified-v1']", "'pg3030-current-resume-native-qualified-v1','pg3188-browser-native-qualified-v1']").replace('PG2390', 'PG3190')
    ns = {**base.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<actual three qualified capsules transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
