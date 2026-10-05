"""Same-source eight native streams after genuine owned TERM; private raw only.
Never starts/stops, attaches an agent, changes baseline, excludes code, or accepts
incomplete coverage. Current app source stays c8 even if tool HEAD is newer.
"""
import datetime,hashlib,json,os,pathlib,subprocess

os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='c8ad413437be409f70ec37bdba33c5e3cd21790b'
for stem in ['pg472-six-full-v1','pg472-native-stop-v1','pg472-readback-native-v1']:
    assert (W/(stem+'.exit')).read_text().strip()=='0'
assert subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'],cwd=T)==b''
roles=['parent','backup','cleanup','expiry','root-api193','root-web193','ordinary-api193','ordinary-web193']
names=['parent.exec','backup.exec','cleanup.exec','expiry.exec','f7560ea108ae4e7aaca9246602194143.before-exec.exec','fc1cec99569542298175864fcc8b6daf.before-exec.exec','f7560ea108ae4e7aaca9246602194143.terminal.exec','fc1cec99569542298175864fcc8b6daf.terminal.exec']
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
native=[];metadata=[]
for role,name in zip(roles,names):
    target=W/('pg472-'+role+'-native-v1.exec');assert not target.exists()
    remote='/run/schubert-nk/pt-coverage/'+role+'/'+name
    payload="""import pathlib,stat,hashlib,json
p=pathlib.Path(%r);s=p.lstat()
assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=16777216
print(json.dumps({'role':%r,'path':str(p),'uid':s.st_uid,'gid':s.st_gid,'mode':600,'bytes':s.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'device':s.st_dev}))
"""%(remote,role)
    r=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),capture_output=True,timeout=15);assert r.returncode==0
    m=json.loads(r.stdout)
    if role.startswith('root-') or role in ['parent','cleanup','expiry']:assert m['uid']==m['gid']==0
    if role=='backup':assert (m['uid'],m['gid'])==(992,977)
    if role=='ordinary-api193':assert (m['uid'],m['gid'])==(999,981)
    if role=='ordinary-web193':assert (m['uid'],m['gid'])==(997,980)
    with target.open('xb') as stream:r=subprocess.run(ssh+['sudo -n cat '+remote],stdout=stream,stderr=subprocess.PIPE,timeout=15)
    assert r.returncode==0 and not r.stderr and target.stat().st_size==m['bytes'] and hashlib.sha256(target.read_bytes()).hexdigest()==m['sha256']
    native.append(target);metadata.append(m)
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
    files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
tools=W/'pg472-native-counter-tools-v1';assert not tools.exists();tools.mkdir(mode=0o700)
r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(tools),str(T/'tools/quality/vm/050_s1/NativeCoverage.java'),str(T/'tools/quality/vm/050_s1/NativeSessions472.java')],capture_output=True)
assert r.returncode==0 and not r.stdout and not r.stderr
end=int(datetime.datetime.fromisoformat((W/'pg472-native-stop-v1.completed').read_text().strip()).timestamp()*1000)
with (W/'pg472-native-session-check-v1.private.log').open('xb') as stream:
    r=subprocess.run([str(J/'java'),'-cp',str(tools)+':'+':'.join(cp),'NativeSessions472']+[str(p) for p in native]+['1791240444000',str(end)],stdout=stream,stderr=stream)
assert r.returncode==0
modules=['protocol','storage','bootstrap','api','web','batch'];host=[W/'pg472-host'/m/'jacoco.exec' for m in modules];result={}
for module in modules:
    jar=W/'pg472-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    r=subprocess.run([str(J/'java'),'-cp',str(tools)+':'+':'.join(cp),'NativeCoverage',str(jar)]+[str(p) for p in host+native],capture_output=True,timeout=45)
    with (W/('pg472-'+module+'-native-counter-v1.private.log')).open('xb') as stream:stream.write(r.stdout);stream.write(r.stderr)
    assert r.returncode==0 and not r.stderr
    d=json.loads(r.stdout);assert d['classByteMismatch']==0;result[module]=d
out=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG472-native-eight-counter-v1';assert not out.exists();out.mkdir(parents=True)
d={'id':'PG472-native-eight-counter-v1','programId':'NK-OPS-001','testIds':['PT-OPS-NPARENT195006','PT-OPS-NPARENT195008','PT-OPS-NPARENT195010'],'productionSource':SOURCE,'branch':'dev-foundation','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':{'JDK':'25.0.4','JaCoCo':'0.8.15','guest':'Ubuntu26.04'},'actualExit':0,'command':'python3 -B tools/quality/vm/050_s1/pg472_collect_native_v1.py','eightFreshSingleSessions':True,'rootOrdinaryFourRoleIdsMatched':True,'classByteMismatch':0,'sameFrozenSixBytes':True,'ownedStopActualExit':0,'nativeFiles':metadata,'hostPlusNativeCounters':result,'coverage100':all(d[c]['missed']==0 for d in result.values() for c in ['LINE','METHOD','CLASS','BRANCH']),'BUG':['BUG-753','BUG-754'],'YKT':['YKT-533','YKT-534'],'SSC':['SSC-193','SSC-194','SSC-195'],'formalUpdated':False,'rawExported':False,'ITSTAccepted':False}
with (out/'manifest.json').open('x') as stream:json.dump(d,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'nativeStreams':8,'single':True,'sameSource':SOURCE,'noMatch':0,'coverage100':d['coverage100'],'missed':{m:{c:r[c]['missed'] for c in ['BRANCH','LINE','METHOD','CLASS']} for m,r in result.items()},'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()}))
