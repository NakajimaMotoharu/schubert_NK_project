"""Host-only actualA2 ABI of RO-only296 role; all qualified shared class bytes retained."""
import inspect
import types
import pg5002_ssc304_ro_compile as previous
import pg5446_ownership_ro_sources as role

W=role.W
TARGET=W/role.TOOLS
PRIOR=W/role.unused.TOOLS
sha=previous.sha
TEMPLATE=previous.TEMPLATE


def generated():
    ns={**vars(previous),'role':role,'PRIOR':PRIOR}
    raw=inspect.getsource(previous.generated).replace('pg5000','pg5446')
    exec(compile(raw,'<all18 A2 exact common bundle RO>','exec'),ns)
    return ns['generated']()


def compiler():
    raw=previous.compiler()
    for old,new in(('pg5002','pg5448'),('pg4988','pg5440'),('Pg4986','Pg5438'),('pg4860-release-v1','pg4980-release-v1')):
        raw=raw.replace(old,new)
    return raw


def main():
    ns={**vars(TEMPLATE),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':PRIOR,'generated':generated}
    ns['write']=types.FunctionType(TEMPLATE.write.__code__,ns)
    exec(compile(compiler(),'<RO only actualA2 ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
