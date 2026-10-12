"""SSC274 exact Ref then Java ordinary TERM; same-connection durable fresh proof.

No service action, force kill, backend termination or business operation.
"""
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH, W
import pg1664_current_unused_pair_readonly_proof as proof
from pg1665_unused_pair_contract import fresh_parent, parent_after_ref
from pg782_owned_handoff import terminate
from pg1657_same_connection_fresh_handoff import design_scope as previous_scope

SLOT = 'pg1667-unused-pair-owned-handoff-v1'
PROOF_SHA = 'c0036f9a79672f32ad9c51453b7ca16e067d4ec34cc183d6321ab63b42fe0e8a'
DESIGN = ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md', 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md', 'documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md', 'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']

BODY = r'''
import time,signal,select
saved=(base/'pg1664-current-unused-pair-proof-v1/proof.private.json').read_bytes()
require(hashlib.sha256(saved).hexdigest()==PROOF_SHA);expected=json.loads(saved)
require(expected['signals0']is True and expected['oldCloseUnknown']is True and expected['candidateNotPlaced']is True)
save=base/'pg1667-unused-pair-owned-handoff-v1';require(not os.path.lexists(save))
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 def normalized(v):return json.loads(json.dumps(v))
 def original():
  require(snapshot()==snapshot()==expected['native'])
  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')
  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
 original();fresh=normalized(pair());require(fresh==normalized(pair()))
 fresh_parent(expected['pair']['parent'],fresh['parent'],time.time_ns())
 require(fresh['child']==expected['pair']['child']and fresh['peer']==expected['pair']['peer'])
 require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks'])
 run=pathlib.Path('/run');require(not os.listxattr(run))
 require(list(metadata9(run.lstat()))==fresh['parent']['fds']['29']['metadata']==fresh['parent']['fds']['32']['metadata'])
 save.mkdir(mode=0o700)
 base_fd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(base_fd)
 finally:os.close(base_fd)
 def private(name,raw):
  fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   require(os.fstat(fd).st_ino==save.lstat().st_ino)
   f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
   with os.fdopen(f,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
   os.fsync(fd);require(os.fstat(fd).st_ino==save.lstat().st_ino)
  finally:os.close(fd)
 private('old-proof.private.json',saved)
 fresh_raw=json.dumps({'pair':fresh,'locks':expected['locks'],'native':native,'allOriginalValuesUnchanged':True,'oldProofSha256':PROOF_SHA,'independentFreshProofComplete':True,'signalsIssued':0},sort_keys=True).encode()
 fresh_sha=hashlib.sha256(fresh_raw).hexdigest();private('fresh-proof.private.json',fresh_raw)
 private('fresh-complete.private',('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+fresh_sha+'\n').encode())
 print(json.dumps({'stage':'FRESH_READONLY_PROOF_COMPLETE','actualExit':0,'proofSha256':fresh_sha,'signalsIssued':0,'sameConnection':True,'formalAccepted':False}),flush=True)
 def before_child(pid,ticks):
  require((pid,ticks)==(291242,5962938));original();require(normalized(pair())==fresh)
  return fresh['child']
 def wait(fd):
  p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
 def reserve(pid,a):
  # Recheck the complete fresh generation after the durable reservation too.
  private(str(pid)+'.term-once.private',json.dumps({'pid':pid,'actor':a,'signal':'TERM','replayAllowed':False},sort_keys=True).encode())
  require((before_child(pid,5962938)if pid==291242 else before_parent(pid,5962776))==a)
 def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def reap(pid,ticks):
  deadline=time.monotonic()+30
  while pathlib.Path('/proc',str(pid)).exists():
   try:require(int(pathlib.Path('/proc',str(pid),'stat').read_text().rpartition(')')[2].split()[19])==ticks)
   except FileNotFoundError:break
   require(time.monotonic()<deadline);time.sleep(.05)
 def before_parent(pid,ticks):
  require((pid,ticks)==(291213,5962776)and not pathlib.Path('/proc/291242').exists())
  original();a=normalized(actor());parent_after_ref(fresh['parent'],a,{fresh['child']['fds'][n]['target']for n in ['0','1']})
  require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks']and same_peer()==fresh['peer'])
  daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  require(not any(daemon.NameHasOwner(n)for n in fresh['child']['busNames']))
  return a
 terminate(291242,5962938,before_child,reserve,os.pidfd_open,send,wait,os.close)
 reap(291242,5962938);REF_CLOSED=True;before_parent(291213,5962776)
 terminate(291213,5962776,before_parent,reserve,os.pidfd_open,send,wait,os.close)
 reap(291213,5962776)
 require(not pathlib.Path('/proc/291213').exists()and not pathlib.Path('/proc/291242').exists())
 q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
 for value in expected['locks']:
  s=(pathlib.Path('/run/schubert-nk')/value['name']).lstat();require(list(metadata9(s))==value['metadata'])
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':')
   require(len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 private('complete.private',b'ownedRefThenJavaGone=true\nallOldResources0=true\noldCloseUnknown=true\nfullIndependentPostPending=true\n')
 print(json.dumps({'actualExit':0,'freshProofSha256':fresh_sha,'refThenJavaOwnedTerm':True,'ownedActorsDBAdvisoryFlockAndBusGone':True,'sameConnection':True,'oldCloseUnknown':True,'fullIndependentPostPending':True,'formalAccepted':False}),flush=True)
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
'''


def payload():
    raw = proof.payload()
    raw = raw[:raw.index("save=base/'pg1664-current-unused-pair-proof-v1'")]
    raw = raw.replace('require(children=={291242})', 'require(children==(set()if REF_CLOSED else{291242}))')
    raw = 'REF_CLOSED=False\nPROOF_SHA=' + repr(PROOF_SHA) + '\n' + inspect.getsource(fresh_parent) + '\n' + inspect.getsource(parent_after_ref) + '\n' + inspect.getsource(terminate) + '\n' + raw + BODY
    compile(raw, '<SSC274 current once owned pair handoff>', 'exec')
    return raw


def design_scope(text, path):
    ns = dict(previous_scope.__globals__)
    exec(inspect.getsource(previous_scope).replace('273', '274'), ns)
    return ns['design_scope'](text, path)


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    for path in DESIGN:
        local = subprocess.check_output(['git', 'show', 'HEAD:' + path], text=True)
        remote = subprocess.check_output(['git', 'show', 'origin/main:' + path], text=True)
        if design_scope(local, path) != design_scope(remote, path):
            raise ValueError('SSC274 published design authority required')
    old = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['guest']['proofSha256'] != PROOF_SHA:
        raise ValueError('actual full pair proof required')
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-'], input=raw, capture_output=True, timeout=180)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    (out / 'stages.private.jsonl').write_bytes(r.stdout)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'oldCloseUnknown': True, 'formalAccepted': False}
    rows = [json.loads(line) for line in r.stdout.splitlines() if line.startswith(b'{')]
    if rows:
        value['stages'] = rows
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
