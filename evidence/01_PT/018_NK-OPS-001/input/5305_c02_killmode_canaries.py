"""Compare explicit and inherited shutdown scopes without calling systemd."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve()
BASE = runpy.run_path(str(HERE.with_name('5276_c02_unit_text_order.py')))
E, D = BASE['E'], BASE['D']
GUARD = HERE.with_name('5306_c02_killmode_contract.py')
TESTS = {
    'PT-C02-TEXT-010': None,
    'PT-C02-TEXT-011': 'KILLMODE_EXPLICIT_REQUIRED',
    'PT-C02-TEXT-012': 'KILLMODE_EXPLICIT_REQUIRED',
    'PT-C02-TEXT-013': 'KILLMODE_INVALID_OVERRIDE',
    'PT-C02-TEXT-014': 'REPEATED_DIRECTIVE',
    'PT-C02-TEXT-015': None,
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main(after):
    start = json.loads(next(D.glob('649_C02*')).read_bytes())['values']
    frozen, prior, design = start['oracleReferences']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert (head != start['source']) == after
    assert ref(frozen['path']) == frozen and ref(prior['path']) == prior
    basis = git('show', f"{start['canonicalDesign']}:{design['path']}")
    assert sha(basis) == design['sha256'] and 'loaded/control-group/no以外を停止0回で拒否'.encode() in basis
    official = json.loads(Path(frozen['path']).read_bytes())
    assert official['sourceCore'] == start['productionCoreMain']
    configurations = {}
    for row in official['currentFiles']:
        f = Path(row['path'])
        data = git('show', f"{head}:{f}")
        assert sha(data) == row['sha256']
        configurations[f.relative_to(BASE['ROOT']).as_posix().removesuffix('.template')] = data
    assert len(configurations) == 14
    old, mutate = BASE['validate'], BASE['mutate']
    art, caddy, api, web = (BASE[k] for k in ('ART', 'START', 'API', 'WEB'))
    explicit = b'\nKillMode=control-group\n'
    sig = b'\nSendSIGKILL=no\n'
    fixtures = (
        configurations,
        mutate(configurations, art, explicit, b'\nKillMode=process\n'),
        mutate(configurations, caddy, explicit, b'\n'),
        mutate(configurations, api, sig, sig + b'KillMode=process\n'),
        mutate(configurations, web, sig, sig + b'KillMode=control-group\nKillMode=mixed\n'),
        mutate(configurations, web, sig, sig + b'KillMode=control-group\n'),
    )
    results = []
    check = runpy.run_path(str(GUARD))['validate_shutdown_text'] if after else None
    for (test_id, expected), fixture in zip(TESTS.items(), fixtures, strict=True):
        old(fixture)
        actual = None
        observations = {}
        if check:
            try:
                observations = check(fixture, BASE)
            except ValueError as message:
                actual = str(message)
        results.append(dict(testId=test_id, expected=expected, actual=actual,
                            qualified=actual == expected,
                            ordinaryServiceModes={k: observations[k] for k in (api, web)} if observations else {}))
    assert sum(r['qualified'] for r in results) == (6 if after else 2)
    folder = E / ('PG40180-c02-source-killmode-green-v1' if after else start['run'])
    folder.mkdir()
    p = folder / 'manifest.json'
    artifact = dict(actualExit=0, core=start['productionCoreMain'], source=head, mode='green' if after else 'red',
                    sourceDefinitions=official['currentFiles'], prior=frozen, design=design,
                    gate=ref(GUARD.relative_to(Path.cwd())) if after else prior, results=results,
                    qualified=sum(r['qualified'] for r in results), effectiveSystemdPolicyObserved=False,
                    backendActions=0, productTests=0, wholeC02Accepted=False, newFormalAcceptance=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    p.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + '\n')
    print(ref(p), artifact['qualified'])


if __name__ == '__main__':
    main({'before': False, 'after': True}[sys.argv[1]])
