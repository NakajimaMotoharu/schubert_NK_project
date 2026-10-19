"""New finite24 only, actual296 ABI and seven independent host phases."""
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg5618_current_ro_compile as ro_compile
import pg5624_current_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=ro_compile.sha(ro_compile.PRIOR/'bundle.safe.json')
    values['pg5624_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg5624_native_refs.py']
    require_bound(values['pg5624_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<all finite0ea roles>'):raise ValueError('complete finite publication namespace')
    return values


def compiler():
    raw=ro_compile.compiler().replace('pg5618-','pg5626-')
    raw=raw.replace("role.CLASS.replace('CandidateRo',suffix)","'Pg5624'+suffix")
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('one independent transition host phase boundary')
    return raw.replace(marker,marker+",('transition','TransitionTest')",1)


def main():
    template=ro_compile.TEMPLATE
    scope={**vars(template),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':ro_compile.PRIOR,'generated':generated}
    scope['write']=types.FunctionType(template.write.__code__,scope)
    exec(compile(compiler(),'<all24 finite current296 ABI>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
