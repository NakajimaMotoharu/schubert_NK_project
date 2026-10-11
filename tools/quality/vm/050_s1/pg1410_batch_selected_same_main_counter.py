"""Add one fresh selected exec to qualified current Main evidence; no fresh whole-run claim."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1406_batch_boundary_selected import SOURCE,W,J,T,CHANGED,class_hashes

def require(v):
    if not v:raise ValueError('same Main selected counter qualification refused')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077);require(not subprocess.check_output(['git','status','--porcelain']))
    require(subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],text=True).splitlines()==CHANGED)
    current=W/'pg1401-current-bootstrap-ten-native-v1';eight=W/'pg1341-published-eight-native-v1';host=W/'pg1279-held-channel-six-host-v1';selected=W/'pg1409-batch-boundary-selected-v1'
    require(sha(current/'manifest.safe.json')=='c05911e9ddbf292c2375d155166fc8602bcc41345de47a15e8b7f723efdd1502'and sha(eight/'manifest.safe.json')=='99ace9ae4497d33c331700ec656502e543de2e64192ba5350b4f1dfa456f4d71'and sha(host/'manifest.safe.json')=='1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b')
    old=json.loads((current/'manifest.safe.json').read_bytes());e=json.loads((eight/'manifest.safe.json').read_bytes());h=json.loads((host/'manifest.safe.json').read_bytes());s=json.loads((selected/'manifest.safe.json').read_bytes())
    require(s['actualExit']==0 and s['productionMainSource']==SOURCE and s['staticIssues']==0 and s['allBatchMainClassBytesEqual1279']is True and s['freshXmlRequired']is True and s['notRunCount']==0)
    require(sum(v['tests']for v in s['testCounts'].values())==24 and all(v['failures']==v['errors']==v['skipped']==0 for v in s['testCounts'].values()))
    for n,d in s['sourceHashes'].items():require(sha(T/n)==d)
    require(sha(selected/'selected.exec')==s['execSha256'])
    modules=('protocol','storage','bootstrap','api','web','batch');data=[]
    for m in modules:
        p=host/m/'jacoco.exec';require(sha(p)==e['hostExecHashes'][m]==h['moduleResults'][m]['execSha256']);data.append(p)
    for i,v in enumerate(e['selected']):
        p=eight/(str(i)+'.exec');require(sha(p)==v['sha256']and p.stat().st_size==v['bytes']);data.append(p)
    for i,d in enumerate(old['bootstrapNativeHashes']):
        p=current/('bootstrap-'+str(i)+'.exec');require(sha(p)==d);data.append(p)
    data.append(selected/'selected.exec');require(len(data)==17)
    require(class_hashes(selected/'schubert-nk-batch-0.1.0-SNAPSHOT.jar')==class_hashes(host/'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'))
    helper=W/'pg571-current-ten-native-v2/classes';require(sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a')
    cp=[str(helper)];repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        v=list(repo.glob(pattern));require(len(v)==1);cp.append(str(v[0]))
    run=W/'pg1410-batch-selected-same-main-counter-v1';run.mkdir(mode=0o700);counters={}
    for m in modules:
        jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');require(sha(jar)==h['moduleResults'][m]['jarSha256'])
        r=subprocess.run([str(J/'bin/java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*map(str,data)],capture_output=True,timeout=45)
        with(run/(m+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
        require(r.returncode==0 and not r.stderr);v=json.loads(r.stdout);require(v['classByteMismatch']==0 and v['formal']is False);counters[m]=v
    kinds=('LINE','METHOD','CLASS','BRANCH');remaining={k:sum(v[k]['missed']for v in counters.values())for k in kinds};gain={k:old['remaining'][k]-remaining[k]for k in kinds};require(all(v>=0 for v in gain.values()))
    value={'run':'PG1410-batch-selected-same-main-counter-v1','actualExit':0,'productionMainSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostWholeRun':'PG1279','hostWholeTestsHistorical':3569,'freshSelectedTests':24,'newTestMethods':3,'sameMainByte':True,'classByteMismatch':0,'qualifiedNativeStreams':10,'totalExecInputs':17,'selectedManifestSha256':sha(selected/'manifest.safe.json'),'previousNativeManifestSha256':sha(current/'manifest.safe.json'),'moduleCounters':counters,'gainVs1401':gain,'remaining':remaining,'formalAccepted':False,'freshWholeRunClaimed':False,'coverage100':all(n==0 for n in remaining.values()),'vmActions0':True}
    with(run/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in ('actualExit','gainVs1401','remaining','freshSelectedTests','formalAccepted')}));return 0

if __name__=='__main__':raise SystemExit(main())
