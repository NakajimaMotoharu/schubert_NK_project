"""QA047 current cold/stopped cohort proof; all15 Ref FDs are role-bound."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1883_publication_retained_diagnosis import owner
import pg1849_warning_completed_current_before as engine
from pg1650_retained_no_db_readonly_proof import BODY as ACTOR
from pg1651_retained_no_db_readonly_proof_v2 import BODY as LOCKS,fd_relation
from pg1664_current_unused_pair_readonly_proof import PAIR
from pg1877_warning_publication_sources import once,TOOLS,SAVE,BEFORE

SLOT='pg1884-publication-current-pair-proof-v1'
EXTRA={'3':'/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0','5':'/etc/systemd/system','6':'/var/lib/pgpt-s1-preservation/'+SAVE,'7':'/etc/systemd/system/schubert-nk-morning-controller.service','8':'/run/schubert-nk/startup','9':'/etc/schubert-nk/release-approval','10':'/opt/schubert-nk','11':'/var/lib/pgpt-s1-preservation/'+SAVE,'12':'/run/schubert-nk/startup/epoch.current','13':'/etc/schubert-nk/release-approval/current','14':'/opt/schubert-nk/current'}


class Typed(ast.NodeTransformer):
    def visit_Constant(self,node):
        numbers={289328:490998,5627480:9782388,289326:490996,291213:490998,5962776:9782388,291242:491029,5962938:9782567,291240:491027}
        value=node.value
        if type(value)is int:value=numbers.get(value,value)
        elif type(value)is str:
            for a,b in numbers.items():value=value.replace(str(a),str(b))
            value=value.replace('pg1659-completed-unused-tools-v3/pg1640_native_refs.py',TOOLS+'/pg1877_native_refs.py').replace('pg1662-completed-unused-placement-v3',SAVE)
        elif type(value)is bytes:
            value=value.replace(b'pg1659-completed-unused-tools-v3/pg1640_native_refs.py',(TOOLS+'/pg1877_native_refs.py').encode()).replace(b'\x00place\x00',b'\x00activate\x00').replace(b'291240',b'491027')
        return ast.copy_location(ast.Constant(value),node)


def helpers():
    actor=ACTOR[:ACTOR.index('def owned_lock(')]
    actor=once(actor,'require(not children)','require(children=={491029})')
    pairs=PAIR
    pairs=once(pairs,"require(set(fds)=={'0','1','2','3'} and fds['0']['target'].startswith('pipe:[')and fds['1']['target'].startswith('pipe:[')and fds['3']['target'].startswith('socket:['))","require(set(fds)=={str(i)for i in range(15)}and fds['0']['target'].startswith('pipe:[')and fds['1']['target'].startswith('pipe:[')and fds['4']['target'].startswith('socket:['))\n for number,path in EXTRA.items():\n  require(fds[number]['target']==path and fds[number]['metadata']==metadata9(pathlib.Path(path).lstat()))")
    raw=actor+'\n'+inspect.getsource(fd_relation)+'\n'+LOCKS+'\n'+pairs
    tree=Typed().visit(ast.parse(raw));ast.fix_missing_locations(tree)
    return ast.unparse(tree)+'\n'


def payload():
    raw=engine.payload(json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes()))
    raw=raw[:raw.index("save=base/'"+engine.SLOT+"'")]
    raw=once(raw,"lines[-2:] == [b'0', b'0']","lines[-2:] == [b'1', b'1']")
    begin=raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):")
    end=raw.index("        require(tree(pathlib.Path('/run/systemd/system'))",begin)
    raw=raw[:begin]+"        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    raw=once(raw,'\nbus = dbus.SystemBus(private=True)\n','\n'+helpers()+'\nbus = dbus.SystemBus(private=True)\n')
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1877OrdinaryPublication','activate']
    frozen=json.loads((W/'pg1879-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('actual frozen full tool required')
    raw='EXPECTED_ARGV='+repr(b'\0'.join(v.encode()for v in argv)+b'\0')+'\nEXTRA='+repr(EXTRA)+'\nTOOL_HASHES='+repr(frozen['fileHashes'])+'\n'+raw
    raw+=TAIL.replace('__SAVE__',SAVE).replace('__TOOLS__',TOOLS).replace('__SLOT__',SLOT).replace('__BEFORE__',BEFORE)
    from pyflakes.api import check
    if check(raw,'<current full stopped publication pair>'):raise ValueError('actual all helper globals required')
    compile(raw,'<current publication pair full proof>','exec');return raw


TAIL=r'''
tool=base/'__TOOLS__'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tool/'payload-sha256.json').read_bytes())==TOOL_HASHES)
failure=base/'__SAVE__';require({p.name for p in failure.iterdir()}=={'refs-prepare.private.log'})
log=(failure/'refs-prepare.private.log').read_bytes();require(log==b'PG1877_READBACK_UNKNOWN type=AttributeError\nPG1877_FRAME method=<module> line=227\nPG1877_FRAME method=main line=184\nPG1877_FRAME method=capture_data line=94\n')
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'__SLOT__';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'originalAfterSha256':'__BEFORE__','native':native,'toolHashes':TOOL_HASHES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'normalNewRefScope':True,'currentPublicationNotStarted':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':490998,'childPid':491029,'backendPid':491027,'parentFdCount':101,'childFdCount':15,'samePeer':True,'ownedLocks':2,'allOriginalValuesUnchanged':True,'currentPublicationNotStarted':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('same retained host owner required')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
