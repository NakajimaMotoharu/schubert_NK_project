"""Preserved actual PG408 observations only; no VM start, secret or raw receipt export."""
import datetime, hashlib, json, pathlib, re
repo = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
before, after = rows('pg408-native-db-before-full.log'), rows('pg408-native-db-final-full.log')
assert len(before) == 152 and len(after) == 162 and after[:152] == before
steps = ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
for i, line in enumerate(after[152:]):
    v = line.split('|')
    assert len(v) == 14 and v[0] == str(153+i) and v[3] == steps[i]
    assert v[5] == v[6] and v[7:] == ['SKIPPED','0','0','0','0','ALREADY_SUCCESSFUL','step already successful for business date']
watch = [json.loads(s) for s in (run/'pg408-root-watch-private.jsonl').read_text().splitlines()]
api = [r['units']['schubert-nk-api.service'] for r in watch if 'units' in r]
root = [r for r in api if r.get('entry') == 'dev.codex.schubert.nk.batch.file.RootServiceLauncher']
ordinary = [r for r in api if r.get('entry') == 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain']
assert root and ordinary
assert len({r['MainPID'] for r in root+ordinary}) == 1
assert len({r['InvocationID'] for r in root+ordinary}) == 1
for r in ordinary:
    p = r['process']
    assert p['Uid'].split() == ['999']*4 and p['Gid'].split() == ['981']*4
    assert p['NoNewPrivs'] == '1'
    assert all(p[k] == '0000000000000000' for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb'])
assert watch[-1]['terminalObserved'] and watch[-1]['readyClaimed'] is False
blocks = (run/'pg408-native-full18-private.txt').read_text().strip().split('\n\n')
receipts = [dict(s.split('=',1) for s in b.splitlines()) for b in blocks]
assert len(receipts) == 3 and all(len(r) == 18 for r in receipts)
m,a,w = receipts
assert m['Id'] == 'schubert-nk-morning-controller.service' and a['Id'] == 'schubert-nk-api.service'
assert (m['ExecMainCode'],m['ExecMainStatus'],m['Result']) == ('1','30','exit-code')
assert (a['ExecMainCode'],a['ExecMainStatus'],a['Result']) == ('1','1','exit-code')
assert a['InvocationID'] == ordinary[0]['InvocationID'] and w['MainPID'] == '0'
assert all(r['MainPID'] == r['ControlPID'] == '0' and r['Job'] == '' for r in receipts)
journal = (run/'pg408-broker-journal-private.txt').read_text()
assert 'AMQ229031: Unable to validate user' in journal and 'Username: nk_api;' in journal
assert (run/'pg408-backup-before-private.json').read_bytes() == (run/'pg408-backup-after-private.json').read_bytes()
roles = ['parent','backup','cleanup','expiry']
assert (run/'pg408-native/root-api-observed.exec').stat().st_size == 0
base = json.loads((repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG408-root-recovery-baseline/manifest.json').read_text())
assert base['sourceCommit'] == '32c6a7b1e79abf114901003c4a8f1300b33bf0c0'
coverage = {n:json.loads((run/f'pg408-native/{n}-union.json').read_text()) for n in ['protocol','storage','bootstrap','api','web','batch']}
assert all(v['classByteMismatch'] == 0 for v in coverage.values())
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {
 'id':'PG408-native-same-pid-auth-refused','formal':False,'sourceCommit':base['sourceCommit'],'branch':'dev-foundation',
 'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15',
 'command':'pg408_deploy.sh signed same source; pg408_native.sh one external Morning; pg408_collect_union.py preserved four exec',
 'collectorExit':0,'applicationParentExit':30,'applicationApiExit':1,'wholeStartupAccepted':False,
 'bugs':['BUG-403','BUG-409','BUG-410','BUG-411','BUG-412'],'ssc':['SSC-143','SSC-144','SSC-145','SSC-146','SSC-147'],
 'actual':{'old152RowsAll14ColumnsUnchanged':True,'rows':162,'freshSkippedSteps':10,'backupInventoryUnchanged':True,
   'genuineRootEntry':True,'samePidOrdinaryApi':True,'sameInvocation':True,'ordinaryUid':999,'ordinaryGid':981,
   'ordinaryAllFiveCapabilitySetsZero':True,'ordinaryNoNewPrivileges':True,'apiAuthenticationRefused':True,
   'rootExecDumpEmpty':True,'rootPositiveCoverageCollected':False,'webStarted':False,'businessReady':False},
 'coverage':{'classByteMismatch':0,'sameRunRoles':roles,'moduleUnion':coverage,'totalMissed':miss,
   'resolvedFromOwnHost':{k:sum(v[k]['missed'] for v in base['coverage'].values())-miss[k] for k in miss}},
 'nativeExecHashes':{n:sha(run/f'pg408-native/{n}.exec') for n in roles},
 'logs':[{'path':str(run/n),'sha256':sha(run/n)} for n in ['pg408-six.log','pg408-deploy.log','pg408-native-driver.log',
   'pg408-native-db-before-full.log','pg408-native-db-final-full.log','pg408-native-full18-private.txt',
   'pg408-root-watch-private.jsonl','pg408-broker-journal-private.txt','pg408-backup-after-private.json']],
 'limitations':['S1/S2/S3 full negative coverage pending','Root positive exec has no shutdown-hook coverage dump',
   'Api unassembled runtime/full layout registration, Web readiness and actual CHR pending','formal run24 and 48.3% unchanged'],
 'redaction':'No raw DB/receipts/journal/native exec/credentials/session/key/master/dump exported to Git'}
out = repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True,exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':miss,'resolved':manifest['coverage']['resolvedFromOwnHost']}))
