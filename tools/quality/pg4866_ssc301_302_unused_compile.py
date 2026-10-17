"""All18 emitted roles against actual825e signed ABI; no guest action."""
import inspect
import pg4708_ssc299_unused_compile as previous
import pg4864_ssc301_302_unused_sources as role

TARGET=role.W/role.TOOLS
ARCHIVE=previous.ARCHIVE.parent/role.ARCHIVE


def compiler():
    raw=role.normalized_text(previous.compiler())
    for old,new in [('pg4654-frozen-v1','pg4774-frozen-v1'),('pg4652-current-owned-tools-v1','pg4772-new-current-owned-tools-v1'),('Pg4652','Pg4772')]:raw=raw.replace(old,new)
    for marker in ("old = W / 'pg4702-release-v1'", "'pg4774-frozen-v1.safe.json'", 'pg4860-candidate-build-v1.safe.json', role.view.SLOT):
        if marker not in raw:raise ValueError('actual current/candidate/fresh data compiler boundary '+marker)
    compile(raw,'<all18 actual current825e ABI>','exec');return raw


def validate_actual_graph(target,hashes):
    ns={**vars(previous.old),'role':role,'ARCHIVE':ARCHIVE}
    raw=inspect.getsource(previous.old.validate_actual_graph).replace('pg3982','pg4864').replace('pg3976','pg4860')
    exec(compile(raw,'<exact new candidate bundle/signature>','exec'),ns)
    return ns['validate_actual_graph'](target,hashes)


def main():
    ns={**vars(previous.old),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'__file__':__file__,
        'compiler':compiler,'validate_actual_graph':validate_actual_graph}
    exec(compile(inspect.getsource(previous.old.main),'<host-only current825e all18 ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
