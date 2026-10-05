"""Read-only bootstrap terminal journal after systemd GC. No start/retry/reset or secret values."""
import hashlib,json,os,pathlib,subprocess
from pg466_term_witness import unique
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg467-bootstrap-existing')
def require(b):
    if not b:raise ValueError('fixed bootstrap terminal readback refused')
require(os.geteuid()==0)
actor=json.loads((ROOT/'actor.private.json').read_text(),object_pairs_hook=unique)
raw=subprocess.check_output(['/usr/bin/journalctl','--boot=e07aa7061acd4e65b309d7f330f79d54','--unit=schubert-nk-bootstrap-admin.service','--output=json','--no-pager'],timeout=5)
require(0<len(raw)<=4194304 and raw.endswith(b'\n'))
with (ROOT/'terminal-journal.private.jsonl').open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
rows=[json.loads(line,object_pairs_hook=unique) for line in raw.decode('utf-8',errors='strict').splitlines()]
for row in rows:
    if row.get('_PID')=='1' and row.get('UNIT')=='schubert-nk-bootstrap-admin.service':
        print(json.dumps({k:row[k] for k in ('MESSAGE_ID','INVOCATION_ID','JOB_ID','JOB_RESULT','UNIT_RESULT','EXIT_CODE','EXIT_STATUS') if k in row},sort_keys=True))
finished=[r for r in rows if r.get('_SYSTEMD_INVOCATION_ID')==actor['invocation'] and r.get('_PID')==actor['pid'] and r.get('MESSAGE')=='Initial ADMIN bootstrap finished']
require(len(finished)==1 and finished[0].get('_UID')=='999')
failed=[r for r in rows if r.get('_SYSTEMD_INVOCATION_ID')==actor['invocation'] and r.get('MESSAGE')=='Initial ADMIN bootstrap failed'];require(not failed)
require(not pathlib.Path('/proc',actor['pid']).exists())
print('PG467_BOOTSTRAP_GC_DIAGNOSTIC trustedFinished1=true failed0=true actorAbsent=true journalSha256='+hashlib.sha256(raw).hexdigest())
