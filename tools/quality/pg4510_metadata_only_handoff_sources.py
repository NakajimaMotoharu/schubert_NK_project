"""SSC298 metadata-only handoff with genuine wait, no unstable child-FD census."""
import inspect
from pyflakes.api import check
import pg4490_inspect_pair_handoff_sources as previous

SLOT='pg4510-metadata-only-handoff-v1'


def metadata_owner(old,now,terminal):
    def require(v):
        if v is not True:raise ValueError('exact metadata-only owner refused')
    require(type(old)is dict and type(now)is dict and old==now)
    require((now.get('pid'),now.get('ticks'),now.get('argvSha256'))==(828676,16705476,'51c27aa637200ae1f7a30fccb7dd27511286366392131c40edf7fde823787349'))
    require(now.get('cgroup')=='0::/user.slice/user-1000.slice/session-1042.scope\n'and now.get('children')==[829193])
    a=now.get('authority',{});require(a.get('PPid')=='828674'and a.get('Uid','').split()==['0']*4 and a.get('Gid','').split()==['0']*4 and a.get('Groups','').split()==['0'])
    require(a.get('NoNewPrivs')=='0'and a.get('CapInh')==a.get('CapAmb')=='0000000000000000'and all(a.get(k)=='000001ffffffffff'for k in ['CapPrm','CapEff','CapBnd']))
    fds=now.get('fds',{});require(set(fds)=={'0','1','2','3'})
    require([fds[str(n)]['target']for n in range(4)]==['pipe:[14183497]','pipe:[14183498]','pipe:[14183499]','socket:[14182061]'])
    require(type(terminal)is dict and terminal=={'pid':829193,'ticks':16712075,'state':'Z','ppid':828676,'rawWaitStatus':0,'statSha256':'dd7f940c77cd271cb77d48de7f99d4a4e3d26fb69b71c65a344a7e597cc57efb'})
    return True


def post_source():
    raw=previous.independent_post();marker='pg4490-inspect-pair-handoff-v2-independent-post'
    if raw.count(marker)!=1:raise ValueError('one new-only fresh post namespace')
    return raw.replace(marker,'pg4510-metadata-only-handoff-v1-independent-post',1)


def payload():
    raw=previous.payload();marker='import sys,time,signal,select,dbus,traceback'
    if raw.count(marker)!=1:raise ValueError('one complete read-only prelude')
    raw=raw[:raw.index(marker)]
    # Replace the embedded fixed post with a distinct post-ownership-change run;
    # no already successful post is reissued or rewritten.
    assignment='POST_SOURCE='+repr(previous.independent_post())
    if raw.count(assignment)!=1:raise ValueError('one independent post binding')
    raw=raw.replace(assignment,'POST_SOURCE='+repr(post_source()),1)
    raw+='\n'+inspect.getsource(metadata_owner)+'\n'+BODY
    if check(raw,'<metadata-only fresh handoff>'):raise ValueError('all emitted static0')
    compile(raw,'<metadata-only fresh handoff>','exec');return raw


BODY=r'''
import sys,time,signal,select,dbus,traceback
MODE=sys.argv[1];require(MODE in ['proof','recover']);os.umask(0o077)
save=base/('pg4510-metadata-only-handoff-v1-'+MODE);save.mkdir(mode=0o700)
def fixed(path,digest):
 encoded=(base/path).read_bytes();require(hashlib.sha256(encoded).hexdigest()==digest);return json.loads(encoded)
owner=fixed('pg4504-post-retainer-full-read-v1/first-owner.private.json','fcf88a7b143639ff54bcc7f217db0a1c7bf659eafbe118b360955b8b65e79164')
reference=fixed('pg4504-post-retainer-full-read-v1/first-data.private.json','148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148')
configuration=fixed('pg4504-post-retainer-full-read-v1/first-config.private.json','457c2d37338dbee9667efa689840c09fa43003c0e88988dcf9d9d93e281ef015')
identity=fixed('pg4504-post-retainer-full-read-v1/identity.private.json','e4cbc5fd7310fb3f7a73d06db8070652de96dd4b6b0d73f4188ec87acc5214f6')
old_post=fixed('pg4490-inspect-pair-handoff-v2-independent-post/manifest.safe.json','7ab5cdc6f68904cd44fcd42aa1e64009f679b3ed6acb59b853ba68a79e0bc55a')
require(old_post['actualExit']==0 and old_post['newMARDDBTenRefNormalClose']is True and old_post['oldParentNormal']is False)
sequence=0;gone=False;issued=False
def release():
 require(current.resolve(strict=True)==root and hashlib.sha256(manifest.read_bytes()).hexdigest()==sha)
 for row in rows:
  p=root/row['path'];require(not p.is_symlink()and p.resolve().is_relative_to(root)and p.is_file()and p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
 result=subprocess.run(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(pin),'-in',str(manifest),'-sigfile',str(signature)],capture_output=True,timeout=15);require(result.returncode==0)
 require(not os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG4432')and not os.path.lexists('/var/lib/pgpt-s1-preservation/pg4432-manifest.sig'))
def terminal():
 p=Path('/proc/829193');raw=(p/'stat').read_text();fields=raw.rsplit(')',1)[1].split()
 require(not(p/'cmdline').read_bytes()and not list((p/'fd').iterdir()))
 return {'pid':829193,'ticks':int(fields[19]),'state':fields[0],'ppid':int(fields[1]),'rawWaitStatus':int(fields[49]),'statSha256':hashlib.sha256(raw.encode()).hexdigest()}
def capture(label):
 global sequence
 sequence+=1;prefix=f'{sequence:03d}-{label}';image={}
 if not gone:
  image['owner']=proc(828676);private(prefix+'-owner.private.json',image['owner'])
  image['terminal']=terminal();private(prefix+'-terminal.private.json',image['terminal'])
  p=Path('/proc/828676');image['identity']={'exe':str((p/'exe').readlink()),'root':str((p/'root').readlink()),'cwd':str((p/'cwd').readlink())}
  keys=[b.split(b'=',1)[0].decode('ascii')for b in(p/'environ').read_bytes().split(b'\0')if b];image['agentKeys']=[k for k in keys if k in ['LD_PRELOAD','LD_AUDIT','JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','PYTHONPATH','PYTHONSTARTUP']]
 image['data']=snapshot();private(prefix+'-data.private.json',image['data']);image['config']=config();private(prefix+'-config.private.json',image['config'])
 digest=private(prefix+'-image.private.json',image);return image,digest
def check_image(v):
 require(v['data']==reference and v['config']==configuration and v['data']['database']['peers']==[]and v['data']['database']['locks']==[]and v['data']['flocks']==[])
 if not gone:require(metadata_owner(owner,v['owner'],v['terminal'])and v['identity']==identity and not v['agentKeys'])
 else:require(not Path('/proc/828676').exists()and not Path('/proc/829193').exists())
def invariant(label):
 release();a,ash=capture(label+'-first');b,bsh=capture(label+'-second');check_image(a);check_image(b);require(a==b)
 return private(label+'-boundary.private.json',{'first':ash,'second':bsh})
def verify(pid,ticks):
 require((pid,ticks)==(828676,16705476));invariant('verify-'+str(sequence));value=proc(pid);require(metadata_owner(owner,value,terminal()));return value
def reserve(pid,value):
 private(str(pid)+'.term-reserved.private.json',{'pid':pid,'ticks':value['ticks'],'actor':value,'signal':'TERM','replayAllowed':False});require(verify(pid,value['ticks'])==value)
def wait(fd):
 p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
def absent():
 deadline=time.monotonic()+30
 while any(Path('/proc',str(pid)).exists()for pid in [828676,829193]):require(time.monotonic()<deadline);time.sleep(.05)
def frame(message):
 print(message,flush=True);p=select.poll();p.register(sys.stdin.fileno(),select.POLLIN);require(bool(p.poll(180000))and sys.stdin.buffer.readline(129)==b'CONTINUE\n')
def run_post():
 private('post-start-reservation.private.json',{'payloadSha256':hashlib.sha256(POST_SOURCE.encode()).hexdigest(),'parentPid':os.getpid(),'oldPostReplayed':False,'replayAllowed':False})
 with(save/'post.stdout.private.log').open('xb')as output,(save/'post.stderr.private.log').open('xb')as error:
  child=subprocess.Popen(['/usr/bin/python3','-B','-c',POST_SOURCE],stdin=subprocess.DEVNULL,stdout=output,stderr=error)
  private('post-start-pid.private.json',{'pid':child.pid,'parentPid':os.getpid()})
  code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
 tail=(save/'post.stdout.private.log').read_bytes();private('post-exit.safe.json',{'actualExit':code,'stdoutSha256':hashlib.sha256(tail).hexdigest()})
 require(code==0);result=json.loads(tail.splitlines()[-1]);require(result['actualExit']==0 and result['newMARDDBTenRefNormalClose']is True and result['all24OriginalBackupNativeUnitConfigUnchanged']is True and result['oldParentNormal']is False);return result
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in sorted(reference['units']):manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 require(len(refs)==10);proof=invariant('proof')
 if MODE=='recover':
  frame('SSC298_METADATA_READY '+proof);issued=True
  terminate(828676,16705476,verify,reserve,os.pidfd_open,lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
  absent();gone=True;invariant('metadata-gone');frame('SSC298_METADATA_GONE originalTransportRequired=true')
  post_result=run_post();invariant('new-post-gone')
except BaseException as failure:
 if issued:
  try:private('failure.private.json',{'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]})
  except OSError:pass
  try:print('SSC298_UNKNOWN metadataRetained=true noReplay=true',flush=True)
  except OSError:pass
  while True:time.sleep(1)
 raise
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,
 'proofSha256':proof,'signalsIssued':1 if issued else 0,'childSignalsIssued':0,'oldScopesNormal':False,'newTenRefsNormalClose':True,'oldPostReplayed':False,'unitOperationsIssued':0,'formalAccepted':False}
if MODE=='recover':value.update(allOldProcessesAndResourcesGone=True,independentPost=post_result)
private('manifest.safe.json',value);print(json.dumps(value))
'''
