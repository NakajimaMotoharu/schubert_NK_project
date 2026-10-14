"""Fresh read-only actual Root/newrun identity after separate currenta9 once start."""
import datetime
import hashlib
import json
import os
import subprocess
import pg2686_operation_current_live_binding as prior
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2862_network_newcurrent_observer import SOURCE,BOM
from pg2814_network_newboot_readonly import one,BOOT

SLOT='pg2874-network-newcurrent-live-binding-v1'


def body():
    raw=prior.body().replace('PG2654','PG2802').replace('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT).replace('b2d6f60561cf425f8fbd12d606f6ee66',BOOT.replace('-',''))
    # All historical guards precede any successful output, including this
    # resume's completed data-only run/activation, never reused as authority.
    start=raw.index('print(json.dumps(');end=raw.index('\n',start)
    output=raw[start:end]
    raw=raw[:start]+raw[end:]+"\nrequire(fields[1]!='77601cf8-0ade-40fd-813f-c81d5210845e'and fields[3]!='26250063-8755-43b6-9ac7-f76d5eee7257')\n"+output+'\n'
    from pyflakes.api import check
    # SOURCE/DIGEST/EXPECTED are the closed dispatcher input constants.
    if check('SOURCE="a"\nDIGEST="b"\nEXPECTED={}\n'+raw,'<actual new root identity>'):raise ValueError('complete Root identity namespace required')
    compile(raw,'<same boot/source/newrun stable live Root>','exec');return raw


def main():
    v=json.loads((W/'pg2872-network-newcurrent-noargs-once-v2/manifest.safe.json').read_bytes())
    if v.get('actualExit')!=0 or v.get('productionSource')!=SOURCE:raise ValueError('actual single current start required')
    expected=v['guest'];required={'MainPID','Job','InvocationID','ExecMainStartTimestampMonotonic'}
    if not required<=expected.keys()or not expected['MainPID'].isdigit()or int(expected['MainPID'])<=1 or not expected['Job']or not expected['InvocationID']:
        raise ValueError('captured new Root generation required, no inferred PID/Invocation')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(BOM)+'\nEXPECTED='+repr(expected)+'\n'+body()).encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,stdout=f,stderr=f,timeout=30);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),'startedUTC':started,
        'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'startsStops0':True,'formalAccepted':False}
    if not r.returncode:result.update(json.loads((out/'observer.private.log').read_bytes()))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
