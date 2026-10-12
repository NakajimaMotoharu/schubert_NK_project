"""Separate closed-resource partial post: keeps current/Unit, never claims reload or old success."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1899_partial_publication_snapshot import payload as previous

SLOT='pg1904-partial-recovery-closed-post-v1'


def payload():
    raw=previous().replace('pg1896-complete-publication-full-post-v1',SLOT)
    raw=raw.replace("'normalSingleReload':True","'normalSingleReload':False,'partialUnitExchangedNotReloaded':True,'oldCloseUnknownRetained':True")
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one independent closed partial save required')
    raw=raw.replace(marker,"require(not pathlib.Path('/proc/493115').exists()and not pathlib.Path('/proc/493146').exists())\n"+marker)
    from pyflakes.api import check
    if check(raw,'<actual partial recovery full post>'):raise ValueError('all actual partial post globals required')
    compile(raw,'<independent closed resources partial current>','exec');return raw


def main():
    actual=json.loads((W/'pg1903-partial-pair-once-handoff-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['queuedSameHostGateAcquired']is not True or actual['oldNormalCloseUnknown']is not True or subprocess.check_output(['git','status','--porcelain']):raise ValueError('actual recovered clean partial required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
