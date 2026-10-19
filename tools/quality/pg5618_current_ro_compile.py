"""Host-only RO18 compile against actual deployed296 ABI; never whole replay."""
import inspect
import types
from pyflakes.api import check
import pg5448_ownership_ro_compile as previous
import pg5616_current_ro_sources as role
import pg5622_current_ro_post as post

W=role.W
TARGET=W/role.TOOLS
PRIOR=W/role.unused.TOOLS
sha=previous.sha
TEMPLATE=previous.TEMPLATE


def generated():
    scope={**vars(previous),'role':role,'PRIOR':PRIOR}
    raw=inspect.getsource(previous.generated).replace('pg5446','pg5616')
    exec(compile(raw,'<all18 current296 shared bundle RO>','exec'),scope)
    return scope['generated']()


def compiler():
    raw=previous.compiler()
    for old,new in(('pg5448','pg5618'),('pg5440','pg5610'),('Pg5438','Pg5608'),('pg4980-release-v1','pg5430-release-v1')):raw=raw.replace(old,new)
    return raw


def main():
    if check(post.payload(),'<independent RO post before compiler/stage>'):raise ValueError('post namespace must qualify before RO stage')
    scope={**vars(TEMPLATE),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':PRIOR,'generated':generated}
    scope['write']=types.FunctionType(TEMPLATE.write.__code__,scope)
    exec(compile(compiler(),'<RO only actual296 ABI>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
