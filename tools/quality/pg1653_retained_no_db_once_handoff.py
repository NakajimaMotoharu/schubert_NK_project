"""SSC272 exact current noDB/noChild Java pidfd TERM once; full original post.

Requires actual independent1651 proof and published SSC272. Keeps fresh ten
metadata Ref scopes through before, single TERM, finite reap and full post.
Old transport143/closeUNKNOWN remain unknown, never normal application close.
"""
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import pg1651_retained_no_db_readonly_proof_v2 as proof
from pg782_owned_handoff import terminate

SLOT = 'pg1653-retained-no-db-handoff-v1'
PROOF_SHA = '6297a9d8efb937b67a480f67051efa5907207ed14c257df2b36605ab3a4839bb'

BODY = r'''
import signal,select,time
oldproof=base/'pg1651-retained-no-db-proof-v2/proof.private.json';saved=oldproof.read_bytes();require(hashlib.sha256(saved).hexdigest()==PROOF_SHA);expected=json.loads(saved)
tool=base/'pg1645-completed-unused-tools-v2'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tool/'payload-sha256.json').read_bytes())==TOOL_HASHES)
require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
save=base/'pg1653-retained-no-db-handoff-v1';require(not os.path.lexists(save))
def private(name,raw):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def owner(pid,ticks):
 require(pid==289328 and ticks==5627480)
 a=actor();locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
 require(json.loads(json.dumps(a))==expected['actor']and json.loads(json.dumps(locks))==expected['locks'])
 return a
def reserve(pid,before):
 require(pid==289328)
 private('289328.term-once.private',json.dumps({'pid':pid,'ticks':5627480,'actor':before,'proofSha256':PROOF_SHA,'signal':'TERM','replayAllowed':False},sort_keys=True).encode())
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
def free_lock(name):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 require(metadata9(s)==tuple(next(v['metadata']for v in expected['locks']if v['name']==name)))
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':');require(len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 require(not pathlib.Path('/proc/289328').exists())
 return True
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 validate_schema(after);native=snapshot();require(native==snapshot()and json.loads(json.dumps(native))==expected['native'])
 catalog=independent_native_catalog();require(len(catalog['selected'])==8 and len(catalog['excludedHistorical'])==6)
 owner(289328,5627480)
 save.mkdir(mode=0o700);private('proof-before.private.json',saved)
 terminate(289328,5627480,owner,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+30
 while pathlib.Path('/proc/289328').exists():
  require(int(pathlib.Path('/proc/289328/stat').read_text().rpartition(')')[2].split()[19])==5627480 and time.monotonic()<deadline);time.sleep(.05)
 CURRENT_LOCK_CHECK=free_lock
 require(snapshot()==native==snapshot())
 require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
 private('post.private.json',json.dumps({'originalAfterSha256':'9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37','native':native,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'clientAdvisoryFlock0':True,'ownedActorGone':True,'candidateNotPlaced':True,'oldCloseUnknown':True},sort_keys=True).encode())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
private('complete.private',b'ownedJavaGone=true\nallOriginalValuesUnchanged=true\nallOldResources0=true\nnewRefScopeNormal=true\noldCloseUnknown=true\n')
print(json.dumps({'actualExit':0,'pid':289328,'ticks':5627480,'ownedTermSignals':1,'ownedActorGone':True,'allOriginalValuesUnchanged':True,'allOldResources0':True,'normalNewRefScope':True,'candidateNotPlaced':True,'oldCloseUnknown':True,'serviceStartsStopsReloadsSqlWrites0':True,'formalAccepted':False}))
'''


def payload():
    raw = proof.payload()
    tree = ast.parse(raw)
    current = next(n for n in tree.body if isinstance(n, ast.Try) and any(isinstance(v, ast.FunctionDef) and v.name == 'snapshot' for v in n.body))
    snapshot = next(n for n in current.body if isinstance(n, ast.FunctionDef) and n.name == 'snapshot')
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ['validate_schema', 'independent_native_catalog']]
    definitions += [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'KEYS' for t in n.targets)]
    if len(definitions) != 3:
        raise ValueError('actual complete current native/schema definitions required')
    prefix = raw[:raw.index('bus=dbus.SystemBus(private=True);manager=')]
    full_snapshot = ast.unparse(snapshot).replace('owned_lock(name)', 'CURRENT_LOCK_CHECK(name)')
    result = 'PROOF_SHA=' + repr(PROOF_SHA) + '\n' + prefix + '\nCURRENT_LOCK_CHECK=owned_lock\n' + full_snapshot + '\n' + ast.unparse(ast.Module(body=definitions, type_ignores=[])) + '\n' + inspect.getsource(terminate) + '\n' + BODY
    compile(result, '<SSC272 fixed noDB once TERM full-scope handoff>', 'exec')
    return result


def main():
    from pg1446_current_cold_stage import W, SSH
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    paths = ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md', 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md', 'documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md', 'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']
    for path in paths:
        published = subprocess.check_output(['git', 'show', 'origin/main:' + path], text=True)
        local = (Path(__file__).resolve().parents[2] / path).read_text()
        if design_scope(published, path) != design_scope(local, path):
            raise ValueError('published SSC272 exact scope equality required')
    actual = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if actual['actualExit'] != 0 or actual['guest']['proofSha256'] != PROOF_SHA:
        raise ValueError('actual fixed independent complete proof required')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-'], input=raw, capture_output=True, timeout=90)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'oldCloseUnknown': True, 'formalAccepted': False}
    if r.returncode == 0:
        value['guest'] = json.loads(r.stdout)
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(value))
    return r.returncode


def design_scope(text, path):
    marker = '## SSC-272（' if '/914_' in path else 'SSC272（' if '/354_' in path else 'SSC272：'
    if text.count(marker) != 1:
        raise ValueError('one published current recovery authority required')
    tail = text[text.index(marker):]
    boundary = '\n## SSC-' if '/914_' in path else '\n\n'
    return tail.split(boundary, 1)[0].strip()


if __name__ == '__main__':
    raise SystemExit(main())
