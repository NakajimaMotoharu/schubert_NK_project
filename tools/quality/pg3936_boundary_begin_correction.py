"""Append-only metadata correction; never edit original begin/payload or reissue running whole."""
import hashlib
import json
import subprocess
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, TEST, BASIS, TRIGGER, require


def main():
    p = W / 'pg3928-server-six-v1/begin.safe.json'
    raw = p.read_bytes(); v = json.loads(raw)
    old = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    require(v['productionSource'] == SOURCE and (v['expectedTests'], v['expectedSuites'], v['expectedClasses']) == (3716, 545, 1643), 'original genuine fixed tuple')
    require(subprocess.check_output(['git', 'diff', '--name-only', old['sourceSnapshot'], v['snapshot'], '--', 'src', 'pom.xml', '.mvn'], cwd=ROOT, text=True).splitlines() == [TEST], 'actual one Test-only scope')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3936-boundary-begin-description-correction-v1'
    out.mkdir()
    value = {'actualExit': 0, 'bug': 'BUG1329', 'horizontal': 'YKT1095', 'run': 'PG3928-six-v1', 'productionSource': SOURCE, 'snapshot': v['snapshot'],
             'originalBeginSha256': hashlib.sha256(raw).hexdigest(), 'originalTransferHashes': v['transferHashes'],
             'originalDescription': {'expectedCountBasis': v['expectedCountBasis'], 'trigger': v['trigger']},
             'correctedDescription': {'expectedCountBasis': BASIS, 'trigger': TRIGGER}, 'numericExpectedUnchanged': {'tests': 3716, 'suites': 545, 'physicalMain': 1643},
             'originalBeginAndPayloadModified': False, 'testOrMainModifiedByCorrection': False, 'jobRestartedOrStopped': False,
             'wholeSuccessInferred': False, 'independentOriginalCaseAndPhysicalQualificationRequired': 'PG3930'}
    serialized = (json.dumps(value, sort_keys=True) + '\n').encode(); (out / 'manifest.json').write_bytes(serialized)
    require(p.read_bytes() == raw, 'original begin preserved')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(serialized).hexdigest(), 'jobReissued': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
