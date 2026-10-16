"""Newv2 host compile plus actual full141 runtime import closure certificate."""
import hashlib
import inspect
import json
import pg4524_failed_current_ro_compile as previous
from closed_role_import_graph import check_graph


def compiler():return previous.compiler().replace('pg4524','pg4530')


def certify():
    from pg4522_failed_current_ro_sources import W,TOOLS
    target=W/TOOLS;raw=(W/'pg4530-frozen-v1.safe.json').read_bytes();frozen=json.loads(raw)
    if frozen['actualExit']!=0:raise ValueError('actual complete current-JAR compile0 first')
    pins=frozen['fileHashes']
    for name,digest in pins.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('all frozen bytes unchanged')
    preflight=(target/'pg4522_input_preflight.py').read_text()
    result=check_graph(preflight,{n:(target/n).read_bytes()for n in pins if n.endswith('.py')},pins,('Pg4522CandidateRo.class','Pg4522CandidateRo$References.class'))
    value={**result,'frozenManifestSha256':hashlib.sha256(raw).hexdigest(),'inputSha256':hashlib.sha256(preflight.encode()).hexdigest(),'formalAccepted':False}
    with(W/'pg4530-import-graph-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return value


def main():
    ns={**vars(previous),'compiler':compiler};exec(compile(inspect.getsource(previous.main),'<newv2 current RO ABI>','exec'),ns)
    code=ns['main']()
    if code==0:certify()
    return code


if __name__=='__main__':raise SystemExit(main())
