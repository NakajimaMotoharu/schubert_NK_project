"""Actual current964e ABI, all eighteen normal unused roles; host only."""
import inspect
import pg3984_literal_invariant_unused_compile as old
import pg4706_ssc299_unused_sources as role

TARGET = role.W / role.TOOLS
ARCHIVE = old.ARCHIVE.parent / role.ARCHIVE


def compiler():
    raw = role.normalized_text(old.compiler())
    for before,after in [('pg3878-frozen-v1','pg4654-frozen-v1'),
                         ('pg3876-current-resume-owned-tools-v1','pg4652-current-owned-tools-v1'),
                         ('Pg3876','Pg4652')]: raw=raw.replace(before,after)
    if "old = W / 'pg4432-release-v1'" not in raw or "'pg4654-frozen-v1.safe.json'" not in raw:
        raise ValueError('actual same current Jar ABI and frozen shared graph required')
    compile(raw,'<current964e unused full graph compiler>','exec')
    return raw


def validate_actual_graph(target,hashes):
    ns={**vars(old),'role':role,'ARCHIVE':ARCHIVE}
    raw=inspect.getsource(old.validate_actual_graph).replace('pg3982','pg4706').replace('pg3976','pg4702')
    exec(compile(raw,'<exact normal unused bundle qualification>','exec'),ns)
    return ns['validate_actual_graph'](target,hashes)


def main():
    ns={**vars(old),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,
        '__file__':__file__,'compiler':compiler,'validate_actual_graph':validate_actual_graph}
    exec(compile(inspect.getsource(old.main),'<host-only normal unused all18>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
