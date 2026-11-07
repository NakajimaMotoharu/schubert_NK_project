"""Current API stop candidate artifact and occurrence lineage, without Product or analyzer replay."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess
r=Path.cwd();base=r/'evidence/01_PT/018_NK-OPS-001/evidence';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
source='7aed8eace7c844c2f79f2e39db766faf914890d5';head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();mains={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/'+n+'.java' for n in ['ApiStopBudget','ApiProcessLifetime']}
oldp=base/'PG22040-current54d5-lineage-style-v1/manifest.json';assert sha(oldp)=='1ac9a761197e533fd921baf35cd1679a927dbbc38ab4b86cc26d05d39a33b68c';old=load(oldp);ap=oldp.parent/'artifacts.json';assert sha(ap)==old['files']['artifacts.json'];prior=load(ap);assert len(prior)==1068
eligible=lambda n:('/src/main/java/' in n and n.endswith('.java')) or '/src/main/resources/' in n or n.startswith('src/deployment/')
held={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'};names=sorted(a['path'] for a in prior);assert all(eligible(n) and Path(n).name not in held for n in names)
for rev in [source,head]:
 tree=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'--','src','program/characterization'],text=True).splitlines();assert sorted(n for n in tree if eligible(n))==names
status=subprocess.check_output(['git','diff','--name-status',old['source'],source,'--',*names],text=True).splitlines();assert sorted(status)==sorted('M\t'+n for n in mains)
assert not subprocess.check_output(['git','diff','--name-only',source,head,'--',*names]);root=old['rootLineage']['source'];status=[x.split('\t') for x in subprocess.check_output(['git','diff','--name-status','--no-renames',root,source,'--',*names],text=True).splitlines()];assert sum(k=='M' for k,n in status)==30 and sum(k=='A' for k,n in status)==3 and len(status)==33
normalp=r.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=load(normalp);assert sha(normalp)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and normal['actualExit']==0 and normal['source']==source
toolp=r.parent/'pgpt-runs/PG379/pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json';assert sha(toolp)=='068773debc310f76f580ef1eea8de2e5735cada128d2e6c677ce62ebdffd2e0a';tool=load(toolp);java={n:h for m in [normal,tool] for n,h in m['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')};assert len(java)==972
current=[];changes=[]
for a in prior:
 n=a['path'];h=sha(r/n);assert n in mains or h==a['sha256']
 if n.endswith('.java'):assert h==java[n]
 row=copy.deepcopy(a);row.update(previousLineage=a['lineage'],lineage=dict(source=old['source'],path=n,oldSha256=a['sha256'],byteChanged=h!=a['sha256'],domain='SAME_PATH_RESPONSIBILITY_RETAINED_NOT_ACCEPTANCE'),sha256=h,staticSource=source)
 assert row['owner']==a['owner'] and row['costOwner']==a['costOwner'] and row['additionalBudgetPp']==0
 if h!=a['sha256']:changes.append(dict(path=n,oldSha256=a['sha256'],sha256=h,owner=a['owner'],costOwner=a['costOwner']))
 current.append(row)
assert len(changes)==2 and all(x['owner']==x['costOwner']=='WBS-P018-05' for x in changes)
op=oldp.parent/'current-occurrences.json';assert sha(op)==old['files']['current-occurrences.json'];rows=load(op);assert len(rows)==1494
oldnormalp=r.parent/'pgpt-runs/PG379/pg22012-web-stop-clock-six-main-compile-v1/manifest.safe.json';oldnormal=load(oldnormalp);assert sha(oldnormalp)=='e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640' and oldnormal['source']==old['source']
oldjava={n:h for n,h in oldnormal['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')};newjava={n:h for n,h in normal['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')};assert set(newjava)==set(oldjava) and {n for n in newjava if newjava[n]!=oldjava[n]}==mains
postp=base/'PG22106-api-stop-static-independent-input-v1/manifest.json';assert sha(postp)=='8337343b6f8e98529d34e6c71e5372afb7f40ead39bbe59de6e218a64356828c';post=load(postp);jp=postp.parent/'style-applicability.json';assert sha(jp)==post['files']['style-applicability.json'];judgments=[x for x in load(jp)['judgments'] if x['raw']['path'] in mains];assert len(judgments)==9
oldids={x['originalId'] for x in rows if x['finding']['path'] in mains};assert len(oldids)==9;assigned={}
for judgment in judgments:
 assert judgment['actualViolation'] is False
 candidates=[x for x in judgment['priorMatches'] if x in oldids and x not in assigned];assert candidates;assigned[candidates[0]]=judgment
assert set(assigned)==oldids;rebound=0
for row in rows:
 n=row['finding']['path'];assert newjava[n]==sha(r/n)
 if n in mains:
  now=assigned[row['originalId']]['raw'];before=row['finding'];assert before['path']==now['path'] and before['message']==now['message'];a=dict(before['attributes']);b=dict(now['attributes'])
  for d in [a,b]:d.pop('beginline');d.pop('endline')
  assert a==b;row.update(currentSourceSha256=newjava[n],finding=dict(path=n,attributes=now['attributes'],message=now['message']),basis='CURRENT22094_RAW_AND22106_INDIVIDUAL_SOURCE_REVIEW');rebound+=1
 else:assert row['currentSourceSha256']==newjava[n]
assert rebound==9 and all(x['classification']=='CONTEXTUAL_NONAPPLICABLE' and x['actualViolation'] is False for x in rows)
out=base/'PG22122-current7aed-lineage-style-v1';assert not out.exists();out.mkdir();write(out/'artifacts.json',current);write(out/'current-occurrences.json',rows)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,source=source,artifactCount=1068,javaSources=972,changed=changes,added=0,removed=0,unchanged=1066,rootLineage=dict(source=root,changed=30,added=3),ownerAndCostPreserved=True,additionalBudgetPp=0,mainSources=967,rawPmdOccurrences=1494,currentReboundOccurrences=9,unchangedOccurrences=1485,applicableViolations=0,unclassified=0,checkstyle=0,rawGateExitPreserved=old['rawGateExitPreserved'],rawMultiplicityPreserved=True,priorDuplicateGroups=old['priorDuplicateGroups'],refs=[dict(path=str(p),sha256=sha(p)) for p in [oldp,postp,normalp,toolp]],files={n:sha(out/n) for n in ['artifacts.json','current-occurrences.json']},wholeF03Accepted=False,wholeG13Accepted=False,whole451Accepted=False,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,checkerSha256=sha(__file__))
write(out/'manifest.json',v);print(json.dumps(dict(actualExit=0,artifacts=1068,modified=2,raw1494=1494,rebound=9,manifestSha256=sha(out/'manifest.json'))))
