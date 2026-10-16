"""SSC294 remaining-only controller. No Java/Caddy/Root action is present."""
import hashlib
import inspect
import pg4376_scoped_half_handoff_read as previous
import pg4378_half_handoff_contract as owners
import pg4338_current_partial_sources as pair
import pg4360_pool_bound_partial_sources as current
import pg4368_pool_bound_recover as fixed_entry
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4380-half-handoff-v1'


def payload():
    raw = previous.payload()
    if hashlib.sha256(raw.encode()).hexdigest() != '6d861fa740003a23ffc317e787f172f7702562958d2b19e3bb6ea9cc0872fb81':
        raise ValueError('exact current half-handoff evidence prelude required')
    raw = raw[:raw.index('KEEPER_PROGRAM=')]
    raw = once(raw, "save=base/'" + previous.SLOT + "'", "save=base/('" + SLOT + "-'+MODE)")
    raw += '\nOWNER_SOURCE=' + repr(inspect.getsource(owners)) + '\nPYTHON_SOURCE=' + repr(pair.profile_source()) + '\n'
    raw += '\n' + current.BOUNDARY
    hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in current.files().items()}
    programs = {name: fixed_entry.bootstrap(name, hashes) for name in ['partial.py', 'post.py']}
    return raw + '\nPROGRAMS=' + repr(programs) + '\n' + BODY


BODY = r'''
import time,signal,select,dbus,traceback,datetime
owner_contract={};exec(OWNER_SOURCE,owner_contract)
python_contract={};exec(PYTHON_SOURCE,python_contract)
signed={};exec(SIGNED_SOURCE,signed)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
def fixed_json(path,digest):
 encoded=Path(path).read_bytes();require(hashlib.sha256(encoded).hexdigest()==digest);return json.loads(encoded)
reference=fixed_json(str(base/'pg4376-scoped-half-handoff-read-v1/second.private.json'),'078c7f92555bdeecb9b9fc925c69f51ebedba40f89fea251f9c9f40c6b17cb7f')
owners=fixed_json(str(base/'pg4376-scoped-half-handoff-read-v1/owners.private.json'),'627510dfc462519adcdc2a34f33d915ca72cb44297a80c08140361288bdafa83')
configuration=fixed_json(str(base/'pg4356-current-pool-witness-v1/observed.private.json'),'cd2d8421d9fb9c70821d2f5a3d9b05ba491c1a24ff5988122bde14e12ceabb75')['configuration']
def invariant():
 require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
 value=snapshot()
 try:
  for key in ['units','actors','durable','native','startup','runtime']:require(value[key]==reference[key])
  require(value['database']['rows']==reference['database']['rows']and not value['flocks']and not value['database']['locks'])
  require(fd_contract['same_details'](reference['detailedActors'],value['detailedActors'],reference['ordinaryDatabaseFds'],value['ordinaryDatabaseFds']))
  require(declaration_contract['same_configurations'](configuration,config(),CONFIG_CONTRACT['same'],exec_record))
 except BaseException:
  save_pair('rejected-invariant',{'reference':reference,'current':value});raise
 return value
def zombie_or_absent():
 p=Path('/proc/815726')
 if not p.exists():return True
 tail=(p/'stat').read_text().rsplit(')',1)[1].split()
 return tail[0]=='Z'and int(tail[1])==815643 and int(tail[19])==15409721 and not list((p/'fd').iterdir())
python_gone=False
def verify(pid,ticks):
 require(owner_contract['target'](pid,ticks));value=proc(pid)
 if pid==815643:
  require(not python_gone and zombie_or_absent())
  require(python_contract['stable'](owners['python'],value,time.time_ns(),child_terminal=True))
  require(owner_contract['stable_retainer'](owners['retainer'],proc(817783)))
 else:
  require(owner_contract['stable_retainer'](owners['retainer'],value))
  if python_gone:require(not Path('/proc/815643').exists()and not Path('/proc/815726').exists())
  else:require(zombie_or_absent()and python_contract['stable'](owners['python'],proc(815643),time.time_ns(),child_terminal=True))
 require(Path('/proc/'+str(pid)+'/exe').resolve()==Path('/usr/bin/python3').resolve()and Path('/proc/'+str(pid)+'/root').readlink()==Path('/'))
 invariant();require(proc(pid)==value);return value
def reserve(pid,value):
 private_record(str(pid)+'.term-reserved.private.json',{'pid':pid,'ticks':value['ticks'],'actor':value,'signal':'TERM','replayAllowed':False})
 require(verify(pid,value['ticks'])==value)
def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
def absent(pids):
 deadline=time.monotonic()+30
 while any(Path('/proc/'+str(pid)).exists()for pid in pids):require(time.monotonic()<deadline);time.sleep(.05)
def frame(message):
 print(message,flush=True);poll=select.poll();poll.register(sys.stdin.fileno(),select.POLLIN)
 require(bool(poll.poll(180000))and sys.stdin.buffer.readline(129)==b'CONTINUE\n')
def job(name,mode,label):
 with(save/(label+'.stdout.private.log')).open('xb')as output,(save/(label+'.stderr.private.log')).open('xb')as error:
  child=subprocess.Popen(['/usr/bin/python3','-B','-c',PROGRAMS[name]]+([mode]if mode else[]),stdin=subprocess.DEVNULL,stdout=output,stderr=error)
  private_record(label+'.process.private.json',{'pid':child.pid,'actor':proc(child.pid)})
  code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
 content=(save/(label+'.stdout.private.log')).read_bytes();private_record(label+'.exit.safe.json',{'actualExit':code,'stdoutSha256':hashlib.sha256(content).hexdigest()})
 require(code==0);result=json.loads(content.splitlines()[-1]);require(result['actualExit']==0 and result['source']==data['source']['commit']);return result
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];issued=False
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 py=verify(815643,15408795);retainer=verify(817783,15666115)
 proof=private_record('proof.private.json',{'python':py,'retainer':retainer,'current':invariant(),'oldScopesNormal':False})
 if MODE=='recover':
  private_record('ready.private.json',{'proofSha256':proof,'signalsIssued':0,'javaSignalPermitted':False})
  frame('SSC294_OWNERS_READY '+proof);issued=True
  terminate(815643,15408795,verify,reserve,os.pidfd_open,send,wait,os.close)
  absent([815643,815726]);python_gone=True;invariant()
  private_record('old-python-java-gone.private.json',{'pythonTermOnce':True,'javaSignalIssued':False,'bothOldPidsGone':True,'oldCloseNormal':False})
  frame('SSC294_OLD_PYTHON_GONE originalTransportRequired=true')
  terminate(817783,15666115,verify,reserve,os.pidfd_open,send,wait,os.close);absent([817783]);invariant()
  private_record('old-metadata-gone.private.json',{'retainerTermOnce':True,'oldRetainerNormalClose':False,'oldRetainerTransportExit':None})
  frame('SSC294_OLD_METADATA_GONE transportUnknownPreserved=true')
  inspect_result=job('partial.py','inspect','partial-inspect');require(inspect_result['newScopeNormalClose']is True)
  recover_result=job('partial.py','recover','partial-recover')
  require(recover_result['newStopCount']==5 and recover_result['caddyPriorStopAuthenticated']is True and recover_result['original58917Normal']is False and recover_result['recoverySixNormal']is True)
  post_result=job('post.py',None,'independent-post')
  require(post_result['newMARDDBTenRefNormalClose']is True and post_result['independentFailedDoneRecoveryPost']is True)
except BaseException as failure:
 if issued:
  try:private_record('failure.private.json',{'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]})
  except OSError:pass
  try:print('SSC294_UNKNOWN metadataRetained=true noReplay=true',flush=True)
  except OSError:pass
  while True:time.sleep(1)
 raise
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,
 'proofSha256':proof,'signalsIssued':2 if issued else 0,'javaSignalsIssued':0,'caddyStopsReissued':0,'oldScopesNormal':False,'newTenRefsNormalClose':True,'formalAccepted':False}
if MODE=='recover':value.update(partialInspect=inspect_result,partialRecover=recover_result,independentPost=post_result)
private_record('manifest.safe.json',value);print(json.dumps(value))
'''
