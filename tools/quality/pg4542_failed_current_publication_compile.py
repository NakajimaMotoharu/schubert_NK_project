"""Full24 finite publication current ABI + actual complete import graph certificate."""
import hashlib
import json
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
from closed_role_import_graph import check_graph
import pg4524_failed_current_ro_compile as ro_compile
import pg4530_closed_failed_current_ro_compile as closed_ro
import pg4540_failed_current_publication_sources as role

TARGET=role.W/role.TOOLS


def generated():
    values=role.sources();digest=hashlib.sha256((ro_compile.PRIOR/'bundle.safe.json').read_bytes()).hexdigest()
    values['pg4540_native_refs.py']='BUNDLE_HASH='+repr(digest)+'\n'+values['pg4540_native_refs.py'];require_bound(values['pg4540_native_refs.py'],digest)
    for name,raw in values.items():
        if name.endswith('.py')and check(raw,'<full publication emitted source>'):raise ValueError('all emitted static0')
    return values


def compiler():
    raw=closed_ro.compiler().replace('pg4530-','pg4542-')
    old="role.CLASS.replace('CandidateRo',suffix)"
    if raw.count(old)!=1:raise ValueError('one actual publication helper family')
    raw=raw.replace(old,"'Pg4540'+suffix",1)
    marker="('input','InputBoundaryTest')"
    if raw.count(marker)!=1:raise ValueError('all five plus transition oracle required')
    return raw.replace(marker,marker+",('transition','TransitionTest')",1)


def main():
    ns={**vars(ro_compile.base),'role':role,'TARGET':TARGET,'PRIOR':ro_compile.PRIOR,'generated':generated}
    ns['write']=types.FunctionType(ro_compile.base.write.__code__,ns)
    exec(compile(compiler(),'<all finite publication current ABI>','exec'),ns);code=ns['main']()
    if code==0:
        raw=(role.W/'pg4542-frozen-v1.safe.json').read_bytes();frozen=json.loads(raw);pins=frozen['fileHashes']
        for name,digest in pins.items():
            if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('all frozen publication files unchanged')
        preflight=(TARGET/'pg4540_input_preflight.py').read_text()
        value=check_graph(preflight,{n:(TARGET/n).read_bytes()for n in pins if n.endswith('.py')},pins,('Pg4540OrdinaryPublication.class','Pg4540OrdinaryPublication$References.class','Pg4540TransitionTest.class'))
        value.update(frozenManifestSha256=hashlib.sha256(raw).hexdigest(),inputSha256=hashlib.sha256(preflight.encode()).hexdigest(),formalAccepted=False)
        with(role.W/'pg4542-import-graph-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
        print(json.dumps(value))
    return code


if __name__=='__main__':raise SystemExit(main())
