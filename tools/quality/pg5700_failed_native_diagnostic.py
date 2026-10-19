"""BUG1470 copy stable original stoppedRoot exec for diagnosis only; no formal/native success."""
import base64
import datetime
import hashlib
import inspect
import json
import os
import re
from pathlib import Path
import subprocess
import pg5644_current_admission_image as admission
from pg5638_new_normal_root_once import SSH,W

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg5700-failed-native-diagnostic-v2'
MODULES=('protocol','storage','bootstrap','api','web','batch')


def stable(before,after,old_unit,new_unit,first_sha,second_sha):
    keys=('device','inode','uid','gid','mode','links','size','mtimeNanos','ctimeNanos')
    if type(before)is not dict or type(after)is not dict or set(before)!=set(keys)|{'atimeNanos'}or set(after)!=set(before):return False
    if any(type(v)is not int or v<0 for values in(before,after)for v in values.values()):return False
    return(all(before[k]==after[k]for k in keys)and type(old_unit)is dict and type(new_unit)is dict and old_unit==new_unit
      and type(first_sha)is str and re.fullmatch('[0-9a-f]{64}',first_sha)is not None and first_sha==second_sha)


GUEST=r'''
import base64,datetime,hashlib,json,os,pathlib,re,stat,subprocess
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
mr=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(mr).hexdigest()=='1aa1fb6300946d086c60f005f6e4253b1ffd0da873ada103dd89c94cac89b173'
args=['systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,ControlPID,Job,InvocationID,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,ExecMainStatus,ExecStart']
def read():
 r=subprocess.run(args,capture_output=True,text=True,timeout=10);assert r.returncode==0;return dict(s.split('=',1)for s in r.stdout.splitlines())
unit=read();assert unit['InvocationID']=='8df395b5d8284acf88aae7c36a8354a3'and unit['ExecMainStartTimestampMonotonic']=='417804186824'and unit['MainPID']==unit['ControlPID']=='0'and unit['Job']==''and unit['ExecMainStatus']=='30'
assert 'destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false'in unit['ExecStart']
p=pathlib.Path('/run/schubert-nk/pt-coverage/parent/parent.exec');s=p.lstat()
assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and s.st_nlink==1 and 0<s.st_size<=16777216 and 1792418550<=s.st_mtime<=1792419845
def meta(s):return dict(zip(('device','inode','uid','gid','mode','links','size','mtimeNanos','ctimeNanos','atimeNanos'),(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_atime_ns)))
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg5700-failed-native-input-v2');os.umask(0o077);out.mkdir(mode=0o700)
def save(name,value):
 with(out/name).open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
before=meta(s);save('before.private.json',{'metadata':before,'unit':unit})
raw=p.read_bytes();first_sha=hashlib.sha256(raw).hexdigest();second_sha=hashlib.sha256(p.read_bytes()).hexdigest();after=meta(p.lstat());second=read()
save('after.private.json',{'metadata':after,'unit':second,'firstSha256':first_sha,'secondSha256':second_sha})
assert stable(before,after,unit,second,first_sha,second_sha)
print(json.dumps({'actualExit':0,'originalFailedRootInvocation':unit['InvocationID'],'rootExit':30,'nativeSha256':hashlib.sha256(raw).hexdigest(),'nativeSize':len(raw),'mtimeNanos':s.st_mtime_ns,'base64':base64.b64encode(raw).decode(),'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'diagnosticOnly':True,'formalAccepted':False}))
'''
GUEST=inspect.getsource(stable)+'\n'+GUEST


def main():
    admission.authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=GUEST.encode(),capture_output=True,timeout=45)
    for name,data in(('original-reply.private.json',r.stdout),('capture-stderr.private.log',r.stderr),('payload.private.py',GUEST.encode())):
        with(out/name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    if r.returncode:raise ValueError('original stopped failedRoot native proof unavailable; no capture command fallback')
    v=json.loads(r.stdout);data=base64.b64decode(v.pop('base64'),validate=True)
    if hashlib.sha256(data).hexdigest()!=v['nativeSha256']or len(data)!=v['nativeSize']:raise ValueError('original failed native bytes')
    with(out/'failed-parent.private.exec').open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    whole=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json').read_bytes())
    roots=[W/'pg5566-private-monitor-green-v3/source'/('src/schubert-nk-'+m+'/target/classes')for m in MODULES]
    actual={m+':'+p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for m,root in zip(MODULES,roots)for p in root.rglob('*.class')}
    if len(actual)!=1664 or actual!=whole['allPhysicalMainSha256']or whole['productionSource']!=admission.SOURCE:raise ValueError('all current1664 actual class bytes, no historical substitute')
    repo=Path('/home/mini/.m2/repository');libs=[repo/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar']
    libs += [repo/('org/ow2/asm/'+n+'/9.10.1/'+n+'-9.10.1.jar')for n in('asm','asm-tree','asm-commons')]
    cp=os.pathsep.join(map(str,libs));jdk=ROOT.parent/'toolchain/jdk-25.0.4/bin';classes=out/'classes';classes.mkdir()
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    commands=[[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(ROOT/'tools/quality/FailedRootCoverageDiagnostic.java')],
      [str(jdk/'java'),'-Xmx512m','-cp',str(classes)+os.pathsep+cp,'FailedRootCoverageDiagnostic',str(out/'failed-parent.private.exec'),*map(str,roots)]]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for i,command in enumerate(commands):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=90)
        if result.returncode:raise ValueError('diagnostic helper/actual class CRC refusal; failedRoot stays failed')
    value={**v,'source':admission.SOURCE,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'classMainCount':len(actual),'classByteMismatch':0,'libraryHashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in libs},
      'helperSha256':hashlib.sha256((ROOT/'tools/quality/FailedRootCoverageDiagnostic.java').read_bytes()).hexdigest(),
      'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'normalNativeQualified':False,'wholeMorningAccepted':False,'formalAccepted':False,'F03Accepted':False,'acceptedLeafDelta':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','source','rootExit','nativeSha256','classMainCount','classByteMismatch','diagnosticOnly','normalNativeQualified','wholeMorningAccepted','formalAccepted')}))


if __name__=='__main__':main()
