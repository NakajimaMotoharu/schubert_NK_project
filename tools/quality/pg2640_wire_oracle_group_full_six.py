"""One necessary all-six integration of independently qualified wire oracles."""
import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2620_permit_expiry_group_full_six as previous
import pg2600_retention_group_full_six as transport_base
from pg2510_strict_reference_full_six import SCOPE
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
HEADER = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/header/HeaderModelTest.java'
SEMANTIC = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/semantic/ProtocolSemanticTypeTest.java'


def validate(snapshot):
    root = Path(__file__).resolve().parents[2]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    baseline = json.loads((W / 'pg2621-permit-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if baseline['actualExit'] != 0 or baseline['result']['tests'] != 3663 or baseline['result']['productionSource'] != SOURCE:
        raise ValueError('actual complete3663 baseline required')
    original = baseline['result']['sourceSnapshot']
    previous.validate(original)
    if set(git('diff', '--name-only', original, snapshot, '--', *SCOPE).decode().splitlines()) != {HEADER, SEMANTIC}:
        raise ValueError('only independently qualified two Protocol Test changes permitted')
    normal = json.loads((W / 'pg2634-protocol-oracle-regression-v2/manifest.safe.json').read_bytes())
    mutation = json.loads((W / 'pg2636-wire-enum-mutations-v1/manifest.safe.json').read_bytes())
    if normal['actualExit'] != 0 or normal['result']['tests'] != 82 or mutation['actualExit'] != 0 or mutation['result']['mutationsRejected'] != 36:
        raise ValueError('actual independent Protocol and36 mutation qualification required')
    if normal['source'] != SOURCE or mutation['source'] != SOURCE:
        raise ValueError('same Production required')
    for name in (HEADER, SEMANTIC):
        if git('show', snapshot + ':' + name) != git('show', normal['testSource'] + ':' + name):
            raise ValueError('exact normally tested whole Test files required')
    script = (W / 'pg2636-wire-enum-mutations-v1/mutations.private.py').read_bytes()
    if hashlib.sha256(script).hexdigest() != mutation['payloadSha256']:
        raise ValueError('exact independently rejected mutation payload required')
    inputs = ast.literal_eval(script.decode().splitlines()[0].removeprefix('INPUT='))
    if hashlib.sha256(git('show', snapshot + ':' + SEMANTIC)).hexdigest() != inputs['files']['ProtocolSemanticTypeTest.java']:
        raise ValueError('whole rejected semantic Test source required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2620', 'PG2640').replace('3663', '3664')
    compile(raw, '<necessary independent oracle group full3664>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport_base.main).replace('PG2600', 'PG2640').replace('pg2600', 'pg2640').replace('3657', '3664')
    raw = raw.replace('3653 retained plus four independently accepted JDBC boundary methods; unchanged Main540suite1643',
        '3663 retained with independently corrected header oracle and one semantic allowlist Test; Main unchanged540suite1643')
    raw = raw.replace('One required integration for2588/2590/2592/2594; no management-only repetition',
        'BUG1244/YKT1010 independent header and18enum oracle changes require consumer all-six integration once')
    ns = {**transport_base.__dict__, 'validate': validate, 'server_source': server_source, 'SOURCE': SOURCE}
    exec(compile(raw, '<oracle group immutable transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
