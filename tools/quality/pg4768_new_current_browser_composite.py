"""Exact normal Root→real Browser→present24 chain; original owned SSH until actual exit."""
import datetime
import hashlib
import json
import os
import subprocess
import types
from pyflakes.api import check
import pg4272_current_browser_composite as previous
import pg4752_new_current_admission_image as admission
import pg4760_new_current_whole_seal as root
import pg4764_new_current_same_owner_browser as actual
from pg1446_current_cold_stage import P,SSH
from pg1674_critical_management_gate import management_gate
from pg4188_exact_partial_recover import process

SLOT='pg4768-new-current-browser-composite-v1'


def compose(raw,chain,digest):
    ns={**vars(previous.previous),'root':types.SimpleNamespace(SEAL=root.SLOT),'SOURCE':admission.SOURCE,'BOM':admission.BOM,'SLOT':SLOT}
    return types.FunctionType(previous.previous.compose.__code__,ns)(raw,chain,digest)


def payload(observed):
    root_view=types.SimpleNamespace(SEAL=root.SLOT,seal_payload=root.payload)
    ns={**vars(previous),'actual':actual,'root':root_view,'SOURCE':admission.SOURCE,'BOM':admission.BOM,'before':admission.before,'compose':compose}
    return types.FunctionType(previous.payload.__code__,ns)(observed)


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed composite operator')
    admission.authenticate_host();raw=payload(admission.live())
    if check(raw,'<complete immutable browser chain>'):raise ValueError('complete emitted static0')
    compile(raw,'<normal actual browser composite>','exec')
    os.umask(0o077);out=admission.W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'source':admission.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'replayAllowed':False}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':admission.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes())
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
