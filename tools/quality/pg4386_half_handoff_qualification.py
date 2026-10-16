"""New remaining-only8 tests and exact no-action proof; no repeated whole Production gate."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check, checkPath
import pg4382_half_handoff_stage as stage
from pg1446_current_cold_stage import W

SLOT = 'pg4386-half-handoff-qualification-v1'


def main():
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    r = subprocess.run(['python3', '-B', '-m', 'unittest', 'pg4378_half_handoff_contract_test',
                        'pg4380_half_handoff_sources_test', 'pg4384_half_handoff_recover_test', '-v'], capture_output=True)
    log = r.stdout + r.stderr
    with (out / 'host-tests.log').open('xb') as f: f.write(log)
    if r.returncode or b'Ran 8 tests' not in log or not log.rstrip().endswith(b'OK'):
        raise ValueError('all new current8 tools FES0 required')
    paths = sorted(p for pattern in ['pg4374*.py', 'pg4376*.py', 'pg4378*.py', 'pg4380*.py', 'pg4382*.py', 'pg4384*.py', 'pg4386*.py'] for p in Path('tools/quality').glob(pattern))
    generated = {**stage.files(), 'stage.py': stage.stage_payload()}
    if sum(checkPath(str(p)) for p in paths) + sum(check(raw, '<' + name + '>') for name, raw in generated.items()):
        raise ValueError('all current host/full generated static0 first')
    staged = json.loads((W / (stage.SLOT + '-stage') / 'manifest.safe.json').read_bytes())
    proof = json.loads((W / (stage.SLOT + '-proof') / 'manifest.safe.json').read_bytes())
    if staged['actualExit'] != 0 or staged['result']['files'] != {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in stage.files().items()}:
        raise ValueError('same frozen current bytes required')
    if proof['actualExit'] != 0 or proof['result']['signalsIssued'] != 0 or proof['result']['javaSignalsIssued'] != 0 or proof['result']['newTenRefsNormalClose'] is not True:
        raise ValueError('same actual no-action full scope proof first')
    value = {'actualExit': 0, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'toolTests': 8,
             'FES': 0, 'staticFindings': 0, 'logSha256': hashlib.sha256(log).hexdigest(),
             'hostSha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'emittedSha256': {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in generated.items()},
             'actualNoActionProof': proof['result'], 'designMain': 'd6c8b23fdcec49e6cc086a0dd435a895b2bf2ce9', 'designPR': 140,
             'productionPtAdded': 0, 'recoveryAccepted': False, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as f: json.dump(value, f, sort_keys=True)
    print(json.dumps(value))


if __name__ == '__main__':
    main()
