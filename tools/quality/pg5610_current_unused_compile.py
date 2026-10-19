"""All18 current296 ABI; independent full11 post must be valid before archive/stage."""
import inspect
from pyflakes.api import check
import pg5608_current_unused_sources as role
import pg5440_ownership_unused_compile as previous
import pg5614_current_unused_post as post

TARGET=role.W/role.TOOLS
ARCHIVE=previous.ARCHIVE.parent/role.ARCHIVE
TEMPLATE=previous.TEMPLATE


def compiler():
    raw=role.normalized_text(previous.compiler())
    for old,new in(('pg5062-frozen-v1','pg5498-frozen-v1'),('pg5060-current-owned-tools-v1','pg5496-current-owned-tools-v1'),('Pg5060','Pg5496')):raw=raw.replace(old,new)
    for marker in("old = W / 'pg5430-release-v1'","'pg5498-frozen-v1.safe.json'",'pg5598-candidate-build-v1.safe.json',role.capture.SLOT):
        if marker not in raw:raise ValueError('actual current296 ABI/new0ea signature/fresh full11 boundary: '+marker)
    compile(raw,'<all18 actual deployed296 ABI>','exec')
    return raw


def validate_actual_graph(target,hashes):
    scope={**vars(TEMPLATE),'role':role,'ARCHIVE':ARCHIVE}
    raw=inspect.getsource(TEMPLATE.validate_actual_graph).replace('pg3982','pg5608').replace('pg3976','pg5598')
    exec(compile(raw,'<new actual0ea bundle/signature dependency graph>','exec'),scope)
    return scope['validate_actual_graph'](target,hashes)


def main():
    if check(post.payload(),'<complete independent post before host artifacts>'):raise ValueError('independent post must compile before stage')
    scope={**vars(TEMPLATE),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'__file__':__file__,
      'compiler':compiler,'validate_actual_graph':validate_actual_graph}
    exec(compile(inspect.getsource(TEMPLATE.main),'<host only current296/all18 ABI>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
