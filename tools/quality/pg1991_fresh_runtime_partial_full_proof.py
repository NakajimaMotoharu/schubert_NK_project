"""Readonly full partial runtime/current101/4FD peer/OFD proof, no reload or signal."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1988_fresh_resume_retained_diagnosis import owner
from pg1963_reload_ref_scoped_full_post import payload as closed_post
from pg1885_publication_current_fd_proof import payload as old_pair
from pg1664_current_unused_pair_readonly_proof import PAIR
from pg1877_warning_publication_sources import once

SLOT='pg1991-fresh-runtime-partial-full-proof-v1'


class Current(ast.NodeTransformer):
    def visit_Constant(self,node):
        values={490998:498727,9782388:10276205,490996:498725,491029:498758,9782567:10276392,491027:498756,291213:498727,5962776:10276205,291242:498758,5962938:10276392,291240:498756}
        v=node.value
        if type(v)is int:v=values.get(v,v)
        elif type(v)is str:
            for a,b in values.items():v=v.replace(str(a),str(b))
            v=v.replace('pg1662-completed-unused-placement-v3','pg1984-fresh-resume-preparation-v1')
        elif type(v)is bytes:
            v=v.replace(b'pg1659-completed-unused-tools-v3/pg1640_native_refs.py',b'pg1980-fresh-resume-tools-v1/pg1980_native_refs.py').replace(b'\x00place\x00',b'\x00prepare-resume\x00').replace(b'291240',b'498756')
        return ast.copy_location(ast.Constant(v),node)


def helpers():
    tree=ast.parse(old_pair());names={'actor','same_peer','pair','fd_relation','owned_lock'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='P'for t in n.targets)]
    nodes.append(next(n for n in ast.parse(PAIR).body if isinstance(n,ast.FunctionDef)and n.name=='refs_actor'))
    if len(nodes)!=7:raise ValueError('whole actual101/4FD helper closure required')
    tree=Current().visit(ast.Module(body=nodes,type_ignores=[]));ast.fix_missing_locations(tree)
    return ast.unparse(tree)+'\n'


PARTIAL=r'''
partial_root=base/'pg1984-fresh-resume-preparation-v1'
require({p.name for p in partial_root.iterdir()}=={'before.private.json','refs-prepare.private.log'})
require(hashlib.sha256((partial_root/'before.private.json').read_bytes()).hexdigest()=='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15')
require(hashlib.sha256((partial_root/'refs-prepare.private.log').read_bytes()).hexdigest()=='20e863574277376ab37603b391e8633f8199c983a2c51a3447adb1ec03e5c9eb')
directory='/run/systemd/system/schubert-nk-morning-controller.service.d';target=directory+'/zz-pg1980-once-resume.conf'
current_runtime=tree(pathlib.Path('/run/systemd/system'));old_runtime=json.loads((partial_root/'before.private.json').read_bytes())['runtime']
require(set(current_runtime)==set(old_runtime)|{target}and current_runtime['/run/systemd/system']==old_runtime['/run/systemd/system'])
require(current_runtime[directory]['metadata']==[28,5514,0,0,stat.S_IFDIR|0o755,2,60,1791850609774000000,1791850609774000000])
require(current_runtime[target]['metadata']==[28,15250,0,0,stat.S_IFREG|0o644,1,644,1791850609774873609,1791850609774873609])
require(current_runtime[target]['sha256']=='78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec')
require(not os.listxattr(directory)and not os.listxattr(target))
native=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
require(hashlib.sha256(native).hexdigest()=='9a6d94310d1f18e1a0b09882503948e43f1a76386962c7ba8a73a166091201b7')
argv=[l[len(b'ExecStart='):]for l in native.splitlines()if l.startswith(b'ExecStart=')and l!=b'ExecStart='];require(len(argv)==1)
literal=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv[0]+b' --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e\n'
require(pathlib.Path(target).read_bytes()==literal)
after['runtime']=current_runtime
'''


def payload():
    raw=closed_post();raw=raw[:raw.index("save=base/'pg1963-reload-ref-scoped-full-post-v1'")]
    raw=once(raw,"lines[-2:] == [b'0', b'0']","lines[-2:] == [b'1', b'1']")
    start=raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):");end=raw.index("        require(tree(pathlib.Path('/run/systemd/system'))",start)
    raw=raw[:start]+"        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    raw=once(raw,'\nbus = dbus.SystemBus(private=True)\n','\n'+helpers()+'\nbus = dbus.SystemBus(private=True)\n')
    marker='    def snapshot():\n';raw=once(raw,marker,'\n'.join('    '+line for line in PARTIAL.splitlines())+'\n\n'+marker)
    cp='/var/lib/pgpt-s1-preservation/pg1980-fresh-resume-tools-v1:/opt/schubert-nk/releases/0.1.0-PG1846/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1846/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1846/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1846/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1980FreshResumePreparation','prepare-resume']
    frozen=json.loads((W/'pg1982-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('sameSource actual sixABI required')
    raw='EXPECTED_ARGV='+repr(b'\0'.join(x.encode()for x in argv)+b'\0')+'\nFILES='+repr(frozen['fileHashes'])+'\n'+raw+TAIL.replace('__SLOT__',SLOT)
    from pyflakes.api import check
    if check(raw,'<actual partial freshresume full proof>'):raise ValueError('all proof globals required')
    compile(raw,'<current partial runtime101/4FD>','exec');return raw


TAIL=r'''
tool=base/'pg1980-fresh-resume-tools-v1'
for name,digest in FILES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'__SLOT__';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'current':after,'native':native,'toolHashes':FILES,'partialRuntimeFileVerified':True,'reloadNotReserved':True,'allOriginalValuesPreserved':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':498727,'childPid':498758,'backendPid':498756,'parentFdCount':101,'childFdCount':4,'samePeer':True,'ownedLocks':2,'allOriginalValuesPreserved':True,'partialRuntimeVerifiedNoReload':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120);(out/'stderr.private.log').write_bytes(r.stderr)
    if held!=owner():raise ValueError('same retained actual owner required')
    value={'actualExit':r.returncode,'hostRetainedOwner':held,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
