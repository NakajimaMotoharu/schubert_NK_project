"""SSC285 bounded failed-phase TCP-family diagnosis; no Ref, signals or writes."""
import datetime
import hashlib
import json
import os
import subprocess
import pg3502_signed_current_retained_readonly as frozen
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate

SLOT = 'pg3508-signed-current-tcp-readonly-v1'


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = frozen.payload().split("a=actors();require(not a[0]['children'])", 1)[0]
    raw = raw.replace(frozen.SLOT, SLOT) + r'''
a=actors();require(len(a)==1 and a[0]['pid']==410196 and not a[0]['children'])
q="begin read only;set local statement_timeout='5s';select json_build_object('pid',pid,'role',usename,'application',application_name,'address',host(client_addr),'port',client_port)from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid();commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],capture_output=True,timeout=15);require(r.returncode==0 and len(r.stdout)<65536)
peers=[json.loads(l)for l in r.stdout.splitlines()]
pids={int(v['MainPID'])for v in seal['units'].values()if int(v['MainPID'])>0}|{p['pid']for p in peers}
sockets={}
for pid in pids:
 found=[]
 for f in pathlib.Path('/proc',str(pid),'fd').iterdir():
  try:target=os.readlink(f)
  except(FileNotFoundError,ProcessLookupError):continue
  if target.startswith('socket:['):found.append(target[8:-1])
 sockets[str(pid)]=found
tables={n:pathlib.Path('/proc/net',n).read_text()for n in ['tcp','tcp6']}
value={'peers':peers,'sockets':sockets,'tables':tables,'signals0':True,'refs0':True}
encoded=json.dumps(value,sort_keys=True).encode();save.mkdir(mode=0o700)
with(save/'proof.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'peerCount':len(peers),'tcpRows':len(tables['tcp'].splitlines())-1,'tcp6Rows':len(tables['tcp6'].splitlines())-1,'signals0':True,'refs0':True,'formalAccepted':False}))
'''
    compile(raw, '<bounded retained TCP readonly>', 'exec')
    (out / 'payload.private.py').write_text(raw)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P / 'current-management-critical.lock', validate_owner=frozen.host_owner,
                     require_completion=lambda: False):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'],
                           input=raw.encode(), capture_output=True, timeout=60)
        frozen.host_owner(P / 'current-management-critical.lock')
    (out / 'stdout.private.json').write_bytes(r.stdout)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    v = {'actualExit': r.returncode, 'startedUTC': started,
         'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'signals0': True}
    if r.returncode == 0:
        v['guest'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(v, sort_keys=True))
    print(json.dumps(v))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
