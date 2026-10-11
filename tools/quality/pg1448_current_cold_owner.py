"""SSC265 fixed current parent proof / once-TERM; no repair or business start.

Observe and handoff are distinct new-only runs. No auto retry or failed-run reuse.
All observation material is root-private; stdout contains a safe receipt only.
"""
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

from pg1441_current_cold_refs import source as child_source
from pg1442_current_cold_compile import W


def payload(mode):
    if mode not in {'observe', 'handoff'}:
        raise ValueError('fixed mode required')
    frozen=json.loads((W/'pg1444-current-cold-frozen-v2.safe.json').read_bytes())
    if frozen['operatorSource']!='0fe8c91ae7ebacfbb03318443f8a22fbedad8193' or frozen['actualExit']!=0:
        raise ValueError('old frozen source required')
    prefix=child_source().split('import dbus,time,sys,types\n',1)[0]
    # Paired namespace execs are retained by child_source and separately tested.
    value=prefix+'\nMODE='+repr(mode)+'\nFROZEN='+repr(frozen['fileHashes'])+'\n'+BODY
    ast.parse(value)
    return value


BODY=r'''
import dbus,types,time,signal,select,sys
os.umask(0o077)
PID=3323;TICKS=388541;BACKEND=3344;OWNER=True
ARGV='6f8b48e1ce163811e45b2e2695151393e4260eb44e56022efbb89032e73db148'
TOOLS=BASE/'pg1441-current-cold-tools-v1'
RUN='PG1448-current-cold-owner-proof-v1' if MODE=='observe' else 'PG1449-current-cold-owner-handoff-v1'
SAVE=BASE/RUN.lower();SAVE.mkdir(mode=0o700)
contract=types.ModuleType('contract');exec(INVENTORY_SOURCE,contract.__dict__)
locks=types.ModuleType('locks');exec(LOCK_SOURCE,locks.__dict__)
ROOT=pathlib.Path('/run/schubert-nk');held=[];refs=[];bus=None;reservation_fd=None
phase='ENTRY';RESERVED=False;SENT=False
def meta_any(path,follow):
 s=path.stat()if follow else path.lstat()
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def persist(name,value):
 data=json.dumps(value,sort_keys=True).encode()
 with(SAVE/name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
 return hashlib.sha256(data).hexdigest()
def runtime_check():
 require(set(os.listdir(ROOT))=={'maintenance.lock','startup-admission.lock','maintenance'})
 require(metadata(ROOT)[2:6]==[0,0,stat.S_IFDIR|0o755,3] and not os.listxattr(ROOT))
 require(metadata(ROOT/'maintenance')[2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listdir(ROOT/'maintenance') and not os.listxattr(ROOT/'maintenance'))
def peer_check():
 sql=contract.all_client_sql(BACKEND if OWNER else 0)
 sql+="select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==([b'0',b'1']if OWNER else[b'0',b'0']))
 if OWNER:
  row=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',"select pid,usename,application_name,client_addr,client_port,state from pg_stat_activity where pid=3344 and datname='schubert_nk' and backend_type='client backend' and exists(select 1 from pg_locks where pid=3344 and locktype='advisory' and classid=0 and objid=71419602 and granted);"],4096).decode().strip().split('|')
  require(row[:5]==['3344','schubert_batch','PG243-cold-empty','127.0.0.1','56616'] and row[5:]in[['active'],['idle in transaction']])
def actor():
 p=pathlib.Path('/proc')/str(PID);fields=(p/'stat').read_text().rpartition(')')[2].split()
 require(int(fields[19])==TICKS and int(fields[1])==3321)
 argv=(p/'cmdline').read_bytes();require(hashlib.sha256(argv).hexdigest()==ARGV and str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 authority={k:status[k].split()for k in['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']}
 require(authority=={'Uid':['0']*4,'Gid':['0']*4,'Groups':['0'],'CapInh':['0000000000000000'],'CapPrm':['000001ffffffffff'],'CapEff':['000001ffffffffff'],'CapBnd':['000001ffffffffff'],'CapAmb':['0000000000000000'],'NoNewPrivs':['0']})
 cg=(p/'cgroup').read_text();require(cg=='0::/user.slice/user-1000.slice/session-37.scope\n')
 tasks={t.name:(t/'children').read_text().strip()for t in(p/'task').iterdir()};require(not any(tasks.values()))
 fds={f.name:{'link':os.readlink(f),'metadata':meta_any(f,True)}for f in(p/'fd').iterdir()}
 require(fds['93']['link']=='socket:[26546]' and fds['92']['link']=='socket:[26539]')
 rows=[line.split()for line in(p/'net/tcp6').read_text().splitlines()[1:]]
 socket=[r for r in rows if len(r)>9 and r[9]=='26546'];require(len(socket)==1)
 r=socket[0];require(r[1:4]==['0000000000000000FFFF00000100007F:DD28','0000000000000000FFFF00000100007F:1538','01'] and r[7]=='0')
 # tx/rx queue and keepalive timers, and DB active/idle heartbeat state, are
 # volatile. Address/port/ESTABLISHED/UID/inode/FD + exact backend are mandatory.
 socket_identity=[r[1],r[2],r[3],r[7],r[9]]
 metas={name:metadata(ROOT/name)for name in['maintenance.lock','startup-admission.lock']}
 locks.owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),metas,PID)
 for name,digest in FROZEN.items():
  file=TOOLS/name;m=metadata(file)
  require(m[2:7]==[0,0,stat.S_IFREG|0o400,1,m[6]] and hashlib.sha256(file.read_bytes()).hexdigest()==digest and metadata(file)==m)
 require(len(FROZEN)==113 and len(os.listdir(TOOLS))==114)
 return {'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'authority':authority,'cgroup':cg,'tasks':tasks,'fds':fds,'socket':socket_identity,'locks':metas,'frozenHashes':FROZEN}
def read():
 s=snapshot()
 baseline=BASE/'pg1440-current-cold-readonly-v4/after.private.json';raw=baseline.read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='3252ba1de423ba4ee736c849a293f59430230f660c73350b47b480c3b5b1b230' and json.loads(raw)==s)
 return {'snapshot':s,'runtime':{n:metadata(ROOT/n)for n in['maintenance.lock','startup-admission.lock','maintenance']},'runtimeRoot':metadata(ROOT),'currentLink':meta_any(pathlib.Path('/opt/schubert-nk/current'),False),'held':[h.capture()for h in held],'actor':actor()if OWNER else None}
def retain(failure):
 sys.stderr.write('SSC265_UNKNOWN phase='+phase+' type='+type(failure).__name__+' reserved='+str(RESERVED)+' sent='+str(SENT)+'\n');sys.stderr.flush()
 while True:time.sleep(1)
try:
 phase='PIN_SCOPE'
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM)
 data=json.loads(manifest);sums=contract.canonical_sum_bytes(data['artifacts'],BOM);require((release/'SHA256SUMS').read_bytes()==sums)
 records=data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':BOM},{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}]
 held.append(contract.HeldInventory(str(release),records,0).open())
 for path,digest in[(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),'3378dbf29039d9fd0194f8c949a8793f00aff460bfeb6c69aba492498f4de221'),(BASE/'pg1292-manifest.sig','97fd4c41a795c5f2465cf2f5074831723db0c3942fa8d62d16a5aad54cb318f7')]:
  held.append(contract.HeldInventory(str(path.parent),[{'path':path.name,'size':path.stat().st_size,'sha256':digest}],0).open_file())
 approval=pathlib.Path('/etc/schubert-nk/release-approval/current');expected=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256='+BOM+'\n').encode();require(approval.read_bytes()==expected)
 held.append(contract.HeldInventory(str(approval.parent),[{'path':approval.name,'size':len(expected),'sha256':hashlib.sha256(expected).hexdigest()}],0).open_file())
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in UNITS:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==PID for n in daemon.ListNames()))
 phase='FULL_BEFORE_TWICE';before=read();require(before==read());before_hash=persist('before.private.json',before)
 if MODE=='handoff':
  reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  def verify(pid,ticks):
   require(pid==PID and ticks==TICKS);v=read();require(v==before);return v
  def reserve(pid,value):
   global RESERVED
   RESERVED=True;contract.durable_reservation(reservation_fd,str(PID)+'.term-reserved.private.json',json.dumps({'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'beforeSha256':before_hash},sort_keys=True).encode())
  def send(fd):
   global SENT
   SENT=True;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
  def wait(fd):
   poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
  phase='ONCE_PIDFD_TERM';contract.terminate_once(PID,TICKS,verify,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
  deadline=time.monotonic()+15
  while pathlib.Path('/proc/3323').exists()and time.monotonic()<deadline:time.sleep(.02)
  require(not pathlib.Path('/proc/3323').exists());OWNER=False
  phase='FULL_AFTER_TWICE';after=read();require(after==read())
  expected=dict(before,actor=None);require(after==expected)
  require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),before['actor']['locks']))
 else:after=before
 after_hash=persist('after.private.json',after)
 phase='NORMAL_CLOSE'
 for name in reversed(refs):manager.UnrefUnit(name)
 refs=[];bus.close();bus=None
 for h in reversed(held):h.close()
 held=[]
 if reservation_fd is not None:os.close(reservation_fd);reservation_fd=None
 result={'run':RUN,'actualExit':0,'source':SOURCE,'boot':BOOT,'sameCurrentOriginalsDbTwice':True,'allTenColdFull18Full32':True,'fixedParentProof':True,'reservationDurable':RESERVED,'signalAttempted':SENT,'parentGone':not OWNER,'allScopesClosedNormally':True,'oldJavaNormalClose':False,'formalAccepted':False,'beforePrivateSha256':before_hash,'afterPrivateSha256':after_hash}
 persist('result.safe.json',result);print(json.dumps(result,sort_keys=True))
except BaseException as failure:
 if RESERVED or SENT:retain(failure)
 errors=[]
 for name in reversed(refs):
  try:manager.UnrefUnit(name)
  except Exception as e:errors.append(type(e).__name__)
 if bus is not None:
  try:bus.close()
  except Exception as e:errors.append(type(e).__name__)
 for h in reversed(held):
  try:h.close()
  except Exception as e:errors.append(type(e).__name__)
 if errors:retain(failure)
 print(json.dumps({'run':RUN,'actualExit':1,'refusedPhase':phase,'type':type(failure).__name__,'signalAttempted':False,'allScopesClosedNormally':True,'formalAccepted':False}));sys.exit(1)
'''


def main(mode):
    os.umask(0o077)
    slot='pg1448-current-cold-owner-proof-v1' if mode=='observe' else 'pg1449-current-cold-owner-handoff-v1'
    out=W/slot;out.mkdir(mode=0o700)
    source=payload(mode).encode()
    with(out/'payload.private.py').open('xb')as f:f.write(source);f.flush();os.fsync(f.fileno())
    keys=Path('/home/mini/codex/project1/work/pgpt-vm/private')
    args=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(keys/'known_hosts'),'-o','ConnectTimeout=10','-i',str(keys/'vm-access'),'-p','22222','ubuntu@127.0.0.1','sudo','-n','python3','-']
    with(out/'observer.private.log').open('xb')as f:
        r=subprocess.run(args,input=source,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(source).hexdigest(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True));return r.returncode


if __name__=='__main__':
    if sys.argv[1:] not in [['observe'],['handoff']]:raise SystemExit('fixed observe/handoff required')
    raise SystemExit(main(sys.argv[1]))
