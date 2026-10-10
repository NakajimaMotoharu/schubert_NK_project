"""Owned completed-cold readback profile; runtime namespace/mount/epoch changes are absent."""
import ast
import hashlib
from pathlib import Path
from pg1002_cold_readonly import payload

R=Path(__file__).resolve().parent

def guest():
    tree=ast.parse(payload())
    names={'BOOT','SOURCE','BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS'}
    nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))or
           isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in names for t in n.targets)]
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    # Same real dedicated DB owner, not a guessed count or a lost session.
    sql="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
    assert raw.count(repr(sql))==1
    raw=raw.replace(repr(sql),'owned_peer_sql(OWNER_BACKEND)')
    marker="require(peers.splitlines() == [b'0', b'0'])";assert raw.count(marker)==1
    raw=raw.replace(marker,"require(peers.splitlines() == ([b'0',b'0',b'1'] if OWNER_BACKEND else [b'0',b'0',b'0']))")
    begin="    for name in ['maintenance.lock', 'startup-admission.lock']:\n"
    end="    require(not pathlib.Path('/run/schubert-nk/startup').exists()"
    assert raw.count(begin)==raw.count(end)==1
    first=raw.index(begin);last=raw.index(end)
    raw=raw[:first]+"    owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),{n:metadata(pathlib.Path('/run/schubert-nk')/n)for n in ['maintenance.lock','startup-admission.lock']},OWNER_PID)\n"+raw[last:]
    parser=(R/'pg477_unit_references.py').read_bytes()
    assert hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
    function=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
    raw+='\n'+ast.unparse(function)+'\n'+(R/'pg847_configuration.py').read_text().replace('FIELDS','CONFIG_FIELDS')
    raw+='\n'+(R/'pg1004_cold_refs.py').read_text()+'\n'+BODY
    ast.parse(raw);return raw

BODY=r'''
import sys,time,dbus
require(len(sys.argv)==3 and sys.argv[1]=='verify'and sys.argv[2].isdigit())
OWNER_BACKEND=int(sys.argv[2]);require(1<OWNER_BACKEND<2147483647)
OWNER_PID=os.getppid();require(OWNER_PID>1 and os.geteuid()==0)
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
require(pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
from pg1023_cold_contract import owned_flocks,owned_peer_sql
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()==BASELINE_HASH);old=json.loads(raw)
checkpoint=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1004-cold-readonly-v3/after.private.json').read_bytes()
require(hashlib.sha256(checkpoint).hexdigest()=='1cbb10fa83df138d5f3fe6b40b8107e16475e280745797f6e9e5a58d030073a9')
sealed=json.loads(checkpoint)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1023-cold-owned-v1')
require(SAVE.is_dir()and SAVE.stat().st_uid==0 and stat.S_IMODE(SAVE.stat().st_mode)==0o700)
held=[];before=None;post=None;phase='ENTRY'
def verify_fds():
 for path,fd,fixed in held:
  require(metadata(path)==fixed)
  s=os.fstat(fd);require([s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==fixed)
def read_pair():
 verify_fds();a=snapshot();b=snapshot();require(a==b)
 for name,v in a['configuration'].items():
  require(same(sealed['configuration'][name],v,exec_record))
  start=exec_record(v['ExecStart']);require(start is not None and start[3:]==('n/a','n/a','0','(null)','0/0'))
  require(v['ExecStop']=='')
 require(a['units']==sealed['units']and a['rows']==sealed['rows']and a['durable']==sealed['durable']and a['artifacts']==sealed['artifacts'])
 verify_fds();return a
def private_save(name,value):
 p=SAVE/name
 with p.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 directory=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(directory)
 finally:os.close(directory)
def body():
 global phase,before,post,OWNER_BACKEND
 phase='HELD_FDS'
 for name in ['/run/schubert-nk','/var/lib/schubert-nk/maintenance']:
  path=pathlib.Path(name);fixed=metadata(path)
  require(stat.S_ISDIR(fixed[4])and fixed[2]==fixed[3]==0 and not os.listxattr(path))
  fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);held.append((path,fd,fixed))
 verify_fds();print('REF_READY',flush=True)
 phase='BEFORE_OWNED';require(sys.stdin.readline()=='prepare\n')
 before=read_pair();private_save('before.private.json',before);print('REF_CHECKED',flush=True)
 phase='POST_DATABASE_CLOSE';require(sys.stdin.readline()=='run\n')
 OWNER_BACKEND=0;post=read_pair();require(before==post);private_save('after.private.json',post)
 print('REF_CHECKED',flush=True)
 phase='NORMAL_RELEASE';require(sys.stdin.readline()=='release\n');verify_fds();return True
try:
 bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 require(with_references(manager,bus,list(old['units']),body))
 for _,fd,_ in reversed(held):os.close(fd)
 phase='NORMAL_CLOSED'
 private_save('readback.safe.json',{'run':'PG1023-cold-owned-v1','source':SOURCE,'boot':BOOT,'all24Unchanged':True,'allTenColdFull32':True,'ownedServerDatabaseObservedAndClosed':True,'sameParentFlocksObserved':True,'refsFdBusReturnedNormally':True,'readbackOnly':True,'fullColdPreparationAccepted':False})
 print('REF_RELEASED',flush=True)
except BaseException as failure:
 print('PG1023_REFS_UNKNOWN phase='+phase+' type='+type(failure).__name__+' isolationRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
'''

def files():
    return {'Pg1023ColdOwnedReadback.java':(R/'Pg1023ColdOwnedReadback.java').read_text(),
            'Pg1023ColdOwnedReadbackTest.java':(R/'Pg1023ColdOwnedReadbackTest.java').read_text(),
            'pg1023_cold_refs.py':guest(),'pg1023_cold_contract.py':(R/'pg1023_cold_contract.py').read_text()}
