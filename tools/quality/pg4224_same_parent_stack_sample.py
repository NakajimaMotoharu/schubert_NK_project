"""SSC290 bounded read-only current parent stack. No heap/JFR/env/flags or service commands."""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pg1446_current_cold_stage import W,SSH
from pg4220_same_peer_current_observer import SOURCE,BOM


def select_parent(frames):
    rows=[r['states']['morning']for r in frames if type(r)is dict and type(r.get('states'))is dict and 'morning'in r['states']]
    if not rows:raise ValueError('original fresh observer parent frame required')
    value=rows[-1]
    if value.get('race')or value.get('entry')!='dev.codex.schubert.nk.batch.file.MorningProcessMain' or not value.get('MainPID','').isdecimal()or int(value['MainPID'])<2:
        raise ValueError('current live Root parent required; terminal/old frame is not a sample')
    if value.get('InvocationID')=='820851b8291a4c958bb34f6c48430ca3'or re.fullmatch(r'(?!0{32}$)[0-9a-f]{32}',value.get('InvocationID',''))is None:raise ValueError('distinct current invocation required')
    if value.get('process',{}).get('Uid','').split()!=['0']*4:raise ValueError('same Root authority required')
    if type(value.get('startTicks'))is not int or value['startTicks']<=0:raise ValueError('exact kernel generation required')
    return value


def frames_from(raw):
    if type(raw)is not bytes or len(raw)>4194304:raise ValueError('bounded original stack bytes required')
    text=raw.decode('utf-8');sections=text.split('"main"',1)
    if len(sections)!=2:raise ValueError('original main thread required')
    main=sections[1].split('\n\n',1)[0]
    frames=[line.strip()for line in main.splitlines()if re.fullmatch(r'\s+at [A-Za-z0-9_.$/]+\([^\r\n()]{1,180}\)',line)]
    if not frames:raise ValueError('bounded method frames required')
    return frames[:32]


def payload(expected,slot):
    return 'EXPECTED='+repr(expected)+'\nSLOT='+repr(slot)+'\nSOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\n'+BODY


BODY=r'''
from pathlib import Path
import os,hashlib,json,subprocess,time,datetime,select
require=lambda v:None if v else(_ for _ in()).throw(ValueError('current generation stack refusal'))
require(os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
pid=EXPECTED['MainPID'];p=Path('/proc')/pid
def owner():
 value=dict(line.split('=',1)for line in subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,InvocationID,ExecMainStartTimestampMonotonic,ActiveState,SubState'],text=True,timeout=5).splitlines())
 require(value['MainPID']==pid and value['InvocationID']==EXPECTED['InvocationID']and value['ExecMainStartTimestampMonotonic']==EXPECTED['ExecMainStartTimestampMonotonic']and value['ActiveState']=='activating')
 require(int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==EXPECTED['startTicks'])
 argv=(p/'cmdline').read_bytes();require(argv.endswith(b'\0')and argv.split(b'\0')[-2]==b'dev.codex.schubert.nk.batch.file.MorningProcessMain')
 require(Path(p/'exe').resolve()==Path('/opt/jdk-25.0.4/bin/java').resolve())
 value['argvSha256']=hashlib.sha256(argv).hexdigest()
 uid=next(l for l in(p/'status').read_text().splitlines()if l.startswith('Uid:'));require(uid.split()[1:]==['0']*4)
 require(time.monotonic_ns()//1000<int(value['ExecMainStartTimestampMonotonic'])+1770000000)
 return value
before=owner();fd=os.pidfd_open(int(pid));poll=select.poll();poll.register(fd,select.POLLIN)
save=Path('/var/lib/pgpt-s1-preservation')/SLOT;os.umask(0o077);save.mkdir(mode=0o700)
try:
 require(not poll.poll(0)and owner()==before)
 started=time.monotonic_ns()
 result=subprocess.run(['/opt/jdk-25.0.4/bin/jcmd',pid,'Thread.print','-l'],capture_output=True,timeout=20)
 for name,raw in [('stack.private.log',result.stdout),('error.private.log',result.stderr)]:
  with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 require(result.returncode==0 and not poll.poll(0)and owner()==before)
 require(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()==manifest)
 print(json.dumps({'actualExit':0,'source':SOURCE,'BOM':BOM,'invocation':EXPECTED['InvocationID'],'pid':int(pid),'ticks':EXPECTED['startTicks'],
 'elapsedNanos':time.monotonic_ns()-started,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'stackSha256':hashlib.sha256(result.stdout).hexdigest(),'rawStackExported':False,'operationAuthority':False,'formalAccepted':False}))
 # The host receives private stack bytes for local bounded method-only extraction.
 import sys
 sys.stdout.flush();sys.stdout.buffer.write(result.stdout)
finally:os.close(fd)
'''


def main():
    if len(sys.argv)!=2 or re.fullmatch(r'(?:0[0-9]|1[01])',sys.argv[1])is None:raise SystemExit('one new sample00..11 only')
    slot='pg4224-current-parent-stack-'+sys.argv[1]
    source=(W/'pg4220-parent-watch-v1.private.jsonl').read_bytes();frames=[json.loads(line)for line in source.splitlines()]
    parent=select_parent(frames)
    os.umask(0o077);out=W/slot;out.mkdir(mode=0o700);raw=payload(parent,slot);(out/'payload.private.py').write_text(raw)
    actual=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=35)
    (out/'stdout.private.log').write_bytes(actual.stdout);(out/'stderr.private.log').write_bytes(actual.stderr)
    value={'actualExit':actual.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'slot':slot,'formalAccepted':False,'productionPtAdded':0,'hostObservedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if actual.returncode==0:
        first,stack=actual.stdout.split(b'\n',1);value.update(json.loads(first));value['mainFrames']=frames_from(stack)
        if value['stackSha256']!=hashlib.sha256(stack).hexdigest():raise ValueError('original unchanged stack required')
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return actual.returncode


if __name__=='__main__':raise SystemExit(main())
