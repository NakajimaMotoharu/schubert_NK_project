"""Independently reconcile the source-only KillMode outcomes and frozen inputs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RUNS = ('PG40178-c02-source-killmode-red-v1', 'PG40180-c02-source-killmode-green-v1')
OUT = E / 'PG40182-c02-source-killmode-independent-v1'
API = 'schubert-nk-api.service'
WEB = 'schubert-nk-web.service'
INHERITED = 'INHERITED_EFFECTIVE_UNOBSERVED'
REQUIRED = ('KILLMODE_EXPLICIT_REQUIRED', 'KILLMODE_EXPLICIT_REQUIRED', 'KILLMODE_INVALID_OVERRIDE', 'REPEATED_DIRECTIVE')


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def main():
    files = [E / folder / 'manifest.json' for folder in RUNS]
    old, current = (json.loads(p.read_bytes()) for p in files)
    assert old['source'] != current['source'] and old['core'] == current['core']
    assert old['sourceDefinitions'] == current['sourceDefinitions'] and len(current['sourceDefinitions']) == 14
    for row in current['sourceDefinitions']:
        data = subprocess.check_output(['git', 'show', f"{current['source']}:{row['path']}"], timeout=20)
        assert hashlib.sha256(data).hexdigest() == row['sha256']
    assert ref(current['gate']['path']) == current['gate']
    assert [r['actual'] for r in old['results']] == [None] * 6
    assert [r['actual'] for r in current['results']] == [None, *REQUIRED, None]
    assert [r['testId'] for r in current['results']] == [f'PT-C02-TEXT-{n:03}' for n in range(10, 16)]
    assert current['results'][0]['ordinaryServiceModes'] == {API: INHERITED, WEB: INHERITED}
    assert current['results'][-1]['ordinaryServiceModes'] == {API: INHERITED, WEB: 'control-group'}
    assert current['qualified'] == 6 and old['qualified'] == 2
    assert not current['effectiveSystemdPolicyObserved'] and current['backendActions'] == 0
    result = dict(actualExit=0, source=current['source'], productionCore=current['core'], candidates=[ref(p) for p in files],
                  outcomes=current['results'], beforeMatched=2, afterMatched=6,
                  actualEffectiveUnits=0, productTests=0, wholeC02Accepted=False, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    OUT.mkdir()
    p = OUT / 'manifest.json'
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(ref(p))


if __name__ == '__main__':
    main()
