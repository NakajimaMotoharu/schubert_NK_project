"""SSC251 new child owns full fixed partial proof; only one old-part rename."""
import ast
from pg1098_partial_exchange_preflight import payload as previous


def source():
    t=ast.parse(previous());nodes=[]
    for n in t.body:
        if isinstance(n,ast.Try):break
        nodes.append(n)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    start=raw.index("query = ");end=raw.index("expected_runtime = ",start)
    raw=raw[:start]+"assert len(sys.argv)==2 and sys.argv[1].isdigit()\nOWNER_PID=os.getppid();env['OWNER_PID']=OWNER_PID;env['OWNER_BACKEND']=int(sys.argv[1]);assert env['OWNER_BACKEND']>1\n"+raw[end:]
    start=raw.index('save = OLD_SAVE / ');end=raw.index('held = []',start)
    raw=raw[:start]+"save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1100-linked-preservation-v1')\nassert env['metadata'](save)[2:6]==[0,0,stat.S_IFDIR|0o700,2]\n"+raw[end:]
    # No old actor/old DB profile may grant this new process admission.
    tree=ast.parse(raw)
    tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef)or n.name not in ('actor','peer','safe','tree_identity','read','retain')]
    raw=ast.unparse(tree)
    raw=raw.replace('import ast, pathlib, os, hashlib, json, types, traceback, dbus, time, stat, subprocess',
                    'import ast, pathlib, os, hashlib, json, types, traceback, dbus, time, stat, subprocess,sys')
    raw+='\n'+BODY
    ast.parse(raw);return raw


BODY=r'''
PHASE='partial';captured_parent=None;captured_holds=None;old_link_fd=None;current_fd=None;save_fd=None
def parent():
 root=pathlib.Path('/proc')/str(OWNER_PID);s=(root/'stat').read_text().rpartition(')')[2].split()
 status=dict(l.split(':',1)for l in(root/'status').read_text().splitlines()if ':'in l)
 assert status['Uid'].split()==status['Gid'].split()==['0']*4
 assert str((root/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'
 argv=(root/'cmdline').read_bytes();assert argv.split(b'\0')[-3:]==[b'Pg1100LinkedPreservation',b'preserve',b'']
 assert {int(c)for t in(root/'task').iterdir()for c in(t/'children').read_text().split()}=={os.getpid()}
 m={n:env['metadata'](pathlib.Path('/run/schubert-nk')/n)for n in ('maintenance.lock','startup-admission.lock')}
 env['owned_flocks'](pathlib.Path('/proc/locks').read_text().splitlines(),m,OWNER_PID)
 return {'pid':OWNER_PID,'ticks':int(s[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','CapEff','CapPrm','CapBnd','NoNewPrivs')},'cgroup':(root/'cgroup').read_text(),'locks':m}
def retained_inventory(trees):
 for h in held:
  for fd,parent_fd,name,fixed,attrs in h.held:
   path=os.readlink('/proc/self/fd/'+str(fd));row=io.fd_record(fd)
   expected={'metadata':list(fixed),'sha256':None,'target':None,'acl':[a[0]for a in attrs]}
   if stat.S_ISREG(fixed[4]):expected['sha256']=h.records[str(pathlib.PurePosixPath(path).relative_to(h.root))]['sha256']
   if path==pub.CURRENT and PHASE=='after':pub.verify_retained(path,expected,row,'after',trees,begin_ns,time.time_ns())
   else:assert row==expected
   assert io.metadata(os.stat(name,dir_fd=parent_fd,follow_symlinks=False))==row['metadata']
 alias='pg1088-current.part'if PHASE=='partial'else'current-link.private'
 d=current_fd if PHASE=='partial'else save_fd
 row=exchange_io.linked_attributes(d,alias,old_link_fd)
 pub.verify_retained(pub.CURRENT+'/current',original_before['trees'][pub.CURRENT][pub.CURRENT+'/current'],row,'after',trees,begin_ns,time.time_ns())
def pair():
 assert parent()==captured_parent;env['controls']()
 trees={r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}
 if PHASE=='partial':partial.partial(original_before['trees'],trees,epoch,begin_ns,time.time_ns())
 else:pub.verify(original_before['trees'],trees,'after',epoch,begin_ns,time.time_ns())
 retained_inventory(trees)
 a=env['snapshot']();b=env['snapshot']();assert a==b
 assert all(a[k]==sealed[k]for k in ('units','rows','durable','artifacts'))
 for n,v in a['configuration'].items():assert env['same'](sealed['configuration'][n],v,env['exec_record'])
 assert parent()==captured_parent;retained_inventory(trees)
 return {'snapshot':a,'trees':trees,'runtime':runtime()}
def private(name,value):
 with(save/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 os.fsync(save_fd)
def retain(failure):
 print('PG1100_REFS_UNKNOWN phase='+phase+' type='+type(failure).__name__+' ownershipRetained=true',file=sys.stderr,flush=True)
 for f in traceback.extract_tb(failure.__traceback__)[-4:]:print(json.dumps({'safeFrame':f.name,'line':f.lineno,'file':pathlib.Path(f.filename).name}),file=sys.stderr,flush=True)
 while True:time.sleep(1)
try:
 phase='AUTHENTICATE';captured_parent=parent();env['controls']();runtime()
 assert not pathlib.Path('/proc/16222').exists()and not pathlib.Path('/proc/16248').exists()
 release(pathlib.Path(pub.OLD_LINK),env['BOM'],env['SOURCE'])
 release(pathlib.Path(pub.NEW_LINK),'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','d5b00104280028d9ea81b44c1d1c805f3c2861ed')
 pin(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),env['PIN_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),env['SIG_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 pin(pathlib.Path(pub.APPROVAL)/'current',hashlib.sha256(pub.NEW_APPROVAL).hexdigest())
 for name in ('before.private.json','epoch.private.json','approval.private.json','new-epoch.private','old-approval.private','old-current.private','refs.private.log'):
  path=OLD_SAVE/name;pin(path,ERROR if name=='refs.private.log'else hashlib.sha256(path.read_bytes()).hexdigest())
 assert(OLD_SAVE/'old-approval.private').read_bytes()==pub.OLD_APPROVAL
 assert(OLD_SAVE/'old-current.private').read_bytes()==pub.OLD_LINK.encode('ascii')
 tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1100-linked-tools-v1');raw=(tools/'payload-sha256.json').read_bytes();records=json.loads(raw)
 inventory(tools,[{'path':n,'size':(tools/n).stat().st_size,'sha256':d}for n,d in records.items()]+[{'path':'payload-sha256.json','size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}])
 current_fd=os.open(pub.CURRENT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);save_fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 old_link_fd=os.open('pg1088-current.part',os.O_PATH|os.O_NOFOLLOW,dir_fd=current_fd)
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in env['old']['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 print('REF_READY',flush=True)
 phase='BEFORE';assert sys.stdin.readline()=='prepare\n';before=pair();private('before.private.json',before);print('REF_CHECKED',flush=True)
 phase='PRESERVE';assert sys.stdin.readline()=='preserve\n';pair()
 assert not os.path.lexists(save/'current-link.private')
 os.rename('pg1088-current.part','current-link.private',src_dir_fd=current_fd,dst_dir_fd=save_fd);os.fsync(current_fd);os.fsync(save_fd)
 PHASE='after';after=pair();private('after.private.json',after);print('REF_CHECKED',flush=True)
 phase='DATABASE_CLOSED';assert sys.stdin.readline()=='run\n';env['OWNER_BACKEND']=0;after=pair();private('database-closed.private.json',after);print('REF_CHECKED',flush=True)
 phase='NORMAL_RELEASE';assert sys.stdin.readline()=='release\n';retained_inventory({r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)})
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close();os.close(old_link_fd);os.close(current_fd);os.close(save_fd)
 for h in reversed(held):h.close()
 print('REF_RELEASED',flush=True)
except BaseException as failure:retain(failure)
'''
