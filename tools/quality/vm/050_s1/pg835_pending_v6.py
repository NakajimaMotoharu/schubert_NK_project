"""New-only actual module-scope source assembly after965; preserve partial v5."""
import ast
from pathlib import Path
import sys
import pg835_pending_sources as profile
import pg835_pending_v5 as previous
from pg835_pending_v4 import source as transport_source
R=Path(__file__).resolve().parent

def bind(raw):return previous.bind(raw).replace('-v5','-v6')
def java(raw):return previous.java(raw).replace('-v5','-v6')
def source(mode):
    raw=transport_source(mode).replace('-v4','-v6')
    if mode=='compile':
        marker="if __name__=='__main__':main()"
        assert raw.count(marker)==1
        wrapper="original_sources=sources\ndef sources():\n    value=original_sources()\n    value['Pg835PendingDeploymentTest.java']=value['Pg835PendingDeploymentTest.java'].replace('    System.out.println(',MOUNT_ORACLE+'\\n    System.out.println(')\n    return value\n\n"
        raw=raw.replace(marker,wrapper+marker)
    tree=ast.parse(raw)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    assert not any(isinstance(n,ast.FunctionDef) and n.name=='sources' for n in ast.walk(main))
    return raw

if __name__=='__main__':
    mode=sys.argv[1];assert mode in('compile','stage','activate')
    if mode=='compile':
        old=profile.java;profile.java=lambda old=old:java(old())
        for name in ('refs','before_freeze'):
            old=getattr(profile,name);setattr(profile,name,lambda old=old:bind(old()))
    exec(compile(source(mode),'<835 module source closure new-only v6>','exec'),{'__file__':str(R/'pg835_pending_v6.py'),'__name__':'__main__','MOUNT_ORACLE':previous.ORACLE.replace('\\\\n','\\n')})
