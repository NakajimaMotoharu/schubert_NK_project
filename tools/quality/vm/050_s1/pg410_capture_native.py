"""PG410 actual observations; frozen PG408 source/class bytes, never current target classes."""
import datetime
import hashlib
import json
import pathlib
import re

repo = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name):
    return [v for v in (run / name).read_text().splitlines() if re.match(r'^\d+\|', v)]
before = rows('pg410-native-db-before-full.log')
after = rows('pg410-native-db-final-full.log')
assert len(before) == 172 and len(after) == 182 and after[:172] == before
steps = ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
for i, row in enumerate(after[172:]):
    v = row.split('|')
    assert len(v) == 14 and v[0] == str(173+i) and v[3] == steps[i]
    assert v[5] == v[6] and v[7:] == ['SKIPPED','0','0','0','0','ALREADY_SUCCESSFUL','step already successful for business date']
watch = [json.loads(v) for v in (run/'pg410-root-watch-private.jsonl').read_text().splitlines()]
api = [v['units']['schubert-nk-api.service'] for v in watch if 'units' in v]
root = [v for v in api if v.get('entry') == 'dev.codex.schubert.nk.batch.file.RootServiceLauncher']
ordinary = [v for v in api if v.get('entry') == 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain']
assert root and ordinary
assert len({v['MainPID'] for v in root+ordinary}) == len({v['InvocationID'] for v in root+ordinary}) == 1
for v in ordinary:
    p = v['process']
    assert p['Uid'].split() == ['999']*4 and p['Gid'].split() == ['981']*4
    assert p['NoNewPrivs'] == '1'
    assert all(p[k] == '0000000000000000' for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb'])
assert watch[-1]['terminalObserved'] and not watch[-1]['readyClaimed']
blocks = (run/'pg410-native-full18-private.txt').read_text().strip().split('\n\n')
receipts = [dict(v.split('=',1) for v in b.splitlines()) for b in blocks]
assert len(receipts) == 3 and all(len(v) == 18 for v in receipts)
morning, service, web = receipts
assert (morning['ExecMainCode'],morning['ExecMainStatus'],morning['Result']) == ('1','30','exit-code')
assert (service['ExecMainCode'],service['ExecMainStatus'],service['Result']) == ('1','50','exit-code')
assert service['InvocationID'] == ordinary[0]['InvocationID'] and web['MainPID'] == '0'
assert all(v['MainPID'] == v['ControlPID'] == '0' and v['Job'] == '' for v in receipts)
assert 'AMQ229031: Unable to validate user' not in (run/'pg410-broker-journal-private.txt').read_text()
assert (run/'pg410-backup-before-private.json').read_bytes() == (run/'pg410-backup-after-private.json').read_bytes()
assert (run/'pg410-native/root-api-observed.exec').stat().st_size == 0
base = json.loads((repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG408-root-recovery-baseline/manifest.json').read_text())
assert base['sourceCommit'] == '32c6a7b1e79abf114901003c4a8f1300b33bf0c0'
coverage = {n: json.loads((run/f'pg410-native/{n}-union.json').read_text()) for n in ['protocol','storage','bootstrap','api','web','batch']}
assert all(v['classByteMismatch'] == 0 for v in coverage.values())
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {
    'id':'PG410-native-effective-auth-exit50','formal':False,'sourceCommit':base['sourceCommit'],
    'branch':'dev-foundation','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'environment':'isolated Ubuntu26.04/kernel7/PostgreSQL18.6/JDK25.0.4/Artemis2.56/JaCoCo0.8.15',
    'command':'Pg410KnownAuthRecovery fixed source; pg410_native.sh one external Morning; pg410_collect_native.sh frozen classes',
    'collectorExit':0,'applicationParentExit':30,'applicationApiExit':50,'wholeStartupAccepted':False,
    'bugs':['BUG-411','BUG-412','BUG-415'],'ssc':['SSC-148'],'horizontal':['YKT-328','YKT-330'],
    'actual':{'old172RowsAll14ColumnsUnchanged':True,'rows':182,'freshSkippedSteps':10,'backupInventoryUnchanged':True,
        'genuineRootEntry':True,'samePidOrdinaryApi':True,'sameInvocation':True,'ordinaryUid':999,'ordinaryGid':981,
        'ordinaryAllFiveCapabilitySetsZero':True,'ordinaryNoNewPrivileges':True,'brokerAuthenticationRejectionObserved':False,
        'rootExecDumpEmpty':True,'rootPositiveCoverageCollected':False,'webStarted':False,'businessReady':False},
    'coverage':{'classByteMismatch':0,'sameRunRoles':['parent','backup','cleanup','expiry'],'moduleUnion':coverage,'totalMissed':miss},
    'logs':[{'path':str(run/n),'sha256':sha(run/n)} for n in ['pg410-known-auth-recovery.log','pg410-auth-readback.log',
        'pg410-native-driver.log','pg410-native-db-before-full.log','pg410-native-db-final-full.log',
        'pg410-native-full18-private.txt','pg410-root-watch-private.jsonl','pg410-broker-journal-private.txt','pg410-backup-after-private.json']],
    'limitations':['Exit50 alone does not prove every IO path or full dependency/ready success',
        'PG411 working-tree source was not deployed or mixed into frozen coverage',
        'API full business registration/Web readiness/actual CHR/Root positive coverage remain pending',
        'Formal run24 and48.3% unchanged'],
    'redaction':'No raw DB/receipt/journal/native exec/credential/session/key/master/dump exported to Git'}
out = repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True,exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha256':sha(out/'manifest.json'),'missed':miss}))
