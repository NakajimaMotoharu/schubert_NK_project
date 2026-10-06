"""BOOT482005 same frozen PG479 full + preserved nine + genuine existing Bootstrap."""
import datetime,hashlib,json,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='bab704707b8fd7e0dc7581c4489f0892236efe73'
original=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG481-native-nine-counter-v1/manifest.json';assert hashlib.sha256(original.read_bytes()).hexdigest()=='73624508e8bd45a89908f8da795c4b21cfd2d05477c8bccc213851c6e4ea76ec'
prior=json.loads(original.read_text());assert prior['productionSource']==SOURCE and prior['nineFreshSingleSessions'] and prior['classByteMismatch']==0
assert subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'],cwd=T)==b'' and (W/'pg482-bootstrap-native-v1.exit').read_text().strip()=='0'
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import pathlib,hashlib,json,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg482-bootstrap-existing');assert hashlib.sha256((r/'complete.private').read_bytes()).hexdigest()=='633b89135d5dfe738a9ee9dee098976e6855ff2c555e2b9d7a6122c358e03a43'
t=json.loads((r/'terminal.private.json').read_text());assert t['InvocationID']=='9af0cd0f91984eac95995c0cdf265c88' and t['ExecMainStatus']=='20'
a=json.loads((r/'after.private.json').read_text());before=json.loads((r/'before.private.json').read_text());assert before['rows']==a['rows']
p=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-bootstrap196/9af0cd0f91984eac95995c0cdf265c88.terminal.exec');s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and (s.st_uid,s.st_gid)==(999,981) and 0<s.st_size<=16777216
print(json.dumps({'role':'ordinary-bootstrap196','path':str(p),'uid':s.st_uid,'gid':s.st_gid,'mode':600,'bytes':s.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'device':s.st_dev,'existingExit20':True,'all24DatabaseUnchanged':True,'syntheticSourcesRetired':True}))
'''
meta=json.loads(subprocess.check_output(SSH+['sudo -n python3 -B -'],input=PAYLOAD.encode(),timeout=15))
target=W/'pg482-bootstrap-native-v1.exec';assert not target.exists()
with target.open('xb') as f:r=subprocess.run(SSH+['sudo -n cat '+meta['path']],stdout=f,stderr=subprocess.PIPE,timeout=15)
assert r.returncode==0 and not r.stderr and target.stat().st_size==meta['bytes'] and hashlib.sha256(target.read_bytes()).hexdigest()==meta['sha256']
native=[]
for m in prior['nativeFiles']:
 p=W/('pg481-'+m['role']+'-native-v1.exec');assert p.stat().st_size==m['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];native.append(p)
native.append(target)
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
 files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
tools=W/'pg482-native-counter-tools-v1';assert not tools.exists();tools.mkdir(mode=0o700)
r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(tools),str(T/'tools/quality/vm/050_s1/NativeCoverage.java'),str(T/'tools/quality/vm/050_s1/NativeSession482.java')],capture_output=True);assert r.returncode==0 and not r.stdout and not r.stderr
with (W/'pg482-native-session-check-v1.private.log').open('xb') as f:r=subprocess.run([str(J/'java'),'-cp',str(tools)+':'+':'.join(cp),'NativeSession482',str(target)],stdout=f,stderr=f)
assert r.returncode==0
modules=['protocol','storage','bootstrap','api','web','batch'];host=[W/'pg479-host'/m/'jacoco.exec' for m in modules];result={}
for module in modules:
 jar=W/'pg479-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');r=subprocess.run([str(J/'java'),'-cp',str(tools)+':'+':'.join(cp),'NativeCoverage',str(jar)]+[str(p) for p in host+native],capture_output=True,timeout=45)
 with (W/('pg482-'+module+'-native-counter-v1.private.log')).open('xb') as f:f.write(r.stdout);f.write(r.stderr)
 assert r.returncode==0 and not r.stderr;d=json.loads(r.stdout);assert d['classByteMismatch']==0;result[module]=d
out=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG482-native-ten-counter-v1';assert not out.exists();out.mkdir(parents=True)
d={'id':'PG482-native-ten-counter-v1','programId':'NK-OPS-001','testIds':['BOOT482001','BOOT482002','BOOT482003','BOOT482004','BOOT482005','BREC198010-V06'],'productionSource':SOURCE,'branch':'dev-foundation','actualExit':0,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':'python3 -B tools/quality/vm/050_s1/pg482_collect_native_v1.py','parentCohort':'PG481','bootstrapCohort':'PG482','allTenSameFrozenSixBytes':True,'previousNineUnchanged':True,'allTenSingleSessions':True,'classByteMismatch':0,'existingBootstrapExit20':True,'all24DatabaseUnchanged':True,'syntheticSourcesRetired':True,'nativeFiles':prior['nativeFiles']+[meta],'hostPlusNativeCounters':result,'coverage100':all(x[c]['missed']==0 for x in result.values() for c in ['LINE','METHOD','CLASS','BRANCH']),'formalUpdated':False,'rawExported':False,'ITSTAccepted':False}
with (out/'manifest.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'streams':10,'classByteMismatch':0,'coverage100':d['coverage100'],'missed':{m:{c:x[c]['missed'] for c in ['BRANCH','LINE','METHOD','CLASS']} for m,x in result.items()},'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()}))
