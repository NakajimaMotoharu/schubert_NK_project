"""New source frozen six host + eight qualified actual native streams. Diagnostic, not formal."""
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
SOURCE='23b14a44b10504172e030bbd6625926bf049fb5c'
HASHES={"backup/backup.exec":"a1d48ac5bbed0db049ee385aa0b80342c307ca9075573aad86a6417d2fee7324","cleanup/cleanup.exec":"cdb44f1fedfad4733487217421b623facb46d4cf3ec665231ea47c469a5a1ff0","expiry/expiry.exec":"b1c3afe18437df69b79d572c70edd2de47b0eac2a6e323eba5747851b47d5215","parent/parent.exec":"42f52d94aab7572ef81f1eb2fb1c65b1c8f3859e3ab95db5d32110a72c32c928","ordinary-api193/4db7f8a4637a4b9f909de4d319677179.terminal.exec":"ddf0353d9e315eace72f1ce8600a7050d78651944b66273a457e701209b7dec0","root-api193/4db7f8a4637a4b9f909de4d319677179.before-exec.exec":"152fe772bef9ba3723deb01d1b046e8fa9b73ffbd6f6247ad8e0c8cbbd383fbd","ordinary-web193/866af4c303904f1e998a5a50f6ccc716.terminal.exec":"eee5d61502cf972fb216626befa797b2301dbcc48faeec246e8e6013a9d6aade","root-web193/866af4c303904f1e998a5a50f6ccc716.before-exec.exec":"c31a14fb5f0c6c3e6f9549e904c442de4ce3e2d8b4672322a0822c85234d036a"}
PAYLOAD=r'''
import hashlib,json,pathlib,stat
def metadata(s):
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg611-native-stop-v1');raw=(root/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849';a=json.loads(raw)
before=(root/'before.private.json').read_bytes();assert hashlib.sha256(before).hexdigest()=='19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912';b=json.loads(before);assert a['rows']==b['rows']and len(a['rows'])==24
parents=a['pid1'];d=[v for v in parents if v.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and v.get('JOB_ID')=='87863'and v.get('JOB_TYPE')=='start'and v.get('JOB_RESULT')=='done'];assert len(d)==1
assert d[0]['_BOOT_ID']=='cc9ed8747f4f450ea1888de1e42c8441'and d[0]['_PID']=='1'and d[0]['_UID']=='0'and d[0]['INVOCATION_ID']=='5a1acaa0c35e484c979401e3b6dfb36a'
offset=int(d[0]['__REALTIME_TIMESTAMP'])-int(d[0]['__MONOTONIC_TIMESTAMP'])
parent=pathlib.Path('/run/schubert-nk/pt-coverage');selected=[]
names=[('backup/backup.exec','schubert-nk-backup.service'),('cleanup/cleanup.exec','schubert-nk-cleanup.service'),('expiry/expiry.exec','schubert-nk-expiry-cleanup.service'),('parent/parent.exec','schubert-nk-morning-controller.service')]
for role,unit in [('api','schubert-nk-api.service'),('web','schubert-nk-web.service')]:
 inv=b['units'][unit]['InvocationID'];names.extend([('ordinary-'+role+'193/'+inv+'.terminal.exec',unit),('root-'+role+'193/'+inv+'.before-exec.exec',unit)])
for name,unit in names:
 if unit=='schubert-nk-morning-controller.service':start=86264628081;end=87761979588
 else:start=int(b['units'][unit]['ExecMainStartTimestampMonotonic']);end=int(a['units'][unit]['ExecMainExitTimestampMonotonic'])
 assert 0<start<=end and start>=86264628081 and end<=max(int(x['ExecMainExitTimestampMonotonic'])for x in a['units'].values())
 p=parent/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216
 raw=p.read_bytes();assert metadata(s)==metadata(p.lstat());digest=hashlib.sha256(raw).hexdigest();assert digest==HASHES[name];selected.append({'relative':name,'unit':unit,'sha256':digest,'bytes':s.st_size,'metadata':metadata(s),'lowerMs':(offset+start)//1000-1000,'upperMs':(offset+end)//1000+1000})
assert len(selected)==8 and len({v['relative']for v in selected})==8
print(json.dumps(selected))
'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T)
    assert (W/'pg611-native-stop-v1.exit').read_bytes()==b'0\n' and (W/'pg613-terminal-final-v1.exit').read_bytes()==b'0\n'
    host=W/'pg599-candidate-bootstrap-six-host-v1'
    manifest=host/'manifest.safe.json'
    # Actual fresh host provenance, not the old PG540/969 host or old18 native.
    assert sha(manifest)=='cdd971634fe0f5acabe091db476f25838a55730172d3cc07244180e708f4e47d'
    host_record=json.loads(manifest.read_bytes())
    assert host_record['candidateSource']==SOURCE and host_record['actualExit']==0 and host_record['tests']==3457
    work=W/'pg614-current-eight-native-v1';assert not os.path.lexists(work)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
    selected=json.loads(subprocess.check_output(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(HASHES)+'\n'+PAYLOAD).encode(),timeout=30))
    work.mkdir(mode=0o700)
    helper=W/'pg571-current-ten-native-v2/classes'
    assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'
    assert sha(helper/'NativeSessions571.class')=='24eef12a79368196666f1c596469ab5518c3a5c00375be0c706ebb1cdec88d39'
    repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    cp=[str(helper)]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
    streams=[];sessions=[]
    for i,v in enumerate(selected):
        p=work/(str(i)+'.exec')
        with p.open('xb')as f:
            result=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=15)
            f.flush();os.fsync(f.fileno())
        assert result.returncode==0 and not result.stderr and p.stat().st_size==v['bytes'] and sha(p)==v['sha256']
        result=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeSessions571',str(v['lowerMs']),str(v['upperMs']),str(p)],capture_output=True,timeout=30)
        with(work/(str(i)+'-session.private.log')).open('xb')as f:f.write(result.stdout+result.stderr)
        assert result.returncode==0 and not result.stderr
        info=[json.loads(l)for l in result.stdout.splitlines()];assert len(info)==1;sessions.extend(info);streams.append(p)
    modules=('protocol','storage','bootstrap','api','web','batch')
    executions=[host/m/'jacoco.exec'for m in modules]
    assert all(sha(p)==host_record['moduleResults'][m]['execSha256']for m,p in zip(modules,executions))
    counters={};hostOnly={};moduleLocal={};gain={}
    for m in modules:
        jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
        assert sha(jar)==host_record['moduleResults'][m]['jarSha256']
        for label,files in [('local',[executions[modules.index(m)]]),('host',executions),('union',executions+streams)]:
            q=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in files]],capture_output=True,timeout=45)
            with(work/(m+'-'+label+'.private.log')).open('xb')as f:f.write(q.stdout+q.stderr)
            assert q.returncode==0 and not q.stderr
            v=json.loads(q.stdout);assert v['classByteMismatch']==0 and v['formal']is False
            (moduleLocal if label=='local' else hostOnly if label=='host' else counters)[m]=v
        gain[m]={k:hostOnly[m][k]['missed']-counters[m][k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')}
        assert all(v>=0 for v in gain[m].values())
        # BUG999/YKT768: XML is module-local, not cross-module shared-class probes.
        assert all(moduleLocal[m][k]==host_record['moduleResults'][m]['hostCounters'][k]for k in ('LINE','METHOD','CLASS','BRANCH'))
        assert all(hostOnly[m][k]['missed']<=moduleLocal[m][k]['missed'] and sum(hostOnly[m][k].values())==sum(moduleLocal[m][k].values()) for k in ('LINE','METHOD','CLASS','BRANCH'))
    record={'run':'PG614-current-eight-native-v1','actualExit':0,'productionSource':SOURCE,
        'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
        'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'frozenHostManifestSha256':sha(manifest),'hostExecHashes':{m:sha(p)for m,p in zip(modules,executions)},
        'currentNativeStreams':8,'historicalNativeNotImported':True,'selected':selected,'singleSessions':sessions,
        'moduleLocalCounters':moduleLocal,'hostOnlyCounters':hostOnly,'moduleCounters':counters,'gain':gain,
        'coverage100':all(v[k]['missed']==0 for v in counters.values()for k in ('LINE','METHOD','CLASS','BRANCH')),
        'formalAccepted':False,'rawExported':False}
    with(work/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'streams':8,'newlyCovered':{k:sum(v[k]for v in gain.values())for k in ('LINE','METHOD','CLASS','BRANCH')},
        'remaining':{k:sum(v[k]['missed']for v in counters.values())for k in ('LINE','METHOD','CLASS','BRANCH')},
        'manifestSha256':sha(work/'manifest.safe.json'),'formalAccepted':False}))
if __name__=='__main__':main()
