"""Separate actual full-byte post for direct stage/place1865, not an old action slot."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1863_warning_actual_graph_post import payload as previous,SLOT as OLD_SLOT

SLOT='pg1866-warning-unused-independent-post-v1'


def payload(post):return previous(post).replace(OLD_SLOT,SLOT)


def main():
    actual=json.loads((W/'pg1865-place-v1.safe.json').read_bytes());post=json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not False or post['actualExit']!=0:raise ValueError('actual direct sameSource unused placement and closed old current required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload(post)
    from pyflakes.api import check
    if check(raw,'<actual separate unused candidate/current whole post>'):raise ValueError('full actual static closure required')
    (out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
