"""Related actual Protocol85 after two independent oracle corrections; no VM."""
import inspect
import json
import subprocess

import pg2634_protocol_oracle_regression as engine
import pg3266_header_protocol_regression as previous
from pg3274_header_group_full_six import SOURCE, ROOT, W


def server():
    raw = previous.server().replace('PG3266-v1', 'PG3298-v1').replace('PG3248', 'PG3274').replace('tests==84', 'tests==85')
    marker = "(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print("
    if raw.count(marker) != 1:
        raise ValueError('one terminal manifest boundary required')
    raw = raw.replace(marker, "(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(")
    compile('INPUT={}\n' + raw, '<current Protocol85>', 'exec')
    return raw


def main():
    proof = json.loads((W / 'pg3294-directional-oracle-after-v3/manifest.safe.json').read_bytes())
    result = proof['result']
    if proof['actualExit'] != 0 or result['mutationsRejected'] != 2 or result['falseNegatives'] != 0 or result['productionSource'] != SOURCE:
        raise ValueError('normal selectors and both actual wrong implementations rejected required')
    if subprocess.check_output(['git', 'diff', result['testSource'], 'HEAD', '--', 'src/schubert-nk-protocol/src/test'], cwd=ROOT):
        raise ValueError('exact Test/resource bytes as independently exercised selectors required')
    raw = inspect.getsource(engine.main).replace('PG2634-v2', 'PG3298-v1').replace('pg2621-permit-expiry-group-full-qualified-v1', 'pg3276-header-group-full-qualified-v1')
    namespace = {**engine.__dict__, 'SOURCE': SOURCE, 'SLOT': 'pg3298-directional-protocol-regression-v1', 'SERVER': server()}
    exec(compile(raw, '<fixed same-source Protocol85 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
