"""Physical same-universe and public/internal method ABI comparison, no class initialization."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
oldp=b/'evidence/PG37180-service-command-four-main-compile-v1/manifest.json';newp=b/'evidence/PG37224-monitor-lock4-four-main-compile-v2/manifest.json';old=ld(oldp);new=ld(newp);assert old['actualExit']==new['actualExit']==0
changed={m:[n for n,h in rows.items() if h!=old['physicalClassHashes'][m].get(n)] for m,rows in new['physicalClassHashes'].items()};flat=[n for rows in changed.values() for n in rows]
targets=['dev/codex/schubert/nk/batch/monitoring/'+n+'.class' for n in ['BatchMetricRecorder','MonitoringObservationClock','MonitoringPoller']]
assert set(flat)==set(targets) and len(flat)==3
assert all(set(new['physicalClassHashes'][m])==set(old['physicalClassHashes'][m]) for m in changed)
out=b/'evidence/PG37232-monitor-lock4-abi-physical-v1';assert not out.exists();out.mkdir();results={};equal=[]
for name in targets:
 texts={}
 for version,compile_result in [('old',old),('new',new)]:
  p=Path(compile_result['cwd'])/'src/schubert-nk-batch/target/classes'/name;assert sha(p)==compile_result['physicalClassHashes']['batch'][name]
  for flag in ['-public','-p']:
   cmd=[str(tc/'jdk-25.0.4/bin/javap'),flag,'-s',str(p)];result=subprocess.run(cmd,capture_output=True,text=True,timeout=60);key=Path(name).stem+'-'+version+flag
   (out/(key+'.stdout')).write_text(result.stdout);(out/(key+'.stderr')).write_text(result.stderr);results[key]=dict(command=cmd,actualExit=result.returncode);assert result.returncode==0 and not result.stderr;texts[(version,flag)]=result.stdout
 assert texts[('old','-public')]==texts[('new','-public')]
 assert texts[('old','-p')].replace('java.lang.Object lock','java.util.concurrent.locks.ReentrantLock lock').replace('descriptor: Ljava/lang/Object;','descriptor: Ljava/util/concurrent/locks/ReentrantLock;',1)==texts[('new','-p')]
 equal.append(dict(path=name,publicAbiExact=True,internalSignaturesExactExceptPrivateLockField=True))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=new['sourceCore'],oldSourceCore=old['sourceCore'],oldCompile=ref(oldp),newCompile=ref(newp),physicalUniverse=1101,changedPhysical=changed,changedPhysicalCount=3,unchangedPhysicalCount=1098,publicAbiAndInternalMethods=equal,commands=results,productTestsExecuted=0,oldSourceExecutionsTransferred=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedPhysical=3,unchanged=1098,publicAbiExact=True,productTests=0)))
