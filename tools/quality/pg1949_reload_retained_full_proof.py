"""Current post-reload retained pair: exact FD/OFD/peer and independent full originals."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1943_reload_retained_diagnosis import owner
from pg1899_partial_publication_snapshot import payload as partial
from pg1885_publication_current_fd_proof import payload as old_pair
from pg1948_reload_closed_configuration import reload_configuration_same,RESET_UNITS,CLOSED
from pg1877_warning_publication_sources import once

SLOT='pg1949-reload-retained-full-proof-v1'
TOOLS='pg1925-partial-reload-tools-v1'
SAVE='pg1929-partial-reload-v1'
EXTRA={'3':'/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0','5':'/etc/systemd/system','6':'/var/lib/pgpt-s1-preservation/pg1895-warning-publication-v1','7':'/var/lib/pgpt-s1-preservation/'+SAVE,'8':'/var/lib/pgpt-s1-preservation/pg1895-warning-publication-v1/morning-unit-old.private'}


class Current(ast.NodeTransformer):
    def visit_Constant(self,node):
        values={490998:495729,9782388:10124906,490996:495727,491029:495760,9782567:10125088,491027:495758}
        v=node.value
        if type(v)is int:v=values.get(v,v)
        elif type(v)is str:
            for a,b in values.items():v=v.replace(str(a),str(b))
            v=v.replace('pg1881-warning-publication-v1',SAVE).replace('pg1877-warning-publication-tools-v1/pg1877_native_refs.py',TOOLS+'/pg1925_native_refs.py')
        elif type(v)is bytes:
            v=v.replace(b'pg1877-warning-publication-tools-v1/pg1877_native_refs.py',(TOOLS+'/pg1925_native_refs.py').encode()).replace(b'\x00activate\x00',b'\x00finish-reload\x00').replace(b'491027',b'495758')
        return ast.copy_location(ast.Constant(v),node)


def helpers():
    tree=ast.parse(old_pair());names={'actor','refs_actor','same_peer','pair','fd_relation','owned_lock'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='P'for t in n.targets)]
    if len(nodes)!=7:raise ValueError('exact actual pair helper closure required')
    tree=Current().visit(ast.Module(body=nodes,type_ignores=[]));ast.fix_missing_locations(tree)
    return once(ast.unparse(tree)+'\n','range(15)','range(9)')


def snapshot_source():
    raw=partial();raw=raw[:raw.index("save=base/'pg1896-complete-publication-full-post-v1'")]
    raw=once(raw,"[b'SuccessExitStatus=',b'Type=oneshot']","[b'SuccessExitStatus=10',b'Type=oneshot']")
    marker='\nbus = dbus.SystemBus(private=True)\n'
    code='RESET_UNITS='+repr(RESET_UNITS)+'\nCLOSED='+repr(CLOSED)+'\n'+inspect.getsource(reload_configuration_same)+r'''
parser_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
parser_node=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
parser_namespace={'re':re};exec(compile(ast.Module(body=[parser_node],type_ignores=[]),'<fixed actual declaration parser>','exec'),parser_namespace)
exec_record=parser_namespace['exec_record']
original_configuration=after['configuration'];new_configuration={}
for unit,expected in original_configuration.items():
 actual=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit)
 require(reload_configuration_same(unit,expected,actual,exec_record))
 new_configuration[unit]=actual
after['configuration']=new_configuration
'''
    # Existing independent snapshot already defines its sealed exec_record parser.
    return once(raw,marker,'\n'+code+marker)


def payload():
    raw=snapshot_source()
    raw=once(raw,"lines[-2:] == [b'0', b'0']","lines[-2:] == [b'1', b'1']")
    start=raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):");end=raw.index("        require(tree(pathlib.Path('/run/systemd/system'))",start)
    raw=raw[:start]+"        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    raw=once(raw,'\nbus = dbus.SystemBus(private=True)\n','\n'+helpers()+'\nbus = dbus.SystemBus(private=True)\n')
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG1846/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1846/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1846/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1846/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1925PartialReload','finish-reload']
    fixed=json.loads((W/'pg1926-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('actual full frozen namespace required')
    raw='EXPECTED_ARGV='+repr(b'\0'.join(v.encode()for v in argv)+b'\0')+'\nEXTRA='+repr(EXTRA)+'\nRELOAD_FILES='+repr(fixed['fileHashes'])+'\n'+raw+TAIL.replace('__SLOT__',SLOT)
    from pyflakes.api import check
    if check(raw,'<actual reload retained full proof>'):raise ValueError('all proof globals required')
    compile(raw,'<current owned reload proof>','exec');return raw


TAIL=r'''
tool=base/'pg1925-partial-reload-tools-v1'
for name,digest in RELOAD_FILES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
failure=base/'pg1929-partial-reload-v1';require({p.name for p in failure.iterdir()}=={'before.private.json','refs-prepare.private.log','daemon-reload-reserved.private'})
require(hashlib.sha256((failure/'before.private.json').read_bytes()).hexdigest()=='16ec6b95e9de832eec5eaf90849a64e6a54c94600b3b6f3f7a09527b17515ad4')
require(hashlib.sha256((failure/'refs-prepare.private.log').read_bytes()).hexdigest()=='c137fa585c42d0c3c88adee350027304f4c821aa4711a2c7813a2ffa71ff5e27')
require((failure/'daemon-reload-reserved.private').read_bytes()==b'one normal daemon-reload; no retry\n')
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'__SLOT__';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'current':after,'native':native,'toolHashes':RELOAD_FILES,'reloadActuallyApplied':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'allOriginalValuesPreserved':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':495729,'childPid':495760,'backendPid':495758,'parentFdCount':101,'childFdCount':9,'samePeer':True,'ownedLocks':2,'allOriginalValuesPreserved':True,'reloadActuallyApplied':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120);(out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('same retained actual host owner required')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
