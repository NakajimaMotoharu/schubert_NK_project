"""Reuse existing resolved-catch tool on changed Bootstrap/Batch sources, no product generation/run."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tarfile

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from source_catch_context_inventory_test import facts
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';slot=w/'pg37042-current287-catch-facts-v1';assert not slot.exists();os.umask(0o077)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
sp=b/'evidence/PG36960-current287-root-pmd-v1/manifest.json';static=load(sp);cpmeta=load(b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json');assert static['sourceCore']==cpmeta['sourceCore']=='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9'
assert all(sha(r/path)==h for path,h in static['sourceInputs'].items())
assert all(sha(Path(path))==h for path,h in cpmeta['sdkHashes'].items())
helper=r/'tools/quality/SourceCatchContextInventory.java';helperHash=sha(helper);assert subprocess.check_output(['git','diff','9b4a294435ea56780f955d71a9d8c604cc7a16ca','--',str(helper.relative_to(r))])==b''
slot.mkdir();(slot/'toolclasses').mkdir();snapshot=slot/'snapshot';snapshot.mkdir()
with (slot/'source.tar').open('xb') as f:subprocess.run(['git','archive','--format=tar',static['sourceCore'],'src/schubert-nk-bootstrap/src/main/java','src/schubert-nk-batch/src/main/java'],stdout=f,check=True)
with tarfile.open(slot/'source.tar') as t:t.extractall(snapshot,filter='data')
assert {str(p.relative_to(snapshot)):sha(p) for p in snapshot.glob('src/*/src/main/java/**/*.java')}==static['sourceInputs']
def save(name,value):(slot/name).open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def step(name,cmd):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();save(name+'.begin.json',dict(command=cmd,startUTC=start,cwd=str(slot)))
 with (slot/(name+'.stdout')).open('xb') as out,(slot/(name+'.stderr')).open('xb') as err:
  child=subprocess.run(cmd,cwd=slot,stdout=out,stderr=err,timeout=180,env=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',LANG='C.UTF-8'))
 v=dict(actualExit=child.returncode,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdoutSha256=sha(slot/(name+'.stdout')),stderrSha256=sha(slot/(name+'.stderr')));save(name+'.exit.json',v);assert child.returncode==0;return v
jdk=tc/'jdk-25.0.4/bin';stages={};stages['helperCompile']=step('helper-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','-d',str(slot/'toolclasses'),str(helper)])
toolClasses={str(p.relative_to(slot/'toolclasses')):sha(p) for p in (slot/'toolclasses').rglob('*.class')};joined=[];targets=load(b/'evidence/PG37040-f03-specific38-applicability-v1/remaining-unmatched.json');generic=[x for x in targets if x['raw']['rule']=='AvoidCatchingGenericException'];assert len(generic)==261
allfacts={}
for module in ['bootstrap','batch']:
 cp=':'.join(cpmeta['contexts'][module]['classpath']);source=snapshot/('src/schubert-nk-'+module+'/src/main/java')
 stages[module]=step(module,[str(jdk/'java'),'-Xmx1536m','-cp',str(slot/'toolclasses'),'SourceCatchContextInventory',str(source),cp]);values=facts((slot/(module+'.stdout')).read_text());allfacts[module]=values
 for item in generic:
  raw=item['raw'];prefix='src/schubert-nk-'+module+'/src/main/java/'
  if not raw['path'].startswith(prefix):continue
  found=[x for x in values if x['path']==raw['path'][len(prefix):] and int(x['firstLine'])<=int(raw['beginline'])<=int(x['lastLine'])];assert len(found)==1
  joined.append(dict(originalFindingIndex=item['rawFindingIndex'],raw=raw,sourceSha256=item['sourceSha256'],facts=found[0],classification='FACTS_ONLY_NOT_DISPOSITION'))
assert len(joined)==261 and len({x['originalFindingIndex'] for x in joined})==261
assert not list(snapshot.rglob('*.class')) and {str(p.relative_to(slot/'toolclasses')):sha(p) for p in (slot/'toolclasses').rglob('*.class')}==toolClasses
assert all(sha(r/path)==h for path,h in static['sourceInputs'].items()) and sha(helper)==helperHash
out=b/'evidence/PG37042-current287-catch-facts-v1';out.mkdir();(out/'joined-facts.json').write_text(json.dumps(joined,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=static['sourceCore'],sourceInputs=static['sourceInputs'],qualifiedPriorStatic=ref(sp),helper=dict(path=str(helper.relative_to(r)),sha256=helperHash,lastChangedCommit='9b4a294435ea56780f955d71a9d8c604cc7a16ca'),stages=stages,joinedWarnings=261,allCatchFacts={k:len(v) for k,v in allfacts.items()},toolClassHashes=toolClasses,productClassfilesGenerated=0,productTestsExecuted=0,productRuntimeClassesInToolJvmClasspath=0,facts=ref(out/'joined-facts.json'),classificationUnchanged=True,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,joined=261,allCatchFacts=value['allCatchFacts'],productGenerated=0,productTests=0)))
