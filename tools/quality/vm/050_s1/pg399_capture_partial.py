"""PG399 failed native attempt: preserve actual metadata, never accept unexecuted gates."""
import datetime, hashlib, json, pathlib, re
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before = rows('pg399-native-db-before-full.log')
after = rows('pg399-native-db-final-full.log')
assert len(before) == 73 and len(after) == 82 and after[:73] == before
steps = ['BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION', 'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN', 'CLEAN_TRANSFER']
for index, line in enumerate(after[73:]):
    values = line.split('|')
    assert len(values) == 14 and values[0] == str(74 + index) and values[3] == steps[index]
    assert values[4] == ('15' if index < 2 else '7') and values[5] == values[6]
    assert values[7:] == ['SKIPPED', '0', '0', '0', '0', 'ALREADY_SUCCESSFUL', 'step already successful for business date']
observed = json.loads((run/'pg399-native-final-private.json').read_text())
assert observed['units']['schubert-nk-morning-controller.service']['ExecMainStatus'] == '30'
assert observed['invalid'] and observed['permits'] == 0 and observed['namespaces']['startup'] == ['epoch.current']
assert all(not observed['namespaces'][n] for n in ['maintenance', 'backup-request', 'cleanup-request', 'expiry-request'])
assert all(observed['units'][n]['kernelEmpty'] for n in ['schubert-nk-morning-controller.service', 'schubert-nk-backup.service', 'schubert-nk-cleanup.service'])
assert all(observed['brokerJournal']['requiredVendorCodes'].values()) and observed['brokerJournal']['errorEntries'] == 0
assert not (run/'pg399-native/MorningGateEvidence-reached.txt').read_text()
coverage = {n:json.loads((run/f'pg399-native/{n}-fresh-union.json').read_text()) for n in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']}
assert all(value['classByteMismatch'] == 0 for value in coverage.values())
base = json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG399-issuer-three-gates-baseline/manifest.json').read_text())
manifest = {'id':'PG399-native-broker-double-observation-rejected', 'formal':False, 'sourceCommit':base['sourceCommit'], 'branch':'dev-foundation', 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'environment':base['environment'], 'command':'pg399_native.sh once; actual worker termination/DB readback/native exec; pg399_union_fresh_only.sh', 'applicationParentExit':30, 'wholeStartupAccepted':False, 'bugs':['BUG-385'], 'ykt':['YKT-305'], 'fullRegression':{'tests':2669,'failures':0,'errors':0,'skipped':0,'staticModulesZero':6}, 'releaseManifestSha256':'a0d1214eabf5a8b1bb527737e7a0b97a9e9fc3fb0c587805ebb711c79ae720a3', 'actual':{'old73RowsUnchanged':True,'rows':82,'backupAttempt':15,'backupFreshSkip':2,'cleanupAttempt':7,'cleanupFreshSkip':7,'currentExpiryRows':0,'brokerOpsAndJournalObservedTwice':True,'finalSnapshotCompletionRejected':True,'threeGatesReached':False,'startupInvalid':True,'permitsIssued':0,'requestOwnerIntentEntries':0}, 'coverage':{'classByteMismatch':0,'sameRunRoles':['parent','backup','cleanup'],'staleExpiryExecExcluded':True,'oldInspectorExecExcluded':True,'moduleUnion':coverage,'totalMissed':{k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}}, 'nativeExecHashes':{n:sha(run/f'pg399-native/{n}.exec') for n in ['parent','backup','cleanup']}, 'logs':[{'path':str(run/name),'sha256':sha(run/name)} for name in ['pg399-six.log','pg399-deploy.log','pg399-runtime-inventory.log','pg399-deploy-corrected.log','pg399-native-delivery.log','pg399-native-db-before-full.log','pg399-native-db-final-full.log','pg399-native-exec-times.log']], 'reachabilityHashes':{n:sha(run/f'pg399-native/{n}-reached.txt') for n in ['MorningProcessMain','MorningBrokerExecution','MorningGateEvidence']}, 'limitations':['BUG385 native regression remains failed until corrected-source retest','three gates/legitimate issue/root API Web/CHR not accepted','100% coverage/formal run24 unchanged'], 'redaction':'No raw journal/InvocationIDs/native exec/credentials/tokens/session/master/dump in Git'}
out = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':manifest['coverage']['totalMissed']}))
