"""Two independently qualified current-e016 cohorts only; not old-source evidence union."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin');T=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 source='e01612fcd7f2752df5ae0836b78538fd5e87f120'
 assert subprocess.check_output(['git','diff','--name-only',source,'--','src','pom.xml'])==b''
 cohorts=[W/'pg879-current-eight-native-v1',W/'pg891-current-eight-native-v1'];digests=['317dcf8f294d0b5099875a7566b9299666cb4e76a1797c16bd25f2393ca165f7','a6b28bc447cc0a08a7b0d89ec56321d015e2551f662bb299a56328f73b34fd7e'];records=[];streams=[]
 for base,digest in zip(cohorts,digests):
  manifest=base/'manifest.safe.json';assert sha(manifest)==digest;m=json.loads(manifest.read_bytes());records.append(m)
  assert m['actualExit']==0 and m['productionSource']==source and len(m['selected'])==len(m['singleSessions'])==8
  assert all(v['classByteMismatch']==0 for v in m['moduleCounters'].values())
  for i,selected in enumerate(m['selected']):
   p=base/(str(i)+'.exec');assert sha(p)==selected['sha256'];streams.append(p)
 assert len(streams)==16 and records[0]['hostExecHashes']==records[1]['hostExecHashes']
 ids=[s['id']for m in records for s in m['singleSessions']];assert len(ids)==len(set(ids))==16
 work=W/'pg892-current-sixteen-native-v1';assert not work.exists();work.mkdir(mode=0o700)
 helper=W/'pg571-current-ten-native-v2/classes';assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(helper)]
 for pattern in('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
  files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
 host=W/'pg857-completed-reference-six-host-v1';assert sha(host/'manifest.safe.json')==records[0]['frozenHostManifestSha256']==records[1]['frozenHostManifestSha256'];h=json.loads((host/'manifest.safe.json').read_bytes());assert h['actualExit']==0 and h['candidateSource']==source and h['tests']==3541
 modules=('protocol','storage','bootstrap','api','web','batch');executions=[host/m/'jacoco.exec'for m in modules];assert all(sha(p)==records[0]['hostExecHashes'][m]for m,p in zip(modules,executions))
 counters={};gain={}
 for m in modules:
  jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256']
  p=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(x)for x in executions+streams]],capture_output=True,timeout=45)
  with(work/(m+'.private.log')).open('xb')as f:f.write(p.stdout+p.stderr);f.flush();os.fsync(f.fileno())
  assert p.returncode==0 and not p.stderr;v=json.loads(p.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[m]=v
  gain[m]={k:records[0]['moduleCounters'][m][k]['missed']-v[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')};assert all(x>=0 for x in gain[m].values())
 remain={k:sum(v[k]['missed']for v in counters.values())for k in('LINE','METHOD','CLASS','BRANCH')};increment={k:sum(v[k]for v in gain.values())for k in remain}
 record={'run':'PG892-current-sixteen-native-v1','actualExit':0,'productionSource':source,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualifiedCohortManifestHashes':dict(zip([p.name for p in cohorts],digests)),'sameSourceCurrentCohorts':2,'currentSingleSessionStreams':16,'oldSourceStreamsImported':0,'classByteMismatch':0,'hostRun':'PG857','frozenHostManifestSha256':sha(host/'manifest.safe.json'),'moduleCounters':counters,'incrementalVsFirstCurrentCohort':increment,'remaining':remain,'coverage100':all(v==0 for v in remain.values()),'formalAccepted':False,'rawExported':False}
 with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({'actualExit':0,'streams':16,'sameProductionSource':source,'incrementalVsFirstCurrentCohort':increment,'remaining':remain,'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))
if __name__=='__main__':main()
