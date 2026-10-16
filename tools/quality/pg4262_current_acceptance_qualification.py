"""Freeze affected six tests and complete four emitted closures; no VM actions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4260_stable_admission_image as admission
import pg4252_current_independent_acceptance as actual
from pg1446_current_cold_stage import W

SLOT='pg4262-current-acceptance-qualification-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    run=subprocess.run(['python3','-B','-m','unittest','pg4250_current_admission_image_test','pg4260_stable_admission_image_test','-v'],capture_output=True)
    log=run.stdout+run.stderr;(out/'host-tests.log').write_bytes(log)
    if run.returncode!=0 or b'Ran 6 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('all affected six tests actual0 first')
    binding=admission.live();digest=admission.before()
    payloads={'before':admission.payload(binding),'terminal':actual.terminal_payload(binding),'rows':actual.rows_payload(binding,digest),'seal':actual.seal_payload(binding,digest)}
    paths=sorted(p for pattern in ['pg425*.py','pg426*.py']for p in Path('tools/quality').glob(pattern))
    findings=sum(checkPath(str(p))for p in paths)+sum(check(raw,'<whole '+name+'>')for name,raw in payloads.items())
    if findings:raise ValueError('all host and actual emitted static0 required')
    value={'actualExit':0,'source':admission.SOURCE,'binding':binding,'beforeSha256':digest,'toolTests':6,'failures':0,'errors':0,'skipped':0,'staticFindings':0,
           'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'emittedSha256':{n:hashlib.sha256(r.encode()).hexdigest()for n,r in payloads.items()},
           'logSha256':hashlib.sha256(log).hexdigest(),'productionPtAdded':0,'formalAccepted':False,'rootActions':0}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
