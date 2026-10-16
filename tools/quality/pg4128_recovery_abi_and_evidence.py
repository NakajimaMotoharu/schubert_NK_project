"""Exact host/emitted ABI check and sanitized manifest export. Never invokes a guest action."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from pyflakes.api import checkPath,check
from pg1446_current_cold_stage import W
import pg4104_failed_done_owned_dispatch as candidate

ROOT=Path(__file__).resolve().parents[2]
MODULES=['pg4104_failed_done_owned_dispatch_test','pg4102_failed_done_recovery_protocol_test',
         'pg4086_failed_done_recovery_contract_test','pg4094_failed_done_nine_attribute_inspection_test',
         'pg4084_recovery_inspection_test','pg4074_failed_done_parent_contract_test',
         'pg4078_ordinary_actor_policy_test','pg4122_fixed_terminal_native_contract_test']
SLOTS=['pg4084-recovery-inspection-v1-compile','pg4084-recovery-inspection-v1-run',
       'pg4088-failed-done-owned-tools-v1-compile','pg4090-failed-done-owned-inspect-v1-run',
       'pg4094-failed-done-owned-inspect-v1-run','pg4096-recovery-framing-before-v1',
       'pg4096-recovery-framing-after-v1','pg4096-recovery-framing-interrupt-v2-v1',
       'pg4098-interruption-checked-owned-tools-v1-compile','pg4100-interruption-checked-owned-inspect-v1-run',
       'pg4106-failed-done-dispatch-qualification-v1-inspect','pg4112-canonical-epoch-owned-tools-v1-compile',
       'pg4116-canonical-dispatch-qualification-v1-inspect','pg4120-native-destination-read-v1',
       'pg4124-fixed-native-dispatch-qualification-v1-inspect']


def main():
    os.umask(0o022)
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4128-failed-done-recovery-qualification-v1'
    out.mkdir()
    command=[sys.executable,'-B','-m','unittest',*MODULES]
    r=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
    (out/'host-abi.log').write_bytes(r.stdout+r.stderr)
    if r.returncode:raise ValueError('host ABI failed; preserve and do not operate')
    files=[]
    for pattern in ['pg4086_*.py','pg4088_*.py','pg409[0468]_*.py','pg410[246]_*.py','pg411[26]_*.py','pg412[0248]_*.py']:
        files.extend((ROOT/'tools/quality').glob(pattern))
    findings=sum(checkPath(str(p))for p in files)+check(candidate.payload(),'<complete final dispatch>')
    if findings:raise ValueError('complete static closure failed')
    hashes={'host-abi.log':hashlib.sha256((out/'host-abi.log').read_bytes()).hexdigest()}
    for slot in SLOTS:
        raw=(W/slot/'manifest.safe.json').read_bytes();data=json.loads(raw)
        safe={k:v for k,v in data.items()if k in {'actualExit','source','payloadSha256','action','compileExit',
             'frameSha256','sourceSha256','authorityIssued','productionPtAdded','formalAccepted','recoveryIssued'}}
        if 'result'in data:
            safe['result']={k:v for k,v in data['result'].items()if k not in {'compileCommand','profileCommand'}}
        safe['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        path=out/(slot+'.json');path.write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n')
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    value={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
           'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation',
           'targetHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           'command':command,'testModules':MODULES,'hostToolTests':33,'hostStaticFiles':len(files),
           'staticFindings':findings,'toolSourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},
           'dispatchSha256':hashlib.sha256(candidate.payload().encode()).hexdigest(),
           'files':hashes,'javaFrameIndependentControls':8,'sourceAllRegressionRepeated':False,
           'productionPtAdded':0,'oldRoot143StillFailed':True,'recoveryIssued':False,'formalAccepted':False,
           'BUG':['BUG1336','BUG1337','BUG1338','BUG1339'],'SSC':['SSC286','SSC287'],
           'privateDataExported':False,'coverageClaim':None}
    path=out/'manifest.json';path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'hostToolTests':33,'staticFindings':findings,'results':len(SLOTS),
                      'manifestSha256':hashlib.sha256(path.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
