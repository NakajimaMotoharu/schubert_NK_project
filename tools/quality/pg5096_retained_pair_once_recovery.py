"""SSC305 one exact child→parent TERM with fresh durable proof and queued host handoff."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH, W, P
from pg1724_retained_host_gate import queued_gate
from pg782_owned_handoff import terminate
from pg1665_unused_pair_contract import parent_after_ref
from pg1680_proc_reap_contract import confirmed_absence
import pg5098_failed_phase_full_proof as proof

SLOT = 'pg5096-retained-pair-once-recovery-v1'

BODY = r'''
saved=(base/'pg5098-failed-phase-full-proof-v1/proof.private.json').read_bytes()
require(hashlib.sha256(saved).hexdigest()==OLD_PROOF)
expected=json.loads(saved)
require(expected['productionSource']==SOURCE and expected['signals0']is True and expected['oldCloseUnknown']is True and expected['serverPeerAdvisory0']is True)
fresh=json.loads(encoded)
fresh_current_parent(expected['pair']['parent'],fresh['pair']['parent'],time.time_ns())
require(fresh['pair']['child']==expected['pair']['child'] and fresh['pair']['peer']==expected['pair']['peer'] and fresh['locks']==expected['locks'] and fresh['native']==expected['native'])
def private(name,raw):
 d=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  a=os.fstat(d);b=save.lstat();require((a.st_dev,a.st_ino,a.st_uid,a.st_mode,a.st_nlink)==(b.st_dev,b.st_ino,b.st_uid,b.st_mode,b.st_nlink))
  f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=d)
  with os.fdopen(f,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
  os.fsync(d)
 finally:os.close(d)
private('original-proof.private.json',saved)
private('fresh-complete.private',('freshReadOnlyProofComplete=true\nsignalsIssued=0\nproofSha256='+hashlib.sha256(encoded).hexdigest()+'\n').encode())
print(json.dumps({'stage':'FRESH_READONLY_COMPLETE','actualExit':0,'signalsIssued':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'oldCloseUnknown':True}),flush=True)
def unchanged():require(snapshot()==native and same_peer()==fresh['pair']['peer'])
def before_child(pid,ticks):
 require((pid,ticks)==(927536,31055311));unchanged();a=pair();require(a==fresh['pair']);return a
def reserve_child(pid,a):
 private(str(pid)+'.term-once.private',json.dumps({'pid':pid,'ticks':31055311,'actor':a['child'],'signal':'TERM','replayAllowed':False},sort_keys=True).encode())
 require(before_child(pid,31055311)==a)
def send(fd):signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
def reaped(pid,ticks):
 deadline=time.monotonic()+30;p=pathlib.Path('/proc')/str(pid)
 while p.exists():
  try:require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks)
  except OSError as error:
   if confirmed_absence(error,p.exists()):break
   raise
  require(time.monotonic()<deadline);time.sleep(.05)
 require(not p.exists())
terminate(927536,31055311,before_child,reserve_child,os.pidfd_open,send,wait,os.close)
reaped(927536,31055311)
CURRENT_ACTOR=remaining_actor
remaining=normalized(remaining_actor())
pipes={fresh['pair']['child']['fds'][n]['target']for n in ['0','1']}
require(parent_after_ref(fresh['pair']['parent'],remaining,pipes))
def child_bus_absent():
 connection=dbus.SystemBus(private=True)
 try:
  daemon=dbus.Interface(connection.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  names={str(n)for n in daemon.ListNames()};require(not set(fresh['pair']['child']['busNames'])&names)
 finally:connection.close()
child_bus_absent();unchanged()
def before_parent(pid,ticks):
 require((pid,ticks)==(927504,31055084));unchanged();child_bus_absent()
 a=normalized(remaining_actor());require(a==remaining and parent_after_ref(fresh['pair']['parent'],a,pipes))
 require(normalized([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']])==fresh['locks']);return a
def reserve_parent(pid,a):
 private(str(pid)+'.term-once.private',json.dumps({'pid':pid,'ticks':31055084,'actor':a,'signal':'TERM','replayAllowed':False},sort_keys=True).encode())
 require(before_parent(pid,31055084)==a)
terminate(927504,31055084,before_parent,reserve_parent,os.pidfd_open,send,wait,os.close)
reaped(927504,31055084)
def free_lock(name):
 s=(pathlib.Path('/run/schubert-nk')/name).lstat()
 require(list(metadata9(s))==next(v['metadata']for v in fresh['locks']if v['name']==name))
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':')
  require(len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 return True
owned_lock=free_lock
require(snapshot()==native==snapshot());child_bus_absent()
q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
private('post.private.json',json.dumps({'native':native,'oldCloseUnknown':True,'allOriginalValuesUnchanged':True,'allOldResources0':True,'ownedParentAndChildGone':True},sort_keys=True).encode())
private('complete.private',b'ownedParentAndChildGone=true\noldCloseUnknown=true\nallOldResources0=true\nfullIndependentPostPending=true\n')
'''


def prerequisite():
    path = W / proof.SLOT / 'manifest.safe.json'
    outer = json.loads(path.read_bytes())
    r = outer.get('result', {})
    if not (type(outer.get('actualExit')) is int and outer['actualExit'] == 0
            and outer.get('source') == proof.proof.role.SOURCE and r.get('productionSource') == outer['source']
            and type(r.get('actualExit')) is int and r['actualExit'] == 0
            and all(r.get(k) is True for k in ('allOriginalValuesUnchanged', 'serverPeerAdvisory0', 'normalNewRefScope', 'signals0', 'oldCloseUnknown'))
            and (r.get('parentPid'), r.get('parentTicks'), r.get('childPid'), r.get('childTicks')) == (927504,31055084,927536,31055311)
            and hashlib.sha256((path.parent / 'payload.private.py').read_bytes()).hexdigest() == outer['payloadSha256']):
        raise ValueError('actual same current independent complete proof first')
    return r['proofSha256']


def payload():
    old_proof = prerequisite()
    tree = ast.parse(proof.payload())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SLOT' for t in node.targets):
            node.value = ast.Constant(SLOT)
    actor = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'actor')
    remaining = ast.parse(ast.unparse(actor)).body[0]
    remaining.name = 'remaining_actor'
    raw = ast.unparse(remaining).replace('children == {927536}', 'not children').replace('len(fds) == 100', 'len(fds) <= 100')
    additional = (inspect.getsource(terminate) + '\n' + inspect.getsource(parent_after_ref)
                  + '\n' + inspect.getsource(confirmed_absence) + '\n' + raw + '\nCURRENT_ACTOR=actor\n')
    at = next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bus' for t in n.targets))
    tree.body[at:at] = ast.parse(additional).body
    lock = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owned_lock')
    class CurrentActor(ast.NodeTransformer):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'actor':
                node.func.id = 'CURRENT_ACTOR'
            return self.generic_visit(node)
    CurrentActor().visit(lock)
    scope = next(n for n in tree.body if isinstance(n,ast.Try) and n.finalbody and any(isinstance(v,ast.FunctionDef)and v.name=='snapshot'for v in n.body))
    scope.body += ast.parse(BODY).body
    tree.body = tree.body[:tree.body.index(scope)+1]
    tree.body += ast.parse("print(json.dumps({'actualExit':0,'ownedParentAndChildGone':True,'allOldResources0':True,'allOriginalValuesUnchanged':True,'normalNewRefScope':True,'oldCloseUnknown':True,'ownedTermSignals':2,'fullIndependentPostPending':True,'formalAccepted':False}),flush=True)").body
    raw = 'import errno,signal,select\nOLD_PROOF=' + repr(old_proof) + '\n' + ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    from pyflakes.api import check
    if check(raw, '<complete once-only current owned recovery>'):
        raise ValueError('full recovery namespace refused')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed owned recovery first')
    for path in ('documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',
                 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md',
                 'documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md'):
        if 'SSC305' not in subprocess.check_output(['git','show','origin/main:'+path],text=True):
            raise ValueError('published SSC305 first')
    prerequisite()
    proof.previous.fixed_failure()
    proof.previous.authenticate_host()
    raw = payload().encode()
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    (out / 'payload.private.py').write_bytes(raw)
    completed = False
    with queued_gate(P / 'current-management-critical.lock', validate_owner=proof.previous.host_owner, require_completion=lambda: completed) as acquired:
        r = subprocess.run(SSH + ['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=360)
        for name, blob in [('stdout.private.jsonl',r.stdout),('stderr.private.log',r.stderr)]:
            with(out/name).open('xb')as stream:
                stream.write(blob);stream.flush();os.fsync(stream.fileno())
        completed = r.returncode == 0
        if completed and not acquired.wait(30):
            raise ValueError('same kernel host gate not normally inherited')
        value = {'actualExit':r.returncode,'productionSource':proof.proof.role.SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),
                 'stages':[json.loads(l)for l in r.stdout.splitlines()if l.startswith(b'{')],
                 'oldCloseUnknown':True,'criticalGateNormallyInherited':completed,'formalAccepted':False,
                 'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        with(out/'manifest.safe.json').open('x')as stream:
            json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
