"""New current Bootstrap stream plus sealed current nine, frozen class bytes. Diagnostic only."""
import datetime,hashlib,json,os,pathlib,subprocess
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 os.umask(0o077)
 changed=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T,text=True).splitlines()
 allowed={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/MaintenanceMutationGuardTest.java',*{'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/'+name for name in ('ChildBrokerTest.java','ChildMaintenanceInspectorTest.java','ChildMaintenanceParentTest.java')}}
 assert len(changed)==len(set(changed))and set(changed)<=allowed
 prior=W/'pg561-current-native-v2';old=json.loads((prior/'manifest.safe.json').read_bytes())
 assert sha(prior/'manifest.safe.json')=='e253b4e23d25dc030da33ad67fbb41d9a492426492416931dbeefc31cc73ed8a'and old['actualExit']==0 and old['productionSource']==SOURCE
 assert (W/'pg570-bootstrap-execute-v1.exit').read_bytes()==b'0\n'
 operation=json.loads((W/'pg570-bootstrap-execute-v1.safe.json').read_bytes());assert operation['actualExit']==0 and operation['productionSource']==SOURCE
 work=W/'pg571-current-ten-native-v1';assert not work.exists();work.mkdir(mode=0o700)
 ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
 payload=r'''import hashlib,json,pathlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg570-bootstrap-existing-v1');raw=(r/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='8cd3195cc3a326ba4a2a84ba2cd5abe6e931bcd2131c2609c29983e9c85bd164';a=json.loads(raw)
before=(r/'before.private.json').read_bytes();assert hashlib.sha256(before).hexdigest()=='1d42516cf498d3ae58b5ba8a6253844676ed9162c588492f0cf78478a31ea2c6';b=json.loads(before)
assert a['rows']==b['rows']and len(a['rows'])==24
assert all(a['units'][u]==v for u,v in b['units'].items()if u!='schubert-nk-bootstrap-admin.service')
u=a['units']['schubert-nk-bootstrap-admin.service'];inv=u['InvocationID'];assert inv=='c0592572f0f94070964eb3ee4ff4903c'and u['ExecMainCode']=='1'and u['ExecMainStatus']=='20'
relative='ordinary-bootstrap196/'+inv+'.terminal.exec';p=pathlib.Path('/run/schubert-nk/pt-coverage')/relative;v=a['native'][str(p)];s=p.lstat()
metadata=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
assert metadata==v['metadata']and stat.S_ISREG(s.st_mode)and s.st_nlink==1 and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(999,981,0o600)and 0<s.st_size<=16777216 and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
assert str(p)not in b['native']and set(a['native'])==set(b['native'])|{str(p)}
rows=[json.loads(line)for line in (r/'pid1.private.jsonl').read_bytes().splitlines()];done=[d for d in rows if d.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and d.get('JOB_TYPE')=='start'and d.get('JOB_RESULT')=='done'];assert len(done)==1
d=done[0];assert d.get('_BOOT_ID')=='cc9ed8747f4f450ea1888de1e42c8441'and d.get('_PID')=='1'and d.get('_UID')=='0'and d.get('INVOCATION_ID')==inv
start=int(u['ExecMainStartTimestampMonotonic']);end=int(u['ExecMainExitTimestampMonotonic']);assert 0<end-start<=30000000
lower=(int(d['__REALTIME_TIMESTAMP'])-(int(d['__MONOTONIC_TIMESTAMP'])-start))//1000-1000;upper=int(d['__REALTIME_TIMESTAMP'])//1000+1000
print(json.dumps({'relative':relative,'sha256':v['sha256'],'bytes':s.st_size,'metadata':metadata,'lowerMs':lower,'upperMs':upper,'unitElapsedSeconds':(end-start)/1000000,'actualPid1Job':d['JOB_ID'],'newOrdinary20':True,'all24Unchanged':True}))
'''
 meta=json.loads(subprocess.check_output(ssh+['sudo -n python3 -B -'],input=payload.encode(),timeout=30))
 native=[]
 for n,v in enumerate(old['currentNativeFiles']):
  p=prior/(str(n)+'.exec');assert sha(p)==v['sha256'];native.append(p)
 assert len(native)==9
 new=work/'bootstrap.exec'
 with new.open('xb')as f:
  result=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+meta['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
 assert result.returncode==0 and not result.stderr and new.stat().st_size==meta['bytes']and sha(new)==meta['sha256'];native.append(new)
 repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
 for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
  jars=list(repo.glob(pattern));assert len(jars)==1;cp.append(str(jars[0]))
 classes=work/'classes';classes.mkdir(mode=0o700)
 result=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(T/'tools/quality/vm/050_s1/NativeCoverage.java'),str(T/'tools/quality/vm/050_s1/NativeSessions561.java')],capture_output=True);assert result.returncode==0 and not result.stdout and not result.stderr
 result=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeSessions561',str(meta['lowerMs']),str(meta['upperMs']),str(new)],capture_output=True,timeout=30)
 with(work/'session.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr)
 assert result.returncode==0 and not result.stderr;sessions=[json.loads(line)for line in result.stdout.splitlines()];assert len(sessions)==1
 modules=['protocol','storage','bootstrap','api','web','batch'];host=W/'pg540-six-host-v1';executions=[host/m/'jacoco.exec'for m in modules]
 assert all(sha(p)==old['hostExecHashes'][m]for m,p in zip(modules,executions))
 counters={};delta={}
 for module in modules:
  jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
  result=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in executions+native]],capture_output=True,timeout=45)
  with(work/(module+'-counter.private.log')).open('xb')as f:f.write(result.stdout);f.write(result.stderr)
  assert result.returncode==0 and not result.stderr;value=json.loads(result.stdout);assert value['classByteMismatch']==0 and value['formal']is False;counters[module]=value
  delta[module]={k:old['moduleCounters'][module][k]['missed']-value[k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')};assert all(v>=0 for v in delta[module].values())
 record={'id':'PG571-current-ten-native-v1','productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualExit':0,'currentBootstrap':meta,'bootstrapSingleSession':sessions,'previousNineManifestSha256':sha(prior/'manifest.safe.json'),'hostExecHashes':old['hostExecHashes'],'currentTestOnlyDifferences':changed,'testOnlyHashes':{p:sha(T/p)for p in changed},'moduleCounters':counters,'newBootstrapDelta':delta,'currentStreams':10,'historicalExcluded':5,'PG541565SelectedNotMixed':True,'coverage100':all(v[k]['missed']==0 for v in counters.values()for k in ('LINE','METHOD','CLASS','BRANCH')),'formalAccepted':False,'ITSTAccepted':False,'rawExported':False}
 with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'actualExit':0,'currentNativeStreams':10,'bootstrapElapsedSeconds':meta['unitElapsedSeconds'],'newBootstrapCovered':{k:sum(v[k]for v in delta.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'missed':{m:{k:v[k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')}for m,v in counters.items()},'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))
if __name__=='__main__':main()
