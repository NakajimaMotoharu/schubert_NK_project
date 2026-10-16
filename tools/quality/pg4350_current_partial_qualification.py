"""Current partial recovery tool evidence; no production test or acceptance inflation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check, checkPath
import pg4338_current_partial_sources as sources
import pg4346_current_partial_coordinator as stage
from pg1446_current_cold_stage import W

SLOT = 'pg4350-current-partial-qualification-v1'


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    result = subprocess.run(['python3', '-B', '-m', 'unittest', 'pg4338_current_partial_sources_test',
                             'pg4348_current_partial_recover_test', '-v'], capture_output=True)
    log = result.stdout + result.stderr
    with (out / 'host-tests.log').open('xb') as f:
        f.write(log)
    if result.returncode != 0 or b'Ran 12 tests' not in log or not log.rstrip().endswith(b'OK'):
        raise ValueError('complete current12 tests FES0 required')
    paths = sorted(p for pattern in ['pg4336*.py', 'pg4338*.py', 'pg4346*.py', 'pg4348*.py', 'pg4350*.py']
                   for p in Path('tools/quality').glob(pattern))
    full = {**sources.files(), 'stage.py': stage.stage_payload()}
    if sum(checkPath(str(p)) for p in paths) + sum(check(raw, '<' + name + '>') for name, raw in full.items()):
        raise ValueError('whole current tool closure static0 required')
    staged = json.loads((W / (stage.SLOT + '-stage') / 'manifest.safe.json').read_bytes())
    proof = json.loads((W / (stage.SLOT + '-proof') / 'manifest.safe.json').read_bytes())
    expected = {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in sources.files().items()}
    if staged['actualExit'] != 0 or staged['result']['files'] != expected:
        raise ValueError('same frozen stage required')
    if proof['actualExit'] != 0 or proof['result']['signalsIssued'] != 0 or proof['result']['newTenRefsNormalClose'] is not True:
        raise ValueError('actual same-current no-signal normal proof required')
    value = {'actualExit': 0, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
             'toolTests': 12, 'newToolTests': 9, 'inheritedIndependentFixtureRegression': 3,
             'failures': 0, 'errors': 0, 'skipped': 0, 'staticFindings': 0,
             'emittedSha256': {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in full.items()},
             'hostSha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'logSha256': hashlib.sha256(log).hexdigest(), 'actualPairProof': proof['result'],
             'designMain': 'f9600af73555fb002fc98ddd0af0dea4c0e686b6', 'designPR': 138,
             'originalUnknownNormal': False, 'recoveryAccepted': False, 'productionPtAdded': 0, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
    print(json.dumps(value))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
