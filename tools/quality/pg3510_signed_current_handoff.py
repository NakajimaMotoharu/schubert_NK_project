"""SSC285 one fixed retained Java TERM with fresh full proof and queued gate."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg3506_signed_current_full_proof as proof
import pg3502_signed_current_retained_readonly as frozen
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT = 'pg3510-signed-current-handoff-v1'
OLD_SHA = 'e9e071e218417501d6d64b41561cb45fc63dc34c73114362783c6a5a86177bc5'


def ordinary_helpers():
    # Exact full-proof sections, minus only the terminated actor and its locks.
    raw = proof.HELPERS
    begin = raw.index(" module=pathlib.Path('/opt/jdk-25.0.4/lib/modules')")
    end = raw.index(' for n,v in actor[\'fds\'].items():')
    core = raw[begin:end]
    begin = raw.index(' units={};configuration={}')
    end = raw.index(' after=actors()[0];')
    core += raw[begin:end]
    return '\ndef ordinary_snapshot():\n' + core + " return {'units':units,'configuration':configuration,'rows':rows,'peers':peers,'ordinaryTcp':tcp,'unitFiles':unit_files,'durable':durable,'native':native,'runtime':runtime,'startup':startup}\n"


BODY = r'''
def durable(name,value):
 raw=value if isinstance(value,bytes)else json.dumps(value,sort_keys=True).encode()
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(raw).hexdigest()
def core(value):return {k:v for k,v in value.items()if k not in {'actor','locks','OFD43_128_same','OFD30_33_distinct'}}
def no_old():
 require(not pathlib.Path('/proc/410196').exists())
 for old in fresh['locks']:
  p=pathlib.Path('/run/schubert-nk')/old['name'];require(metadata(p)==old['metadata'])
  s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
  require(not any(len(l.split())>=8 and l.split()[5]==key for l in pathlib.Path('/proc/locks').read_text().splitlines()))
 require(not os.path.lexists(base/'pg3490-native-stop-v1'))
old_raw=(base/'pg3506-signed-current-full-proof-v2/proof.private.json').read_bytes()
require(hashlib.sha256(old_raw).hexdigest()==OLD_SHA)
old=json.loads(old_raw)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in seal['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 fresh=snapshot();second=snapshot()
 fresh39(old['actor'],fresh['actor'],time.time_ns());fresh39(fresh['actor'],second['actor'],time.time_ns())
 require(core(fresh)==core(second)==core(old)and fresh['locks']==second['locks']==old['locks'])
 save.mkdir(mode=0o700)
 parentfd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(parentfd)
 finally:os.close(parentfd)
 durable('old-proof.private.json',old_raw);fresh_sha=durable('fresh-proof.private.json',fresh)
 durable('fresh-complete.private.json',{'freshProofSha256':fresh_sha,'independentFreshProofComplete':True,'signalsIssued':0,'oldCloseUnknown':True})
 print(json.dumps({'stage':'FRESH_READONLY_PROOF_COMPLETE','actualExit':0,'freshProofSha256':fresh_sha,'signalsIssued':0,'sameConnection':True}),flush=True)
 def verify(pid,ticks):
  require((pid,ticks)==(410196,8469964))
  now=snapshot();fresh39(fresh['actor'],now['actor'],time.time_ns())
  require(canonical_actor(now['actor'])==canonical_actor(fresh['actor'])and core(now)==core(fresh)and now['locks']==fresh['locks'])
  return canonical_actor(now['actor'])
 def reserve(pid,value):
  durable('410196.term-once.private.json',{'pid':pid,'ticks':8469964,'actor':value,'signal':'TERM','replayAllowed':False,'freshProofSha256':fresh_sha})
  require(verify(pid,8469964)==value)
 def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait(fd):
  poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
 terminate(410196,8469964,verify,reserve,os.pidfd_open,send,wait,os.close)
 deadline=time.monotonic()+30
 while pathlib.Path('/proc/410196').exists():
  try:require(int(pathlib.Path('/proc/410196/stat').read_text().rpartition(')')[2].split()[19])==8469964)
  except OSError as error:
   if confirmed_absence(error,pathlib.Path('/proc/410196').exists()):break
   raise
  require(time.monotonic()<deadline);time.sleep(.05)
 no_old();after=ordinary_snapshot();again=ordinary_snapshot();require(after==again==core(fresh));no_old()
 after_sha=durable('after.private.json',after)
 durable('complete.private.json',{'ownedJavaGone':True,'oldCloseUnknown':True,'allOldResources0':True,'freshProofSha256':fresh_sha,'afterSha256':after_sha,'signalsIssued':1,'fullIndependentPostPending':True})
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
print(json.dumps({'stage':'OWNED_JAVA_REAPED','actualExit':0,'freshProofSha256':fresh_sha,'afterSha256':after_sha,'signalsIssued':1,'ownedJavaGone':True,'oldCloseUnknown':True,'fourOrdinaryAndAllOriginalsUnchanged':True,'newTenRefsReturnedNormally':True,'fullIndependentPostPending':True,'formalAccepted':False}),flush=True)
'''


def payload():
    raw = proof.helpers(SLOT) + ordinary_helpers() + '\nimport signal,select,errno\n'
    raw += inspect.getsource(terminate) + '\n' + inspect.getsource(confirmed_absence)
    raw += '\nOLD_SHA=' + repr(OLD_SHA) + '\n' + BODY
    if check(raw, '<complete SSC285 one actor recovery>'):
        raise ValueError('complete emitted recovery globals required')
    ast.parse(raw)
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    actual = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if actual['actualExit'] != 0 or actual['guest']['proofSha256'] != OLD_SHA:
        raise ValueError('actual current complete proof required')
    path = 'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    if 'SSC-285' not in subprocess.check_output(['git', 'show', 'origin/main:' + path], text=True):
        raise ValueError('published SSC285 required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=payload();(out/'payload.private.py').write_text(raw)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P/'current-management-critical.lock',validate_owner=frozen.host_owner)as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=240)
        (out/'stderr.private.log').write_bytes(r.stderr);(out/'stages.private.jsonl').write_bytes(r.stdout)
        if r.returncode==0 and not acquired.wait(30):raise ValueError('old sole gate natural release required')
        v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oldCloseUnknown':True,'forceUnlock':False,'formalAccepted':False}
        v['stages']=[json.loads(l)for l in r.stdout.splitlines()if l.startswith(b'{')]
        (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
