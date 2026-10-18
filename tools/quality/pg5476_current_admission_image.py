"""Immutable296 same-cohort full11 admission; all88 prior exec retained as data only."""
import ast
import types
import pg5036_current_admission_image as previous
import pg5470_new_normal_root_once as entry
import pg5472_new_normal_live_binding as binding
from pg4996_resume_connection import authenticate_host

W=entry.W
SLOT='pg5476-current-full11-admission-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='be40ca2ac1ceb36ea8c556e0a884a11cff9762d31f17df8b37e8c62c62cbccfc'
PUBLICATION_PATH='pg5460-ownership-publication-independent-post-v1/after.private.json'


def bind(raw):
    raw=previous.bind(raw)
    for before,after in((previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.ONCE,ONCE),(previous.LIVE,LIVE),
        (previous.PUBLICATION,PUBLICATION),(previous.PUBLICATION_PATH,PUBLICATION_PATH)):
        raw=raw.replace(before,after)
    return raw


def project_source():return previous.project_source().replace('!=80','!=88').replace('all80','all88')


def project(value,publication):
    ns={};exec(compile(project_source(),'<lossless full11/all88 view>','exec'),ns)
    return ns['project'](value,publication)


def payload(observed):
    raw=bind(previous.payload(observed)).replace("'nativeExecEntries':80","'nativeExecEntries':88")
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    return raw.replace(ast.get_source_segment(raw,node),project_source(),1)


def live():return types.FunctionType(previous.live.__code__,{**vars(previous),'SOURCE':SOURCE,'LIVE':LIVE})()


def before():return types.FunctionType(previous.before.__code__,{**vars(previous),'SOURCE':SOURCE,'SLOT':SLOT,'live':live})()


def execute(slot,raw,timeout=90):
    authenticate_host();transport=previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
