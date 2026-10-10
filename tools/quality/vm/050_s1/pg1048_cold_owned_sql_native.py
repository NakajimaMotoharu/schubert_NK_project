"""PG1048 readonly PostgreSQL lexer counterexample and same-peer corrected query."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1046_cold_snapshot_diagnostic import GUEST as previous, P, W
from pg1037_cold_preparation_sources import guest


def main():
    os.umask(0o077)
    out = W / 'pg1048-cold-owned-sql-v1'
    out.mkdir(mode=0o700)
    tree = ast.parse(guest())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'owned_peer_sql')
    fixed = ast.unparse(node)
    raw = previous[:previous.index("phase='CONTROLS'")]
    raw += r'''
sql=env['owned_peer_sql'](env['OWNER_BACKEND'])
args=['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose','-d','schubert_nk','-c']
old=env['subprocess'].run(args+[sql],capture_output=True,timeout=30)
assert old.returncode!=0 and b'42601' in old.stderr
exec(FIXED_FUNCTION,env)
fixed=env['owned_peer_sql'](env['OWNER_BACKEND'])
results=[]
for i in range(2):
 r=env['subprocess'].run(args+[fixed],capture_output=True,timeout=30)
 assert r.returncode==0 and r.stdout.splitlines()==[b'0',b'0',b'1']
 results.append({'exit':r.returncode,'allOtherClients':0,'allOtherAdvisoryPeers':0,'authenticatedParentPeers':1})
assert {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={5489}
print(json.dumps({'diagnostic':'PG1048','historicalExit':old.returncode,'historicalSqlState':'42601','correctedTwoRead':results,'expectedOracle':'literal counts zero other clients, zero other advisory owners, one fixed parent','dataOnly':True,'formalAccepted':False}))
'''
    source = W / 'pg1037-cold-tools-v1/pg1037_cold_refs.py'
    raw = 'SOURCE_SHA=' + repr(hashlib.sha256(source.read_bytes()).hexdigest()) + '\nFIXED_FUNCTION=' + repr(fixed) + '\n' + raw
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    r = subprocess.run(ssh, input=raw.encode(), capture_output=True, timeout=60)
    with (out / 'result.private.log').open('xb') as f:
        f.write(r.stdout + r.stderr); f.flush(); os.fsync(f.fileno())
    safe = {'run': 'PG1048-cold-owned-sql-v1', 'actualExit': r.returncode,
            'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scriptSha256': hashlib.sha256(raw.encode()).hexdigest(),
            'logSha256': hashlib.sha256(r.stdout + r.stderr).hexdigest(),
            'historicalSourceUnchanged': True, 'dataOnly': True, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(safe, f, sort_keys=True)
    for line in r.stdout.decode().splitlines():
        if line.startswith('{"diagnostic": "PG1048"'):
            print(line)
    print(json.dumps(safe))
    raise SystemExit(r.returncode)


if __name__ == '__main__':
    main()
