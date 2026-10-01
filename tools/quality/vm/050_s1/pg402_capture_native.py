"""Same-source actual native issuer frame reachability; not startup or formal acceptance."""
import datetime, hashlib, json, pathlib, re
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before = rows('pg402-native-db-before-full.log')
after = rows('pg402-native-db-final-full.log')
assert len(before) == 102 and len(after) == 112 and after[:102] == before
steps = ['BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION', 'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN', 'CLEAN_TRANSFER', 'CLEAN_EXPIRY']
for index, line in enumerate(after[102:]):
    values = line.split('|')
    assert len(values) == 14 and values[0] == str(103 + index) and values[3] == steps[index]
    assert values[4] == ('18' if index < 2 else '10' if index < 9 else '6') and values[5] == values[6]
    assert values[7:] == ['SKIPPED', '0', '0', '0', '0', 'ALREADY_SUCCESSFUL', 'step already successful for business date']
observed = json.loads((run/'pg402-native-final-private.json').read_text())
old = json.loads((run/'pg401-native-final-private.json').read_text())
assert observed['units']['schubert-nk-morning-controller.service']['ExecMainStatus'] == '30'
for name in ['schubert-nk-morning-controller.service', 'schubert-nk-backup.service', 'schubert-nk-cleanup.service', 'schubert-nk-expiry-cleanup.service']:
    assert observed['units'][name]['kernelEmpty']
    if 'controller' not in name: assert observed['units'][name]['ExecMainStatus'] == '0'
assert observed['units']['artemis.service']['InvocationID'] != old['units']['artemis.service']['InvocationID']
assert observed['invalid'] and observed['permits'] == 0 and observed['namespaces']['startup'] == ['epoch.current']
assert all(not observed['namespaces'][n] for n in ['maintenance', 'backup-request', 'cleanup-request', 'expiry-request'])
assert all(observed['brokerJournal']['requiredVendorCodes'].values()) and observed['brokerJournal']['errorEntries'] == 0
main = (run/'pg402-native/MorningProcessMain-reached.txt').read_text()
assert re.search(r'coveredLines=.*(?:,|=)260,', main)
gate = (run/'pg402-native/MorningGateEvidence-reached.txt').read_text()
for name in ['broker(', 'postgres(', 'release(', 'stop(', 'retention(']: assert name in gate
previous = (run/'pg402-native/MorningPreviousBroker-reached.txt').read_text()
assert 'capture(' in previous and 'recheck()' in previous and 'collect(' in previous
retention = (run/'pg402-native/MorningBackupRetention-reached.txt').read_text()
for method in ['use(', 'collect(', 'recheck()', 'result()']: assert method in retention
backup_before = (run/'pg402-backup-before-private.json').read_bytes()
backup_after = (run/'pg402-backup-after-private.json').read_bytes()
assert backup_before == backup_after
completion = (run/'pg402-native/MorningBrokerExecution-reached.txt').read_text()
assert 'MorningBrokerExecution$Completion' in completion and 'observe()' in completion
start = int((run/'pg402-native-start.log').stat().st_mtime)
exec_times = {}
for line in (run/'pg402-native-exec-times.log').read_text().splitlines():
    path, at, size = line.split()
    role = pathlib.Path(path).stem
    assert int(at) >= start and int(size) > 0
    exec_times[role] = int(at)
assert set(exec_times) == {'parent', 'backup', 'cleanup', 'expiry'}
coverage = {n:json.loads((run/f'pg402-native/{n}-union.json').read_text()) for n in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']}
assert all(value['classByteMismatch'] == 0 for value in coverage.values())
base = json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG402-backup-retention-baseline/manifest.json').read_text())
signed = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private/pg402-release/RELEASE-MANIFEST.json')
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {'id':'PG402-native-five-actual-gates', 'formal':False, 'sourceCommit':base['sourceCommit'], 'branch':'dev-foundation', 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15', 'command':'pg402_deploy.sh signed exact source; pg402_native.sh once; pg402_collect_native.sh same-byte actual four exec; private full DB readback', 'applicationParentExit':30, 'wholeStartupAccepted':False, 'bugs':['BUG-384','BUG-385'], 'ssc':['SSC-129','SSC-130'], 'ykt':['YKT-304','YKT-305'], 'fullRegression':{'tests':base['tests'],'failures':0,'errors':0,'skipped':0,'staticModulesZero':6}, 'releaseManifestSha256':sha(signed), 'actual':{'old92RowsUnchanged':True,'rows':92,'backupAttempt':16,'backupFreshSkip':2,'cleanupAttempt':8,'cleanupFreshSkip':7,'expiryAttempt':4,'expiryFreshSkip':1,'actualOwnedDatabaseReleaseBrokerFramesConstructed':True,'mainReturnLineCovered':227,'startupInvalid':True,'permitsIssued':0,'requestOwnerIntentEntries':0}, 'coverage':{'classByteMismatch':0,'sameRunRoles':['parent','backup','cleanup','expiry'],'oldInspectorExecExcluded':True,'moduleUnion':coverage,'totalMissed':miss,'resolvedFromOwnHost':{k:sum(v[k]['missed'] for v in base['coverage'].values())-miss[k] for k in miss}}, 'nativeExecHashes':{n:sha(run/f'pg402-native/{n}.exec') for n in ['parent','backup','cleanup','expiry']}, 'logs':[{'path':str(run/name),'sha256':sha(run/name)} for name in ['pg402-six.log','pg402-deploy.log','pg402-native-delivery.log','pg402-native-db-before-full.log','pg402-native-db-final-full.log','pg402-native-exec-times.log']], 'reachabilityHashes':{n:sha(run/f'pg402-native/{n}-reached.txt') for n in ['MorningProcessMain','MorningBrokerExecution','MorningGateEvidence','MorningDatabaseSession']}, 'limitations':['actual gate bytes are not emitted or issued; independent golden comparison is host only','STOP_SET/retention/ten step full proof/publication/A handoff/root API Web/CHR incomplete','native negative/hard-timeout/coverage100/formal run24 unchanged'], 'redaction':'No raw journal/InvocationIDs/native exec/credentials/tokens/session/master/dump in Git'}
manifest.update(bugs=['BUG-387'], ssc=['SSC-131','SSC-132','SSC-133'], ykt=['YKT-307'])
manifest['actual'].pop('old92RowsUnchanged')
manifest['actual'].update(old102RowsUnchanged=True, rows=112, backupAttempt=18, cleanupAttempt=10, expiryAttempt=6,
    mainReturnLineCovered=260, actualRetainerMode='REUSED_SUCCESS',
    actualFiveGateFramesConstructed=True, backupInventoryUnchanged=True,
    backupInventorySha256=hashlib.sha256(backup_before).hexdigest(),
    actualInitialStoppedUnitsAndOldJournalFrameConstructed=True,
    actualOldJournalCapturedAndRechecked=True,
    oldJournalRawRetainedAndCompleteCanonicalContentCompared=True)
manifest['reachabilityHashes']['MorningPreviousBroker'] = sha(run/'pg402-native/MorningPreviousBroker-reached.txt')
manifest['reachabilityHashes']['MorningBackupRetention'] = sha(run/'pg402-native/MorningBackupRetention-reached.txt')
manifest['limitations'] = ['actual five gate bytes are not emitted or issued; independent golden comparison is host only',
    'native NEW_SUCCESS8-to7/FAILED and retention negative routes pending; host positive/negative passed',
    'first-bootstrap journal-absent route/ten-step full proof/publication/A handoff/API/Web/CHR incomplete',
    'native negatives/hard-timeout/coverage100/formal run24 unchanged']
out = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':miss,'resolved':manifest['coverage']['resolvedFromOwnHost']}))
