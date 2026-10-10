"""Fixed data-only snapshot diagnosis. No Ref, writer, lifecycle or signal authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

from pg1041_cold_policy_diagnostic import P, W

GUEST = r'''
import ast,pathlib,os,hashlib,json,types,traceback
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
p=pathlib.Path('/proc/5463');assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==1373880
assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='fcb09442d0ad0bc9d0b71433c7a01f54b1c86941f3ab42e0c1cd6ba4f9f311c8'
assert {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={5489}
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-tools-v1/pg1037_cold_refs.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
tree=ast.parse(raw);nodes=[]
for n in tree.body:
 if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)):nodes.append(n)
 elif isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)for t in n.targets):
  names={t.id for t in n.targets}
  if names <= {'CHECKSUM_HASH','CONTRACT_SOURCE','LOCK_SOURCE','MANIFEST_SIZE','BOOT','SOURCE','BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS'}:nodes.append(n)
env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen1037', 'exec'),env)
contract=types.ModuleType('contract');exec(env['CONTRACT_SOURCE'],contract.__dict__);env['contract']=contract
locks=types.ModuleType('locks');exec(env['LOCK_SOURCE'],locks.__dict__);env['owned_flocks']=locks.owned_flocks
env['old']=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes())
sealed=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1004-cold-readonly-v3/after.private.json').read_bytes())
query="select pid from pg_stat_activity where datname='schubert_nk' and usename='schubert_batch' and application_name='PG243-cold-empty' and backend_type='client backend';"
peers=env['command'](['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query],4096).splitlines()
assert len(peers)==1 and peers[0].isdigit();env['OWNER_BACKEND']=int(peers[0]);env['OWNER_PID']=5463;env['PREPARED']=False
phase='CONTROLS'
try:
 env['controls']();phase='SNAPSHOT';a=env['snapshot']();phase='SEALED_COMPARISON'
 result={k:a[k]==sealed[k]for k in ('units','rows','durable','artifacts')}
 config=[]
 for name,v in a['configuration'].items():
  start=env['exec_record'](v['ExecStart'])
  config.append({'unit':name,'sameConfiguration':env['same'](sealed['configuration'][name],v,env['exec_record']),
   'parsedStart':start is not None,'coldStart':start is not None and start[3:]==('n/a','n/a','0','(null)','0/0'),'emptyStop':v['ExecStop']==''})
 print(json.dumps({'diagnostic':'PG1046','phase':phase,'snapshotComparisons':result,'configurationComparisons':config,'dataOnly':True,'formalAccepted':False}))
except Exception as failure:
 frames=[{'function':x.name,'line':x.lineno,'file':pathlib.Path(x.filename).name}for x in traceback.extract_tb(failure.__traceback__) if x.filename=='frozen1037']
 print(json.dumps({'diagnostic':'PG1046','phase':phase,'type':type(failure).__name__,'frames':frames,'dataOnly':True,'formalAccepted':False}))
 raise SystemExit(1)
'''


def main():
    os.umask(0o077)
    root = W / 'pg1046-cold-snapshot-diagnostic-v1'
    root.mkdir(mode=0o700)
    source = W / 'pg1037-cold-tools-v1/pg1037_cold_refs.py'
    raw = 'SOURCE_SHA=' + repr(hashlib.sha256(source.read_bytes()).hexdigest()) + '\n' + GUEST
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=raw.encode(), capture_output=True, timeout=60)
    with (root / 'diagnostic.private.log').open('xb') as f:
        f.write(result.stdout + result.stderr); f.flush(); os.fsync(f.fileno())
    safe = {'run': 'PG1046-cold-snapshot-diagnostic-v1', 'actualExit': result.returncode,
            'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scriptSha256': hashlib.sha256(raw.encode()).hexdigest(),
            'logSha256': hashlib.sha256(result.stdout + result.stderr).hexdigest(),
            'dataOnly': True, 'formalAccepted': False}
    with (root / 'manifest.safe.json').open('x') as f:
        json.dump(safe, f, sort_keys=True)
    for line in result.stdout.decode().splitlines():
        if line.startswith('{"diagnostic": "PG1046"'):
            print(line)
    print(json.dumps(safe))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
