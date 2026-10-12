"""BUG1165: all emitted failed-manager predicates, separately from stop authority.

SSC278/279/280. Frozen old helpers remain untouched; same Main/Root/owners.
"""
import ast
import inspect
from pyflakes.api import check
import pg1772_warning_owned_stop_sources as previous
import pg1799_warning_parent_projection_contract as contract

TOOLS='pg1800-warning-owned-stop-tools-v1'
SOURCE=previous.SOURCE
context=previous.context


def replace_function(raw,name,body):
    matches=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name==name]
    if len(matches)!=1:raise ValueError('one actual helper boundary required')
    return raw.replace(ast.get_source_segment(raw,matches[0]),body.strip(),1)


def sources():
    result={}
    for old_name,raw in previous.sources().items():
        name=old_name.replace('1772','1800')
        raw=raw.replace('1772','1800').replace('PG1772','PG1800')
        if name=='pg1800_native_refs.py':
            guard="require(parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ActiveState']=='inactive' and parent['SubState']=='dead')"
            if raw.count(guard)!=1:raise ValueError('one retained parent capture predicate required')
            raw=raw.replace(guard,"qualify_warning_parent(parent)")
            raw='from pg1800_warning_parent_projection import qualify_warning_parent\n'+raw
        elif name=='pg1800_native_owned_stop.py':
            raw=replace_function(raw,'parent_receipt','''
def parent_receipt():
 owner=holder()
 data=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','-o','json','--no-pager'])
 records=[json.loads(line,object_pairs_hook=unique)for line in data.decode('utf-8').splitlines()]
 rows=[r for r in records if r.get('INVOCATION_ID')=='b5a12ee25dc44ec49b08f5d084b4052f']
 original=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/9adbf05a-61d0-408b-b51d-ab19c7e5b16a.done').read_bytes()
 receipt=completed(rows,original)
 require(receipt['genuinePid1Failure']is True and receipt['genuinePid1StartDone']is False and receipt['genuineRootDone']is True and receipt['managerFailureRetained']is True and receipt['completionOutcome']=='WARNING'and receipt['endMonotonicUs']==83018953880)
 fields=show('schubert-nk-morning-controller.service')
 qualify_warning_parent(fields,True)
 kernel_empty('schubert-nk-morning-controller.service')
 require(not pathlib.Path('/proc/389748').exists()and holder()==owner)
 raw=('\\n'.join(json.dumps(r,sort_keys=True)for r in rows)+'\\n').encode()
 save('parent.private.jsonl',raw)
 save('parent.normal.private',json.dumps({'actualPid1JobDone':False,'parentOrdinaryExit0':False,'genuineRootWarningOriginal':True,'managerFailureRetained':True,'notUnitGcZeroInference':True,'sha256':hashlib.sha256(raw).hexdigest()},sort_keys=True).encode())
''')
            raw='from pg1800_parent_receipt import completed\nfrom pg1800_warning_parent_projection import qualify_warning_parent\n'+raw
        if name.endswith('.py'):
            if check(raw,'<actual fixed WARNING helper '+name+'>'):raise ValueError('closed actual emitted globals required')
            compile(raw,'<actual fixed WARNING helper>','exec')
        result[name]=raw
    result['pg1800_warning_parent_projection.py']=inspect.getsource(contract)
    return result
