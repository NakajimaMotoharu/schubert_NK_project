"""New finite24 only, actualA2 ABI and all seven independent host phases."""
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg5448_ownership_ro_compile as ro_compile
import pg5454_ownership_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=ro_compile.sha(ro_compile.PRIOR/'bundle.safe.json')
    values['pg5454_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg5454_native_refs.py']
    require_bound(values['pg5454_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<all finite296 roles>'):raise ValueError('complete publication namespace static0')
    return values


def compiler():
    raw=ro_compile.compiler().replace('pg5448-','pg5456-')
    raw=raw.replace("role.CLASS.replace('CandidateRo',suffix)","'Pg5454'+suffix")
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('one transition host test boundary')
    return raw.replace(marker,marker+",('transition','TransitionTest')",1)


def main():
    template=ro_compile.TEMPLATE
    ns={**vars(template),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':ro_compile.PRIOR,'generated':generated}
    ns['write']=types.FunctionType(template.write.__code__,ns)
    exec(compile(compiler(),'<all24 finite actualA2 ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
