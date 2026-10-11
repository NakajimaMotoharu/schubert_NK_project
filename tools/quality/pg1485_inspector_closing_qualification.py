"""PT-OPS-INS1485001: saved genuine Inspector, independent latest-only qualification.

SS324/331/342/343/354, 451. No Unit/DB/epoch mutation or business replay.
Session IDs remain private; only independent boolean receipt is published.
"""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import SSH, W

SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
FIXED={'terminal.exec':(17315,'6283aef1d747a9ab83b70e84e274f3dce1fb65ed931063ad09e1c4106f603ef6'),
       'closing.exec':(17315,'8086ecb87fbb75e473a9e975445b17177ff4c97f3fb025eb6b8e36ce5c0ff051'),
       'pid1.private.jsonl':(None,'da53410e59f307cec4f196105e0ce1afec19e8d766913ca3ee088827ed3e87b4')}

def require(value):
    if not value:raise ValueError('fixed saved Inspector closing qualification refused')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def bounds(records):
    require(type(records)is list and len(records)==5)
    for r in records:
        require(type(r)is dict and r.get('_BOOT_ID')=='3d69f5af6bac46b1a5407591c4a79a0d' and r.get('_PID')=='1' and r.get('_UID')=='0' and r.get('UNIT')=='schubert-nk-inbox-inspector.service' and r.get('INVOCATION_ID')=='d69f0f99b48a47a5b51ad571ac996c31')
    def one(mid,kind,job,result):
        matched=[r for r in records if r.get('MESSAGE_ID')==mid and r.get('JOB_TYPE')==kind and r.get('JOB_ID')==job and (result is None or r.get('JOB_RESULT')==result)]
        require(len(matched)==1);return matched[0]
    a=one('7d4958e842da4a758f6c1cdc7b36dcc5','start','13787',None)
    b=one('39f53479d3a045ac8e11786248231fbf','start','13787','done')
    c=one('9d1aaa27d60140bd96365438aad20286','stop','13934','done')
    require(5711141318<int(a['__MONOTONIC_TIMESTAMP'])<int(b['__MONOTONIC_TIMESTAMP'])<int(c['__MONOTONIC_TIMESTAMP'])<7511141318)
    low=int(a['__REALTIME_TIMESTAMP'])//1000;high=(int(c['__REALTIME_TIMESTAMP'])+999)//1000
    require(0<low<=high);return low,high

def payload():
    return "FIXED="+repr(FIXED)+"\n"+r'''
import base64,hashlib,json,os,pathlib,stat
def require(v):
 if not v:raise ValueError('fixed saved Inspector export refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
bom=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(bom).hexdigest()=='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99' and json.loads(bom)['source']['commit']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f')
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1462-current-day-inspector-v1')
m=root.lstat();require(stat.S_ISDIR(m.st_mode)and not root.is_symlink()and m.st_uid==m.st_gid==0 and stat.S_IMODE(m.st_mode)==0o700)
out={}
for name,(size,digest)in FIXED.items():
 p=root/name;fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  before=os.fstat(fd);require(stat.S_ISREG(before.st_mode)and before.st_uid==before.st_gid==0 and stat.S_IMODE(before.st_mode)==0o600 and before.st_nlink==1)
  with os.fdopen(os.dup(fd),'rb')as f:body=f.read(8388609)
  after=os.fstat(fd);vector=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  require(vector(before)==vector(after)==vector(p.lstat())and len(body)<=8388608 and(size is None or len(body)==size)and hashlib.sha256(body).hexdigest()==digest and not os.listxattr(fd))
  out[name]=base64.b64encode(body).decode('ascii')
 finally:os.close(fd)
print(json.dumps(out,sort_keys=True))
'''

def main():
    os.umask(0o077);out=W/'pg1485-inspector-closing-qualification-v1';out.mkdir(mode=0o700)
    require(not subprocess.check_output(['git','diff',SOURCE,'--','src/*/src/main','pom.xml','src/*/pom.xml']))
    prior=W/'pg1462-current-day-inspector-v1/manifest.safe.json';v=json.loads(prior.read_bytes())
    require(v['actualExit']==0 and v['guest']['productionSource']==SOURCE and v['guest']['genuinePid1StartDoneStop']is True)
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    start=datetime.datetime.now(datetime.timezone.utc)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=45)
    (out/'transport.private.log').write_bytes(r.stderr);require(r.returncode==0 and not r.stderr)
    exported=json.loads(r.stdout);require(set(exported)==set(FIXED))
    for name,(size,digest)in FIXED.items():
        b=base64.b64decode(exported[name],validate=True);require(hashlib.sha256(b).hexdigest()==digest and(size is None or len(b)==size))
        with(out/name).open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
    low,high=bounds([json.loads(x)for x in(out/'pid1.private.jsonl').read_bytes().splitlines()])
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');libs=[]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        found=list(repo.glob(pattern));require(len(found)==1);libs.append(str(found[0]))
    cp=':'.join(libs);java=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin');tools=Path('tools/quality/vm/050_s1')
    classes=out/'classes';classes.mkdir(mode=0o700)
    with(out/'oracle.private.log').open('xb')as f:
        for args in ([str(java/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(tools/'NativeClosingSelect1411.java'),str(tools/'NativeClosingSelect1411Test.java')],[str(java/'java'),'-cp',str(classes)+':'+cp,'NativeClosingSelect1411Test']):
            require(subprocess.run(args,stdout=f,stderr=f).returncode==0)
    r=subprocess.run([str(java/'java'),'-cp',str(classes)+':'+cp,'NativeClosingSelect1411',str(out/'terminal.exec'),str(out/'closing.exec'),str(low),str(high)],capture_output=True)
    (out/'actual-monotonic.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
    proof=json.loads(r.stdout);require(all(proof[k]is True for k in ('sameSession','probeMonotonic','latestClosingOnly')))
    host=W/'pg1279-held-channel-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes());require(h['candidateSource']==SOURCE)
    jar=host/'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar';require(sha(jar)==h['moduleResults']['batch']['jarSha256'])
    helper=W/'pg571-current-ten-native-v2/classes';require(sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a')
    r=subprocess.run([str(java/'java'),'-cp',str(helper)+':'+cp,'NativeCoverage',str(jar),str(out/'closing.exec')],capture_output=True,timeout=45)
    (out/'crc.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
    coverage=json.loads(r.stdout);require(coverage['classByteMismatch']==0)
    manifest={'run':'PG1485-inspector-closing-qualification-v1','actualExit':0,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startUTC':start.isoformat(),'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeHashes':{n:d for n,(_,d)in FIXED.items()},'priorInspectorManifestSha256':sha(prior),'batchJarSha256':sha(jar),'closingOracle':proof,'classByteMismatch':0,'terminalRetainedNotSelected':True,'sameSessionUnion0':True,'standaloneClosingCounters':coverage,'vmActions0':True,'formalAccepted':False,'wholeParentAccepted':False,'globalCounterPending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:manifest[k]for k in ('actualExit','closingOracle','classByteMismatch','formalAccepted','globalCounterPending')}));return 0

if __name__=='__main__':raise SystemExit(main())
