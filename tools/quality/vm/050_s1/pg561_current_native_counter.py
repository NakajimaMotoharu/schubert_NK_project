"""Nine current source streams only; historical five retained but never merged. Diagnostic, not formal."""
import datetime,hashlib,json,os,pathlib,subprocess
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
SELECTED=['backup/backup.exec','cleanup/cleanup.exec','expiry/expiry.exec','ordinary-api193/0df039719b644400b1da023c6cc604eb.terminal.exec','ordinary-inspector196/93b40ddf81204c6ead974d2627dc6686.terminal.exec','ordinary-web193/3bcfbad981e64d8fadda66f27d1994fa.terminal.exec','parent/parent.exec','root-api193/0df039719b644400b1da023c6cc604eb.before-exec.exec','root-web193/3bcfbad981e64d8fadda66f27d1994fa.before-exec.exec']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
KNOWN_TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/MaintenanceMutationGuardTest.java'
def same_production_paths(changed):
 return type(changed)is list and all(type(p)is str and p==KNOWN_TEST for p in changed)and len(changed)==len(set(changed))
def main():
 os.umask(0o077)
 changed=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T,text=True).splitlines();assert same_production_paths(changed)
 work=W/'pg561-current-native-v2';assert not work.exists();work.mkdir(mode=0o700)
 assert (W/'pg559-terminal-native-v2.exit').read_bytes()==b'0\n'
 payload='SELECTED='+repr(SELECTED)+'\n'+'''import pathlib,hashlib,json,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v2');assert hashlib.sha256((r/'after.private.json').read_bytes()).hexdigest()=='23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677'
b=json.loads((r/'after.private.json').read_bytes());native=pathlib.Path('/run/schubert-nk/pt-coverage');items=[]
for relative in SELECTED:
 p=native/relative;s=p.lstat();v=b['native'][str(p)];assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=16777216 and not p.is_symlink();assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'];assert [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==v['metadata']
 items.append({'relative':relative,'sha256':v['sha256'],'bytes':s.st_size,'uid':s.st_uid,'gid':s.st_gid,'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'device':s.st_dev})
done=[x for x in b['parentPid1']if x.get('JOB_ID')=='59402'and x.get('JOB_TYPE')=='start'and x.get('JOB_RESULT')=='done'];assert len(done)==1
end=done[0];lower=(int(end['__REALTIME_TIMESTAMP'])-(int(end['__MONOTONIC_TIMESTAMP'])-44878901762))//1000-1000
upper=max(int(rows[0]['__REALTIME_TIMESTAMP'])for rows in b['pid1Stop'].values())//1000+1000
assert len(items)==9 and upper>lower
print(json.dumps({'lowerMs':lower,'upperMs':upper,'files':items,'historicalStreamsExcluded':5,'freshBootstrapIncluded':False}))
'''
 ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
 meta=json.loads(subprocess.check_output(ssh+['sudo -n python3 -B -'],input=payload.encode(),timeout=30));native=[]
 for i,m in enumerate(meta['files']):
  p=work/(str(i)+'.exec')
  with p.open('xb')as f:r=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+m['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
  assert r.returncode==0 and not r.stderr and p.stat().st_size==m['bytes']and sha(p)==m['sha256'];native.append(p)
 repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
 for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
  files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
 classes=work/'classes';classes.mkdir(mode=0o700)
 r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(T/'tools/quality/vm/050_s1/NativeCoverage.java'),str(T/'tools/quality/vm/050_s1/NativeSessions561.java')],capture_output=True);assert r.returncode==0 and not r.stdout and not r.stderr
 r=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeSessions561',str(meta['lowerMs']),str(meta['upperMs']),*[str(p)for p in native]],capture_output=True,timeout=30)
 with (work/'session-check.private.log').open('xb')as f:f.write(r.stdout);f.write(r.stderr)
 assert r.returncode==0 and not r.stderr;sessions=[json.loads(l)for l in r.stdout.splitlines()];assert len(sessions)==9
 modules=['protocol','storage','bootstrap','api','web','batch'];host=W/'pg540-six-host-v1';host_exec=[host/m/'jacoco.exec'for m in modules];counters={}
 for m in modules:
  jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert jar.is_file()
  r=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in host_exec+native]],capture_output=True,timeout=45)
  with (work/(m+'-counter.private.log')).open('xb')as f:f.write(r.stdout);f.write(r.stderr)
  assert r.returncode==0 and not r.stderr;value=json.loads(r.stdout);assert value['classByteMismatch']==0 and value['formal']is False;counters[m]=value
 record={'id':'PG561-current-nine-native-v2','productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'run':'PG554-ordinary-newrun-v1','classification':'PROVISIONAL_SAME_SOURCE_COUNTER_DIAGNOSTIC','recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualExit':0,'command':'python3 -B tools/quality/vm/050_s1/pg561_current_native_counter.py','hostSourceRun':'PG540','currentTestOnlyDifferences':changed,'currentTestOnlyHashes':{p:sha(T/p)for p in changed},'additionalTestsNotCountedInFrozenRun':True,'currentNativeFiles':meta['files'],'nativeSessions':sessions,'bounds':{k:meta[k]for k in ('lowerMs','upperMs')},'hostExecHashes':{m:sha(p)for m,p in zip(modules,host_exec)},'moduleCounters':counters,'historicalFiveExcluded':True,'currentBootstrapNativeAccepted':False,'fullNativeAccepted':False,'formalAccepted':False,'rawExported':False,'ITSTAccepted':False,'coverage100':all(c[k]['missed']==0 for c in counters.values()for k in ('LINE','METHOD','CLASS','BRANCH'))}
 with (work/'manifest.safe.json').open('x')as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'nativeCurrentStreams':9,'historicalExcluded':5,'bootstrapCurrentMissing':True,'missed':{m:{k:c[k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')}for m,c in counters.items()},'coverage100':record['coverage100'],'formalAccepted':False,'manifestSha256':sha(work/'manifest.safe.json')}))
if __name__=='__main__':main()
