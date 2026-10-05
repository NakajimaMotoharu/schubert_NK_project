"""Completed same-source connection evidence; raw journal/session/DB remains private."""
import hashlib,json,pathlib,subprocess,collections
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
S='c8ad413437be409f70ec37bdba33c5e3cd21790b'
subprocess.run(['git','diff','--exit-code',S,'--','src','pom.xml'],cwd=R,check=True)
stems=['pg472-parent-observer-v1','pg472-readback-native-v1','pg472-a01-native-v1','pg472-l01-native-v1','pg472-native-stop-v1']
for n in stems:assert (W/(n+'.exit')).read_text().strip()=='0'
rs=[json.loads(x) for x in (W/'pg472-parent-watch-private-v1.jsonl').read_text().splitlines()]
ts=[r for r in rs if r.get('terminalObserved')];assert len(ts)==1
t=ts[0];assert t['parentResult']=='success' and t['parentExit']=='0' and t['rootsCaptured']==t['readyObserved']==['api','web'] and t['caddyTlsLogin200'] and all(t['backendAlive'].values())
for role in ['api','web']:assert any(r.get('ready')==role and r['sameRootOrdinary'] and r['info']['commit']==S for r in rs)
payload="""import pathlib,hashlib,json,os
assert os.geteuid()==0
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg472-native-stop-v1')
assert (p/'complete.private').read_bytes()==b'allNewScopesReturnedNormally=true\\noldUnknownNormalized=false\\n'
assert (p/'body.complete.private').read_bytes()==b'sameSource=true\\nallEightOwnedTerminal=true\\nrows381=true\\npostL01BusinessPreserved=true\\noriginalBackupStartupPreserved=true\\nstarts0=true\\n'
assert len(list(p.glob('*.stopped.private')))==8
print(json.dumps({'normalScopes':True,'oldUnknownNormalized':False,'allEightReceipts':True,'bodySha256':hashlib.sha256((p/'body.complete.private').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((p/'complete.private').read_bytes()).hexdigest()}))
"""
v=subprocess.run(['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
stop=json.loads(v.stdout)
l=json.loads((W/'pg472-l01-v1/L01-observed.private.json').read_text());assert l['status']=='OBSERVED_NOT_ACCEPTED' and l['productionSource']==S
a=json.loads((R/'program/characterization/reports/nk/PG472-native-a01-v1/artifacts/CHR-A01.json').read_text());assert a['status']=='PASS' and a['csrf']=='<TOKEN>' and a['passwordValue']==''
m={'id':'PG472-real-parent-connection-v1','productionSource':S,'branch':'dev-foundation','tests':['PT-OPS-PG472-PARENT001','PT-OPS-PG472-READ001','PT-OPS-PG472-READ002','PT-OPS-PG472-TERM001','PT-OPS-PG472-TERM002','PT-OPS-PG472-NATIVE001','PT-OPS-PG472-CHR001'],'actualParentDone':True,'sameRootOrdinaryApiWeb':True,'sameSourceInfoSocketsIdentities':True,'caddyTlsLogin200':True,'parentJournalSha256':hashlib.sha256((W/'pg472-parent-journal-private-v1.jsonl').read_bytes()).hexdigest(),'old371Full14Preserved':True,'rows381New10Skipped':True,'namespace53Intent0':True,'originalBackupPreserved':True,'ownedStop':stop,'readbackIndependentAssertions':396,'stopIndependentJavaAssertions':24,'stopIndependentPythonAssertions':265,'A01':'PASS','L01':{'status':'OBSERVED_NOT_ACCEPTED','relatedQA':'QA-051','actions':dict(collections.Counter(l['databaseActions'])),'displayedRows':l['displayedRows'],'detailsCount':l['detailsElements'],'privateSha256':hashlib.sha256((W/'pg472-l01-v1/L01-observed.private.json').read_bytes()).hexdigest(),'fixtureReset':False,'comparisonAccepted':False},'runs':{n:{'actualExit':0,'started':(W/(n+'.started')).read_text().strip(),'completed':(W/(n+'.completed')).read_text().strip()} for n in stems},'environment':{'JDK':'25.0.4','JaCoCo':'0.8.15','guest':'Ubuntu26.04'},'rawInGit':False,'formalUpdated':False,'globalCoverage100':False,'ITSTAccepted':False}
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG472-real-parent-connection-v1/manifest.json';assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x') as f:f.write(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'actualExit':0,'parentDone':True,'scopeNormal':True,'A01':'PASS','L01Accepted':False,'manifestSha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
