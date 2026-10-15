"""Publish genuine recovered3398/3400/3402 receipts; no execution or requalification."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077)
    paths = [W / s / 'manifest.safe.json' for s in [
        'pg3398-server-six-v1', 'pg3400-oracle-boundary-full-qualified-v1',
        'pg3402-oracle-boundary-native-qualified-v2']]
    whole, qualified, native = [json.loads(p.read_bytes()) for p in paths]
    f, n = qualified['result'], native['result']
    assert whole['actualExit'] == qualified['actualExit'] == native['actualExit'] == f['actualExit'] == n['actualExit'] == 0
    assert f['tests'] == n['qualifiedFullTests'] == 3707 and f['suites'] == 543
    assert f['mainClasses'] == n['mainClassesIdentical'] == 1643
    assert n['allResourceMetaMembersIdentical'] == 79
    assert n['distinctSessions'] == n['qualifiedNativeStreams'] == 28
    assert f['FESFlakyNotRun'] == f['staticSixModules'] == 0
    assert whole['snapshot'] == f['sourceSnapshot'] == '497fdb37f99529c7f233f5ef86030ab8590a902d'
    assert f['productionSource'] == n['productionSource'] == whole['productionSource']
    assert not n['oldSourceNativeImported'] and n['VMOperations'] == 0
    remaining = {k: sum(v[k]['missed'] for v in n['moduleCounters'].values())
                 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}
    assert remaining == {'LINE': 598, 'METHOD': 114, 'CLASS': 0, 'BRANCH': 466}
    output = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3398-retain-owner-whole'
    output.mkdir()
    result = {'actualExit': 0, 'productionSource': f['productionSource'],
              'run': 'PG3398-six-v1', 'originalJobRecoveredWithoutReplay': True,
              'sourceSnapshot': f['sourceSnapshot'], 'sourceArchiveSha256': f['sourceArchiveSha256'],
              'startUTC': f['startUTC'], 'endUTC': f['endUTC'], 'elapsedSeconds': f['elapsedSeconds'],
              'tests': f['tests'], 'suites': f['suites'], 'mainClasses': f['mainClasses'],
              'modules': f['modules'], 'FESFlakyNotRun': 0, 'existingStaticSixModules': 0,
              'staticBoundary': 'Compiler/NullAway/SpotBugs/format only; unresolved PMD2220/Checkstyle645 not accepted',
              'nativeStreams': 28, 'allMainAndDebugMemberBytesIdentical': True,
              'resourceMetaMembersIdentical': 79, 'remainingCounters': remaining,
              'combinedModuleCounters': n['moduleCounters'],
              'authorityManifestSha256': {p.parent.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
              'serverManifestSha256': f['serverManifestSha256'],
              'nativeManifestSha256': native['manifestSha256'],
              'nativePayloadSha256': native['payloadSha256'],
              'qualificationSourceSha256': qualified['qualificationSourceSha256'],
              'nativeToolFirstAttempt': 'local suite guard rejected before send; subsequent v1 old output guard rejected before writes; both preserved; new-only v2 actual0',
              'bug1299Unfixed': True, 'bug1300Ykt1066FiniteToolScopeVerified': True,
              'formalUpdated': False, 'formal': '1964PT/53scope', 'individualAccepted': 17,
              'individualTotal': 190, 'effortCompletionRate': None, 'qa051Final': 'HELD',
              'vmActions': 0, 'pgptAllComplete': False}
    path = output / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'tests': 3707, 'suites': 543, 'native': 28,
                      'remaining': remaining, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
