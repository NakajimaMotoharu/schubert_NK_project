"""Read-only actual role populations; no old peer counts inferred as current."""
import hashlib
import json
import os
import subprocess
from pg1805_retained_stop_readonly_diagnosis import owner,W,SSH

SLOT='pg1811-current-warning-peer-diagnosis-v1'
PAYLOAD=r'''
import hashlib,json,pathlib,subprocess
child=pathlib.Path('/proc/479219/cmdline').read_bytes();assert hashlib.sha256(child).hexdigest()=='43b9447f91fd401abfb93ab77ce8b874842d124f94ef49724a035fcc7a80757c'
backend=int(child.split(b'\0')[-2])
q="begin read only;select json_build_object('pid',pid,'port',client_port,'role',usename,'app',application_name,'state',state,'address',host(client_addr))from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()order by pid;select json_build_object('pid',pid,'mode',mode,'granted',granted)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],capture_output=True,timeout=10);assert r.returncode==0
rows=[json.loads(l)for l in r.stdout.splitlines()]
assert all(set(v)in[{'pid','port','role','app','state','address'},{'pid','mode','granted'}]for v in rows)
print(json.dumps({'actualExit':0,'childBackendPid':backend,'currentRows':rows,'rawSecretsCopied':False,'sqlWrites0':True}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('fixed retained host owner changed')
    result={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest()}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
