"""BUG853/854 actual readonly PostgreSQL query parse, no operational authority."""
import ast,hashlib,json,os,pathlib,subprocess,sys
R=pathlib.Path(__file__).parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
env={};parsed=ast.parse((R/'pg559_terminal_refs.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in ('require','peer_query')],type_ignores=[]),'<independent SQL boundary>','exec'),env)
sql=env['peer_query'](77);os.umask(0o077)
payload='SQL='+repr(sql)+'\n'+'''import json,subprocess
assert SQL.count(';')==4 and 'a.pid=77 and ' in SQL and '77and' not in SQL
q=['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',SQL]
r=subprocess.run(q,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert r.returncode==0 and r.stdout.splitlines()==[b'0',b'0',b'0',b'0']
print('PG559_SQL_PEER_PARSE actualPostgres0=true allOwnerPeerAdvisory0=true authorityFalse=true')
'''
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
log=W/'pg559-peer-sql-probe-v2.private.log';exit_file=W/'pg559-peer-sql-probe-v2.exit';assert not log.exists()and not exit_file.exists()
with log.open('xb')as f:r=subprocess.run(ssh,input=payload.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with exit_file.open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':r.returncode,'logSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'productionPT0':True}));sys.exit(r.returncode)
