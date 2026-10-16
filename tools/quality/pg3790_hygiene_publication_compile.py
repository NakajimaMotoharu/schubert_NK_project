"""Host-only full publication ABI using qualified same-source shared classes."""
import inspect
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg3782_hygiene_ro_compile as previous
import pg3788_hygiene_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=previous.sha(previous.PRIOR/'bundle.safe.json')
    values['pg3788_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg3788_native_refs.py']
    require_bound(values['pg3788_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<actual finite publication emitted Python>'):raise ValueError('complete namespace required')
    return values


def compiler():
    raw=inspect.getsource(previous.main).replace('pg3782-','pg3790-')
    raw=raw.replace("role.CLASS.replace('CandidateRo',suffix)","'Pg3788'+suffix")
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('full five tests plus independent transition required')
    return raw.replace(marker,marker+",('transition','TransitionTest')")


def main():
    namespace={**previous.__dict__,'TARGET':TARGET,'role':role,'generated':generated}
    namespace['write']=types.FunctionType(previous.write.__code__,namespace)
    exec(compile(compiler(),'<new whole finite publication ABI>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
