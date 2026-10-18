"""Host-only actualA2 ABI for all18 distinct296 roles; independent post must already compile."""
import inspect
from pyflakes.api import check
import pg5438_ownership_unused_sources as role
import pg4988_ssc304_unused_compile as previous
import pg5444_ownership_unused_post as post

TARGET=role.W/role.TOOLS
ARCHIVE=previous.ARCHIVE.parent/role.ARCHIVE
TEMPLATE=previous.TEMPLATE


def compiler():
    raw=role.normalized_text(previous.compiler())
    for old,new in(('pg4918-frozen-v1','pg5062-frozen-v1'),('pg4916-current-owned-tools-v1','pg5060-current-owned-tools-v1'),('Pg4916','Pg5060')):
        raw=raw.replace(old,new)
    for marker in("old = W / 'pg4980-release-v1'","'pg5062-frozen-v1.safe.json'",'pg5430-candidate-build-v1.safe.json',role.view.SLOT):
        if marker not in raw:raise ValueError('actual A2 ABI/296 signature/fresh full11 boundary '+marker)
    compile(raw,'<all18 actual currentA2 ABI>','exec');return raw


def validate_actual_graph(target,hashes):
    ns={**vars(TEMPLATE),'role':role,'ARCHIVE':ARCHIVE}
    raw=inspect.getsource(TEMPLATE.validate_actual_graph).replace('pg3982','pg5438').replace('pg3976','pg5430')
    exec(compile(raw,'<exact296 candidate bundle/signature>','exec'),ns)
    return ns['validate_actual_graph'](target,hashes)


def main():
    # The independent post is required before ANY host archive construction or guest operation.
    if check(post.payload(),'<before-stage complete independent post>'):raise ValueError('post dependency qualification before compile')
    ns={**vars(TEMPLATE),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'__file__':__file__,
        'compiler':compiler,'validate_actual_graph':validate_actual_graph}
    exec(compile(inspect.getsource(TEMPLATE.main),'<host-only all18 currentA2 ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
