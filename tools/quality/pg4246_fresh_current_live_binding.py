"""Independent read-only distinct current Root/run/activation binding; never starts or renews."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4018_literal_invariant_current_live_binding as previous
from pg4240_typed_bom_fresh_noargs_once import SLOT as ONCE
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg4246-fresh-current-live-binding-v1'
SOURCE,BOM=previous.SOURCE,previous.BOM


def body():
    raw=previous.body()
    return raw+"\nrequire(fields[1]!='dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f'and fields[3]!='d9d58371-bf80-49f6-bad9-3d1e0916fb04')\nrequire(unit['InvocationID']!='820851b8291a4c958bb34f6c48430ca3')\n"


def main():
    proof=json.loads((W/ONCE/'manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['source']!=SOURCE:raise ValueError('original new entry actual0 first')
    parent=proof['result'];expected={k:parent[k]for k in ['MainPID','InvocationID','Job','ExecMainStartTimestampMonotonic']}
    raw='SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(BOM)+'\nEXPECTED='+repr(expected)+'\n'+body()
    if check(raw,'<fresh current binding>'):raise ValueError('whole exact live namespace required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=45)
    (out/'stdout.private.log').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
