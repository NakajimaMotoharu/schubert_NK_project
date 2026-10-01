"""Same-source actual native issuer frame reachability; not startup or formal acceptance."""
import datetime, hashlib, json, pathlib, re
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before = rows('pg401-native-db-before-full.log')
after = rows('pg401-native-db-final-full.log')
assert len(before) == 92 and len(after) == 102 and after[:92] == before
steps = ['BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION', 'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN', 'CLEAN_TRANSFER', 'CLEAN_EXPIRY']
for index, line in enumerate(after[92:]):
    values = line.split('|')
    assert len(values) == 14 and values[0] == str(93 + index) and values[3] == steps[index]
    assert values[4] == ('17' if index < 2 else '9' if index < 9 else '5') and values[5] == values[6]
    assert values[7:] == ['SKIPPED', '0', '0', '0', '0', 'ALREADY_SUCCESSFUL', 'step already successful for business date']
observed = json.loads((run/'pg401-native-final-private.json').read_text())
old = json.loads((run/'pg400-native-final-private.json').read_text())
assert observed['units']['schubert-nk-morning-controller.service']['ExecMainStatus'] == '30'
for name in ['schubert-nk-morning-controller.service', 'schubert-nk-backup.service', 'schubert-nk-cleanup.service', 'schubert-nk-expiry-cleanup.service']:
    assert observed['units'][name]['kernelEmpty']
    if 'controller' not in name: assert observed['units'][name]['ExecMainStatus'] == '0'
assert observed['units']['artemis.service']['InvocationID'] != old['units']['artemis.service']['InvocationID']
assert observed['invalid'] and observed['permits'] == 0 and observed['namespaces']['startup'] == ['epoch.current']
assert all(not observed['namespaces'][n] for n in ['maintenance', 'backup-request', 'cleanup-request', 'expiry-request'])
assert all(observed['brokerJournal']['requiredVendorCodes'].values()) and observed['brokerJournal']['errorEntries'] == 0
main = (run/'pg401-native/MorningProcessMain-reached.txt').read_text()
assert re.search(r'coveredLines=.*(?:,|=)227,', main)
gate = (run/'pg401-native/MorningGateEvidence-reached.txt').read_text()
for name in ['broker(', 'postgres(', 'release(', 'stop(']: assert name in gate
previous = (run/'pg401-native/MorningPreviousBroker-reached.txt').read_text()
assert 'capture(' in previous and 'recheck()' in previous and 'collect(' in previous
completion = (run/'pg401-native/MorningBrokerExecution-reached.txt').read_text()
assert 'MorningBrokerExecution$Completion' in completion and 'observe()' in completion
start = int((run/'pg401-native-start.log').stat().st_mtime)
exec_times = {}
for line in (run/'pg401-native-exec-times.log').read_text().splitlines():
    path, at, size = line.split()
    role = pathlib.Path(path).stem
    assert int(at) >= start and int(size) > 0
    exec_times[role] = int(at)
assert set(exec_times) == {'parent', 'backup', 'cleanup', 'expiry'}
coverage = {n:json.loads((run/f'pg401-native/{n}-union.json').read_text()) for n in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']}
assert all(value['classByteMismatch'] == 0 for value in coverage.values())
base = json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG401-stop-journal-content-baseline/manifest.json').read_text())
signed = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private/pg401-release/RELEASE-MANIFEST.json')
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {'id':'PG401-native-four-actual-gates', 'formal':False, 'sourceCommit':base['sourceCommit'], 'branch':'dev-foundation', 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15', 'command':'pg401_deploy.sh signed exact source; pg401_native.sh once; pg401_collect_native.sh same-byte actual four exec; private full DB readback', 'applicationParentExit':30, 'wholeStartupAccepted':False, 'bugs':['BUG-384','BUG-385'], 'ssc':['SSC-129','SSC-130'], 'ykt':['YKT-304','YKT-305'], 'fullRegression':{'tests':base['tests'],'failures':0,'errors':0,'skipped':0,'staticModulesZero':6}, 'releaseManifestSha256':sha(signed), 'actual':{'old92RowsUnchanged':True,'rows':92,'backupAttempt':16,'backupFreshSkip':2,'cleanupAttempt':8,'cleanupFreshSkip':7,'expiryAttempt':4,'expiryFreshSkip':1,'actualOwnedDatabaseReleaseBrokerFramesConstructed':True,'mainReturnLineCovered':227,'startupInvalid':True,'permitsIssued':0,'requestOwnerIntentEntries':0}, 'coverage':{'classByteMismatch':0,'sameRunRoles':['parent','backup','cleanup','expiry'],'oldInspectorExecExcluded':True,'moduleUnion':coverage,'totalMissed':miss,'resolvedFromOwnHost':{k:sum(v[k]['missed'] for v in base['coverage'].values())-miss[k] for k in miss}}, 'nativeExecHashes':{n:sha(run/f'pg401-native/{n}.exec') for n in ['parent','backup','cleanup','expiry']}, 'logs':[{'path':str(run/name),'sha256':sha(run/name)} for name in ['pg401-six.log','pg401-deploy.log','pg401-native-delivery.log','pg401-native-db-before-full.log','pg401-native-db-final-full.log','pg401-native-exec-times.log']], 'reachabilityHashes':{n:sha(run/f'pg401-native/{n}-reached.txt') for n in ['MorningProcessMain','MorningBrokerExecution','MorningGateEvidence','MorningDatabaseSession']}, 'limitations':['actual gate bytes are not emitted or issued; independent golden comparison is host only','STOP_SET/retention/ten step full proof/publication/A handoff/root API Web/CHR incomplete','native negative/hard-timeout/coverage100/formal run24 unchanged'], 'redaction':'No raw journal/InvocationIDs/native exec/credentials/tokens/session/master/dump in Git'}
manifest.update(bugs=['BUG-386'], ssc=['SSC-131','SSC-132'], ykt=['YKT-306'])
manifest['actual'].update(rows=102, backupAttempt=17, cleanupAttempt=9, expiryAttempt=5,
    actualInitialStoppedUnitsAndOldJournalFrameConstructed=True,
    actualOldJournalCapturedAndRechecked=True,
    oldJournalRawRetainedAndCompleteCanonicalContentCompared=True)
manifest['reachabilityHashes']['MorningPreviousBroker'] = sha(run/'pg401-native/MorningPreviousBroker-reached.txt')
manifest['limitations'] = ['actual four gate bytes are not emitted or issued; independent golden comparison is host only',
    'first-bootstrap journal-absent route/retention/ten-step full proof/publication/A handoff/API/Web/CHR incomplete',
    'native negatives/hard-timeout/coverage100/formal run24 unchanged']
out = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':miss,'resolved':manifest['coverage']['resolvedFromOwnHost']}))
