"""Publish completed candidate3712/host-signature receipts, no execution or native credit."""
import hashlib
import json
import os
from pathlib import Path

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    full_path = W / 'pg3414-outbox-full-qualified-v1/manifest.safe.json'
    full = json.loads(full_path.read_bytes()); f = full['result']
    signed_path = W / 'pg3420-candidate-build-v1.safe.json'; signed = json.loads(signed_path.read_bytes())
    assert full['actualExit'] == f['actualExit'] == signed['actualExit'] == 0
    assert f['tests'] == signed['tests'] == 3712 and f['suites'] == signed['suites'] == 545
    assert f['productionSource'] == signed['candidateSource'] == '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
    assert f['allOriginalCaseIdentitiesRetained'] and len(f['newCases']) == 5
    assert signed['hostGateSha256'] == hashlib.sha256(full_path.read_bytes()).hexdigest()
    assert signed['signatureVerified'] and signed['candidateNotDeployed'] and signed['guestMutations0']
    command = """python3 - <<'WHOLE'
import json,hashlib
from pathlib import Path
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3412-six-v1/manifest.safe.json');v=json.loads(p.read_bytes())
print(json.dumps({**{k:v[k]for k in ['run','actualExit','mavenExit','startUTC','endUTC','elapsedSeconds','sourceSnapshotHead','productionSource','sourceInputsUnchanged','logSha256']},'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
WHOLE"""
    rc, text = run(command, timeout=30); assert rc == 0
    actual = json.loads(text.strip()); assert actual['actualExit'] == actual['mavenExit'] == 0
    assert actual['manifestSha256'] == f['serverManifestSha256'] and actual['sourceSnapshotHead'] == f['sourceSnapshot']
    assert actual['sourceInputsUnchanged']
    result = {'actualExit': 0, 'candidateSource': f['productionSource'], 'candidateRelease': signed['release'],
              'candidateBomSha256': signed['manifestSha256'], 'candidateSignatureSha256': signed['signatureSha256'],
              'deployedSourceUnchanged': signed['priorSource'], 'wholeOriginal': actual,
              'tests': 3712, 'suites': 545, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'existingStaticSixModules': 0,
              'allOriginal3707CaseIdentitiesRetained': True, 'newCases': f['newCases'],
              'modules': f['modules'], 'jarHashes': f['jarHashes'], 'hostOnlyModuleCounters': f['coverage'],
              'hostOnlyMissed': {k: sum(v[k]['missed'] for v in f['coverage'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
              'semanticChangedClasses': 1, 'debugOnlyChangedClasses': 1, 'changedPhysicalClasses': f['changedClasses'],
              'generatedSwitchDebug': f['generatedSwitchDebug'], 'artifacts': 187, 'schema': '028', 'sql': 28, 'history': 29,
              'independentManifestSha256': hashlib.sha256(full_path.read_bytes()).hexdigest(),
              'signedCandidateReportSha256': hashlib.sha256(signed_path.read_bytes()).hexdigest(),
              'signatureVerifiedOnHost': True, 'candidateDeployed': False, 'candidateNativePending': True,
              'oldNativeImported': False, 'formalUpdated': False, 'formal': '1964PT/53scope',
              'individualAccepted': 17, 'individualTotal': 190, 'effortCompletionRate': None,
              'qa051Final': 'HELD', 'F03Accepted': False, 'pgptAllComplete': False, 'wholeReplayed': False}
    os.umask(0o077); out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3431-candidate-whole-signed'; out.mkdir()
    path = out / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'tests': 3712, 'suites': 545, 'bom': signed['manifestSha256'],
                      'nativePending': True, 'hostOnlyMissed': result['hostOnlyMissed'],
                      'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
