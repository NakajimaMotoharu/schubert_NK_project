"""Persist current candidate and the original whole job without restarting any process."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
W = ROOT.parent / 'pgpt-runs/PG379'


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    processes = []
    for p in Path('/proc').iterdir():
        if not p.name.isdecimal(): continue
        try:
            argv = (p / 'cmdline').read_bytes(); parts = argv.split(b'\0')
            if not any(part.endswith(b'/pg4420_shared_manager_full.py') for part in parts): continue
            processes.append({'pid': int(p.name), 'ticks': int((p / 'stat').read_text().rsplit(')', 1)[1].split()[19]),
                              'argvSha256': hashlib.sha256(argv).hexdigest()})
        except (FileNotFoundError, ProcessLookupError, PermissionError): continue
    whole = W / 'pg4420-shared-manager-six-v1'
    result = json.loads((whole / 'manifest.safe.json').read_bytes()) if (whole / 'manifest.safe.json').exists() else None
    value = {'createdUTC': stamp, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'branch': 'dev-foundation', 'gitStatus': subprocess.check_output(['git', '-c', 'core.quotepath=false', 'status', '--short'], cwd=ROOT, text=True).splitlines(),
             'deployedSource': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'release': 'PG3976',
             'candidateSource': '964e96e45bb588e7e75798b5adf425cbd9985427',
             'BOM': '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
             'guestBootLastAuthenticated': '79a3260a-e16d-42bf-942a-b914ed144c28', 'newVmOrRootOperations': 0,
             'currentRecovery': {'original4384ActualExit': 0, 'fiveStopsAndIndependentPost': 0, 'replayAllowed': False,
                 'original4328ActualExit': 255, 'original4368ActualExit': 1, 'oldRootExit': 143, 'oldCloseUnknown': True,
                 'savedPriorCheckpoint': str(W / 'pg4391-recovery-completed-checkpoint.json')},
             'whole4420': {'originalExec': 79478, 'localOwnersObserved': processes,
                 'remoteOwnerLastAuthenticated': {'pid': 1604790, 'ticks': 16180186, 'startUTC': '2026-10-16T14:38:59.147846+00:00'},
                 'begin': json.loads((whole / 'begin.safe.json').read_bytes()), 'result': result,
                 'remoteManifestWasAbsentAtRead': True, 'remoteSource': '/home/mini/schubert-nk-pgpt/source-full-PG4420',
                 'remoteLog': '/home/mini/schubert-nk-pgpt/runs/PG4420-six-v1/maven.private.log', 'replayAllowed': False},
             'priorSelected4412': {'actualExit': 1, 'targetTests': 0, 'reason': 'literal NoTests upstream; not-run remains not accepted'},
             'readOnlyCandidate4408': {'actualExit': 0, 'originalExec': 87255, 'allSevenValuesEqual': True,
                 'rootAuthority': False, 'rootPerformanceAccepted': False},
             'designMain': '48b3856c01326ebecb9224733a4905d458ba2381', 'designPR': 141,
             'formal': '1964PT/53scope', 'effortCompletion': None, 'QA051final': 'HELD', 'acceptedLeafDelta': 0,
             'allOriginalDbBackupKeysNative58AndStartup37Preserved': True,
             'next': 'Collect only original79478; if session lost read exact remote original manifest/process/source. Never restart4420 for missing response. Qualify full XML/old-case alias/all physical Main/source/6static independently. Complete tool-only BUG1354..56/static before using tools. Then new source signature/unused/RO/finite publication/post, one normal Root/ownedstop/native/Browser/CHR/F03/four100/451/trace/handoff.',
             'stopRequested': False}
    output = W / 'pg4416-current-source-checkpoint.json'
    if output.exists(): raise ValueError('new checkpoint path required; do not overwrite prior checkpoint')
    with output.open('x') as target:
        json.dump(value, target, ensure_ascii=False, sort_keys=True); target.flush(); os.fsync(target.fileno())
    print(json.dumps({'checkpoint': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'wholeHasTerminal': result is not None, 'localOwnerCount': len(processes)}))


if __name__ == '__main__':
    main()
