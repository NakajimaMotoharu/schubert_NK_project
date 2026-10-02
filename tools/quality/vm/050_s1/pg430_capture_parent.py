"""Fixed PG430 genuine parent observations: safe metadata only, never startup acceptance."""
import datetime
import hashlib
import json
import pathlib

repo = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
source = '91b010509e715e2b097c955d04f21c23f3529966'
watch = [json.loads(s) for s in (run/'pg430-parent-watch-private.jsonl').read_text().splitlines()]
assert len(watch) == 16 and (run/'pg430-parent-watch-errors.log').stat().st_size == 0
assert watch[-1] == {'terminalObserved': True, 'readyObserved': ['api'], 'rootsCaptured': ['api', 'web'], 'automaticStop': False, 'wholeMorningAccepted': False}
info = {'commit': source, 'app': '0.1.0-SNAPSHOT', 'config': '1', 'schema': '025', 'protocol': '0.1.0-SNAPSHOT'}
ready = [v for v in watch if v.get('ready') == 'api']
assert len(ready) == 1 and ready[0]['info'] == info
assert all(ready[0][k] is True for k in ['sameRootOrdinary', 'sameParent', 'ownedSocket'])
generations = {}
for role, pid, invocation in [('api','149131','61b650cebb7d42ab95cf96a12ee58a67'), ('web','151035','a3437b2c9efb40c88bae8949dd6ae46a')]:
    values = [v['states'][role] for v in watch if 'states' in v]
    roots = [v for v in values if v.get('entry') == 'dev.codex.schubert.nk.batch.file.RootServiceLauncher']
    ordinary = [v for v in values if v.get('entry') == f'dev.codex.schubert.nk.{role}.bootstrap.{role.capitalize()}ProcessMain']
    assert roots and ordinary
    actors = roots+ordinary
    assert {v['MainPID'] for v in actors} == {pid} and {v['InvocationID'] for v in actors} == {invocation}
    assert len({v['startTicks'] for v in actors}) == 1
    for v in ordinary:
        p = v['process']
        assert p['NoNewPrivs'] == '1' and all(p[k]=='0000000000000000' for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb'])
        assert len(set(p['Uid'].split())) == len(set(p['Gid'].split())) == 1 and p['Uid'].split()[0] != '0'
    generations[role] = {'sameRootOrdinary': True, 'ordinaryObservations': len(ordinary), 'fiveCapabilitiesZero': True, 'noNewPrivileges': True}
blocks = (run/'pg430-full18-before-pair-private.properties').read_text().strip().split('\n\n')
receipts = [dict(s.split('=',1) for s in b.splitlines()) for b in blocks]
assert len(receipts)==3 and all(len(v)==18 and v['LoadState']=='loaded' and v['MainPID']==v['ControlPID']=='0' and not v['Job'] for v in receipts)
for v, name, invocation, status in zip(receipts, ['morning-controller','api','web'], ['334c1680493c41719f556f6eea92fadc','61b650cebb7d42ab95cf96a12ee58a67','a3437b2c9efb40c88bae8949dd6ae46a'], ['30','143','50'], strict=True):
    assert v['Id']==f'schubert-nk-{name}.service' and v['InvocationID']==invocation and v['ExecMainCode']=='1' and v['ExecMainStatus']==status
journal = (run/'pg430-api-journal-private.log').read_text()
assert 'API cleanup complete' in journal and 'API process stopped' in journal
names = ['pg430-parent-watch-private.jsonl','pg430-parent-watch-errors.log','pg430-full18-before-pair-private.properties','pg430-api-journal-private.log','pg430-web-journal-private.log','pg430-terminal-units-private.log','pg430-parent-native.exec']
manifest = {
    'id':'PG430-native-parent-api-ready-web50','formal':False,'sourceCommit':source,'branch':'dev-foundation',
    'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'command':'one external ordinary Morning; read-only pg430_watch_parent.py; canonical full18 after genuine parent termination',
    'observerExit':0,'parentExit':30,'apiOwnedTermExit':143,'webExit':50,'wholeStartupAccepted':False,
    'actual':{'genuineApi200UpAndSignedInfo':True,'parentReadyThenWebRootOrdinary':True,'apiNormalCleanupObserved':True,'generations':generations,'threeProcessAndJobTerminal':True,'brokerStillActiveAtCollection':True,'pairIntentsRetained':True},
    'testIds':['S3-NATIVE-PARENT-READY','ROOTPAIR008'],'ssc':['SSC-164','SSC-166','SSC-167','SSC-168'],'bugs':['BUG-539'],'horizontal':['YKT-383'],
    'logs':[{'privatePath':str(run/n),'sha256':hashlib.sha256((run/n).read_bytes()).hexdigest()} for n in names],
    'limitations':['Web business assembly/ready, Caddy, original DONE and normal intent retirement pending','Root exec dump and ordinary native coverage not accepted','Current baseline not rewritten; real CHR-A01/L01 pending','Formal PT-WEB-20260925-24/1964PT/53scope/48.3% unchanged'],
    'redaction':'No raw observation/DB/permit/credential/session/token/key/master/dump/native exec exported to Git'
}
out = repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True,exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'wholeStartupAccepted':False}))
