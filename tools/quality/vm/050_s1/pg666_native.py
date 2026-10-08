"""Qualify new current Bootstrap single stream then same-source16+1+host6 union."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg658_same_source_union import admissible

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
INV='65bfe1da3b9e454997f1d899fea9510e'
HOST_SHA='067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b'
PAYLOAD=r'''
import hashlib,json,pathlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg664-bootstrap-existing-v1')
raw=(r/'after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98';a=json.loads(raw)
raw=(r/'before.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='8767e53ccfc2ea3f434689674dad7395feaef31cec48d53a92bc6fd7eed81c08';b=json.loads(raw)
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert a['rows']==b['rows']and len(a['rows'])==24 and len(a['rows']['schubert.batch_runs'])==514
u=a['units']['schubert-nk-bootstrap-admin.service'];inv=u['InvocationID'];assert inv=='65bfe1da3b9e454997f1d899fea9510e'and u['ExecMainCode']=='1'and u['ExecMainStatus']=='20'
relative='ordinary-bootstrap196/'+inv+'.terminal.exec';p=pathlib.Path('/run/schubert-nk/pt-coverage')/relative;value=a['native'][str(p)]
def meta(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
s=p.lstat();assert meta(s)==value['metadata']and stat.S_ISREG(s.st_mode)and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(999,981,0o600,1)and 0<s.st_size<=16777216 and not __import__('os').listxattr(p)
assert hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256']and meta(p.lstat())==meta(s)
assert str(p)not in b['native']and set(a['native'])==set(b['native'])|{str(p)}
actor=json.loads((r/'actor.private.json').read_bytes());assert actor=={'pid':'2142585','ticks':'11164505','invocation':inv,'zeroCapabilities':True}and not pathlib.Path('/proc','2142585').exists()
jobs=[v for v in map(json.loads,(r/'pid1.private.jsonl').read_bytes().splitlines())if v.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and v.get('JOB_ID')=='119175'and v.get('JOB_TYPE')=='start'and v.get('JOB_RESULT')=='done'];assert len(jobs)==1;d=jobs[0]
assert d['_PID']=='1'and d['_UID']=='0'and d['_COMM']=='systemd'and d['_BOOT_ID']=='cc9ed8747f4f450ea1888de1e42c8441'and d['INVOCATION_ID']==inv
start=int(u['ExecMainStartTimestampMonotonic']);end=int(u['ExecMainExitTimestampMonotonic']);assert start==111645058422 and end==111646651773 and 0<end-start<=30000000
offset=int(d['__REALTIME_TIMESTAMP'])-int(d['__MONOTONIC_TIMESTAMP']);lower=(start+offset)//1000-1000;upper=(int(d['__REALTIME_TIMESTAMP']))//1000+1000
print(json.dumps({'relative':relative,'sha256':value['sha256'],'bytes':s.st_size,'metadata':meta(s),'lowerMs':lower,'upperMs':upper,'invocation':inv,'pid':'2142585','ticks':'11164505','boot':'cc9ed874-7f4f-450e-a188-8de1e42c8441','role':'BOOTSTRAP','point':'TERMINAL','unitElapsedSeconds':(end-start)/1000000,'pid1Job':'119175'}))
'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def session_valid(value,metadata):
    expected=hashlib.sha256(b'BOOTSTRAP-65bfe1da3b9e454997f1d899fea9510e-ordinary').hexdigest()
    return(type(value)is dict and value.get('sessions')==1 and type(value.get('sessions'))is int
           and value.get('sessionIdSha256')==expected and type(value.get('startMs'))is int and type(value.get('dumpMs'))is int
           and metadata['lowerMs']<=value['startMs']<=value['dumpMs']<=metadata['upperMs'])


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'])==b''
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'])
    assert (W/'pg665-bootstrap-final-v3.exit').read_bytes()==b'0\n'
    final=json.loads((W/'pg665-bootstrap-final-v3.safe.json').read_bytes())
    assert final['actualExit']==0 and final['productionSource']==SOURCE and final['full20Fields']and final['allClientAdvisoryFlock0']
    assert final['executeProofs']['after.private.json']['sha256']=='fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98'
    prior=W/'pg658-same-source-sixteen-native-v1';old=json.loads((prior/'manifest.safe.json').read_bytes())
    assert old['actualExit']==0 and old['source']==SOURCE and old['qualifiedSingleSessions']==16
    first=W/'pg644-current-eight-native-v1';second=W/'pg657-normal-eight-native-v1'
    records=[json.loads((p/'manifest.safe.json').read_bytes())for p in(first,second)];admissible(*records)
    for p in(first,second):assert sha(p/'manifest.safe.json')==old['qualificationManifests'][p.name]
    host=W/'pg630-retention-factory-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes())
    assert sha(host/'manifest.safe.json')==HOST_SHA and h['candidateSource']==SOURCE and h['actualExit']==0
    target=W/'pg666-current-seventeen-native-v1';target.mkdir(mode=0o700)
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
    selected=json.loads(subprocess.check_output(ssh+['sudo -n python3 -B -'],input=PAYLOAD.encode(),timeout=30))
    stream=target/'bootstrap.exec'
    with stream.open('xb')as f:
        result=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+selected['relative']],stdout=f,stderr=subprocess.PIPE,timeout=20);f.flush();os.fsync(f.fileno())
    assert result.returncode==0 and not result.stderr and stream.stat().st_size==selected['bytes']and sha(stream)==selected['sha256']
    helper=W/'pg571-current-ten-native-v2/classes'
    assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'
    assert sha(helper/'NativeSessions571.class')=='24eef12a79368196666f1c596469ab5518c3a5c00375be0c706ebb1cdec88d39'
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(helper)]
    for pattern in('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths=list(repo.glob(pattern));assert len(paths)==1;cp.append(str(paths[0]))
    java='/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java'
    result=subprocess.run([java,'-cp',':'.join(cp),'NativeSessions571',str(selected['lowerMs']),str(selected['upperMs']),str(stream)],capture_output=True,timeout=30)
    assert result.returncode==0 and not result.stderr
    session=json.loads(result.stdout);assert session_valid(session,selected)
    assert session['sessionIdSha256']not in {s['sessionIdSha256']for r in records for s in r['singleSessions']}
    streams=[]
    for directory,r in zip((first,second),records):
        for i,value in enumerate(r['selected']):
            p=directory/(str(i)+'.exec');assert p.stat().st_size==value['bytes']and sha(p)==value['sha256'];streams.append(p)
    streams.append(stream);assert len(streams)==17
    modules=('protocol','storage','bootstrap','api','web','batch');data=[host/m/'jacoco.exec'for m in modules]
    counters={};gain={}
    for m,p in zip(modules,data):assert sha(p)==h['moduleResults'][m]['execSha256']==records[0]['hostExecHashes'][m]
    for m in modules:
        jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256']
        result=subprocess.run([java,'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in data+streams]],capture_output=True,timeout=45)
        with(target/(m+'.private.log')).open('xb')as f:f.write(result.stdout+result.stderr)
        assert result.returncode==0 and not result.stderr;v=json.loads(result.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[m]=v
        gain[m]={k:old['moduleCounters'][m][k]['missed']-v[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')};assert all(n>=0 for n in gain[m].values())
    record={'run':'PG666-current-seventeen-native-v1','actualExit':0,'source':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'qualifiedSingleSessions':17,'qualificationManifests':old['qualificationManifests'],'previousUnionSha256':sha(prior/'manifest.safe.json'),'frozenHostManifestSha256':HOST_SHA,
            'bootstrap':selected,'bootstrapSession':session,'finalProofSha256':sha(W/'pg665-bootstrap-final-v3.safe.json'),'moduleCounters':counters,'gainVsPG658':gain,
            'remaining':{k:sum(v[k]['missed']for v in counters.values())for k in('LINE','METHOD','CLASS','BRANCH')},'otherSourceStreamsImported':False,'formalAccepted':False,'rawExported':False}
    record['coverage100']=all(v==0 for v in record['remaining'].values())
    with(target/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'native17':True,'gain':{k:sum(v[k]for v in gain.values())for k in('LINE','METHOD','CLASS','BRANCH')},'remaining':record['remaining'],'manifestSha256':sha(target/'manifest.safe.json'),'formalAccepted':False}))


if __name__=='__main__':main()
