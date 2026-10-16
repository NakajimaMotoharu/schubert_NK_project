"""Authenticate actual new Root's immutable before; old native58 is data, not new credit."""
import inspect
import types
import pg4260_stable_admission_image as previous
import pg4576_current_fresh_noargs_once as entry
import pg4578_current_live_binding as binding
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4596-current-admission-image-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='f14b97d22963b2ad3eeea7dbcb5087fcb6885047d965256ffca444fbf1f306b5'
PUBLICATION_PATH='pg4552-failed-current-publication-post-v1/second-full11.private.json'


def project(value,publication):
    """Map only the nine actual fields. Never fabricate old detailedActors data."""
    expected={'units','actors','database','flocks','durable','native','startup','runtime','configuration'}
    if type(value)is not dict or set(value)!=expected:raise ValueError('complete actual nine-field admission schema required')
    units={'caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service'}
    if type(value['units'])is not dict or set(value['units'])!=units:raise ValueError('all ten actually captured Units required')
    fields={'Id','LoadState','ActiveState','SubState','MainPID','ControlPID','Job','InvocationID','ControlGroup','Result','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','Type','KillMode','SendSIGKILL','RemainAfterExit','Restart'}
    for name,row in value['units'].items():
        if type(row)is not dict or set(row)!=fields or any(type(v)is not str for v in row.values())or row['Id']!=name or row['MainPID']!='0'or row['ControlPID']!='0'or row['Job']!='':raise ValueError('actual Unit generation not quiescent')
    if type(value['configuration'])is not dict or set(value['configuration'])!=units:raise ValueError('all actual configurations required')
    database=value['database']
    if type(database)is not dict or set(database)!={'rows','peers','locks'}or type(database['rows'])is not dict or len(database['rows'])!=24:raise ValueError('all24 captured rows required')
    if value['actors']!={}or database['peers']!=[]or database['locks']!=[]or value['flocks']!=[]:raise ValueError('actual before ownership must be empty')
    if type(value['native'])is not dict or sum(k.endswith('.exec')for k in value['native'])!=58:raise ValueError('all58 original native streams required')
    return {'rows':database['rows'],'durable':value['durable'],'oneTimeRuntime':value['runtime'],'configuration':value['configuration'],'unitFilesActual':publication['unitFilesActual'],'native':value['native']}


def payload(observed):
    raw=previous.payload(observed)
    for old,new in [(previous.ONCE,ONCE),(previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.PUBLICATION,PUBLICATION),
        ('pg4008-literal-invariant-publication-independent-post-v1/after.private.json',PUBLICATION_PATH),('!=52','!=58'),('all52','all58'),("'nativeExecEntries':52","'nativeExecEntries':58")]:raw=raw.replace(old,new)
    import ast
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='project')
    original=ast.get_source_segment(raw,node)
    return raw.replace(original,inspect.getsource(project),1)


def live():
    ns={**vars(previous.previous),'SOURCE':SOURCE,'LIVE':LIVE}
    return types.FunctionType(previous.live.__code__,ns)()


def before():
    ns={**vars(previous.previous),'SLOT':SLOT,'SOURCE':SOURCE,'live':live}
    raw=inspect.getsource(previous.previous.before)
    exec(compile(raw,'<actual immutable before receipt>','exec'),ns);return ns['before']()


def execute(slot,raw,timeout=60):
    authenticate_host()
    return types.FunctionType(previous.execute.__code__,{**vars(previous.previous),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
