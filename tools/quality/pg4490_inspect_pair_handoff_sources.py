"""SSC297 fixed new ten-Ref controller; proof/recover share exactly the same bytes."""
import ast
import hashlib
import inspect
from pyflakes.api import check
import pg4488_inspect_pair_contract as contract
import pg4360_pool_bound_partial_sources as post
from pg1446_current_cold_stage import W
from pg782_owned_handoff import terminate

SLOT='pg4490-inspect-pair-handoff-v2'


def independent_post():
    raw=post.files()['post.py']
    if hashlib.sha256(raw.encode()).hexdigest()!='d64b8c588d337609a9b788f7540df50de2fb61dd69e9351ef2745d536bf7835b':raise ValueError('pinned old complete post')
    marker="save=base/'pg4362-pool-bound-post-v3'"
    if raw.count(marker)!=1:raise ValueError('one new-only post boundary')
    return raw.replace(marker,"save=base/'pg4490-inspect-pair-handoff-v2-independent-post'",1)


def payload():
    raw=(W/'pg4482-bound-configuration-pair-read-v1/payload.private.py').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='f2cac6424e371314b6c7661b520bb78a1584510e20faf0da40af6870507b7376':raise ValueError('fixed complete19/32 full reader')
    text=raw.decode();marker="os.umask(0o077);save=base/'pg4482-bound-configuration-pair-read-v1'"
    if text.count(marker)!=1:raise ValueError('one fixed capture boundary')
    prefix=text[:text.index(marker)]
    top=ast.parse(text);private=next(n for n in top.body if isinstance(n,ast.FunctionDef)and n.name=='private')
    result=prefix+'\nCONTRACT_SOURCE='+repr(inspect.getsource(contract))+'\nPOST_SOURCE='+repr(independent_post())+'\n'+inspect.getsource(terminate)+'\n'+ast.get_source_segment(text,private)+'\n'+BODY
    if check(result,'<exact inspect pair handoff>'):raise ValueError('all emitted static0')
    compile(result,'<exact inspect pair handoff>','exec');return result


BODY=r'''
import sys,time,signal,select,dbus,traceback
MODE=sys.argv[1];require(MODE in ['proof','recover']);os.umask(0o077)
save=base/('pg4490-inspect-pair-handoff-v2-'+MODE);save.mkdir(mode=0o700)
contract={};exec(CONTRACT_SOURCE,contract)
def fixed(path,digest):
 b=(base/path).read_bytes();require(hashlib.sha256(b).hexdigest()==digest);return json.loads(b)
reference=fixed('pg4482-bound-configuration-pair-read-v1/second-data.private.json','cf3a4d1d3cd190600054566609666a99421da7fcbb58bc6423e74da77c8f8211')
owners=fixed('pg4482-bound-configuration-pair-read-v1/second-pair.private.json','e1558f41bdf20aa2c85eaf7a821820d4d339b9f1dc0a657f1e4c0b9924c5dbaa')
configuration=fixed('pg4482-bound-configuration-pair-read-v1/second-config.private.json','457c2d37338dbee9667efa689840c09fa43003c0e88988dcf9d9d93e281ef015')
identities=fixed('pg4484-inspect-pair-identity-read-v1/identity.private.json','62787733f66625dfa2f94e897d6785e21b3dea4bb1cda1747d733ff330b686da')['identity']
java_gone=False;python_gone=False;sequence=0;issued=False;signals=0
def identity(label):
 p=Path('/proc')/str(identities[label]['pid']);keys=[b.split(b'=',1)[0].decode('ascii')for b in(p/'environ').read_bytes().split(b'\0')if b]
 value={'pid':identities[label]['pid'],'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),
  'exe':str((p/'exe').readlink()),'root':str((p/'root').readlink()),'cwd':str((p/'cwd').readlink()),
  'agentVariableNamesPresent':[k for k in keys if k in ['LD_PRELOAD','LD_AUDIT','JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','PYTHONPATH','PYTHONSTARTUP']]}
 require(value==identities[label]);return value
def release():
 require(current.resolve(strict=True)==root and hashlib.sha256(manifest.read_bytes()).hexdigest()==sha)
 for row in rows:
  p=root/row['path'];require(not p.is_symlink()and p.resolve().is_relative_to(root)and p.is_file()and p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
 verified=subprocess.run(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(pin),'-in',str(manifest),'-sigfile',str(signature)],capture_output=True,timeout=15);require(verified.returncode==0)
 require(not os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG4432')and not os.path.lexists('/var/lib/pgpt-s1-preservation/pg4432-manifest.sig'))
def capture(label):
 global sequence
 sequence+=1;prefix=f'{sequence:03d}-{label}'
 pair={}
 for name,pid in [('java',827198),('python',827230),('backend',827228)]:
  if not(java_gone and name in ['java','backend']or python_gone and name=='python'):
   pair[name]=proc(pid);private(prefix+'-'+name+'.private.json',pair[name])
 pair['tcp']=Path('/proc/net/tcp').read_text();pair['tcp6']=Path('/proc/net/tcp6').read_text();pair['unix']=Path('/proc/net/unix').read_text()
 pair_sha=private(prefix+'-pair.private.json',pair)
 value=snapshot();value_sha=private(prefix+'-data.private.json',value)
 configs=config();config_sha=private(prefix+'-config.private.json',configs)
 return {'pair':pair,'data':value,'config':configs,'hashes':{'pair':pair_sha,'data':value_sha,'config':config_sha}}
def check_one(value):
 pair=value['pair'];contract['peers'](reference,value['data'],java_gone);require(value['config']==configuration)
 for label in ['java','python']:
  if label=='java'and java_gone or label=='python'and python_gone:continue
  contract['stable'](label,owners[label],pair[label],java_gone,time.time_ns());identity(label)
 if not java_gone:
  for key in ['pid','ticks','argvSha256','authority','cgroup','children']:require(pair['backend'][key]==owners['backend'][key])
  contract['database_socket'](pair)
def invariant(label):
 release();a=capture(label+'-first');b=capture(label+'-second')
 check_one(a);check_one(b)
 for target in ['java','python','backend']:
  if target in a['pair']:require(a['pair'][target]==b['pair'][target])
 require(a['data']==b['data']and a['config']==b['config'])
 return private(label+'-boundary.private.json',{'first':a['hashes'],'second':b['hashes']})
def verify(pid,ticks):
 label='java'if pid==827198 else'python'if pid==827230 else'';require(label!=''and ticks==identities[label]['ticks'])
 invariant('verify-'+str(sequence));value=proc(pid);contract['stable'](label,owners[label],value,java_gone,time.time_ns());identity(label);return value
def reserve(pid,value):
 private(str(pid)+'.term-reserved.private.json',{'pid':pid,'ticks':value['ticks'],'actor':value,'signal':'TERM','replayAllowed':False})
 require(verify(pid,value['ticks'])==value)
def send(fd):
 global signals
 signal.pidfd_send_signal(fd,signal.SIGTERM,None,0);signals+=1
def wait(fd):
 p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
def absent(pids):
 deadline=time.monotonic()+30
 while any(Path('/proc',str(pid)).exists()for pid in pids):require(time.monotonic()<deadline);time.sleep(.05)
def frame(message):
 print(message,flush=True);p=select.poll();p.register(sys.stdin.fileno(),select.POLLIN)
 require(bool(p.poll(180000))and sys.stdin.buffer.readline(129)==b'CONTINUE\n')
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in sorted(reference['units']):manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 require(len(refs)==10);proof=invariant('proof')
 if MODE=='recover':
  frame('SSC297_OWNERS_READY '+proof);issued=True
  terminate(827198,16494387,verify,reserve,os.pidfd_open,send,wait,os.close)
  absent([827198]);java_gone=True
  deadline=time.monotonic()+30
  while True:
   state=snapshot();private('java-terminal-check-'+str(sequence)+'.private.json',state);sequence+=1
   if not state['database']['peers']and not state['database']['locks']and not state['flocks']:break
   require(time.monotonic()<deadline);time.sleep(.05)
  if not Path('/proc/827230').exists():python_gone=True
  invariant('java-gone');frame('SSC297_JAVA_GONE originalTransportRequired=true')
  if Path('/proc/827230').exists():terminate(827230,16494598,verify,reserve,os.pidfd_open,send,wait,os.close)
  absent([827230]);python_gone=True;invariant('pair-gone')
  frame('SSC297_PAIR_GONE oldCloseUnknown=true')
  with(save/'independent-post.stdout.private.log').open('xb')as output,(save/'independent-post.stderr.private.log').open('xb')as error:
   child=subprocess.Popen(['/usr/bin/python3','-B','-c',POST_SOURCE],stdin=subprocess.DEVNULL,stdout=output,stderr=error)
   private('independent-post.process.private.json',{'pid':child.pid,'actor':proc(child.pid)})
   code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
  tail=(save/'independent-post.stdout.private.log').read_bytes();private('independent-post.exit.safe.json',{'actualExit':code,'stdoutSha256':hashlib.sha256(tail).hexdigest()})
  require(code==0);post_result=json.loads(tail.splitlines()[-1])
  require(post_result['actualExit']==0 and post_result['newMARDDBTenRefNormalClose']is True and post_result['all24OriginalBackupNativeUnitConfigUnchanged']is True and post_result['oldParentNormal']is False)
  invariant('independent-post-gone')
except BaseException as failure:
 if issued:
  try:private('failure.private.json',{'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]})
  except OSError:pass
  try:print('SSC297_UNKNOWN newMetadataRetained=true noReplay=true',flush=True)
  except OSError:pass
  while True:time.sleep(1)
 raise
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,'proofSha256':proof,'signalsIssued':signals,
 'oldScopesNormal':False,'newTenRefsNormalClose':True,'unitOperationsIssued':0,'candidatePlaced':False,'formalAccepted':False}
if MODE=='recover':value.update(allOldProcessesAndResourcesGone=True,independentPost=post_result)
private('manifest.safe.json',value);print(json.dumps(value))
'''
