"""New ordinary Source825e immutable admission image; old64 native data only."""
import ast
import inspect
import types
import pg4584_current_admission_image as previous
import pg4736_new_normal_root_once as entry
import pg4738_new_normal_live_binding as binding
from pg1446_current_cold_stage import W
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4758-new-current-full11-admission-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601'
PUBLICATION_PATH='pg4728-ssc299-publication-independent-post-v1/after.private.json'


def bind(raw):
    for old,new in [(previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.ONCE,ONCE),(previous.LIVE,LIVE),
                    (previous.PUBLICATION,PUBLICATION),(previous.PUBLICATION_PATH,PUBLICATION_PATH)]:raw=raw.replace(old,new)
    return raw


def project_source():return inspect.getsource(project)


def project(value,publication):
    expected={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native'}
    if type(value)is not dict or set(value)!=expected:raise ValueError('complete actual normal full11 required')
    if type(publication)is not dict or value['unitFilesActual']!=publication['unitFilesActual']:raise ValueError('actual publication Unit files required')
    if type(value['rows'])is not dict or len(value['rows'])!=24:raise ValueError('actual all24 rows required')
    if type(value['extraDurable'])is not dict or set(value['extraDurable'])!={'credentials','oldProofs'}:raise ValueError('exact two extra durable groups')
    if type(value['native'])is not dict or sum(k.endswith('.exec')for k in value['native'])!=64:raise ValueError('all64 old native data required')
    if type(value['units'])is not dict or len(value['units'])!=10 or set(value['units'])!=set(value['configuration']):raise ValueError('ten actual Units/configurations')
    for row in value['units'].values():
        if type(row)is not dict or row['MainPID']!='0'or row['ControlPID']!='0'or row['Job']!='':raise ValueError('actual quiescent before Units')
    return {'rows':value['rows'],'durable':{'originals':value['originals'],'backup':value['backup'],**value['extraDurable']},'oneTimeRuntime':value['runtime'],'configuration':value['configuration'],'unitFilesActual':value['unitFilesActual'],'native':value['native']}


def payload(observed):
    raw=bind(previous.payload(observed)).replace("'nativeExecEntries':58","'nativeExecEntries':64")
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    return raw.replace(ast.get_source_segment(raw,node),project_source(),1)


def live():
    proof=previous.previous.previous
    return types.FunctionType(previous.previous.live.__code__,{**vars(proof),'SOURCE':SOURCE,'LIVE':LIVE})()


def before():
    m=__import__('json').loads((W/SLOT/'manifest.safe.json').read_bytes())
    if not(type(m['actualExit'])is int and m['actualExit']==0 and m['source']==SOURCE and m['result']['binding']==live()):raise ValueError('actual same-cohort immutable image required')
    return m['result']['privateBeforeSha256']


def execute(slot,raw,timeout=60):
    authenticate_host()
    transport=previous.previous.previous
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
