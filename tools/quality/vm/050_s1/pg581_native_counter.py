"""Frozen six host + sealed current ten + eight new same-source single streams. Diagnostic only."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess

T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
R=T/'tools/quality/vm/050_s1'
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
PAYLOAD=r'''
import hashlib,json,pathlib,stat
def metadata(s):
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg579-native-stop-v1');raw=(root/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='cb5951e30fda2ef63f2691a24f302e46b8cffcff6c8345e69644672b9135eaf6';a=json.loads(raw)
before=(root/'before.private.json').read_bytes();assert hashlib.sha256(before).hexdigest()=='3a302026f6fa536e745c627da360dc0fb9c3898941aff24a610319d80df1c232';b=json.loads(before);assert a['rows']==b['rows']and len(a['rows'])==24
parents=a['pid1'];d=[v for v in parents if v.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and v.get('JOB_ID')=='76444'and v.get('JOB_TYPE')=='start'and v.get('JOB_RESULT')=='done'];assert len(d)==1
assert d[0]['_BOOT_ID']=='cc9ed8747f4f450ea1888de1e42c8441'and d[0]['_PID']=='1'and d[0]['_UID']=='0'and d[0]['INVOCATION_ID']=='267003d6e12845dd8690cd9bd5afcad0'
offset=int(d[0]['__REALTIME_TIMESTAMP'])-int(d[0]['__MONOTONIC_TIMESTAMP'])
parent=pathlib.Path('/run/schubert-nk/pt-coverage');selected=[]
names=[('backup/backup.exec','schubert-nk-backup.service'),('cleanup/cleanup.exec','schubert-nk-cleanup.service'),('expiry/expiry.exec','schubert-nk-expiry-cleanup.service'),('parent/parent.exec','schubert-nk-morning-controller.service')]
for role,unit in [('api','schubert-nk-api.service'),('web','schubert-nk-web.service')]:
 inv=b['units'][unit]['InvocationID'];names.extend([('ordinary-'+role+'193/'+inv+'.terminal.exec',unit),('root-'+role+'193/'+inv+'.before-exec.exec',unit)])
for name,unit in names:
 if unit=='schubert-nk-morning-controller.service':start=57679957905;end=59234299969
 else:start=int(b['units'][unit]['ExecMainStartTimestampMonotonic']);end=int(a['units'][unit]['ExecMainExitTimestampMonotonic'])
 assert 0<start<=end and start>=57679957905 and end<=60394564274
 p=parent/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216
 raw=p.read_bytes();assert metadata(s)==metadata(p.lstat());sealed=a['native'][str(p)];assert metadata(s)==sealed['metadata']and hashlib.sha256(raw).hexdigest()==sealed['sha256'];selected.append({'relative':name,'unit':unit,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':s.st_size,'metadata':metadata(s),'lowerMs':(offset+start)//1000-1000,'upperMs':(offset+end)//1000+1000})
assert len(selected)==8 and len({v['relative']for v in selected})==8
print(json.dumps(selected))
'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
    changed=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T,text=True).splitlines()
    allowed={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/MaintenanceMutationGuardTest.java',*{'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/'+n for n in ('ChildBrokerTest.java','ChildMaintenanceInspectorTest.java','ChildMaintenanceParentTest.java')}}
    assert set(changed)<=allowed
    work=W/'pg581-current-eighteen-native-v2';assert not os.path.lexists(work)
    prior=W/'pg571-current-ten-native-v2';assert sha(prior/'manifest.safe.json')=='1b3cbe0935f3435411854f38ce66779b3923bbf13e57201765527a19a99eb48f'
    old=json.loads((prior/'manifest.safe.json').read_bytes());nine=W/'pg561-current-native-v2';nine_manifest=json.loads((nine/'manifest.safe.json').read_bytes())
    assert sha(nine/'manifest.safe.json')=='e253b4e23d25dc030da33ad67fbb41d9a492426492416931dbeefc31cc73ed8a'and old['productionSource']==SOURCE and old['actualExit']==0
    assert (W/'pg579-native-stop-v1.exit').read_bytes()==b'0\n'and(W/'pg580-terminal-final-v1.exit').read_bytes()==b'0\n'
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
    selected=json.loads(subprocess.check_output(ssh+['sudo -n python3 -B -'],input=PAYLOAD.encode(),timeout=30))
    work.mkdir(mode=0o700);native=[]
    for i,v in enumerate(nine_manifest['currentNativeFiles']):
        p=nine/(str(i)+'.exec');assert sha(p)==v['sha256'];native.append(p)
    assert len(native)==9 and sha(prior/'bootstrap.exec')==old['currentBootstrap']['sha256'];native.append(prior/'bootstrap.exec')
    classes=prior/'classes';repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(classes)]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        jars=list(repo.glob(pattern));assert len(jars)==1;cp.append(str(jars[0]))
    sessions=[]
    for i,v in enumerate(selected):
        p=work/(str(i)+'.exec')
        with p.open('xb')as f:
            r=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15);f.flush();os.fsync(f.fileno())
        assert r.returncode==0 and not r.stderr and p.stat().st_size==v['bytes']and sha(p)==v['sha256']
        r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeSessions571',str(v['lowerMs']),str(v['upperMs']),str(p)],capture_output=True,timeout=30)
        with(work/(str(i)+'-session.private.log')).open('xb')as f:f.write(r.stdout);f.write(r.stderr)
        assert r.returncode==0 and not r.stderr;rows=[json.loads(l)for l in r.stdout.splitlines()];assert len(rows)==1;sessions.extend(rows);native.append(p)
    assert len(native)==18
    modules=('protocol','storage','bootstrap','api','web','batch');host=W/'pg540-six-host-v1';executions=[host/m/'jacoco.exec'for m in modules]
    assert all(sha(p)==old['hostExecHashes'][m]for m,p in zip(modules,executions))
    counters={};gain={}
    for module in modules:
        jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in executions+native]],capture_output=True,timeout=45)
        with(work/(module+'-counter.private.log')).open('xb')as f:f.write(r.stdout);f.write(r.stderr)
        assert r.returncode==0 and not r.stderr;v=json.loads(r.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[module]=v
        gain[module]={k:old['moduleCounters'][module][k]['missed']-v[k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')};assert all(x>=0 for x in gain[module].values())
    record={'run':'PG581-current-eighteen-native-v2','actualExit':0,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorTenManifestSha256':sha(prior/'manifest.safe.json'),'newFiles':selected,'newSingleSessions':sessions,'currentNativeStreams':18,'newStreams':8,'historicalExcluded':5,'moduleCounters':counters,'gain':gain,'PG541565SelectedNotMixed':True,'sameFrozenSixHostHashes':old['hostExecHashes'],'coverage100':all(v[k]['missed']==0 for v in counters.values()for k in ('LINE','METHOD','CLASS','BRANCH')),'formalAccepted':False,'rawExported':False}
    with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'streams':18,'newStreams':8,'newlyCovered':{k:sum(v[k]for v in gain.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'remaining':{k:sum(v[k]['missed']for v in counters.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))


if __name__=='__main__':main()
