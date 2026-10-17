"""All18 unused roles against actual stopped04bb ABI; new candidate bytes separately fixed."""
import inspect
import pg4866_ssc301_302_unused_compile as previous
import pg4986_ssc304_unused_sources as role

TARGET=role.W/role.TOOLS
ARCHIVE=previous.ARCHIVE.parent/role.ARCHIVE
TEMPLATE=previous.previous.old


def compiler():
    raw=role.normalized_text(previous.compiler())
    for old,new in(('pg4774-frozen-v1','pg4918-frozen-v1'),('pg4772-new-current-owned-tools-v1','pg4916-current-owned-tools-v1'),('Pg4772','Pg4916')):raw=raw.replace(old,new)
    for marker in("old = W / 'pg4860-release-v1'","'pg4918-frozen-v1.safe.json'",'pg4980-candidate-build-v1.safe.json',role.view.SLOT):
        if marker not in raw:raise ValueError('actual current/candidate/fresh ABI boundary '+marker)
    compile(raw,'<all18 actual current04bb ABI>','exec');return raw


def validate_actual_graph(target,hashes):
    ns={**vars(TEMPLATE),'role':role,'ARCHIVE':ARCHIVE}
    raw=inspect.getsource(TEMPLATE.validate_actual_graph).replace('pg3982','pg4986').replace('pg3976','pg4980')
    exec(compile(raw,'<actual unused candidate bundle/signature>','exec'),ns)
    return ns['validate_actual_graph'](target,hashes)


def main():
    ns={**vars(TEMPLATE),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'__file__':__file__,
        'compiler':compiler,'validate_actual_graph':validate_actual_graph}
    exec(compile(inspect.getsource(TEMPLATE.main),'<host-only current04bb all18 ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
