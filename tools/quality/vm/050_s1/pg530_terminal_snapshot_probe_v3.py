"""Read-only actual snapshot integration before any new Java owner. NOT a scope acceptance."""
import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
helper=(R/'pg530_terminal_refs.py').read_text();graph=(R/'pg529_dependency_graph.py').read_text()
payload='HELPER='+repr(helper)+'\nGRAPH='+repr(graph)+'\n'+r'''
import ast,datetime,hashlib,json,os,pathlib,stat,subprocess,sys,dbus
env=dict(globals());parsed=ast.parse(HELPER)
names={'require','verify_batch','verify_pid1'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names]
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in{'BOOT','INV','START','END'}for t in n.targets)]
exec(compile(ast.Module(body=nodes+constants,type_ignores=[]),'<pure fixed oracle>','exec'),env);exec(GRAPH,env)
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
p=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel'}
defs=[n for n in p.body if isinstance(n,ast.FunctionDef)and n.name in wanted];assert len(defs)==len(wanted)
constants=[n for n in p.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in{'UNITS','FIELDS'}for t in n.targets)]
exec(compile(ast.Module(body=defs+constants,type_ignores=[]),'<fixed pure actual reader>','exec'),env)
preserved=pathlib.Path('/var/lib/pgpt-s1-preservation/pg527-prestop-owned-handoff-v1');raw=(preserved/'before.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='c8c6b915a380902c3c8d022de24ab91a28e726e0d914a6ae88060bc8c360d5e3'
# This diagnostic bypasses Java owner only for read-only snapshot testing; no production scope credit.
held=('READ_ONLY_DIAGNOSTIC',);env.update(baseline=json.loads(raw),preserved=preserved,last_dependencies={},held=held,owner=lambda:held)
def connection(present):
 assert present is False
 q="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_backup','schubert_app','schubert_web_session','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 assert env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']
env['connection']=connection
node=next(n for n in ast.walk(parsed)if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed actual snapshot path>','exec'),env)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
for u in env['UNITS']:manager.RefUnit(u);refs.append(u)
first=env['snapshot'](False);assert first==env['snapshot'](False)
for u in reversed(refs):manager.UnrefUnit(u)
bus.close()
print('PG530_READONLY_SNAPSHOT_INTEGRATION fullCurrentSnapshotTwice=true graphRawOrderNotContract=true peerLocks0=true scopeAcceptance0=true businessActions0=true')
'''
log=W/'pg530-snapshot-probe-v3.private.log';exit_file=W/'pg530-snapshot-probe-v3.exit';assert not log.exists()and not exit_file.exists()
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
with log.open('xb')as f:r=subprocess.run(ssh,input=payload.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with exit_file.open('x')as f:f.write(str(r.returncode)+'\n')
result={'run':'PG530-snapshot-probe-v3','actualExit':r.returncode,'helperSourceSha256':hashlib.sha256(helper.encode()).hexdigest(),'graphSourceSha256':hashlib.sha256(graph.encode()).hexdigest(),'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'scopeAcceptance0':True,'businessActions0':True}
with(W/'pg530-snapshot-probe-v3.source.json').open('x')as f:json.dump(result,f,sort_keys=True)
print(json.dumps(result))
raise SystemExit(r.returncode)
