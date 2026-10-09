"""Add only retained current1902 Inspector dumps, qualified independently by906/window/byte."""
import datetime,json,os,re,subprocess
from pathlib import Path
from pg903_bootstrap_native_counter import W,P,J,SOURCE,sha
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'])==b''
 assert(W/'pg906-retained-inspector-v2.exit').read_bytes()==b'0\n'
 post=json.loads((W/'pg906-retained-inspector-v2.safe.json').read_bytes());assert post['actualExit']==0 and post['productionSource']==SOURCE and post['allClientAdvisoryFlock0'];meta=post['inspector'];assert meta['firstRootProgressNormal']and len(meta['files'])==2
 old=W/'pg903-current-eighteen-native-v1';assert sha(old/'manifest.safe.json')=='70f040c6f8193539b92b186e2df90113a67ec2b422f0173a3e40cb5d24d61b38';o=json.loads((old/'manifest.safe.json').read_bytes());assert o['actualExit']==0 and o['productionSource']==SOURCE
 prior16=W/'pg892-current-sixteen-native-v1';assert sha(prior16/'manifest.safe.json')==o['previousSixteenManifestSha256'];v16=json.loads((prior16/'manifest.safe.json').read_bytes());prior=[];sessions=[];cohorts=[]
 for name,digest in v16['qualifiedCohortManifestHashes'].items():
  base=W/name;assert sha(base/'manifest.safe.json')==digest;v=json.loads((base/'manifest.safe.json').read_bytes());assert v['actualExit']==0 and v['productionSource']==SOURCE;cohorts.append(v)
  assert len(v['selected'])==len(v['singleSessions'])==8
  for i,item in enumerate(v['selected']):
   p=base/(str(i)+'.exec');assert sha(p)==item['sha256'];prior.append(p)
  sessions+=v['singleSessions']
 for i,digest in enumerate(o['bootstrapNativeHashes']):
  p=old/('bootstrap-'+str(i)+'.exec');assert sha(p)==digest;prior.append(p)
 sessions+=o['bootstrapSingleSessions'];assert len(prior)==len(sessions)==18 and len({s['sessionIdSha256']for s in sessions})==17
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
 # Authenticate against the independently sealed full CURRENT snapshot, not empty live GC fields.
 payload='SHA='+repr(post['beforeSha256'])+'\nFILES='+repr(meta['files'])+'\n'+'''import hashlib,json,pathlib,pwd,stat
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg906-retained-inspector-v2/after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;a=json.loads(raw)
identity=pwd.getpwnam('schubert-inbox-inspector')
for v in FILES:
 p=pathlib.Path('/run/schubert-nk/pt-coverage')/v['relative'];s=p.lstat();m=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
 assert m==a['native'][str(p)]['metadata']and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(identity.pw_uid,identity.pw_gid,0o600,1)and stat.S_ISREG(s.st_mode)and s.st_size==v['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
print('native Inspector current snapshot matches')
'''
 r=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),capture_output=True,timeout=30);assert r.returncode==0 and not r.stderr
 work=W/'pg907-current-twenty-native-v1';assert not work.exists();work.mkdir(mode=0o700);new=[]
 for i,v in enumerate(meta['files']):
  assert re.fullmatch(r'ordinary-inspector196/[0-9a-f]{32}\.(terminal|closing)\.exec',v['relative'])
  p=work/('inspector-'+str(i)+'.exec')
  with p.open('xb')as f:
   r=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
  assert r.returncode==0 and not r.stderr and p.stat().st_size==v['bytes']and sha(p)==v['sha256'];new.append(p)
 helper=W/'pg571-current-ten-native-v2/classes';assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'and sha(helper/'NativeSessions571.class')=='24eef12a79368196666f1c596469ab5518c3a5c00375be0c706ebb1cdec88d39'
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(helper)]
 for pattern in('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
  found=list(repo.glob(pattern));assert len(found)==1;cp.append(str(found[0]))
 new_sessions=[]
 for i,p in enumerate(new):
  r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeSessions571',str(meta['lowerMs']),str(meta['upperMs']),str(p)],capture_output=True,timeout=30)
  with(work/('session-'+str(i)+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0 and not r.stderr;s=json.loads(r.stdout);assert s['sessions']==1 and s['index']==0;new_sessions.append(s)
 assert new_sessions[0]['sessionIdSha256']==new_sessions[1]['sessionIdSha256']and new_sessions[0]['startMs']==new_sessions[1]['startMs']and new_sessions[0]['dumpMs']<=new_sessions[1]['dumpMs']and new_sessions[0]['sessionIdSha256']not in {s['sessionIdSha256']for s in sessions}
 host=W/'pg857-completed-reference-six-host-v1';assert sha(host/'manifest.safe.json')==o['frozenHostManifestSha256'];h=json.loads((host/'manifest.safe.json').read_bytes());assert h['actualExit']==0 and h['candidateSource']==SOURCE and h['tests']==3541
 modules=('protocol','storage','bootstrap','api','web','batch');executions=[host/m/'jacoco.exec'for m in modules];assert cohorts[0]['hostExecHashes']==cohorts[1]['hostExecHashes']and all(sha(p)==cohorts[0]['hostExecHashes'][m]for m,p in zip(modules,executions));counters={};gain={}
 for m in modules:
  jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256']
  r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in executions+prior+new]],capture_output=True,timeout=45)
  with(work/(m+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr)
  assert r.returncode==0 and not r.stderr;v=json.loads(r.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[m]=v
  gain[m]={k:o['moduleCounters'][m][k]['missed']-v[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')};assert all(x>=0 for x in gain[m].values())
 remaining={k:sum(v[k]['missed']for v in counters.values())for k in('LINE','METHOD','CLASS','BRANCH')};delta={k:sum(v[k]for v in gain.values())for k in remaining}
 record={'actualExit':0,'run':'PG907-current-twenty-native-v1','productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostRun':'PG857','frozenHostManifestSha256':sha(host/'manifest.safe.json'),'previousEighteenManifestSha256':sha(old/'manifest.safe.json'),'inspectorPostManifestSha256':sha(W/'pg906-retained-inspector-v2.safe.json'),'inspectorNativeHashes':[v['sha256']for v in meta['files']],'inspectorSingleSessions':new_sessions,'retainedActualCurrentRun':True,'newUnitStarts':0,'currentNativeStreams':20,'distinctCurrentProcesses':18,'classByteMismatch':0,'otherSourceNativeImported':0,'moduleCounters':counters,'incrementalVsPG903':delta,'remaining':remaining,'coverage100':all(x==0 for x in remaining.values()),'formalAccepted':False,'rawExported':False}
 with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({'actualExit':0,'streams':20,'newUnitStarts':0,'incrementalVsPG903':delta,'remaining':remaining,'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))
if __name__=='__main__':main()
