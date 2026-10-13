"""BUG1224/SSC272283: fixed no-child/no-DB actor proof then once pidfd TERM.

No business stop/start/reload, deployment or SQL mutation; old close stays unknown.
The retained dispatcher HEAD must not change until the original session ends.
"""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
from pg1446_current_cold_stage import W, P, SSH
from pg2248_newboot_owned_dispatch import post_payload
from pg2246_newboot_owned_sources import SOURCE, TOOLS
from pg1650_retained_no_db_readonly_proof import BODY as ACTOR
from pg1651_retained_no_db_readonly_proof_v2 import BODY as LOCKS, fd_relation
from pg782_owned_handoff import terminate
from pg1724_retained_host_gate import queued_gate
from pg1665_unused_pair_contract import fresh_parent as historical_fresh_parent

OPERATOR='4ad2701f80cb85b7f3e399b6f971666cf7736ca5'
PID=91637
TICKS=893074
SLOT='pg2271-current-no-db-proof-v2'
HANDOFF='pg2273-current-no-db-handoff-v2'


def qualify_signature_tuple(label,stem,release,source,bom):
    if (label,stem,release,source,bom)!=('PG2126','pg2126','0.1.0-PG2126',SOURCE,'62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c'):
        raise ValueError('one exact signed current generation required')
    return True


def metadata9(s):
    return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def fresh_parent_source():
    return inspect.getsource(historical_fresh_parent).replace('101','39').replace('99','37')


def prefix():
    raw=post_payload();raw=raw[:raw.index('bus=dbus.SystemBus(private=True);manager=')]
    raw=raw.replace("SAVE=BASE/'pg2242-newboot-fresh-day-full-seal-v1';require(not os.path.lexists(SAVE))", "SAVE=BASE/"+repr(SLOT)+";require(not os.path.lexists(SAVE))")
    actors=ACTOR[:ACTOR.index('def owned_lock(')]+inspect.getsource(fd_relation)+LOCKS
    actors=actors.replace('actor()', 'retained_actor()')
    for old,new in [('289328',str(PID)),('5627480',str(TICKS)),('289326','91635')]:actors=actors.replace(old,new)
    fixed=json.loads((W/'pg2247-frozen-v1.safe.json').read_bytes())['fileHashes']
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG2126/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG2126/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG2126/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG2126/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    args=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg2246NativeStop','stop']
    raw+='\nEXPECTED_ARGV='+repr(b'\0'.join(v.encode()for v in args)+b'\0')+'\nFILES='+repr(fixed)+'\n'+actors+'\n'+inspect.getsource(metadata9)+'\n'
    raw+=r'''
def original_tool():
 tool=BASE/'pg2246-newboot-owned-stop-tools-v1'
 for name,digest in FILES.items():
  p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 require(json.loads((tool/'payload-sha256.json').read_bytes())==FILES)
 require(not os.path.lexists(BASE/'pg2246-native-stop-v1'))
 require(hashlib.sha256((BASE/'pg2126-manifest.sig').read_bytes()).hexdigest()=='7ef03cf927c2f5b79b39a5d5187db439c753c57933bfff18b26386a02afaf449')
 require(hashlib.sha256((BASE/'pg1846-manifest.sig').read_bytes()).hexdigest()=='51987a404d2fac98d0f93b6ee606fed9bc40f2587b53b424b704df9204541ea5')
 value=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select count(*)from pg_stat_activity where datname='schubert_nk'and application_name='PG998-native-stop';select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"],4096)
 require(value.splitlines()==[b'0',b'0'])
def same_full():
 original_tool();current=capture();require(current==capture())
 original=(BASE/'pg2242-newboot-fresh-day-full-seal-v1/before.private.json').read_bytes()
 require(hashlib.sha256(original).hexdigest()=='0e88008b096c404d69d994e1fd45685cbfbdcbd75f11011dd72f07bd4d8ba984')
 require(json.loads(json.dumps(current))==json.loads(original))
 return current
def private(save,name,data):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''
    return raw


def payload(action):
    raw=prefix()
    if action=='handoff':
        actual=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
        if actual['actualExit']!=0:raise ValueError('actual independent proof required')
        raw=raw.replace(";require(not os.path.lexists(SAVE))",'')
        raw+='\nPROOF_SHA='+repr(actual['guest']['proofSha256'])+'\n'+inspect.getsource(terminate)+'\n'+fresh_parent_source()+'\n'
    raw+='\nbus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object("org.freedesktop.systemd1","/org/freedesktop/systemd1"),"org.freedesktop.systemd1.Manager");refs=[]\ntry:\n for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)\n'
    if action=='proof':
        body=r'''
 current=same_full();a=actor();require(a==actor());ls=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
 value={'actor':a,'locks':ls,'current':current,'toolHashes':FILES,'oldCloseUnknown':True}
 encoded=json.dumps(value,sort_keys=True).encode();SAVE.mkdir(mode=0o700);private(SAVE,'proof.private.json',encoded)
 result={'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'pid':91637,'ticks':893074,'ownedLocks':2,'noChild':True,'toolDbAdvisory0':True,'all24And32And187Unchanged':True,'fourBusinessOwnersUnchanged':True,'signals0':True,'oldCloseUnknown':True,'formalAccepted':False}
'''
    elif action=='handoff':
        body=r'''
 saved=(SAVE/'proof.private.json').read_bytes();require(hashlib.sha256(saved).hexdigest()==PROOF_SHA);expected=json.loads(saved)
 require(json.loads(json.dumps(same_full()))==expected['current'])
 save=BASE/'pg2273-current-no-db-handoff-v2';require(not os.path.lexists(save))
 def owner(pid,ticks):
  require((pid,ticks)==(91637,893074));a=actor();ls=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
  require(fresh_parent(expected['actor'],json.loads(json.dumps(a)),time.time_ns())and json.loads(json.dumps(ls))==expected['locks']);return a
 def reserve(pid,value):private(save,'91637.term-once.private',json.dumps({'pid':pid,'ticks':893074,'actor':value,'proofSha256':PROOF_SHA,'replayAllowed':False},sort_keys=True).encode())
 def wait(fd):
  import select
  poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
 owner(91637,893074);save.mkdir(mode=0o700)
 import signal
 terminate(91637,893074,owner,reserve,lambda p:os.pidfd_open(p,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+30
 while pathlib.Path('/proc/91637').exists():
  require(int(pathlib.Path('/proc/91637/stat').read_text().rpartition(')')[2].split()[19])==893074 and time.monotonic()<deadline);time.sleep(.05)
 for n in ['maintenance.lock','startup-admission.lock']:
  s=(ROOT/n).lstat();require(metadata9(s)==tuple(next(v['metadata']for v in expected['locks']if v['name']==n)))
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split();d=f[5].split(':')if len(f)>=8 else[]
   require(len(d)!=3 or(int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 require(json.loads(json.dumps(same_full()))==expected['current'])
 result={'actualExit':0,'ownedTermSignals':1,'ownedActorGone':True,'ownedFlocks0':True,'all24And32And187Unchanged':True,'fourBusinessOwnersUnchanged':True,'startsStopsReloadSqlWrites0':True,'oldCloseUnknown':True,'formalAccepted':False}
 private(save,'post.private.json',json.dumps(result,sort_keys=True).encode())
'''
    else:raise ValueError('fixed proof/handoff only')
    body=body.replace('actor()', 'retained_actor()')
    raw+=body+'\nfinally:\n for unit in reversed(refs):manager.UnrefUnit(unit)\n bus.close()\nprint(json.dumps(result))\n'
    from pyflakes.api import check
    if check(raw,'<fixed current no-DB recovery>'):raise ValueError('whole actual recovery namespace required')
    compile(raw,'<fixed current no-DB recovery>','exec');return raw


def host_owner(path):
    p=Path('/proc/43647');t=(p/'stat').read_text().rpartition(')')[2].split()
    if (int(t[19]),int(t[1]))!=(987264,4223)or hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()!='0965803c6e35d76825d25c0e9a871ebf46167f37f2608b61d89d6e59ffe8a34d':raise ValueError('fixed retained host owner required')
    s=path.stat();f=(p/'fd/4').stat()
    if(s.st_dev,s.st_ino)!=(f.st_dev,f.st_ino):raise ValueError('same host gate FD required')
    hits=[l.split()for l in Path('/proc/locks').read_text().splitlines()if len(l.split())>=8 and l.split()[5]==f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}']
    if len(hits)!=1 or hits[0][1:5]!=['FLOCK','ADVISORY','WRITE','43647']:raise ValueError('sole original host exclusion required')
    return True


def main():
    if sys.argv[1:]not in (['proof'],['handoff']):raise ValueError('one fixed action required')
    action=sys.argv[1];os.umask(0o077)
    if subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=OPERATOR:raise ValueError('original operator HEAD required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        published=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC272'not in published or 'SSC283'not in published:raise ValueError('published noDB and normal recovery authority required')
    out=W/(SLOT if action=='proof'else HANDOFF);out.mkdir(mode=0o700);raw=payload(action).encode();(out/'payload.private.py').write_bytes(raw)
    completed=False
    if action=='handoff':
        with queued_gate(P/'current-management-critical.lock',validate_owner=host_owner,require_completion=lambda:completed)as acquired:
            r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=180);completed=r.returncode==0
            if completed and not acquired.wait(30):raise ValueError('original host gate normal handoff required')
    else:
        host_owner(P/'current-management-critical.lock');r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stdout.private.log').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'operatorSource':OPERATOR,'productionSource':SOURCE,'oldCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
