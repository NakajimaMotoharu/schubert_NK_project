"""Normal full24 finite publication ABI with no old static equivalence assumptions."""
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg4716_ssc299_ro_compile as ro_compile
import pg4722_ssc299_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=ro_compile.sha(ro_compile.PRIOR/'bundle.safe.json')
    values['pg4722_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg4722_native_refs.py']
    require_bound(values['pg4722_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<actual normal finite publication>'):
            raise ValueError('all emitted publication globals required')
    return values


def compiler():
    raw=ro_compile.compiler().replace('pg4716-','pg4724-')
    raw=raw.replace("role.CLASS.replace('CandidateRo',suffix)","'Pg4722'+suffix")
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('all five prior phases plus independent transition phase')
    return raw.replace(marker,marker+",('transition','TransitionTest')")


def main():
    ns={**vars(ro_compile.old.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'PRIOR':ro_compile.PRIOR,'generated':generated}
    ns['write']=types.FunctionType(ro_compile.old.previous.write.__code__,ns)
    exec(compile(compiler(),'<normal full24 publication current ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
