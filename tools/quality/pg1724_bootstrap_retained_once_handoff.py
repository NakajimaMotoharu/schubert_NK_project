"""SSC276 one current Java TERM, old UNKNOWN remains; separate post required."""
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1724_retained_host_gate import queued_gate
import pg1723_bootstrap_expired_peer_readonly_proof as proof
from pg1673_sole_owner_contract import source as fresh_guard
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT='pg1724-bootstrap-retained-handoff-v1'
PROOF_SHA='3b84d06a176a9d0e3fe4296d4f72108f787d4391120805450f47891bbb4744e0'

BODY=r'''
saved=(base/'pg1723-bootstrap-expired-peer-proof-v1/proof.private.json').read_bytes();require(hashlib.sha256(saved).hexdigest()==PROOF_SHA)
expected=json.loads(saved);require(expected['signals0']is True and expected['oldCloseUnknown']is True and expected['serverPeerAdvisory0']is True)
def normalized(v):return json.loads(json.dumps(v))
def original():
 require(snapshot()==snapshot()==expected['native']and not list((base/'pg1719-bootstrap-verify-v3').iterdir()))
 require(not any(os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in ('bootstrap-admin-username','bootstrap-admin-password')))
original();fresh=normalized(actor());require(fresh==normalized(actor()))
fresh_sole_parent(expected['actor'],fresh,time.time_ns())
require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks']and same_peer()==expected['peer'])
require(not os.listxattr(pathlib.Path('/run'))and list(metadata9(pathlib.Path('/run').lstat()))==fresh['fds']['29']['metadata']==fresh['fds']['32']['metadata'])
save=base/'pg1724-bootstrap-retained-handoff-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
def private(name,raw):
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  a=os.fstat(fd);b=save.lstat();require((a.st_dev,a.st_ino,a.st_uid,a.st_mode,a.st_nlink)==(b.st_dev,b.st_ino,b.st_uid,b.st_mode,b.st_nlink))
  f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
  with os.fdopen(f,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
  os.fsync(fd)
 finally:os.close(fd)
fd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
private('old-proof.private.json',saved)
fresh_raw=json.dumps({'actor':fresh,'peer':expected['peer'],'locks':expected['locks'],'native':native,'oldProofSha256':PROOF_SHA,'independentFreshProofComplete':True,'signalsIssued':0,'allOriginalValuesUnchanged':True,'oldCloseUnknown':True},sort_keys=True).encode()
fresh_sha=hashlib.sha256(fresh_raw).hexdigest();private('fresh-proof.private.json',fresh_raw)
private('fresh-complete.private',('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+fresh_sha+'\n').encode())
print(json.dumps({'stage':'FRESH_READONLY_PROOF_COMPLETE','actualExit':0,'proofSha256':fresh_sha,'signalsIssued':0,'sameConnection':True,'formalAccepted':False}),flush=True)
def before(pid,ticks):
 require((pid,ticks)==(383695,7281859));original();a=normalized(actor());require(a==fresh)
 require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks']and same_peer()==expected['peer'])
 return a
def reserve(pid,a):
 private(str(pid)+'.term-once.private',json.dumps({'pid':pid,'ticks':7281859,'actor':a,'signal':'TERM','replayAllowed':False},sort_keys=True).encode());require(before(pid,7281859)==a)
def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
terminate(383695,7281859,before,reserve,os.pidfd_open,send,wait,os.close)
deadline=time.monotonic()+30
while pathlib.Path('/proc/383695').exists():
 try:require(int(pathlib.Path('/proc/383695/stat').read_text().rpartition(')')[2].split()[19])==7281859)
 except OSError as error:
  if confirmed_absence(error,pathlib.Path('/proc/383695').exists()):break
  raise
 require(time.monotonic()<deadline);time.sleep(.05)
require(not pathlib.Path('/proc/383695').exists())
q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
for v in expected['locks']:
 s=(pathlib.Path('/run/schubert-nk')/v['name']).lstat();require(list(metadata9(s))==v['metadata'])
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':');require(len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
private('complete.private',b'ownedJavaGone=true\noldCloseUnknown=true\nallOldResources0=true\nfullIndependentPostPending=true\n')
print(json.dumps({'actualExit':0,'freshProofSha256':fresh_sha,'ownedJavaGone':True,'dbAdvisoryMA0':True,'oldCloseUnknown':True,'fullIndependentPostPending':True,'formalAccepted':False}),flush=True)
'''

def payload():
    raw=proof.payload();raw=raw[:raw.index('tool=base/TOOL_NAME')]
    closure=proof.prior.TAIL[:proof.prior.TAIL.index('a=actor();')]
    at=raw.index('bus=dbus.SystemBus(private=True);manager=')
    raw=raw[:at]+closure+'\n'+raw[at:]
    marker=' native=snapshot();require(native==snapshot())'
    if raw.count(marker)!=1:raise ValueError('one continuous original Ref scope required')
    raw=raw.replace(marker,marker+'\n'+'\n'.join(' '+line if line else line for line in BODY.splitlines()))
    raw='import time,signal,select,errno\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh_guard()+'\n'+inspect.getsource(confirmed_absence)+'\n'+inspect.getsource(terminate)+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<current Bootstrap one owner handoff>'):raise ValueError('generated static refused')
    compile(raw,'<current Bootstrap one owner handoff>','exec');return raw

def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        text=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC276'not in text and 'SSC-276'not in text:raise ValueError('published SSC276 required')
    old=json.loads((W/proof.SLOT/'manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or old['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual current complete proof required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with queued_gate(P/'current-management-critical.lock')as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=180)
        if r.returncode==0 and not acquired.wait(30):raise ValueError('old wrapper gate release not proven')
        (out/'stderr.private.log').write_bytes(r.stderr);(out/'stages.private.jsonl').write_bytes(r.stdout)
        v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldCloseUnknown':True,'criticalGateQueuedWithoutForceUnlock':True,'formalAccepted':False}
        v['stages']=[json.loads(l)for l in r.stdout.splitlines()if l.startswith(b'{')]
        with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode

if __name__=='__main__':raise SystemExit(main())
