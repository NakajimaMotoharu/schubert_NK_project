import datetime, hashlib, json, pathlib, re
root=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(n): return [x for x in (run/n).read_text().splitlines() if re.match(r'^[0-9]+\|', x)]
before=rows('pg397-native-db-before-full.log'); after=rows('pg397-native-db-final-full.log')
assert len(before)==63 and len(after)==73 and after[:63]==before
steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
for i,line in enumerate(after[63:]):
    r=line.split('|'); assert len(r)==14 and r[0]==str(64+i) and r[3]==steps[i]
    assert r[4]==('14' if i<2 else '6' if i<9 else '3') and r[5]==r[6]
    assert r[7:]==['SKIPPED','0','0','0','0','ALREADY_SUCCESSFUL','step already successful for business date']
obs=json.loads((run/'pg397-native-final-private.json').read_text())
old=json.loads((run/'pg397-native-first-private.json').read_text())
assert obs['units']['schubert-nk-morning-controller.service']['ExecMainStatus']=='30'
for name in ['schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:
    assert obs['units'][name]['ExecMainStatus']=='0' and obs['units'][name]['kernelEmpty']
assert obs['units']['artemis.service']['InvocationID']!=old['units']['artemis.service']['InvocationID']
assert obs['units']['artemis.service']['ActiveState']=='active'
assert obs['units']['schubert-nk-expiry-cleanup.service']['InvocationID']!=old['units']['schubert-nk-expiry-cleanup.service']['InvocationID']
assert all(obs['brokerJournal']['requiredVendorCodes'].values()) and obs['brokerJournal']['errorEntries']==0
assert obs['invalid'] and obs['permits']==0 and obs['namespaces']['startup']==['epoch.current']
assert all(not obs['namespaces'][n] for n in ['maintenance','backup-request','cleanup-request','expiry-request'])
base=json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG397-owned-reread-baseline/manifest.json').read_text())
native={n:json.loads((run/f'pg397-native/{n}-union.json').read_text()) for n in ['batch','bootstrap','api']}
keys=['BRANCH','LINE','METHOD','CLASS']
miss={k:sum(n[k]['missed'] for n in native.values())+base['coverage']['web'][k]['missed'] for k in keys}
resolved={k:sum(n[k]['missed'] for n in base['coverage'].values())-miss[k] for k in keys}
manifest={'id':'PG397-native-owned-expiry-reread-and-six-roots','formal':False,'sourceCommit':base['sourceCommit'],'branch':'dev-foundation','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15','command':'signed frozen full-BOM deployment with vendor Unit SuccessExitStatus143; external Morning same-run resume; real parent/backup/cleanup/expiry exec','exitCode':0,'applicationParentExit':30,'wholeStartupAccepted':False,'releaseManifestSha256':'530ebcb517af69334f877befc599f4a34114d1ce517ed1ce6daf0ca8baf7b81a','fullRegression':{'tests':2650,'failures':0,'errors':0,'skipped':0,'staticModulesZero':6},'expected':{'oldRows':63,'newRows':10,'brokerFresh':True,'expiryFresh':True,'sameOwnerRootsCollected':True},'actual':{'oldRowsUnchanged':True,'rows':73,'backupFreshSkip':2,'backupAttempt':14,'cleanupFreshSkip':7,'cleanupAttempt':6,'expiryFreshSkip':1,'expiryAttempt':3,'allFourteenColumnsReadBack':True,'coldBaselineAfterNormalStoppedUnitReload':True,'brokerFresh':True,'fullOpsAndStartupJournalAcceptedByActualParent':True,'expiryFresh':True,'expiryReceiptExit':0,'sameOwnerRootsCollected':True,'sameOwnerExpiryAndCleanupReferencesReread':True,'parentAndAllChildrenTerminal':True,'requestOwnerIntentEntries':0,'startupInvalid':True,'permitsIssued':0},'coverage':{'classByteMismatch':0,'sameByteActualRoles':['parent','backup','cleanup','expiry'],'oldInspectorExecExcluded':True,'moduleUnion':native,'totalMissed':miss,'resolvedFromOwnHost':resolved},'bugs':['BUG-375','BUG-376','BUG-377'],'ssc':['SSC-126','SSC-127','SSC-128'],'ykt':['YKT-292','YKT-293','YKT-294','YKT-295','YKT-296','YKT-297'],'logs':[{'path':str(run/n),'sha256':sha(run/n)} for n in ['pg397-six.log','pg397-deploy.log','pg397-old-unit-base.log','pg397-verify.log','pg397-activate.log','pg397-native-db-before-full.log','pg397-native-db-final-full.log']],'nativeExecHashes':{n:sha(run/f'pg397-native/{n}.exec') for n in ['parent','backup','cleanup','expiry']},'limitations':['five gates/normal issuer/root API Web/CHR not accepted','native root canonical hash not emitted/issued yet; independent hash is not actual output','native negative/hard-timeout and coverage100/formal run24 unchanged'],'redaction':'no raw journal/Unit identities/exec/credential/password/token/session/key/master/dump in Git'}
reach=(run/'pg397-native/root-reached.txt').read_text()
main=(run/'pg397-native/main-reached.txt').read_text()
assert 'MorningStartupRoots' in reach and 'capture()' in reach and 'recheck(' in reach
assert re.search(r'coveredLines=.*(?:,|=)181,',main)
oracle=json.loads((run/'pg397-root-oracle-after.json').read_text());assert len(oracle['roots'])==6
manifest['actual']['rootReturnLineCovered']=181
manifest['independentRootOracle']=oracle
manifest['rootReachabilitySha256']=sha(run/'pg397-native/root-reached.txt')
manifest['mainReachabilitySha256']=sha(run/'pg397-native/main-reached.txt')
out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id'];out.mkdir(parents=True,exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'coverageMissed':miss,'resolved':resolved}))
