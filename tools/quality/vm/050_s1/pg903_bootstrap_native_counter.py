"""Qualified new Bootstrap terminal+closing and current e016 sixteen only; no old source."""
import datetime,hashlib,json,os,re,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='e01612fcd7f2752df5ae0836b78538fd5e87f120'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'])==b''
 for mode in ('verify','execute'):assert(W/('pg894-'+mode+'-v3.exit')).read_bytes()==b'0\n'
 assert(W/'pg901-bootstrap-post-v3.exit').read_bytes()==b'0\n'
 post=json.loads((W/'pg901-bootstrap-post-v3.safe.json').read_bytes());assert post['actualExit']==0 and post['productionSource']==SOURCE and post['allClientAdvisoryFlock0']and post['capturedNormal20VerifiedBeforeCurrent']
 meta=post['bootstrap'];assert len(meta['files'])==2 and 0<meta['unitElapsedSeconds']<=30
 old=W/'pg892-current-sixteen-native-v1';assert sha(old/'manifest.safe.json')=='56387c9cd6fc198ca5fd1fd8824b6d5e794ef743c82e5e3e657891a9f4cb5d48';old_record=json.loads((old/'manifest.safe.json').read_bytes());assert old_record['actualExit']==0 and old_record['productionSource']==SOURCE
 prior=[];sessions=[];cohorts=[]
 for name,digest in old_record['qualifiedCohortManifestHashes'].items():
  base=W/name;assert sha(base/'manifest.safe.json')==digest;m=json.loads((base/'manifest.safe.json').read_bytes());cohorts.append(m)
  assert m['actualExit']==0 and m['productionSource']==SOURCE and len(m['selected'])==len(m['singleSessions'])==8
  for i,s in enumerate(m['selected']):
   p=base/(str(i)+'.exec');assert sha(p)==s['sha256'];prior.append(p)
  sessions+=m['singleSessions']
 assert len(prior)==16 and len({s['sessionIdSha256']for s in sessions})==16
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
 payload='PROOFS='+repr(post['bootstrapProofHashes'])+'\nFILES='+repr(meta['files'])+'\n'+'''import hashlib,json,pathlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg894-bootstrap-existing-v3')
for n,d in PROOFS.items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==d
a=json.loads((r/'after.private.json').read_bytes())
for v in FILES:
 p=pathlib.Path('/run/schubert-nk/pt-coverage')/v['relative'];s=p.lstat();m=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
 assert m==a['native'][str(p)]['metadata']and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(999,981,0o600,1)and stat.S_ISREG(s.st_mode)and s.st_size==v['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
print('native files match qualified current Bootstrap proof')
'''
 r=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),capture_output=True,timeout=30);assert r.returncode==0 and not r.stderr
 work=W/'pg903-current-eighteen-native-v1';assert not work.exists();work.mkdir(mode=0o700)
 new=[]
 for i,v in enumerate(meta['files']):
  assert re.fullmatch(r'ordinary-bootstrap196/[0-9a-f]{32}\.(terminal|closing)\.exec',v['relative'])
  p=work/('bootstrap-'+str(i)+'.exec')
  with p.open('xb')as f:
   r=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
  assert r.returncode==0 and not r.stderr and p.stat().st_size==v['bytes']and sha(p)==v['sha256'];new.append(p)
 helper=W/'pg571-current-ten-native-v2/classes';assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a';assert sha(helper/'NativeSessions571.class')=='24eef12a79368196666f1c596469ab5518c3a5c00375be0c706ebb1cdec88d39'
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(helper)]
 for pattern in('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
  found=list(repo.glob(pattern));assert len(found)==1;cp.append(str(found[0]))
 new_sessions=[]
 for i,p in enumerate(new):
  r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeSessions571',str(meta['lowerMs']),str(meta['upperMs']),str(p)],capture_output=True,timeout=30)
  with(work/('session-'+str(i)+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0 and not r.stderr;v=json.loads(r.stdout);assert v['sessions']==1 and v['index']==0;new_sessions.append(v)
 # Two dumps from ONE qualified Bootstrap process: not two unrelated sessions.
 assert new_sessions[0]['sessionIdSha256']==new_sessions[1]['sessionIdSha256']and new_sessions[0]['startMs']==new_sessions[1]['startMs']and new_sessions[0]['dumpMs']<=new_sessions[1]['dumpMs']
 assert new_sessions[0]['sessionIdSha256']not in {s['sessionIdSha256']for s in sessions}
 host=W/'pg857-completed-reference-six-host-v1';assert sha(host/'manifest.safe.json')==old_record['frozenHostManifestSha256'];h=json.loads((host/'manifest.safe.json').read_bytes());assert h['actualExit']==0 and h['candidateSource']==SOURCE and h['tests']==3541
 modules=('protocol','storage','bootstrap','api','web','batch');executions=[host/m/'jacoco.exec'for m in modules]
 assert cohorts[0]['hostExecHashes']==cohorts[1]['hostExecHashes']
 assert all(sha(p)==cohorts[0]['hostExecHashes'][m]for m,p in zip(modules,executions))
 counters={};gain={}
 for m in modules:
  jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256']
  r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in executions+prior+new]],capture_output=True,timeout=45)
  with(work/(m+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0 and not r.stderr;v=json.loads(r.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[m]=v
  gain[m]={k:old_record['moduleCounters'][m][k]['missed']-v[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')};assert all(n>=0 for n in gain[m].values())
 remaining={k:sum(v[k]['missed']for v in counters.values())for k in('LINE','METHOD','CLASS','BRANCH')};delta={k:sum(v[k]for v in gain.values())for k in remaining}
 record={'actualExit':0,'run':'PG903-current-eighteen-native-v1','productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostRun':'PG857','frozenHostManifestSha256':sha(host/'manifest.safe.json'),'previousSixteenManifestSha256':sha(old/'manifest.safe.json'),'bootstrapPostManifestSha256':sha(W/'pg901-bootstrap-post-v3.safe.json'),'bootstrapNativeHashes':[v['sha256']for v in meta['files']],'bootstrapSingleSessions':new_sessions,'bootstrapSameProcessDumps':2,'currentNativeStreams':18,'distinctCurrentProcesses':17,'classByteMismatch':0,'otherSourceNativeImported':0,'moduleCounters':counters,'incrementalVsPG892':delta,'remaining':remaining,'coverage100':all(n==0 for n in remaining.values()),'formalAccepted':False,'rawExported':False}
 with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({'actualExit':0,'streams':18,'bootstrapUnitSeconds':meta['unitElapsedSeconds'],'incrementalVsPG892':delta,'remaining':remaining,'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))
if __name__=='__main__':main()
