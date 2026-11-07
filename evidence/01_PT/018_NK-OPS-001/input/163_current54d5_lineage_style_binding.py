"""Incremental artifact and diagnostic binding from immutable prior public evidence; no Product."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess
r=Path.cwd();base=r/'evidence/01_PT/018_NK-OPS-001/evidence';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
source='54d5c19da0117db49edff7b5ae46207fdee59acc';head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();main='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop.java'
oldp=base/'PG21942-current56720-static-artifact-lineage-v1/manifest.json';assert sha(oldp)=='bb8ed9e6d7e33cc2c29e912cb35e055b73f527026b3c49e3b3aab8fcc36d6673';old=load(oldp);ap=oldp.parent/'artifacts.json';assert sha(ap)==old['files']['artifacts.json'];prior=load(ap);assert len(prior)==1068
eligible=lambda n:('/src/main/java/' in n and n.endswith('.java')) or '/src/main/resources/' in n or n.startswith('src/deployment/')
held={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
names=sorted(a['path'] for a in prior);assert all(eligible(n) and Path(n).name not in held for n in names)
for rev in [source,head]:
 tree=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'--','src','program/characterization'],text=True).splitlines();assert sorted(n for n in tree if eligible(n))==names
status=subprocess.check_output(['git','diff','--name-status',old['source'],source,'--',*names],text=True).splitlines();assert status==['M\t'+main]
assert not subprocess.check_output(['git','diff','--name-only',source,head,'--',*names]);rootsource=old['rootLineage']['source'];rootstatus=[x.split('\t') for x in subprocess.check_output(['git','diff','--name-status','--no-renames',rootsource,source,'--',*names],text=True).splitlines()];assert sum(k=='M' for k,n in rootstatus)==28 and sum(k=='A' for k,n in rootstatus)==3 and len(rootstatus)==31
normalp=r.parent/'pgpt-runs/PG379/pg22012-web-stop-clock-six-main-compile-v1/manifest.safe.json';normal=load(normalp);assert sha(normalp)=='e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640' and normal['actualExit']==0 and normal['source']==source
toolp=r.parent/'pgpt-runs/PG379/pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json';assert sha(toolp)=='068773debc310f76f580ef1eea8de2e5735cada128d2e6c677ce62ebdffd2e0a';tool=load(toolp)
java={n:h for m in [normal,tool] for n,h in m['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')};assert len(java)==972
current=[];changes=[]
for a in prior:
 n=a['path'];h=sha(r/n);assert n==main or h==a['sha256']
 if n.endswith('.java'):assert h==java[n]
 row=copy.deepcopy(a);row.update(previousLineage=a['lineage'],lineage=dict(source=old['source'],path=n,oldSha256=a['sha256'],byteChanged=h!=a['sha256'],domain='SAME_PATH_RESPONSIBILITY_RETAINED_NOT_ACCEPTANCE'),sha256=h,staticSource=source)
 assert row['owner']==a['owner'] and row['costOwner']==a['costOwner'] and row['additionalBudgetPp']==0
 if h!=a['sha256']:changes.append(dict(path=n,oldSha256=a['sha256'],sha256=h,owner=a['owner'],costOwner=a['costOwner']))
 current.append(row)
assert len(changes)==1 and changes[0]['owner']=='WBS-P018-06'
stylep=base/'PG21976-current56720-main-style-projection-v1/manifest.json';assert sha(stylep)=='ea8172824b44ed6e7a67f2ce30b7e063e175517263ddc7f93ec72c322090bff3';style=load(stylep);op=stylep.parent/style['occurrences']['path'];assert sha(op)==style['occurrences']['sha256'];rows=load(op);assert len(rows)==1494
oldjava=style['currentMainInputHashes'];newjava={n:h for n,h in normal['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')};assert set(newjava)==set(oldjava) and [n for n in newjava if newjava[n]!=oldjava[n]]==[main]
postp=base/'PG22026-web-stop-clock-independent-post-v1/manifest.json';assert sha(postp)=='dcb4a48da9389653ef8b8e4232d4961ce259e29c86604c04223765b8c6011ad2';post=load(postp);jp=postp.parent/'style-applicability.json';assert sha(jp)==post['files']['style-applicability.json'];judgment=load(jp);assert judgment['actualViolation'] is False
rebound=0
for row in rows:
 n=row['finding']['path'];assert newjava[n]==sha(r/n)
 if n==main:
  before=row['finding'];now=judgment['raw'];assert before['path']==now['path'] and before['message']==now['message'];a=dict(before['attributes']);b=dict(now['attributes'])
  for d in [a,b]:d.pop('beginline');d.pop('endline')
  assert a==b;row.update(currentSourceSha256=newjava[n],finding=dict(path=n,attributes=now['attributes'],message=now['message']),basis='CURRENT22022_RAW_AND22026_INDIVIDUAL_SOURCE_REVIEW');rebound+=1
 else:assert row['currentSourceSha256']==newjava[n]
assert rebound==1 and all(x['classification']=='CONTEXTUAL_NONAPPLICABLE' and x['actualViolation'] is False for x in rows)
out=base/'PG22040-current54d5-lineage-style-v1';assert not out.exists();out.mkdir();write(out/'artifacts.json',current);write(out/'current-occurrences.json',rows)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,source=source,artifactCount=1068,javaSources=972,changed=changes,added=0,removed=0,unchanged=1067,rootLineage=dict(source=rootsource,changed=28,added=3),ownerAndCostPreserved=True,additionalBudgetPp=0,mainSources=967,rawPmdOccurrences=1494,currentReboundOccurrences=1,unchangedOccurrences=1493,applicableViolations=0,unclassified=0,checkstyle=0,rawGateExitPreserved=style['rawGateExitPreserved'],rawMultiplicityPreserved=True,priorDuplicateGroups=style['duplicateCanonicalGroupsOriginal'],refs=[dict(path=str(p),sha256=sha(p)) for p in [oldp,stylep,postp,normalp,toolp]],files={n:sha(out/n) for n in ['artifacts.json','current-occurrences.json']},wholeF03Accepted=False,wholeG13Accepted=False,whole451Accepted=False,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,checkerSha256=sha(__file__))
write(out/'manifest.json',v);print(json.dumps(dict(actualExit=0,artifacts=1068,modified=1,raw1494=1494,rebound=1,manifestSha256=sha(out/'manifest.json'))))
