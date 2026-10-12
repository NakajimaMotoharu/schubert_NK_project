"""Current partial publication: independent canonical state +102/18FD/soleDB/OFD."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1898_partial_publication_diagnosis import owner
from pg1899_partial_publication_snapshot import payload as partial
from pg1885_publication_current_fd_proof import payload as old_pair
from pg1877_warning_publication_sources import once

SLOT='pg1902-partial-publication-pair-proof-v1'
TOOLS='pg1891-warning-publication-tools-v1'
SAVE='pg1895-warning-publication-v1'
EXTRA={'3':'/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0','5':'/etc/systemd/system','6':'/var/lib/pgpt-s1-preservation/'+SAVE,'7':'/var/lib/pgpt-s1-preservation/'+SAVE+'/morning-unit-old.private','8':'/run/schubert-nk/startup','9':'/etc/schubert-nk/release-approval','10':'/opt/schubert-nk','11':'/var/lib/pgpt-s1-preservation/'+SAVE,'14':'/var/lib/pgpt-s1-preservation/'+SAVE+'/current-link.private','15':'/run/schubert-nk/startup/epoch.current','16':'/etc/schubert-nk/release-approval/current','17':'/opt/schubert-nk/current'}


class Current(ast.NodeTransformer):
    def visit_Constant(self,node):
        values={490998:493115,9782388:9883172,490996:493113,491029:493146,9782567:9883367,491027:493144}
        v=node.value
        if type(v)is int:v=values.get(v,v)
        elif type(v)is str:
            for a,b in values.items():v=v.replace(str(a),str(b))
            v=v.replace('pg1881','pg1895').replace('pg1877','pg1891')
        elif type(v)is bytes:
            v=v.replace(b'pg1877',b'pg1891').replace(b'491027',b'493144')
        return ast.copy_location(ast.Constant(v),node)


def helpers():
    tree=ast.parse(old_pair());names={'actor','refs_actor','same_peer','pair','fd_relation','owned_lock'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='P'for t in n.targets)]
    if len(nodes)!=7:raise ValueError('exact current actor/helper closure required')
    tree=Current().visit(ast.Module(body=nodes,type_ignores=[]));ast.fix_missing_locations(tree);raw=ast.unparse(tree)+'\n'
    raw=once(raw,'range(15)','range(18)')
    raw=once(raw,"len(a['fds']) == 101","len(a['fds']) == 102")
    marker="    bus = dbus.SystemBus(private=True)"
    # Prove the two old unlinked regular descriptors against held original
    # metadata+SHA through the independent publication oracle, never new paths.
    extra="""    for number,path in [('12','/run/schubert-nk/startup/epoch.current'),('13','/etc/schubert-nk/release-approval/current')]:
        require(fds[number]['target']==path+' (deleted)')
        file=p/'fd'/number;fd=os.open(file,os.O_RDONLY|os.O_CLOEXEC)
        try:
            s=os.fstat(fd);raw=os.pread(fd,s.st_size+1,0)
            require(len(raw)==s.st_size and metadata9(s)==metadata9(file.stat()))
            observed={'metadata':list(metadata9(s)),'sha256':hashlib.sha256(raw).hexdigest(),'target':None,'acl':list(os.listxattr(fd))}
            root=S if number=='12'else A
            oracle['verify_retained'](path,public_first[root][path],observed,'old-linked-private',public_last,lower,upper)
        finally:os.close(fd)
"""
    raw=once(raw,marker,extra+marker)
    return raw


def payload():
    raw=partial();raw=raw[:raw.index("save=base/'pg1896-complete-publication-full-post-v1'")]
    raw=once(raw,"lines[-2:] == [b'0', b'0']","lines[-2:] == [b'1', b'1']")
    start=raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):")
    end=raw.index("        require(tree(pathlib.Path('/run/systemd/system'))",start)
    raw=raw[:start]+"        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    raw=once(raw,'\nbus = dbus.SystemBus(private=True)\n','\n'+helpers()+'\nbus = dbus.SystemBus(private=True)\n')
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1891OrdinaryPublication','activate']
    raw='EXPECTED_ARGV='+repr(b'\0'.join(v.encode()for v in argv)+b'\0')+'\nEXTRA='+repr(EXTRA)+'\n'+raw
    raw+=TAIL.replace('__SLOT__',SLOT)
    from pyflakes.api import check
    if check(raw,'<current independent partial full pair>'):raise ValueError('all actual partial globals required')
    compile(raw,'<current partial full proof>','exec');return raw


TAIL=r'''
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'__SLOT__';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'current':after,'native':native,'toolHashes':PUBLICATION_FILES,'partialPublicationQualified':True,'all24And32And187UnchangedExceptApprovedPublicationUnit':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'normalNewRefScope':True,'reloadNotReserved':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':493115,'childPid':493146,'backendPid':493144,'parentFdCount':102,'childFdCount':18,'samePeer':True,'ownedLocks':2,'allOriginalValuesPreserved':True,'partialCurrentUnitQualified':True,'reloadNotReserved':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('same retained current partial owner required')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
