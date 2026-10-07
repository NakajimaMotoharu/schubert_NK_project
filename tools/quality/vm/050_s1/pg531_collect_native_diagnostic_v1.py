"""Read-only sealed current native8 export. Per-stream provenance precedes any same-source union."""
import datetime,hashlib,json,os,pathlib,subprocess
os.umask(0o077)
T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c';RUN='PG531-native-current-diagnostic-v1'
assert subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'],cwd=T)==b''
normal=json.loads((T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG530-terminal-readback-v1/manifest.json').read_bytes());assert normal['actualExit']==0 and normal['productionSource']==SOURCE and normal['allNewMAdbRefsBusFdScopesReturnedNormally']
assert (W/'pg530-terminal-native-v1.exit').read_text()=='0\n'
host=json.loads((T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG495-completion-compound-full-v1/manifest.json').read_bytes());assert host['productionSource']==SOURCE and host['actualExit']==0 and host['FES']==0
modules=['protocol','storage','bootstrap','api','web','batch'];jars=[]
for module in modules:
 p=W/'pg495-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');row=next(v for v in host['modules']if v['module']==module)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['projectJarSha256'];jars.append(p)
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
 paths=list(repo.glob(pattern));assert len(paths)==1;cp.append(str(paths[0]))
tools=W/'pg531-native-tools-v1';assert not tools.exists();tools.mkdir(mode=0o700)
compile_result=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(tools),str(R/'NativeStreamInspect531.java'),str(R/'NativeStreamInspect531Test.java'),str(R/'NativeCoverage.java')],capture_output=True)
with(W/'pg531-compile-v1.private.log').open('xb')as f:f.write(compile_result.stdout);f.write(compile_result.stderr)
assert compile_result.returncode==0 and compile_result.stdout==compile_result.stderr==b''
class_path=str(tools)+':'+':'.join(cp)
test=subprocess.run([str(J/'java'),'-cp',class_path,'NativeStreamInspect531Test'],capture_output=True);assert test.returncode==0 and test.stderr==b''
with(W/'pg531-window-oracle-v1.private.log').open('xb')as f:f.write(test.stdout)
assert test.stdout==b'PG531_SESSION_WINDOW_ORACLE independentAssertions=58 nullNegative=true rawSessionOutput0=true vmActions0=true productionPT0=true\n'
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
roles=['parent','backup','cleanup','expiry','root-api193','root-web193','ordinary-api193','ordinary-web193']
names=['parent.exec','backup.exec','cleanup.exec','expiry.exec','844d2217a6494e4f9f852fc4f488a0fa.before-exec.exec','7127bb06489a4218acd2b72570ce1ec5.before-exec.exec','844d2217a6494e4f9f852fc4f488a0fa.terminal.exec','7127bb06489a4218acd2b72570ce1ec5.terminal.exec']
inspection=[];native=[]
for role,name in zip(roles,names):
 remote='/run/schubert-nk/pt-coverage/'+role+'/'+name
 payload='REMOTE='+repr(remote)+'\nROLE='+repr(role)+'\n'+r'''
import pathlib,json,hashlib,stat,os
before=pathlib.Path('/var/lib/pgpt-s1-preservation/pg530-terminal-readback-v1/after.private.json').read_bytes();assert hashlib.sha256(before).hexdigest()=='d08b56b12560c2dd1df35eed5f55a05a4f9fb3164300d802e1b875a0d348a704';expected=json.loads(before)['native'][REMOTE]
p=pathlib.Path(REMOTE);s=p.lstat();assert stat.S_ISREG(s.st_mode)and not p.is_symlink()and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=16777216
meta=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
assert meta==expected['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==expected['sha256']
owner=(999,981)if ROLE=='ordinary-api193'else(997,980)if ROLE=='ordinary-web193'else(992,977)if ROLE=='backup'else(0,0);assert(s.st_uid,s.st_gid)==owner
print(json.dumps({'role':ROLE,'bytes':s.st_size,'sha256':expected['sha256'],'uid':s.st_uid,'gid':s.st_gid,'mode':600,'sourceBoundToSealedTerminal':True}))
'''
 info=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),capture_output=True,timeout=15);assert info.returncode==0 and not info.stderr;metadata=json.loads(info.stdout)
 target=W/('pg531-'+role+'-native-v1.exec');assert not target.exists()
 read_payload='PATH='+repr(remote)+'\n'+r'''
import os,sys,stat,hashlib
fd=os.open(PATH,os.O_RDONLY|os.O_NOFOLLOW);s=os.fstat(fd);assert stat.S_ISREG(s.st_mode)and s.st_nlink==1
def identity(v):return(v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
raw=b''
while True:
 chunk=os.read(fd,65536)
 if not chunk:break
 raw+=chunk;assert len(raw)<=16777216
assert identity(os.fstat(fd))==identity(s);os.close(fd);sys.stdout.buffer.write(raw)
'''
 with target.open('xb')as f:read=subprocess.run(ssh+['sudo -n python3 -B -'],input=read_payload.encode(),stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
 assert read.returncode==0 and not read.stderr and target.stat().st_size==metadata['bytes']and hashlib.sha256(target.read_bytes()).hexdigest()==metadata['sha256']
 result=subprocess.run([str(J/'java'),'-cp',class_path,'NativeStreamInspect531',role,str(target)]+[str(p)for p in jars],capture_output=True,timeout=30);assert result.returncode==0 and not result.stderr
 with(W/('pg531-'+role+'-inspection-v1.private.log')).open('xb')as f:f.write(result.stdout)
 verdict=json.loads(result.stdout);eligible=verdict['singleSession']and verdict['currentWindowAndRole']and verdict['classByteMismatch']==verdict['unknownProductionClasses']==0
 inspection.append({**metadata,**verdict,'eligibleForCurrentUnion':eligible});
 if eligible:native.append(target)
# Every rejected stream remains recorded. Missing native role/branch is a gap, never an exclusion/pass.
result={};host_exec=[W/'pg495-host'/m/'jacoco.exec'for m in modules]
for module,jar in zip(modules,jars):
 probe=subprocess.run([str(J/'java'),'-cp',class_path,'NativeCoverage',str(jar)]+[str(p)for p in host_exec+native],capture_output=True,timeout=45)
 with(W/('pg531-'+module+'-counter-v1.private.log')).open('xb')as f:f.write(probe.stdout);f.write(probe.stderr)
 assert probe.returncode==0 and not probe.stderr;result[module]=json.loads(probe.stdout)
summary={'run':RUN,'productionSource':SOURCE,'collectedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorGitHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'sameFrozenSixJarBytes':True,'streams':inspection,'eligibleCurrentStreams':len(native),'presentStreams':8,'missingRoles':['ordinary-inspector196','root-bootstrapadmin196','ordinary-bootstrapadmin196'],'counters':result,'coverage100':all(v[c]['missed']==0 for v in result.values()for c in['LINE','METHOD','CLASS','BRANCH']),'formalAccepted':False,'nativeAllScopeAccepted':False,'businessActions':0,'rawExportedToGit':False}
with(W/'pg531-native-diagnostic-v1.safe.json').open('x')as f:json.dump(summary,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':RUN,'source':SOURCE,'presentStreams':8,'eligibleCurrentStreams':len(native),'streamVerdicts':[{k:s[k]for k in ['role','singleSession','currentWindowAndRole','classByteMismatch','unknownProductionClasses','eligibleForCurrentUnion']}for s in inspection],'missed':{m:{c:v[c]['missed']for c in ['LINE','METHOD','CLASS','BRANCH']}for m,v in result.items()},'coverage100':summary['coverage100'],'formalAccepted':False,'safeSummarySha256':hashlib.sha256((W/'pg531-native-diagnostic-v1.safe.json').read_bytes()).hexdigest()}))
