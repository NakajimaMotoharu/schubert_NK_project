"""Full current ABI and all24 finite transition roles; host-only compile."""
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg4874_ssc301_302_ro_compile as ro_compile
import pg4880_ssc301_302_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=ro_compile.sha(ro_compile.PRIOR/'bundle.safe.json')
    values['pg4880_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg4880_native_refs.py']
    require_bound(values['pg4880_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<finite actual24>'):raise ValueError('all complete publication globals')
    return values


def compiler():
    raw=ro_compile.compiler().replace('pg4874-','pg4882-')
    raw=raw.replace("role.CLASS.replace('CandidateRo',suffix)","'Pg4880'+suffix")
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('one transition beyond all six prior phases')
    return raw.replace(marker,marker+",('transition','TransitionTest')",1)


def main():
    ns={**vars(ro_compile.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'PRIOR':ro_compile.PRIOR,'generated':generated}
    ns['write']=types.FunctionType(ro_compile.previous.previous.write.__code__,ns)
    exec(compile(compiler(),'<all24 finite current825e ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
