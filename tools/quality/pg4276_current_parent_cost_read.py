"""Bounded same-parent kernel cost read, no jcmd, process signals or service commands."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4224_same_parent_stack_sample as parent
from pg1446_current_cold_stage import W,SSH

SLOT='pg4276-current-parent-cost-read-v1'


def payload(expected):
    raw=parent.payload(expected,SLOT)
    head=raw[:raw.index(' started=time.monotonic_ns()')]
    body=r'''
 stat_value=(p/'stat').read_text().rsplit(')',1)[1].split();io=dict(l.split(':',1)for l in(p/'io').read_text().splitlines())
 cgroup=Path('/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service')
 cpu=dict(l.split()for l in(cgroup/'cpu.stat').read_text().splitlines())
 require(not poll.poll(0)and owner()==before)
 value={'actualExit':0,'source':SOURCE,'BOM':BOM,'invocation':EXPECTED['InvocationID'],'pid':int(pid),'ticks':EXPECTED['startTicks'],
 'elapsedParentUs':time.monotonic_ns()//1000-int(before['ExecMainStartTimestampMonotonic']),'clockTicksPerSecond':os.sysconf('SC_CLK_TCK'),
 'parentUserTicks':int(stat_value[11]),'parentSystemTicks':int(stat_value[12]),'waitedChildrenUserTicks':int(stat_value[13]),'waitedChildrenSystemTicks':int(stat_value[14]),
 'io':{k:int(v)for k,v in io.items()},'cgroupCpu':{k:int(v)for k,v in cpu.items()},'schedstat':[int(v)for v in(p/'schedstat').read_text().split()],
 'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rawExported':False,'formalAccepted':False,'operationAuthority':False}
 print(json.dumps(value))
finally:os.close(fd)
'''
    return head+body


def main():
    frames=[json.loads(l)for l in(W/'pg4220-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    raw=payload(parent.select_parent(frames))
    if check(raw,'<same live Root cost>'):raise ValueError('full kernel reader closure static0 required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=30)
    (out/'stdout.private.log').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'source':parent.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
