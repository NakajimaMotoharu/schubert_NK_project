"""Same v3 actual proof, all independent impacted tests and complete emitted static qualification."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check, checkPath
import pg4360_pool_bound_partial_sources as sources
import pg4366_pool_bound_coordinator as stage
from pg1446_current_cold_stage import W

SLOT = 'pg4370-pool-bound-qualification-v1'


def main():
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    r = subprocess.run(['python3', '-B', '-m', 'unittest', 'pg4358_ordinary_fd_contract_test',
                        'pg4360_pool_bound_partial_sources_test', 'pg4368_pool_bound_recover_test',
                        'pg4348_current_partial_recover_test', '-v'], capture_output=True)
    log = r.stdout + r.stderr
    with (out / 'host-tests.log').open('xb') as f: f.write(log)
    if r.returncode or b'Ran 17 tests' not in log or not log.rstrip().endswith(b'OK'):
        raise ValueError('all current17 impacted tests FES0 required')
    paths = sorted(p for pattern in ['pg4354*.py', 'pg4356*.py', 'pg4358*.py', 'pg4360*.py', 'pg4366*.py', 'pg4368*.py', 'pg4370*.py'] for p in Path('tools/quality').glob(pattern))
    generated = {**sources.files(), 'stage.py': stage.stage_payload()}
    if sum(checkPath(str(p)) for p in paths) + sum(check(raw, '<' + name + '>') for name, raw in generated.items()):
        raise ValueError('all host and complete emitted static0 required')
    actual = json.loads((W / (stage.SLOT + '-proof') / 'manifest.safe.json').read_bytes())
    staged = json.loads((W / (stage.SLOT + '-stage') / 'manifest.safe.json').read_bytes())
    expected = {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in sources.files().items()}
    if staged['actualExit'] != 0 or staged['result']['files'] != expected:
        raise ValueError('same frozen exact v3 files required')
    if actual['actualExit'] != 0 or actual['result']['newTenRefsNormalClose'] is not True or actual['result']['signalsIssued'] != 0:
        raise ValueError('same complete actual no-action proof first')
    value = {'actualExit': 0, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'toolTests': 17,
             'newToolTests': 14, 'inheritedCurrentTransportRegression': 3, 'FES': 0, 'staticFindings': 0,
             'hostSha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'emittedSha256': {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in generated.items()},
             'logSha256': hashlib.sha256(log).hexdigest(), 'actualNoActionProof': actual['result'],
             'designMain': '6eae971276832c6d0cc9e29fbc18c5090d3cf6ad', 'designPR': 139,
             'boundedIndependentReview': 'original server/partial/bind evidence blockers resolved; no additional unsafe acceptance found; read-only',
             'recoveryAccepted': False, 'productionPtAdded': 0, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as f: json.dump(value, f, sort_keys=True)
    print(json.dumps(value))


if __name__ == '__main__':
    main()
