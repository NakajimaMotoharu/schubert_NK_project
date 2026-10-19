"""Immutable0ea full11 admission; prior94 preserved without old native credit."""
import ast
import types
import pg5476_current_admission_image as previous
import pg5638_new_normal_root_once as entry
import pg5640_new_normal_live_binding as binding
from pg4996_resume_connection import authenticate_host

W=entry.W
SLOT='pg5644-current-full11-admission-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='de765f0d4f9c5f7d375b0956326648f8969e7823f254bc394e3c6cc8faa93951'
PUBLICATION_PATH='pg5630-current-publication-independent-post-v1/after.private.json'


def bind(raw):
    raw=previous.bind(raw)
    for before,after in((previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.ONCE,ONCE),(previous.LIVE,LIVE),
      (previous.PUBLICATION,PUBLICATION),(previous.PUBLICATION_PATH,PUBLICATION_PATH)):
        raw=raw.replace(before,after)
    return raw


def project_source():return previous.project_source().replace('!=88','!=94').replace('all88','all94')


def project(value,publication):
    ns={};exec(compile(project_source(),'<lossless full11/all94 view>','exec'),ns)
    return ns['project'](value,publication)


def payload(observed):
    raw=bind(previous.payload(observed)).replace("'nativeExecEntries':88","'nativeExecEntries':94")
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    return raw.replace(ast.get_source_segment(raw,node),project_source(),1)


def live():return types.FunctionType(previous.previous.live.__code__,{**vars(previous.previous),'SOURCE':SOURCE,'LIVE':LIVE})()


def before():return types.FunctionType(previous.previous.before.__code__,{**vars(previous.previous),'SOURCE':SOURCE,'SLOT':SLOT,'live':live})()


def execute(slot,raw,timeout=90):
    authenticate_host();transport=previous.previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
