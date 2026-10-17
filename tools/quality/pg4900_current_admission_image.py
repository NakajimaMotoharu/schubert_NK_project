"""Actual04bb Root immutable full11 admission; all72 old exec are data only."""
import ast
import inspect
import json
import types
import pg4752_new_current_admission_image as previous
import pg4892_new_normal_root_once as entry
import pg4894_new_normal_live_binding as binding
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

W=entry.W
SLOT='pg4900-current-full11-admission-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='4a9ba30a0e6457d7fc15b21d2feb4453837c67d4a78a1df134427894421f5eb0'
PUBLICATION_PATH='pg4886-ssc301-302-publication-independent-post-v1/after.private.json'


def bind(raw):
    # Raw shared seal starts at the older4584 boundary, unlike the already-bound
    # admission/terminal. Resolve that exact prior layer before the current one.
    raw=previous.bind(raw)
    for a,b in [(previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.ONCE,ONCE),(previous.LIVE,LIVE),
                (previous.PUBLICATION,PUBLICATION),(previous.PUBLICATION_PATH,PUBLICATION_PATH)]:raw=raw.replace(a,b)
    return raw


def project_source():
    raw=inspect.getsource(previous.project).replace('!=64','!=72').replace('all64','all72')
    return raw


def project(value,publication):
    ns={};exec(compile(project_source(),'<lossless actual full11/72 data view>','exec'),ns)
    return ns['project'](value,publication)


def payload(observed):
    raw=bind(previous.payload(observed)).replace("'nativeExecEntries':64","'nativeExecEntries':72")
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    return raw.replace(ast.get_source_segment(raw,node),project_source(),1)


def live():
    outer=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==SOURCE and outer['result']['productionSource']==SOURCE):
        raise ValueError('actual current same-generation independent live binding')
    return {**outer['result']['binding'],'rootPid':outer['result']['rootPid']}


def before():
    outer=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==SOURCE and outer['result']['binding']==live()):
        raise ValueError('actual same-cohort immutable before proof')
    return outer['result']['privateBeforeSha256']


def execute(slot,raw,timeout=60):
    authenticate_host()
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
