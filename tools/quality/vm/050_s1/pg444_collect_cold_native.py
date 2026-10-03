"""Fixed independent operator-native acceptance; no business/whole PGPT success claim."""
import hashlib
import json
import pathlib
import re
import subprocess

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
target = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG444-cold-native-v3'
assert not target.exists()
source = (work / 'pg444-cold-native-v2.source').read_text().strip()
assert re.fullmatch('[0-9a-f]{40}', source)
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == source
assert (work / 'pg444-cold-native-v2.exit').read_text().strip() == '0'
log = (work / 'pg444-cold-native-v2.log').read_bytes()
expected = (b'PG430 STAGE FIXED_CANDIDATE_HOST_RO\n'
            b'PG430 STAGE PINNED_SIGNATURE_VERIFIED\n'
            b'PG430 STAGE FULL_CANDIDATE_BOM_VERIFIED\n'
            b'PG428 COLD_BOOT_PREPARED completed=true ownedUnwindReturned=true oldOwnerClose=UNKNOWN '
            b'oldBootSuccessInferred=false oldIntentRetired=0 originalRows=251 backupFixturePreserved=true '
            b'locksSameInode=true freshInvalidOnly=true workersStarted=0 migrationApplied=0\n')
assert log == expected
post = json.loads((work / 'pg444-post-cold-safe.json').read_text())
assert all(post[k] for k in ('success', 'newInvalidOnly', 'originalEqual', 'databaseEqual', 'backupEqual'))
assert post['unitsCold'] == 9 and post['backupEntries'] == 20 and post['transferEntries'] == 3
assert all(post[k] == 0 for k in ('dedicatedAdvisoryOwners', 'currentColdToolProcesses', 'flockOwners', 'oldIntentRetired'))
record = {'id': 'PG444-cold-native-v3', 'actualExecutionId': 'PG444-cold-native-v2', 'formal': False, 'businessStartupAccepted': False,
          'sourceCommit': source, 'branch': 'dev-foundation', 'exitCode': 0,
          'startedAt': (work / 'pg444-cold-native-v2.started').read_text().strip(),
          'finishedAt': (work / 'pg444-cold-native-v2.finished').read_text().strip(),
          'command': 'WorkPG379/pg444_cold_native_v2.sh; root sealed cold tool PG444-V2',
          'environment': 'host Linux/JDK25.0.4; guest Linux7.0.0-34-generic/OpenJDK25.0.4+7-1-26.04-Ubuntu/PostgreSQL18.6 (Ubuntu18.6-0ubuntu0.26.04.1); QEMU10.2.1 (Debian1:10.2.1+ds-1ubuntu3.2)',
          'environmentCommands': ['guest uname -r', 'guest /opt/jdk-25.0.4/bin/java -version', 'guest sudo -u postgres psql -X -A -t -c SHOW server_version', 'host bundled qemu-system-x86_64 --version'],
          'metadataCorrection': {'bug': 'BUG-598', 'field': 'environment PostgreSQL17 -> actual18.6',
                                 'priorManifest': 'PG444-cold-native-v2/manifest.json',
                                 'priorSha256': hashlib.sha256((target.parent/'PG444-cold-native-v2/manifest.json').read_bytes()).hexdigest(),
                                 'priorFieldInvalid': True, 'nativeReexecuted': False},
          'runtimeProductionSource': '91b010509e715e2b097c955d04f21c23f3529966',
          'runtimeProductionLabel': 'PG430 signed fullBOM/hostRO/current approval reauthenticated; cold only',
          'testIds': ['PG444-COLD-NATIVE-001'], 'actual': log.decode().splitlines(),
          'logSha256': hashlib.sha256(log).hexdigest(), 'independentPostcondition': post,
          'productionTestCount': 0, 'bugs': ['BUG-544', 'BUG-595', 'BUG-596', 'BUG-597'],
          'ssc': ['SSC-174'], 'ykt': ['YKT-388', 'YKT-419', 'YKT-420', 'YKT-421'],
          'operatorHostTests': 'PG444-cold-tools-v7; cold414/transfer21/ownership25; independent literals/negative FD',
          'sourceFiles': [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in [root / 'tools/quality/vm/050_s1/Pg428ColdBootPreparation.java',
                                    root / 'tools/quality/vm/050_s1/pg444_stage_cold_tools.py']],
          'rootPlacement': {'classes': 26, 'closedMode': 'root500/file400',
                            'logSha256': hashlib.sha256((work / 'pg444-root-placement-v3.log').read_bytes()).hexdigest(),
                            'old21ClassUnchanged': True},
          'beforeNativeFailure': {'sourceCommit': (work / 'pg444-cold-native.source').read_text().strip(),
                                  'exitCode': 1, 'logSha256': hashlib.sha256((work / 'pg444-cold-native.log').read_bytes()).hexdigest(),
                                  'stage': 'PRESERVATION_READ', 'cause': 'wrong fixed Transfer group BUG597'},
          'limits': ['old UNKNOWN/close remains UNKNOWN, old intent retired0',
                     'signed new manufacture/API/Web/Caddy/DONE/CHR/native coverage/formal pending',
                     'formal PT-WEB-20260925-24/1964PT/53scope unchanged'],
          'redaction': 'no raw epoch/session/permit/credential/DB/original/backup/dump bytes; fixed safe lines/hash only'}
assert not re.search(r'(?i)(authorization|cookie|password|session_id|access_token)\s*[:=]\s*["\']?[^\s<>]', json.dumps(record))
target.mkdir(parents=True)
path = target / 'manifest.json'
path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'success': True, 'coldPreparationAccepted': True, 'formal': False,
                  'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
