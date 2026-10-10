"""Generate fixed completed-cold activation observer, no entrypoint/authority here."""
import ast
import hashlib
import json
from pathlib import Path
from pg1041_cold_policy_diagnostic import W
from pg1069_cold_candidate_sources import replace_once

HERE=Path(__file__).resolve().parent


def source():
    frozen=json.loads((W/'pg1085-cold-candidate-ro-frozen-v1.safe.json').read_bytes())
    p=W/'pg1084-cold-tools-v1/pg1084_cold_refs.py';raw=p.read_bytes()
    if frozen['actualExit']!=0 or hashlib.sha256(raw).hexdigest()!=frozen['fileHashes'][p.name]:
        raise ValueError('qualified fixed readonly base required')
    keep={'CHECKSUM_HASH','CONTRACT_SOURCE','LOCK_SOURCE','MANIFEST_SIZE','BOOT','SOURCE',
          'BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS'}
    nodes=[]
    for n in ast.parse(raw).body:
        if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)):nodes.append(n)
        elif isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)for t in n.targets):
            if {t.id for t in n.targets}<=keep:nodes.append(n)
    code=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'
    # Signed old release/originals/rows are always checked. Only the explicitly
    # approved public pointer binding follows the independent finite phase.
    old="require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == str(RELEASE))"
    new="require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == (pub.NEW_LINK if PHASE in ('after','release') else pub.OLD_LINK))"
    code=replace_once(code,old,new)
    old="require(approval.read_bytes() == ('NKRELEASEAPPROVAL1\\nversion=0.1.0-PG932\\nmanifest_sha256=' + BOM + '\\n').encode())"
    code=replace_once(code,old,"require(approval.read_bytes() == (pub.NEW_APPROVAL if PHASE in ('approval','link-staged','after','release') else pub.OLD_APPROVAL))")
    prefix='FROZEN_BASE_SHA='+repr(hashlib.sha256(raw).hexdigest())+'\n'
    for name,file in [('PUB_SOURCE','pg1083_cold_publication_contract.py'),
                      ('IO_SOURCE','pg1090_cold_finite_capture.py'),('EXCHANGE_SOURCE','pg1088_cold_exchange_io.py')]:
        prefix+=name+'='+repr((HERE/file).read_text())+'\n'
    assembled=prefix+code+BODY
    ast.parse(assembled);return assembled


BODY=r'''
import types,dbus,sys,time,traceback
os.umask(0o077);require(os.geteuid()==0)
require(len(sys.argv)==2 and sys.argv[1].isdigit())
OWNER_BACKEND=int(sys.argv[1]);require(1<OWNER_BACKEND<2147483647)
OWNER_PID=os.getppid();require(OWNER_PID>1)
PHASE='before';BEGIN_NS=time.time_ns();EPOCH=None;before_trees=None
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1091-cold-activate-v1')
require(metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2])
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
contract=types.ModuleType('old_inventory');exec(CONTRACT_SOURCE,contract.__dict__)
locks=types.ModuleType('owned_locks');exec(LOCK_SOURCE,locks.__dict__);owned_flocks=locks.owned_flocks
pub=types.ModuleType('finite_publication');exec(PUB_SOURCE,pub.__dict__)
io=types.ModuleType('finite_capture');exec(IO_SOURCE,io.__dict__)
exchange_io=types.ModuleType('linked_exchange');exec(EXCHANGE_SOURCE,exchange_io.__dict__)
old=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes())
prepared_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1062-cold-prepared-v1/after.private.json').read_bytes()
require(hashlib.sha256(prepared_raw).hexdigest()=='412eb77968cd3f28d5bf2869df52b3625233809ba119b2b90cf9080e976516bf')
prepared=json.loads(prepared_raw);expected_runtime=prepared['runtime']
held=[];directory_fds=[];refs=[];bus=None;captured_parent=None;old_link_fd=None;current_fd=None;save_fd=None;phase='ENTRY'

def tree_records():
 return {root:io.direct_tree(root)for root in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}

def runtime_namespaces():
 root=pathlib.Path('/run/schubert-nk')
 require(set(os.listdir(root))=={'maintenance.lock','startup-admission.lock','maintenance','startup','backup-request','cleanup-request','expiry-request','pt-coverage'})
 value={name:metadata(root/name)for name in expected_runtime if name!='@root'}
 value['@root']=metadata(root)
 require(set(value)==set(expected_runtime))
 for name,m in value.items():
  p=root if name=='@root'else root/name
  require(not os.listxattr(p))
  if name=='startup':
   require(m==tree_records()[pub.STARTUP][pub.STARTUP]['metadata'])
   require(set(os.listdir(p))==({'epoch.current'}if PHASE!='before'else set()))
   if PHASE!='before':require((p/'epoch.current').read_bytes()==EPOCH)
  else:require(m==expected_runtime[name])
  if name not in ('@root','pt-coverage','startup'):require(not os.listdir(p))
 require(set(os.listdir(root/'pt-coverage'))=={'parent','cleanup','expiry','root-api','backup','inspector'})
 return value

def parent():
 p=pathlib.Path('/proc')/str(OWNER_PID);s=(p/'stat').read_text().rpartition(')')[2].split()
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 argv=(p/'cmdline').read_bytes();require(argv.split(b'\0')[-3:]==[b'Pg1091ColdActivation',b'activate',b''])
 require({int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={os.getpid()})
 fixed={name:metadata(pathlib.Path('/run/schubert-nk')/name)for name in ('maintenance.lock','startup-admission.lock')}
 owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),fixed,OWNER_PID)
 return {'pid':OWNER_PID,'ticks':int(s[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','CapEff','CapPrm','CapBnd','NoNewPrivs')},'cgroup':(p/'cgroup').read_text(),'locks':fixed}

def inventory_check(trees):
 for h in held:
  for fd,parent_fd,name,fixed,attrs in h.held:
   spelling=os.readlink('/proc/self/fd/'+str(fd))
   if spelling.endswith(' (deleted)'):spelling=spelling[:-10]
   fixed_row={'metadata':list(fixed),'sha256':None,'target':None,'acl':[x[0]for x in attrs]}
   observed=io.fd_record(fd)
   # Immutable contents are independently bound to manifest/material records.
   if stat.S_ISREG(fixed[4]):
    if spelling==pub.APPROVAL+'/current':fixed_row['sha256']=hashlib.sha256(pub.OLD_APPROVAL).hexdigest()
    else:
     relative=str(pathlib.PurePosixPath(spelling).relative_to(h.root))
     fixed_row['sha256']=h.records[relative]['sha256']
   pub.verify_retained(spelling,fixed_row,observed,PHASE,trees,BEGIN_NS,time.time_ns())
   if not (spelling==pub.APPROVAL+'/current'and PHASE in ('approval','link-staged','after','release')):
    require(io.metadata(os.stat(name,dir_fd=parent_fd,follow_symlinks=False))==observed['metadata'])
 for path,fd,fixed in directory_fds:
  row=io.fd_record(fd);require(row['metadata']==fixed and row==io.path_record(path))
 alias='current'if PHASE not in ('after','release')else'current-link.private'
 directory=current_fd if PHASE not in ('after','release')else save_fd
 link=exchange_io.linked_attributes(directory,alias,old_link_fd)
 pub.verify_retained(pub.CURRENT+'/current',before_trees[pub.CURRENT][pub.CURRENT+'/current'],link,PHASE,trees,BEGIN_NS,time.time_ns())

def pair():
 require(parent()==captured_parent);controls()
 trees=tree_records();pub.verify(before_trees,trees,PHASE,EPOCH,BEGIN_NS,time.time_ns());inventory_check(trees)
 a=snapshot();b=snapshot();require(a==b and a['units']==prepared['snapshot']['units']and a['rows']==prepared['snapshot']['rows']and a['durable']==prepared['snapshot']['durable']and a['artifacts']==prepared['snapshot']['artifacts'])
 for name,value in a['configuration'].items():require(same(prepared['snapshot']['configuration'][name],value,exec_record))
 require(parent()==captured_parent);inventory_check(tree_records())
 return {'immutable':a,'trees':trees,'runtime':runtime_namespaces()}

def private(name,value):
 with(SAVE/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 os.fsync(save_fd)

def retain(failure):
 print('PG1091_REFS_UNKNOWN phase='+phase+' type='+type(failure).__name__+' ownershipRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)

try:
 phase='AUTHENTICATE';captured_parent=parent();controls();authenticate()
 candidate_root=pathlib.Path(pub.NEW_LINK);raw=(candidate_root/'RELEASE-MANIFEST.json').read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
 records=json.loads(raw)['artifacts'];sums=contract.canonical_sum_bytes(records,hashlib.sha256(raw).hexdigest())
 held.append(contract.HeldInventory(str(candidate_root),records+[{'path':'RELEASE-MANIFEST.json','size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}],0).open())
 hold_material(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),64,'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 for path in ('/run/schubert-nk','/run/schubert-nk/maintenance','/var/lib/schubert-nk/maintenance'):
  p=pathlib.Path(path);fixed=metadata(p);require(not os.listxattr(p));directory_fds.append((p,os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW),fixed))
 current_fd=os.open(pub.CURRENT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 save_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 old_link_fd=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=current_fd)
 before_trees=tree_records();pub.verify(before_trees,before_trees,'before',None,BEGIN_NS,time.time_ns())
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in old['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 print('REF_READY',flush=True)
 phase='BEFORE';require(sys.stdin.readline()=='prepare\n');before=pair();private('before.private.json',before);print('REF_CHECKED',flush=True)
 phase='EPOCH';require(sys.stdin.readline()=='epoch\n');EPOCH=(SAVE/'new-epoch.private').read_bytes();PHASE='epoch';value=pair();private('epoch.private.json',value);print('REF_CHECKED',flush=True)
 phase='APPROVAL';require(sys.stdin.readline()=='approval\n');PHASE='approval';value=pair();private('approval.private.json',value);print('REF_CHECKED',flush=True)
 phase='EXCHANGE';require(sys.stdin.readline()=='exchange\n');pair()
 require(not os.path.lexists(pathlib.Path(pub.CURRENT)/'pg1088-current.part'))
 os.symlink(pub.NEW_LINK,'pg1088-current.part',dir_fd=current_fd);os.fsync(current_fd);PHASE='link-staged';pair()
 exchange_io.exchange(current_fd,'pg1088-current.part');os.fsync(current_fd)
 row=exchange_io.linked_attributes(current_fd,'pg1088-current.part',old_link_fd)
 require(row['target']==pub.OLD_LINK and row['metadata'][1]==before_trees[pub.CURRENT][pub.CURRENT+'/current']['metadata'][1])
 require(not os.path.lexists(SAVE/'current-link.private'))
 os.rename('pg1088-current.part','current-link.private',src_dir_fd=current_fd,dst_dir_fd=save_fd);os.fsync(current_fd);os.fsync(save_fd)
 PHASE='after';after=pair();private('after.private.json',after);print('REF_CHECKED',flush=True)
 phase='DATABASE_CLOSED';require(sys.stdin.readline()=='run\n');OWNER_BACKEND=0;after=pair();private('database-closed.private.json',after);print('REF_CHECKED',flush=True)
 phase='NORMAL_RELEASE';require(sys.stdin.readline()=='release\n');inventory_check(tree_records())
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 os.close(old_link_fd);os.close(current_fd);os.close(save_fd)
 for _,fd,_ in reversed(directory_fds):os.close(fd)
 for h in reversed(held):h.close()
 print('REF_RELEASED',flush=True)
except BaseException as failure:retain(failure)
'''
