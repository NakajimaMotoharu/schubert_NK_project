"""Independent full post plus PID1 candidate RO and original normal completion receipt."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg3778_hygiene_unused_held_post as previous
import pg3780_hygiene_ro_sources as role
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg3786-hygiene-ro-independent-post-v1'
EXTRA="""
require(Path('/proc/self/ns/mnt').readlink()==Path('/proc/1/ns/mnt').readlink())
mount=subprocess.run(['findmnt','-n','-o','OPTIONS','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG3748'],capture_output=True,text=True,timeout=10)
options=mount.stdout.strip().split(',');require(mount.returncode==0 and len(options)==len(set(options))and 'ro'in options and 'rw'not in options)
receipt=Path('/var/lib/pgpt-s1-preservation/pg3784-hygiene-ro-completed-v1/complete.private').read_bytes()
require(receipt==b'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\ncandidateReadOnlyVerified=true\\nallNewScopesReturnedNormally=true\\noriginalBackupStartupRowsPreserved=true\\nstartsStopsReloadsEpochWrites0=true\\noldUnknownNormalized=false\\n')
"""


def payload():
    raw=previous.payload();marker='print(json.dumps('
    end=raw.rindex(marker)
    raw=raw[:end]+EXTRA+raw[end:]
    raw=raw.replace("'candidateUnusedOnly':True","'candidateHostReadonlyVerified':True,'candidateUnusedOnly':True")
    if check(raw,'<whole independent RO post>'):raise ValueError('complete post namespace required')
    compile(raw,'<independent full24/187/32/native34/PID1 RO>','exec');return raw


def main():
    actual=json.loads((W/'pg3784-prepare-ro-v1.safe.json').read_bytes())
    if actual.get('actualExit')!=0 or actual.get('sourceQualified')is not True or actual.get('candidateSource')!=role.SOURCE or actual.get('currentApprovalEpochChanged')is not False:raise ValueError('genuine original RO completion required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed independent observer')
    os.umask(0o077);out=W/SLOT;out.mkdir();raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'currentSource':role.CURRENT,'candidateSource':role.SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
