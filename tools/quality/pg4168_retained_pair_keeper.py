"""SSC288 staged bounded keeper/proof source. No operational entry exposed before design qualification."""
import ast
import inspect
import pg4112_canonical_epoch_owned_stage as previous
import pg4160_retained_config_read as observed
import pg4164_retained_pair_profile as profile
import pg4132_signed_phase_invariant as signed
import pg4178_pool_bounds as pool
from pg4060_original_profile_dual_stack import once
from pg782_owned_handoff import terminate

SLOT='pg4180-retained-pair-keeper-v1'


def payload():
    raw=previous.payload('inspect');raw=raw[:raw.index('import dbus\nbus=')]
    raw=once(raw,"save=base/'"+previous.INSPECT+"'","save=base/('"+SLOT+"-'+MODE)")
    raw=once(raw,"  if name in expected_inv:require(v['InvocationID']==expected_inv[name] and v['ActiveState']=='active' and v['SubState']=='running')",
             "  if name in expected_inv:require(v['InvocationID']==expected_inv[name])")
    raw=once(raw,'import base64,selectors','import base64')
    proc=next(n for n in ast.parse(observed.BODY).body if isinstance(n,ast.FunctionDef)and n.name=='proc')
    prelude='import sys\nif sys.argv[1:]not in (["proof"],["recover"]):raise ValueError("one exact keeper mode required")\nMODE=sys.argv[1]\n'
    raw=prelude+raw+'\n'+ast.get_source_segment(observed.BODY,proc)+'\n'
    raw+='PROFILE_SOURCE='+repr(inspect.getsource(profile))+'\nSIGNED_SOURCE='+repr(signed.source())+'\nPOOL_SOURCE='+repr(inspect.getsource(pool))+'\n'
    raw+=inspect.getsource(terminate)+'\n'+BODY
    compile(raw,'<new retained pair keeper>','exec');return raw


BODY=r'''
import time,signal,select,ctypes,dbus,traceback
require(os.uname().machine=='x86_64')
profile={};exec(PROFILE_SOURCE,profile)
signed={};exec(SIGNED_SOURCE,signed)
pool={};exec(POOL_SOURCE,pool)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
reference=Path('/var/lib/pgpt-s1-preservation/pg4160-retained-config-read-v1/observed.private.json').read_bytes()
require(hashlib.sha256(reference).hexdigest()=='e5fff095e3d770b128150029cefa2b3c501462d1e4f5b41279b5d80500be0d0b');reference=json.loads(reference)
def private_record(name,value):
 raw=value if type(value)is bytes else json.dumps(value,sort_keys=True).encode()
 require('/'not in name and 0<len(raw)<=67108864)
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(raw).hexdigest()
def kcmp(a,b):
 c=ctypes.CDLL(None,use_errno=True);c.syscall.restype=ctypes.c_long
 value=c.syscall(312,790010,790010,0,a,b);require(value>=0);return value==0
def ordinary(value):
 require(not value['database']['locks'])
 table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]
 roles={'schubert_app':('schubert-nk-api.service','schubert-nk-api',2),'schubert_web_session':('schubert-nk-web.service','schubert-nk-web',1)};counts={k:0 for k in roles}
 for row in value['database']['peers']:
  require(row['user']in roles);unit,app,unused=roles[row['user']];require(row['application']==app and row['address']=='127.0.0.1');counts[row['user']]+=1
  tcp_pair(table,row['port'],inodes(value['actors'][unit]['pid']),inodes(row['pid']))
 require(pool['counts_valid'](counts,set(),0,len(value['database']['peers']))is True)
def invariant(value):
 require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
 expected=reference['current']
 for key in ['units','actors','durable','native','startup','runtime']:require(value[key]==expected[key])
 require(value['database']['rows']==expected['database']['rows']);ordinary(value)
 configuration=config();require(set(configuration)==set(reference['configuration']))
 require(all(CONFIG_CONTRACT['same'](reference['configuration'][u],v,exec_record)for u,v in configuration.items()))
def pair():
 j=proc(790010);p=proc(789928);profile['stable'](reference['java'],j,time.time_ns());profile['stable'](reference['python'],p,time.time_ns())
 require(str(Path('/proc/790010/exe').readlink())=='/opt/jdk-25.0.4/bin/java'and Path('/proc/789928/exe').resolve()==Path('/usr/bin/python3').resolve())
 require(Path('/proc/790010/root').readlink()==Path('/')and Path('/proc/789928/root').readlink()==Path('/'))
 value=snapshot();invariant(value)
 require(len(value['flocks'])==2 and all(row.split()[4]=='790010'for row in value['flocks']))
 for name in ['maintenance.lock','startup-admission.lock']:
  target='/run/schubert-nk/'+name;aliases=[]
  for key,fd in j['fds'].items():
   if fd['target']==target and any(line.startswith('lock:')for line in fd['fdinfo'].splitlines()):aliases.append(int(key))
  require(bool(aliases)and all(kcmp(aliases[0],a)for a in aliases))
 require(kcmp(100,128)and not kcmp(87,90))
 return {'java':j,'python':p,'current':value,'configuration':config()}
def frame(message,budget=180):
 print(message,flush=True);sel=select.poll();sel.register(sys.stdin.fileno(),select.POLLIN)
 require(bool(sel.poll(budget*1000)));line=sys.stdin.buffer.readline(129);require(line==b'CONTINUE\n')
def zombie_or_absent(pid,ticks,parent):
 p=Path('/proc')/str(pid)
 if not p.exists():return True
 fields=(p/'stat').read_text().rsplit(')',1)[1].split()
 return int(fields[19])==ticks and int(fields[1])==parent and fields[0]=='Z'and not list((p/'fd').iterdir())
def owned_verify(pid,ticks):
 require((pid,ticks)in [(790010,14181503),(789928,14180650)])
 value=proc(pid)
 profile['stable'](reference['java']if pid==790010 else reference['python'],value,time.time_ns(),child_terminal=pid==789928)
 current=snapshot();invariant(current)
 if pid==790010:require(len(current['flocks'])==2 and all(row.split()[4]=='790010'for row in current['flocks']))
 else:require(not current['flocks']and zombie_or_absent(790010,14181503,789928))
 return value
def reserve(pid,value):
 private_record(str(pid)+'.term-reserved.private.json',{'pid':pid,'ticks':value['ticks'],'source':data['source']['commit'],'signal':'TERM','replayAllowed':False,'actor':value})
 require(owned_verify(pid,value['ticks'])==value)
def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];issued=False
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 first=pair();second=pair();require(first==second)
 proof_sha=private_record('proof.private.json',first)
 if MODE=='recover':
  private_record('ready.private.json',{'proofSha256':proof_sha,'signalsIssued':0,'old4152Normal':False})
  frame('SSC288_PAIR_READY '+proof_sha)
  issued=True
  terminate(790010,14181503,owned_verify,reserve,os.pidfd_open,send,wait,os.close)
  require(zombie_or_absent(790010,14181503,789928))
  current=snapshot();invariant(current);require(not current['flocks'])
  private_record('java-terminal.private.json',{'pidfdTerminal':True,'zombieOrAbsent':True,'oldCloseNormal':False,'allOldFlocks0':True})
  terminate(789928,14180650,owned_verify,reserve,os.pidfd_open,send,wait,os.close)
  deadline=time.monotonic()+30
  while Path('/proc/790010').exists()or Path('/proc/789928').exists():require(time.monotonic()<deadline);time.sleep(.05)
  after=snapshot();invariant(after);require(not after['flocks'])
  private_record('old-pair-gone.private.json',{'allOldPidsGone':True,'allOldFlocksAdvisory0':True,'old4152Normal':False,'oldCloseNormal':False})
  frame('SSC288_OLD_PAIR_GONE metadataRefsHeld=true')
  # The coordinator retains this connection's ten metadata references while it inherits
  # the same host gate and executes separately frozen partial inspect/recover/post scripts.
  frame('SSC288_METADATA_HELD postRequired=true',1800)
 else:
  require(not issued)
except BaseException as failure:
 if MODE=='recover'and issued:
  try:private_record('failure.private.json',{'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]})
  except OSError:print('FAILURE_CAPTURE_UNAVAILABLE isolationRetained=true',flush=True)
  print('SSC288_UNKNOWN metadataRetained=true oldCloseNormal=false',flush=True)
  while True:time.sleep(1)
 raise
finally:
 if MODE=='proof'or not issued:
  for unit in reversed(refs):manager.UnrefUnit(unit)
  bus.close()
 elif MODE=='recover':
  for unit in reversed(refs):manager.UnrefUnit(unit)
  bus.close()
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,'proofSha256':proof_sha,'signalsIssued':2 if issued else 0,'newTenRefsNormalClose':True,'old4152Normal':False,'oldCloseNormal':False,'businessUnitActions':0,'formalAccepted':False}
private_record('manifest.safe.json',result);print(json.dumps(result))
'''
