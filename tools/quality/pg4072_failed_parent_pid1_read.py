"""Read actual failed parent's PID1 cohort, preserve private journal, issue no recovery authority."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg4070_failed_root_resource_read import payload as accounting
from pg4002_literal_invariant_publication_sources import SOURCE


def payload():
    raw = accounting(); raw = raw[:raw.index("value={'actualExit':0")]
    return raw + r'''
base=Path('/var/lib/pgpt-s1-preservation/pg4072-failed-parent-pid1-read-v1');assert not os.path.lexists(base);os.umask(0o077);base.mkdir(mode=0o700)
args=['journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','-o','json','--no-pager']
r=subprocess.run(args,capture_output=True,timeout=15);assert r.returncode==0 and len(r.stdout)<=2097152
with(base/'pid1.private.jsonl').open('xb')as f:f.write(r.stdout);f.flush();os.fsync(f.fileno())
records=[json.loads(line)for line in r.stdout.splitlines()];lower=int(first['ExecMainStartTimestampMonotonic']);upper=int(first['ExecMainExitTimestampMonotonic'])+10000000
selected=[v for v in records if lower<=int(v['__MONOTONIC_TIMESTAMP'])<=upper]
keys=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
metadata=[{k:v[k]for k in keys if k in v}for v in selected]
assert first==read()and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failedParentUnit':first,'pid1Metadata':metadata,'privateJournalSha256':hashlib.sha256(r.stdout).hexdigest(),'parentNormal':False,'recoveryAuthorityIssued':False,'stateChangingActions':0,'formalAccepted':False}
(base/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result))
'''


def main():
    os.umask(0o077); out = W / 'pg4072-failed-parent-pid1-read-v1'; out.mkdir()
    raw = payload(); compile(raw, '<actual failed parent PID1 read>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=60)
    (out / 'stdout.safe.json').write_bytes(r.stdout); (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'source': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if not r.returncode: value['result'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return r.returncode


if __name__ == '__main__': raise SystemExit(main())
