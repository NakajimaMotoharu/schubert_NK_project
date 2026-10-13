"""Exact declaration-CLOSED effect and eleven-FD owned peer after known reload return."""
import ast
import inspect
import json
import types
from pyflakes.api import check
import pg2322_current_partial_runtime_pair_proof as prior
from pg1446_current_cold_stage import W
from pg870_ordinary_before import parser_source

SOURCE=prior.SOURCE
SLOT='pg2338-current-reloaded-pair-proof-v1'


def bound(raw):
    for old,new in [('98485','101019'),('1656317','1808679'),('98483','101017'),('98516','101050'),('1656547','1808864'),('98514','101048'),('pg2316-current-cold-resume-tools-v1','pg2330-current-existing-runtime-finish-tools-v1'),('pg2316_native_refs.py','pg2330_native_refs.py'),('Pg2316FreshResumePreparation','Pg2330ExistingRuntimeFinish')]:raw=raw.replace(old,new)
    raw=raw.replace('prepare-resume','finish-runtime')
    return raw


def declared_configuration(old,new,parse):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):return False
    parent='schubert-nk-morning-controller.service'
    for unit,left in old.items():
        right=new[unit]
        if type(left)is not dict or type(right)is not dict or len(left)!=32 or set(left)!=set(right):return False
        if any(type(v)is not str for v in [*left.values(),*right.values()]):return False
        if any(left[k]!=right[k]for k in left if k not in ({'ExecStart','DropInPaths'}if unit==parent else{'ExecStart'})):return False
        a=parse(left['ExecStart']);b=parse(right['ExecStart'])
        if a is None or b is None or len(a)!=8 or len(b)!=8:return False
        expected=(a[0],a[1]+(' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9'if unit==parent else''),a[2])
        if b[:3]!=expected or tuple(b[3:])!=('n/a','n/a','0','(null)','0/0'):return False
        if unit==parent and right['DropInPaths']!=left['DropInPaths']+' /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf':return False
    return parent in old


def body():
    raw=bound(prior.body())
    # Child also retains the existing runtime's full ancestor chain/file and private SAVE.
    old="require(set(fds) == {'0', '1', '2', '3'}"
    if raw.count(old)!=1:raise ValueError('one exact child FD-set boundary required')
    raw=raw.replace(old,"require(set(fds) == {str(i)for i in range(11)}")
    raw=raw.replace('pg2320-current-cold-resume-preparation-v1/refs-prepare.private.log','pg2334-current-existing-runtime-finish-v1/refs-prepare.private.log')
    marker='    bus = dbus.SystemBus(private=True)'
    point=raw.index(marker,raw.index('def refs_actor():'))
    child="""    fixed={'4':'/','5':'/run','6':'/run/systemd','7':'/run/systemd/system','8':'/run/systemd/system/schubert-nk-morning-controller.service.d','9':'/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf','10':'/var/lib/pgpt-s1-preservation/pg2334-current-existing-runtime-finish-v1'}
    for n,target in fixed.items():
        require(fds[n]['target']==target and fds[n]['metadata']==metadata9(pathlib.Path(target).lstat())and not os.listxattr(target))
        require(fds[n]['metadata'][2:4]==[0,0])
        info=dict(line.split(':',1)for line in(p/'fdinfo'/n).read_text().splitlines()if ':'in line);flags=int(info['flags'].strip(),8)
        require(flags&os.O_ACCMODE==os.O_RDONLY and flags&os.O_NOFOLLOW and flags&os.O_CLOEXEC)
        require(stat.S_ISREG(fds[n]['metadata'][4])if n=='9'else stat.S_ISDIR(fds[n]['metadata'][4])and flags&os.O_DIRECTORY)
    require(fds['9']['metadata']==[28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696])
"""
    raw=raw[:point]+child+raw[point:]
    marker='\nbus = dbus.SystemBus(private=True)\n'
    raw=raw.replace(marker,'\ncurrent_view={}\n'+marker)
    old="            require(complete_configuration(command(['systemctl', 'show', u, '--property=' + ','.join(sorted(FIELDS))]).decode(), u) == after['configuration'][u])"
    if raw.count(old)!=1:raise ValueError('one normal declared-config comparison required')
    raw=raw.replace(old,"            current_view[u]=complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u)")
    point=raw.index("        for k, p in [('startup', '/run/schubert-nk/startup')")
    raw=raw[:point]+"        require(declared_configuration(after['configuration'],current_view,exec_record))\n"+raw[point:]
    return parser_source()+'\n'+inspect.getsource(declared_configuration)+'\n'+raw


TAIL=r'''
failed=base/'pg2334-current-existing-runtime-finish-v1'
require({p.name for p in failed.iterdir()}=={'before.private.json','daemon-reload-reserved.private','refs-prepare.private.log'})
require(hashlib.sha256((failed/'before.private.json').read_bytes()).hexdigest()=='cabdde419263ccf365c32c773df9e028f1e7fb4b69f8ed51b21fd5073755d79e')
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='e34d11d01de4317f7ab9f72895eae56ceffa5f5aee9c6419d1eba7196edd08b1')
require((failed/'daemon-reload-reserved.private').read_bytes()==b'one normal existing-runtime daemon-reload; no retry\n')
tool=base/'pg2330-current-existing-runtime-finish-tools-v1'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
refs_source=(tool/'pg2330_native_refs.py').read_text();require('require(not placed);pinned_runtime.reload();placed=True\n            check_data(capture_data(True))'in refs_source)
helper=(tool/'pg2330_existing_runtime.py').read_text();require("require(r.returncode==0 and r.stdout==r.stderr==b'');self.reloaded=True;self.verify()"in helper)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'pg2338-current-reloaded-pair-proof-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'native':native,'toolHashes':TOOL_HASHES,'partialRuntimeFileVerified':True,'reloadKnownReturnedBeforePostGuard':True,'all24And187Unchanged':True,'configurationDeclaredDeltaAndClosedOnly':True,'state18Unchanged':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':101019,'childPid':101050,'backendPid':101048,'parentFdCount':101,'childFdCount':11,'samePeer':True,'ownedLocks':2,'all24And187Unchanged':True,'configurationDeclaredDeltaAndClosedOnly':True,'state18Unchanged':True,'reloadKnownReturnedBeforePostGuard':True,'signals0':True,'formalAccepted':False}))
'''


def payload():
    frozen=json.loads((W/'pg2331-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('actual current existing-file full ABI required')
    raw='TOOL_HASHES='+repr(frozen['fileHashes'])+'\n'+body()+TAIL
    if check(raw,'<whole current reloaded pair>'):raise ValueError('all reloaded pair globals required')
    compile(raw,'<current reloaded same peer>','exec');return raw


def main():
    fn=types.FunctionType(prior.prior.main.__code__,{**prior.prior.__dict__,'SLOT':SLOT,'payload':payload},'current_reloaded_pair_proof')
    return fn()


if __name__=='__main__':raise SystemExit(main())
