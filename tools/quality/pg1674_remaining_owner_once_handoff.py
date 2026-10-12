"""SSC275 new-only sole DB owner once TERM, critical management gate."""
import inspect
import json
import os
import hashlib
import subprocess
from pg1446_current_cold_stage import SSH, W, P
from pg1674_critical_management_gate import management_gate
import pg1672_remaining_db_owner_readonly_proof as proof
import pg1667_unused_pair_once_handoff as pair_handoff
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT = 'pg1674-remaining-owner-handoff-v1'
PROOF_SHA = '537aaccf3ff3f98e17e71dbda28fa7bfe671e44699f9b7d59c6fde9241dd93aa'

BODY = r'''
import time,signal,select
saved=(base/'pg1672-remaining-db-owner-proof-v1/proof.private.json').read_bytes();require(hashlib.sha256(saved).hexdigest()==PROOF_SHA)
expected=json.loads(saved);require(expected['signals0']is True and expected['oldCloseUnknown']is True and expected['childReapedAndBusGone']is True)
save=base/'pg1674-remaining-owner-handoff-v1';require(not os.path.lexists(save))
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 def normalized(v):return json.loads(json.dumps(v))
 def original():
  require(snapshot()==snapshot()==expected['native'])
  require(not pathlib.Path('/proc/291242').exists())
  daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  require(not any(daemon.NameHasOwner(n)for n in expected['oldPair']['child']['busNames']))
  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
 original();fresh=normalized(actor());require(fresh==normalized(actor()))
 fresh_sole_parent(expected['actor'],fresh,time.time_ns())
 require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks']and same_peer()==expected['peer'])
 require(not os.listxattr(pathlib.Path('/run'))and list(metadata9(pathlib.Path('/run').lstat()))==fresh['fds']['29']['metadata']==fresh['fds']['32']['metadata'])
 save.mkdir(mode=0o700)
 base_fd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(base_fd)
 finally:os.close(base_fd)
 def private(name,raw):
  fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   value=os.fstat(fd);linked=save.lstat();require((value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode,value.st_nlink)==(linked.st_dev,linked.st_ino,linked.st_uid,linked.st_gid,linked.st_mode,linked.st_nlink))
   f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
   with os.fdopen(f,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
   os.fsync(fd)
  finally:os.close(fd)
 private('old-proof.private.json',saved)
 fresh_raw=json.dumps({'actor':fresh,'peer':expected['peer'],'locks':expected['locks'],'native':native,'oldProofSha256':PROOF_SHA,'independentFreshProofComplete':True,'signalsIssued':0,'childAlreadyReaped':True,'allOriginalValuesUnchanged':True},sort_keys=True).encode()
 fresh_sha=hashlib.sha256(fresh_raw).hexdigest();private('fresh-proof.private.json',fresh_raw)
 private('fresh-complete.private',('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+fresh_sha+'\n').encode())
 print(json.dumps({'stage':'FRESH_READONLY_PROOF_COMPLETE','actualExit':0,'proofSha256':fresh_sha,'signalsIssued':0,'sameConnection':True,'formalAccepted':False}),flush=True)
 def before(pid,ticks):
  require((pid,ticks)==(291213,5962776));original();a=normalized(actor());require(a==fresh)
  require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==expected['locks']and same_peer()==expected['peer'])
  return a
 def reserve(pid,a):
  private(str(pid)+'.term-once.private',json.dumps({'pid':pid,'ticks':5962776,'actor':a,'signal':'TERM','replayAllowed':False},sort_keys=True).encode())
  require(before(pid,5962776)==a)
 def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait(fd):
  p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
 terminate(291213,5962776,before,reserve,os.pidfd_open,send,wait,os.close)
 deadline=time.monotonic()+30
 while pathlib.Path('/proc/291213').exists():
  try:require(int(pathlib.Path('/proc/291213/stat').read_text().rpartition(')')[2].split()[19])==5962776)
  except OSError as error:
   if confirmed_absence(error,pathlib.Path('/proc/291213').exists()):break
   raise
  require(time.monotonic()<deadline);time.sleep(.05)
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
 private('complete.private',b'ownedJavaGone=true\nchildAlreadyGone=true\nallOldResources0=true\noldCloseUnknown=true\nfullIndependentPostPending=true\n')
 print(json.dumps({'actualExit':0,'freshProofSha256':fresh_sha,'ownedJavaGone':True,'childAlreadyGone':True,'dbAdvisoryMA0':True,'oldCloseUnknown':True,'fullIndependentPostPending':True,'formalAccepted':False}),flush=True)
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
'''


def payload():
    raw = proof.payload()
    raw = raw[:raw.index("private=base/'pg1667-unused-pair-owned-handoff-v1'")]
    raw = 'import errno\n' + inspect.getsource(confirmed_absence) + '\nPROOF_SHA=' + repr(PROOF_SHA) + '\n' + inspect.getsource(terminate) + '\n' + raw + BODY
    compile(raw, '<SSC275 same-connection sole DB owner handoff>', 'exec')
    return raw


def design_scope(text, path):
    ns = dict(pair_handoff.previous_scope.__globals__)
    exec(inspect.getsource(pair_handoff.previous_scope).replace('273', '275'), ns)
    return ns['design_scope'](text, path)


def main():
    os.umask(0o077)
    proof.qualify_no_parent_signal()
    if subprocess.check_output(['git', 'status', '--porcelain']):raise ValueError('clean fixed operator required')
    for path in pair_handoff.DESIGN:
        local=subprocess.check_output(['git','show','HEAD:'+path],text=True)
        remote=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if design_scope(local,path)!=design_scope(remote,path):raise ValueError('SSC275 published authority required')
    old=json.loads((W/proof.SLOT/'manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or old['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual sole99 full proof required')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stages.private.jsonl').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldCloseUnknown':True,'criticalManagementGate':True,'formalAccepted':False}
    rows=[json.loads(line)for line in r.stdout.splitlines()if line.startswith(b'{')]
    if rows:value['stages']=rows
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
