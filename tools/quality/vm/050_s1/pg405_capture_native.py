"""Actual same-source ten-step/five-frame reachability; not permit/startup acceptance."""
import datetime, hashlib, json, pathlib, re
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before, after = rows('pg405-native-db-before-full.log'), rows('pg405-native-db-final-full.log')
assert len(before) == 132 and len(after) == 142 and after[:132] == before
steps = ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
for index, line in enumerate(after[132:]):
    values = line.split('|')
    assert len(values) == 14 and values[0] == str(133+index) and values[3] == steps[index]
    assert values[4] == ('21' if index < 2 else '13' if index < 9 else '9') and values[5] == values[6]
    assert values[7:] == ['SKIPPED','0','0','0','0','ALREADY_SUCCESSFUL','step already successful for business date']
observed = json.loads((run/'pg405-native-final-private.json').read_text())
old = json.loads((run/'pg404-native-final-private.json').read_text())
assert observed['units']['schubert-nk-morning-controller.service']['ExecMainStatus'] == '30'
for name in ['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:
    assert observed['units'][name]['kernelEmpty']
    if 'controller' not in name: assert observed['units'][name]['ExecMainStatus'] == '0'
assert observed['units']['artemis.service']['InvocationID'] != old['units']['artemis.service']['InvocationID']
assert not observed['invalid'] and observed['permits'] == 1
assert len(observed['namespaces']['startup']) == 2 and 'epoch.current' in observed['namespaces']['startup']
permit = json.loads((run/'pg405-native-permit-readback.json').read_text())
assert permit['currentState'] == 'ISSUED' and permit['intentEntries'] == 0
assert all(permit[k] for k in ['permitHashBinding','bootBinding','brokerInvocationBinding','releaseManifestBinding','independentSixRootBytesMatch'])
assert all(not observed['namespaces'][n] for n in ['maintenance','backup-request','cleanup-request','expiry-request'])
assert all(observed['brokerJournal']['requiredVendorCodes'].values()) and observed['brokerJournal']['errorEntries'] == 0
names = ['MorningProcessMain','MorningControlScope','MorningPermitPublication','StartupPermitFiles','BackupStartIntentFiles','MorningGateEvidence','MorningBrokerExecution','MorningDatabaseSession','MorningPreviousBroker','MorningBackupRetention','MorningBackupCompletion','MorningPrestartEvidence','BackupUnitReceiptGate','InspectorUnitSnapshot']
reached = {n:(run/f'pg405-native/{n}-reached.txt').read_text() for n in names}
source = root/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningProcessMain.java'
return_line = next(i for i,s in enumerate(source.read_text().splitlines(),1) if 'return backupOutcome;' in s)
assert re.search(r'coveredLines=.*(?:,|=)'+str(return_line)+r'(?:,|$)', reached['MorningProcessMain'])
for method in ['broker(', 'postgres(', 'release(', 'stop(', 'retention(']: assert method in reached['MorningGateEvidence']
for method in ['complete(', 'recheck()', 'rows()', 'receipt()', 'localExitCode()']: assert method in reached['MorningBackupCompletion']
assert 'encode(' in reached['MorningPrestartEvidence'] and 'requireStoppedResult(' in reached['BackupUnitReceiptGate']
assert 'issue(' in reached['StartupPermitFiles'] and 'verifyPublication(' in reached['StartupPermitFiles']
assert 'issue(' in reached['MorningPermitPublication'] and 'commit(' in reached['MorningPermitPublication']
assert 'retire(' in reached['BackupStartIntentFiles']
backup_before = (run/'pg405-backup-before-private.json').read_bytes()
assert backup_before == (run/'pg405-backup-after-private.json').read_bytes()
start = int((run/'pg405-native-start.log').stat().st_mtime)
exec_times = {}
for line in (run/'pg405-native-exec-times.log').read_text().splitlines():
    path, at, size = line.split()
    assert int(at) >= start and int(size) > 0
    exec_times[pathlib.Path(path).stem] = int(at)
assert set(exec_times) == {'parent','backup','cleanup','expiry'}
coverage = {n:json.loads((run/f'pg405-native/{n}-union.json').read_text()) for n in ['protocol','storage','bootstrap','api','web','batch']}
assert all(value['classByteMismatch'] == 0 for value in coverage.values())
basepath = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG405-regular-issuer-baseline/manifest.json'
base = json.loads(basepath.read_text())
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {
 'id':'PG405-native-regular-issuer','formal':False,'sourceCommit':base['sourceCommit'],'branch':'dev-foundation',
 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15',
 'command':'pg405_deploy.sh signed exact source; pg405_native.sh once; pg405_collect_native.sh same-byte four exec',
 'applicationParentExit':30,'wholeStartupAccepted':False,'bugs':['BUG-389','BUG-390','BUG-391','BUG-393'],'ssc':['SSC-136'],'ykt':['YKT-309','YKT-310','YKT-311','YKT-313'],
 'fullRegression':{'tests':base['tests'],'failures':0,'errors':0,'skipped':0,'staticModulesZero':6},
 'releaseManifestSha256':sha(pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private/pg405-release/RELEASE-MANIFEST.json')),
 'actual':{'old132RowsUnchanged':True,'rows':142,'backupAttempt':21,'cleanupAttempt':13,'expiryAttempt':9,
   'freshSkippedSteps':10,'actualParentConfigCompletion':True,'actualTenStepFiveGateFramesConstructed':True,
   'mainReturnLineCovered':return_line,'stoppedBackupOriginalReceiptRetained':True,'backupInventoryUnchanged':True,
   'backupInventorySha256':hashlib.sha256(backup_before).hexdigest(),'startupInvalid':False,'permitsIssued':1,'requestOwnerIntentEntries':0,
   'regularThreeProofPublication':True,'afterACommit':True,'permitReadback':permit},
 'coverage':{'classByteMismatch':0,'sameRunRoles':['parent','backup','cleanup','expiry'],'oldInspectorExecExcluded':True,
   'moduleUnion':coverage,'totalMissed':miss,'resolvedFromOwnHost':{k:sum(v[k]['missed'] for v in base['coverage'].values())-miss[k] for k in miss}},
 'nativeExecHashes':{n:sha(run/f'pg405-native/{n}.exec') for n in ['parent','backup','cleanup','expiry']},
 'logs':[{'path':str(run/name),'sha256':sha(run/name)} for name in ['pg405-six.log','pg405-deploy.log','pg405-native-delivery.log','pg405-native-db-before-full.log','pg405-native-db-final-full.log','pg405-native-exec-times.log']],
 'reachabilityHashes':{n:sha(run/f'pg405-native/{n}-reached.txt') for n in names},
 'limitations':['prestart canonical whole bytes not independently emitted/compared; host whole golden only', 'M final close/Root original-parent-launch binding/full gates/same-PID exec/API/Web/CHR incomplete','fresh retention/failed Backup/native negatives/hard-timeout/coverage100 pending','formal PT-WEB-20260925-24 unchanged'],
 'redaction':'No raw journal/InvocationIDs/native exec/credentials/tokens/session/master/dump in Git'}
out = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':miss,'resolved':manifest['coverage']['resolvedFromOwnHost']}))
