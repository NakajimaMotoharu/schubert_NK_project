"""Read-only actual new activation binding from the captured external parent generation."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1321_live_root_binding import BODY
from pg2015_completed_run_fresh_resume_once import SOURCE,BOM,RUN

SLOT='pg2017-fresh-resume-live-binding-v1'


def body():
    raw=BODY.replace('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d').replace('cbca87383b244090b77cbf029677cdd6','3d69f5af6bac46b1a5407591c4a79a0d').replace('PG1292','PG1846')
    raw=raw.replace("MorningProcessMain\\0'","MorningProcessMain\\0--resume\\04148e3e8-f107-431a-ab27-d6e6d1f1772e\\0'")
    # Avoid an octal escape consuming the first run-ID digit after the NUL.
    raw=raw.replace("b'dev.codex.schubert.nk.batch.file.MorningProcessMain\\0--resume\\04148e3e8-f107-431a-ab27-d6e6d1f1772e\\0'","b'dev.codex.schubert.nk.batch.file.MorningProcessMain\\0--resume\\0'+b'4148e3e8-f107-431a-ab27-d6e6d1f1772e\\0'")
    point="for name,expected in [('runs/'"
    if raw.count(point)!=1:raise ValueError('one original content point required')
    raw=raw.replace(point,"require(fields[1]=='"+RUN+"'and fields[2]=='2026-10-12T18:20:32.598894Z'and fields[3]!='9adbf05a-61d0-408b-b51d-ab19c7e5b16a')\n"+point)
    return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean current readonly tools required')
    actual=json.loads((W/'pg2015-completed-run-fresh-resume-once-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['productionSource']!=SOURCE:raise ValueError('actual new external start required')
    parent=actual['guest'];expected={k:parent[k]for k in ['MainPID','InvocationID','Job','ExecMainStartTimestampMonotonic']}
    raw='SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(BOM)+'\nEXPECTED='+repr(expected)+'\n'+body()
    from pyflakes.api import check
    if check(raw,'<actual fresh resume live binding>'):raise ValueError('all live globals required')
    out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=30);(out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
