"""Separate full current/hostRO post after actual one owned recovery; no old close success."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1876_warning_ro_marker_post import payload as previous,SLOT as OLD_SLOT

SLOT='pg1890-publication-recovery-full-post-v1'


def payload(post):
    return previous(post).replace(OLD_SLOT,SLOT).replace("'normalFreshReadonlyScopes':True","'normalFreshReadonlyScopes':True,'separateOwnedRecoveryPost':True,'oldCloseUnknownRetained':True")


def main():
    actual=json.loads((W/'pg1887-publication-pair-once-handoff-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['queuedSameHostGateAcquired']is not True or actual['oldNormalCloseUnknown']is not True or subprocess.check_output(['git','status','--porcelain']):raise ValueError('actual recovered clean current owner required')
    post=json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes())
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload(post)
    from pyflakes.api import check
    if check(raw,'<actual separate recovery allpost>'):raise ValueError('all actual post globals required')
    (out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
