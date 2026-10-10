"""SSC258 fresh management: only remaining Cleanup stop, then revoke/intent.

Completed broker/Expiry stops are never replayed. Bind to complete1143 post.
"""
import ast
from pg1134_failed_recovery_sources import files as previous, replace

BASE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/fixed-failed-owner-handoff-v2/after.private.json'
SHA='29106562415499a664428950aa14351ba4f50b7f06983b5ebf617ec389fc5182'


def files():
    result={}
    for name,text in previous().items():
        name=name.replace('Pg1134','Pg1144').replace('pg1134_','pg1144_')
        text=text.replace('Pg1134','Pg1144').replace('PG1134','PG1144').replace('pg1134_','pg1144_')
        text=text.replace('pg1134-issued-api-tools-v1','pg1144-terminal-tools-v1').replace('pg1134-issued-api-recovery-v1','pg1144-terminal-recovery-v1')
        if name=='Pg1144SingleApiRecovery.java':
            text=replace(text,'List.of("artemis.service")','List.of("schubert-nk-cleanup.service")')
        elif name=='pg1144_single_api_refs.py':
            text=replace(text,'/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-capture-v6/observed.private.json',BASE)
            text=replace(text,'df0b989893adbddd6a539b963c07029222c47e1b557cd572f44fdb8864f1fb01',SHA)
            text=replace(text,"ORDER=['artemis.service']","ORDER=['schubert-nk-cleanup.service']")
            # New before has already terminal broker; exact current declaration/history are now immutable.
            text=replace(text,"if unit=='artemis.service':broker_policy.configuration(baseline['configuration'][unit],actual[unit],baseline['units'][unit],show(unit,FIELDS),exec_record)",
                         "if unit=='artemis.service':require(actual[unit]==baseline['configuration'][unit])")
            text=replace(text,"require({u:show(u,FIELDS) for u in UNITS}==baseline['units']);actor('artemis.service',baseline['units']['artemis.service'])",
                         "require({u:show(u,FIELDS) for u in UNITS}==baseline['units']);require_old_gone_and_current_profile()")
            marker='def namespace_failure_proof():\n'
            extra='''def require_old_gone_and_current_profile():
 require(not pathlib.Path('/proc/404585').exists()and not pathlib.Path('/proc/404614').exists()and not pathlib.Path('/proc/253968').exists())
 cleanup=baseline['units']['schubert-nk-cleanup.service']
 require(cleanup['InvocationID']=='48281323ca3743cbbaddd706e0c4edc5'and cleanup['MainPID']==cleanup['ControlPID']=='0'and cleanup['Job']==''and cleanup['Type']=='oneshot'and cleanup['RemainAfterExit']=='yes'and cleanup['ActiveState']=='active'and cleanup['SubState']=='exited')
 require(cleanup['ExecMainCode']=='1'and cleanup['ExecMainStatus']=='0'and cleanup['ExecMainStartTimestampMonotonic']=='34688004646'and cleanup['ExecMainExitTimestampMonotonic']=='34751080043')
 for name in UNITS:
  if name!='schubert-nk-cleanup.service':require(terminal(baseline['units'][name]));kernel(name)
'''
            text=replace(text,marker,extra+marker)
            marker="else:require(normal_terminal(before,v))\n require(v==show(unit,FIELDS) and holder()==owner);values()"
            extra='''else:
  require(normal_terminal(before,v)and all(before[k]==v[k]for k in before.keys()-{'ActiveState','SubState'}))
  journal=command(['/usr/bin/journalctl','--boot','_PID=1','UNIT='+unit,'-o','json','--no-pager'])
  records=[json.loads(line,object_pairs_hook=unique)for line in journal.splitlines()]
  done=[r for r in records if r.get('INVOCATION_ID')==before['InvocationID']and r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
  require(len(done)==1 and done[0].get('_BOOT_ID')==BOOT.replace('-','')and done[0].get('_UID')=='0'and done[0].get('_COMM')=='systemd')
  save('cleanup-manager.private.jsonl',journal)
 require(v==show(unit,FIELDS) and holder()==owner);values()'''
            text=replace(text,marker,extra)
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
