"""Frozen PG404 actual failure: fail-closed evidence, never startup acceptance."""
import datetime
import hashlib
import json
import pathlib
import re

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name):
    return [s for s in (run / name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before = rows('pg404-native-db-before-full.log')
after = rows('pg404-native-db-final-full.log')
assert len(before) == 122 and len(after) == 132 and after[:122] == before
steps = ['BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION',
         'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN',
         'CLEAN_TRANSFER', 'CLEAN_EXPIRY']
for i, line in enumerate(after[122:]):
    v = line.split('|')
    assert len(v) == 14 and v[0] == str(123+i) and v[3] == steps[i]
    assert v[4] == ('20' if i < 2 else '12' if i < 9 else '8') and v[5] == v[6]
    assert v[7:] == ['SKIPPED', '0', '0', '0', '0', 'ALREADY_SUCCESSFUL',
                     'step already successful for business date']
observed = json.loads((run / 'pg404-native-final-private.json').read_text())
assert observed['units']['schubert-nk-morning-controller.service']['ExecMainStatus'] == '1'
for name in ['schubert-nk-morning-controller.service', 'schubert-nk-backup.service',
             'schubert-nk-cleanup.service', 'schubert-nk-expiry-cleanup.service']:
    assert observed['units'][name]['kernelEmpty']
    if 'controller' not in name:
        assert observed['units'][name]['ExecMainStatus'] == '0'
assert observed['invalid'] and observed['permits'] == 0
assert observed['namespaces']['startup'] == ['epoch.current']
assert all(not observed['namespaces'][n] for n in
           ['maintenance', 'backup-request', 'cleanup-request', 'expiry-request'])
assert (run / 'pg404-backup-before-private.json').read_bytes() == (run / 'pg404-backup-after-private.json').read_bytes()
journal = (run / 'pg404-parent-journal-private.log').read_text()
assert 'StartupPermitRecords.hash' in journal and 'MorningProcessMain.java:324' in journal
coverage = {n: json.loads((run / f'pg404-native/{n}-union.json').read_text()) for n in
            ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']}
assert all(v['classByteMismatch'] == 0 for v in coverage.values())
basepath = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG404-regular-issuer-baseline/manifest.json'
base = json.loads(basepath.read_text())
assert base['sourceCommit'] == 'edd1d7569aaac83df78c2940246063a54e049490'
miss = {k: sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH', 'LINE', 'METHOD', 'CLASS']}
manifest = {
    'id': 'PG404-native-permit-construction-failed', 'formal': False, 'accepted': False,
    'sourceCommit': base['sourceCommit'], 'branch': 'dev-foundation',
    'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'environment': 'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15',
    'command': 'pg404_deploy.sh; pg404_native.sh once; pg404_collect_native.sh',
    'applicationParentExit': 1, 'bug': 'BUG-393', 'ykt': 'YKT-313', 'ssc': 'SSC-136',
    'fullRegression': {'tests': base['tests'], 'failures': 0, 'errors': 0, 'skipped': 0, 'staticModulesZero': 6},
    'expected': 'SHA-256 of full NKPRESTART1 canonical bytes in permit field, then regular three-proof publication',
    'actual': {'failure': 'IllegalArgumentException at StartupPermitRecords.hash / MorningProcessMain.java:324',
               'old122RowsUnchanged': True, 'rows': 132, 'newAlreadySuccessfulSkippedSteps': 10,
               'startupInvalid': True, 'permitsIssued': 0, 'allFourWorkerKernelTerminal': True,
               'requestOwnerIntentEntries': 0, 'backupInventoryUnchanged': True},
    'coverage': {'classByteMismatch': 0, 'sameRunRoles': ['parent', 'backup', 'cleanup', 'expiry'],
                 'moduleUnion': coverage, 'totalMissed': miss,
                 'resolvedFromOwnHost': {k: sum(v[k]['missed'] for v in base['coverage'].values())-miss[k] for k in miss}},
    'nativeExecHashes': {n: sha(run / f'pg404-native/{n}.exec') for n in ['parent', 'backup', 'cleanup', 'expiry']},
    'privateEvidenceHashes': {n: sha(run / n) for n in ['pg404-parent-journal-private.log',
        'pg404-native-final-private.json', 'pg404-native-db-before-full.log', 'pg404-native-db-final-full.log',
        'pg404-backup-before-private.json', 'pg404-backup-after-private.json', 'pg404-native-delivery.log']},
    'limitations': ['No permit issued / three-proof or after-A acceptance',
                    'Root same-PID/API/Web/CHR/100%/whole PGPT incomplete', 'formal PT-WEB-20260925-24 unchanged'],
    'redaction': 'Metadata/hashes only; no raw journal, InvocationID, exec, credential, token, session, master or dump in Git'
}
out = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'manifestSha256': sha(out / 'manifest.json'), 'missed': miss, 'accepted': False}))
