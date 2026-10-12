"""SSC283 unused signed sibling placement, exact two-source/Root13 role binding.

Prefix substitutions never rewrite UUID numeric substrings. No activation or
Unit update/reload is performed by this limited placement profile.
"""
import inspect
import re
from pg1681_closed_candidate_sources import sources as previous
from pg1833_readonly_parent_state_sources import sources as actual_warning
import pg1799_warning_parent_projection_contract as warning_contract
from pg1844_warning_unit_full_six import CANDIDATE,OLD

TOOLS='pg1848-warning-unused-tools-v1'
SAVE='pg1852-warning-unused-placement-v1'
REMOTE='/home/ubuntu/pg1851-warning-input-v1'
ARCHIVE='pg1851-warning-release-v1.tar'


def sources(bom,before):
    if any(type(v)is not str or re.fullmatch('[0-9a-f]{64}',v)is None for v in [bom,before]):raise ValueError('exact signed new BOM and sealed current before hashes required')
    result={}
    for old_name,raw in previous(bom).items():
        # Separate NEW and OLD source/release roles before mapping either one.
        raw=raw.replace(OLD,'__NEW_CANDIDATE_SOURCE__').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',OLD).replace('__NEW_CANDIDATE_SOURCE__',CANDIDATE)
        raw=raw.replace('PG1638','__NEW_RELEASE_UPPER__').replace('pg1638','__NEW_RELEASE_LOWER__').replace('PG1544','PG1638').replace('pg1544','pg1638').replace('__NEW_RELEASE_UPPER__','PG1846').replace('__NEW_RELEASE_LOWER__','pg1846')
        replacements=[('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',before),('pg1641-completed-current-before-v2','pg1849-warning-completed-current-before-v1'),('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','4148e3e8-f107-431a-ab27-d6e6d1f1772e'),('d28eead2-941c-4b97-9747-1758c0809e29','9adbf05a-61d0-408b-b51d-ab19c7e5b16a'),('2026-10-12T06:23:13.176261Z','2026-10-12T18:20:32.598894Z'),('2026-10-12T06:48:58.973359Z','2026-10-12T18:46:52.677350Z'),('e4d891c38dde4e16a5c848e23ef3f83c','b5a12ee25dc44ec49b08f5d084b4052f'),('pg1681-completed-unused-tools-v4',TOOLS),('pg1684-completed-unused-placement-v4',SAVE),('pg1683-candidate-input-v4',REMOTE.rsplit('/',1)[1]),('pg1683-release-v4.tar',ARCHIVE)]
        for old,new in replacements:raw=raw.replace(old,new)
        for old,new in [('38365395523','81404764713'),('39951854181','83018953880'),('204695','389748')]:raw=re.sub(r'\b'+old+r'\b',new,raw)
        name=old_name
        for old,new in [('Pg1640','Pg1848'),('pg1640','pg1848'),('PG1640','PG1848'),('Pg1660','Pg1848'),('pg1660','pg1848'),('PG1660','PG1848'),('Pg1681','Pg1848'),('pg1681','pg1848'),('PG1681','PG1848')]:
            name=name.replace(old,new);raw=raw.replace(old,new)
        if name=='pg1848_parent_receipt.py':raw=actual_warning()['pg1833_parent_receipt.py']
        if name=='Pg1848UnusedStage.java':
            raw=raw.replace('MaintenanceCompletion.Outcome.SUCCESS','MaintenanceCompletion.Outcome.WARNING')
            raw=raw.replace('genuineParentDone=true\\n','genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n')
        elif name=='Pg1848OriginalTupleTest.java':
            raw=raw.replace('Outcome.SUCCESS','Outcome.__OLD_SUCCESS__').replace('Outcome.WARNING','Outcome.SUCCESS').replace('Outcome.__OLD_SUCCESS__','Outcome.WARNING')
        elif name=='pg1848_native_refs.py':
            guard="require(parent['MainPID']==parent['ControlPID']=='0' and parent['Job']=='' and parent['ActiveState']=='inactive' and parent['SubState']=='dead')"
            if raw.count(guard)!=1:raise ValueError('one exact old closed-parent predicate required')
            raw=raw.replace(guard,"qualify_warning_parent(parent)\n  parent_config=h.parent_configuration();require(parent_config=={'Type':'oneshot','SuccessExitStatus':''}and parent['Type']==parent_config['Type'])")
            raw='from pg1848_warning_parent_projection import qualify_warning_parent\n'+raw
        elif name=='pg1848_native_owned_stop.py':
            raw+='''
def parent_configuration():
 import subprocess
 raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=Type,SuccessExitStatus'],timeout=5).decode('ascii')
 require(raw.endswith('\\n'))
 items=[]
 for line in raw.splitlines():
  key,sep,value=line.partition('=');require(sep=='='and key in {'Type','SuccessExitStatus'});items.append((key,value))
 require(len(items)==2 and len({k for k,v in items})==2)
 return dict(items)
'''
        if name.endswith('.py'):compile(raw,'<actual closed warning signed sibling helper>','exec')
        if any(v in raw for v in ['0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','d28eead2-941c-4b97-9747-1758c0809e29','e4d891c38dde4e16a5c848e23ef3f83c','__NEW_']):raise ValueError('old Root/role marker survived actual binding')
        result[name]=raw
    result['pg1848_warning_parent_projection.py']=inspect.getsource(warning_contract)
    return result


if __name__=='__main__':raise SystemExit('host source factory only; no operator entry')
