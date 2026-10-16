"""Read retained failed Unit's historical resource counters, not current-host load inference."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg3428_vm_candidate_preflight_readonly as identity
from pg4002_literal_invariant_publication_sources import SOURCE, BOM


def payload():
    raw = identity.GUEST[:identity.GUEST.index('units={}')]
    for a, b in [('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25', SOURCE),
                 ('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863', BOM),
                 ('PG2802', 'PG3976'), ('pg2802-manifest.sig', 'pg3976-manifest.sig')]:
        raw = raw.replace(a, b)
    return raw + r'''
fields='InvocationID,Result,ExecMainCode,ExecMainStatus,MainPID,ControlPID,Job,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,CPUUsageNSec,MemoryPeak,IOReadBytes,IOWriteBytes,TasksCurrent,CPUQuotaPerSecUSec,CPUWeight,CPUAccounting,IOAccounting,MemoryAccounting,TimeoutStartUSec'
def read():
 r=subprocess.run(['systemctl','show','schubert-nk-morning-controller.service','--property='+fields],capture_output=True,text=True,timeout=10);assert r.returncode==0
 v=dict(l.split('=',1)for l in r.stdout.splitlines());assert v['InvocationID']=='820851b8291a4c958bb34f6c48430ca3'and v['Result']=='timeout'and v['ExecMainCode']=='1'and v['ExecMainStatus']=='143'and v['MainPID']==v['ControlPID']=='0'and v['Job']==''
 return v
first=read();assert first==read()and manifest.read_bytes()==raw
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'historicalFailedRootCounters':first,'stateChangingActions':0,'parentNormal':False,'formalAccepted':False}
print(json.dumps(value))
'''


def main():
    os.umask(0o077); out = W / 'pg4070-failed-root-resource-read-v1'; out.mkdir()
    raw = payload(); compile(raw, '<failed Unit accounting only>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=60)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if not r.returncode: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
