"""SSC245 fixed DB-live/child preflight. No signal, Unit start, or DB write."""
import ast
import hashlib
import json
from pg1002_cold_readonly import capture
from pg1046_cold_snapshot_diagnostic import GUEST as diagnostic
from pg1037_cold_preparation_sources import guest
from pg1041_cold_policy_diagnostic import W


def payload():
    frozen_path = W / 'pg1038-cold-preparation-frozen-v1.safe.json'
    frozen = json.loads(frozen_path.read_bytes())
    if frozen['actualExit'] != 0 or frozen['operatorSource'] != '776b7dc53c5366f2de58eb253080db60af0fb19e':
        raise ValueError('fixed old compiled source required')
    root = W / 'pg1037-cold-tools-v1'
    for name, digest in frozen['fileHashes'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError('old frozen tool changed')
    old_child = root / 'pg1037_cold_refs.py'
    head = diagnostic[:diagnostic.index("phase='CONTROLS'")]
    node = next(n for n in ast.parse(guest()).body if isinstance(n, ast.FunctionDef) and n.name == 'owned_peer_sql')
    prefix = 'SOURCE_SHA=' + repr(hashlib.sha256(old_child.read_bytes()).hexdigest()) + '\n'
    prefix += 'PINS=' + repr(frozen['fileHashes']) + '\nFIXED_FUNCTION=' + repr(ast.unparse(node)) + '\n'
    prefix += 'SOCKET_SOURCE=' + repr(__import__('pathlib').Path(__file__).with_name('pg1054_cold_socket_contract.py').read_text()) + '\n'
    prefix += 'CORRECTED_CONTRACT_SOURCE=' + repr(__import__('pathlib').Path(__file__).with_name('pg1026_cold_observation_contract.py').read_text()) + '\n'
    marker="contract=types.ModuleType('contract')"
    if head.count(marker)!=1:
        raise ValueError('fixed corrected contract adapter refused')
    head=head.replace(marker,"env['CONTRACT_SOURCE']=CORRECTED_CONTRACT_SOURCE\n"+marker)
    raw = prefix + head + '\n' + BODY
    ast.parse(raw)
    return raw


BODY = r'''
import dbus,time,stat,re
exec(FIXED_FUNCTION,env)
socket_module=types.ModuleType('socket_contract');exec(SOCKET_SOURCE,socket_module.__dict__)
def readonly_runtime_namespaces():
 root=pathlib.Path('/run/schubert-nk')
 workers={name:(int(env['command'](['id','-u',role],32)),int(env['command'](['id','-g',role],32)))for name,role in [('backup','schubert-backup'),('inspector','schubert-inbox-inspector')]}
 entries={'@root':[p.name for p in root.iterdir()],'maintenance':[p.name for p in (root/'maintenance').iterdir()]}
 meta={'@root':env['metadata'](root),'maintenance':env['metadata'](root/'maintenance')}
 assert not os.listxattr(root)and not os.listxattr(root/'maintenance')
 contract.namespace_layout(entries,meta,workers,False)
 return {}
env['runtime_namespaces']=readonly_runtime_namespaces
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1/tree-preflight-v1')
assert not os.path.lexists(save);save.mkdir(mode=0o700)
held=[];refs=[];bus=None;manager=None;phase='ENTRY'
def retained_error(failure):
 print(json.dumps({'run':'PG1050-cold-tree-preflight-v1','phase':phase,'type':type(failure).__name__,'signalAttempted':False,'ownershipRetained':True,'formalAccepted':False}),flush=True)
 for frame in traceback.extract_tb(failure.__traceback__)[-4:]:
  print(json.dumps({'safeFrame':frame.name,'line':frame.lineno,'file':pathlib.Path(frame.filename).name}),flush=True)
 while True:time.sleep(1)
def pin_file(path,digest):
 size=path.stat().st_size
 h=contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file();held.append(h)
 return h
def actor(pid,ticks,digest,exe,children,ppid=None):
 root=pathlib.Path('/proc')/str(pid);parts=(root/'stat').read_text().rpartition(')')[2].split()
 assert int(parts[19])==ticks and (ppid is None or int(parts[1])==ppid)
 assert str((root/'exe').readlink())==exe and hashlib.sha256((root/'cmdline').read_bytes()).hexdigest()==digest
 status=dict(l.split(':',1)for l in(root/'status').read_text().splitlines()if ':'in l)
 assert status['Uid'].split()==status['Gid'].split()==['0']*4
 tasks=sorted((root/'task').iterdir());actual={int(c)for t in tasks for c in(t/'children').read_text().split()}
 assert actual==children and tasks==sorted((root/'task').iterdir())
 fdmap={}
 for f in sorted((root/'fd').iterdir(),key=lambda x:int(x.name)):
  s=f.stat();target=os.readlink(f);info=(root/'fdinfo'/f.name).read_bytes()
  fdmap[f.name]={'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size],
   'targetSha256':hashlib.sha256(target.encode()).hexdigest(),'fdinfoSha256':hashlib.sha256(info).hexdigest()}
 return {'pid':pid,'ticks':ticks,'argvSha256':digest,'exe':exe,'children':sorted(actual),
  'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb')},
  'cgroup':(root/'cgroup').read_text(),'fds':fdmap}
def tree_identity():
 parent=actor(5463,1373880,'fcb09442d0ad0bc9d0b71433c7a01f54b1c86941f3ab42e0c1cd6ba4f9f311c8','/opt/jdk-25.0.4/bin/java',{5489})
 child=actor(5489,1373951,'8067bb56195ab7f05b1427a9d5cf78f5d71e404000acc5f5f3391c5079e5a1d9','/usr/bin/python3.14',set(),5463)
 locks={n:env['metadata'](pathlib.Path('/run/schubert-nk')/n)for n in ('maintenance.lock','startup-admission.lock')}
 env['owned_flocks'](pathlib.Path('/proc/locks').read_text().splitlines(),locks,5463)
 aliases=[]
 for f in pathlib.Path('/proc/5463/fd').iterdir():
  s=f.stat()
  if any((s.st_dev,s.st_ino)==tuple(m[:2])for m in locks.values()):
   aliases.extend(l.removeprefix('lock:').strip()for l in(pathlib.Path('/proc/5463/fdinfo')/f.name).read_text().splitlines()if l.startswith('lock:'))
 env['owned_flocks'](contract.fd_alias_records(aliases),locks,5463)
 return {'parent':parent,'child':child,'locks':locks}
def peer():
 sql="select json_build_object('pid',pid,'backendStart',backend_start::text,'transactionStart',xact_start::text,'role',usename,'application',application_name,'database',datname,'state',state,'query',query,'clientPort',client_port,'clientAddress',host(client_addr))from pg_stat_activity where datname='schubert_nk'and pid="+str(env['OWNER_BACKEND'])+';'
 rows=env['command'](['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],65536).splitlines()
 assert len(rows)==1;v=json.loads(rows[0]);assert v['pid']==env['OWNER_BACKEND']and v['role']=='schubert_batch'and v['application']=='PG243-cold-empty'and v['database']=='schubert_nk'and v['backendStart']and v['transactionStart']
 assert v['state']in ('active','idle in transaction')
 heartbeat="select pg_backend_pid(),current_user,current_database(),current_setting('application_name'),current_setting('transaction_read_only'),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock' and granted),session_user"
 assert v['query']==heartbeat
 sockets={s.st_ino for f in pathlib.Path('/proc/5463/fd').iterdir()if stat.S_ISSOCK((s:=f.stat()).st_mode)}
 tcp=[]
 assert v['clientAddress']in ('127.0.0.1','::1')
 for net in ('tcp','tcp6'):
  for l in pathlib.Path('/proc/5463/net',net).read_text().splitlines()[1:]:
   f=l.split()
   if int(f[9])in sockets and socket_module.match(net,f[1],f[2],f[3],v['clientAddress'],v['clientPort'],5432):tcp.append(int(f[9]))
 assert len(tcp)==1
 del v['state'];v['heartbeatVerifiedByFrozenSameConnection']=True;v['socketInode']=tcp[0]
 return v
def read():
 first=tree_identity();server=peer();control=env['controls']();snapshot=env['snapshot']()
 assert all(snapshot[k]==sealed[k]for k in ('units','rows','durable','artifacts'))
 for name,v in snapshot['configuration'].items():
  start=env['exec_record'](v['ExecStart']);assert env['same'](sealed['configuration'][name],v,env['exec_record'])
  assert start is not None and start[3:]==('n/a','n/a','0','(null)','0/0')and v['ExecStop']==''
 assert first==tree_identity()and server==peer()and control==env['controls']()
 allheld=[h.capture()for h in held]
 return {'tree':first,'server':server,'controls':control,'snapshot':snapshot,
  'heldWholeMetadata':safe(allheld)}
def safe(v):
 if isinstance(v,bytes):return {'bytesSha256':hashlib.sha256(v).hexdigest(),'length':len(v)}
 if isinstance(v,dict):return {k:safe(x)for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe(x)for x in v]
 return v
try:
 phase='FIXED_TREE_AND_PEER';tree_identity();peer();env['controls']()
 phase='SIGNED_HELD_BYTES'
 manifest=(env['RELEASE']/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()==env['BOM']
 records=json.loads(manifest)['artifacts'];sums=contract.canonical_sum_bytes(records,env['BOM'])
 records=records+[{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':env['BOM']},{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}]
 held.append(contract.HeldInventory(str(env['RELEASE']),records,0).open())
 pin_file(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),env['PIN_HASH']);pin_file(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),env['SIG_HASH'])
 approval=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256='+env['BOM']+'\n').encode()
 pin_file(pathlib.Path('/etc/schubert-nk/release-approval/current'),hashlib.sha256(approval).hexdigest())
 tool=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-tools-v1');payload=(tool/'payload-sha256.json').read_bytes();assert json.loads(payload)==PINS
 records=[{'path':n,'size':(tool/n).stat().st_size,'sha256':d}for n,d in PINS.items()]
 records.append({'path':'payload-sha256.json','size':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
 held.append(contract.HeldInventory(str(tool),records,0).open())
 error=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1/refs.private.log')
 assert error.read_bytes()==b'PG1037_REFS_UNKNOWN phase=BEFORE type=ValueError isolationRetained=true\n'
 pin_file(error,'ed0bd8d35e47d8e65cee98cc06f7eafccd8380ed9d715b5acb8cae9c253293f8')
 phase='TEN_OBSERVER_REFS';bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 old_names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==5489]
 assert len(old_names)==1 and int(daemon.GetConnectionUnixUser(old_names[0]))==0
 for name in env['old']['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='WHOLE_TWO_READ';before=read();assert before==read()
 before['childBusUniqueName']=old_names[0]
 private=json.dumps(before,sort_keys=True).encode()
 with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 phase='OBSERVER_NORMAL_CLOSE'
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 for h in reversed(held):h.close()
except BaseException as failure:retained_error(failure)
print(json.dumps({'run':'PG1050-cold-tree-preflight-v1','actualExit':0,'source':env['SOURCE'],'boot':env['BOOT'],
 'oldParentPid':5463,'oldChildPid':5489,'oldActorUntouched':True,'signalAttempted':False,'oldOperationNormalClose':False,
 'sameReadOnlyParentPeer':True,'otherDBClients0':True,'allTenColdFull32':True,'allOriginalsUnchangedTwice':True,
 'observerNormalClose':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'formalAccepted':False}))
'''


if __name__ == '__main__':
    capture('pg1050-cold-tree-preflight-v1', payload())
