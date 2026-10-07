"""SSC217: current GC is idle only; sealed real normal20 is never reconstructed from zeros."""
from pg535_bootstrap_contract import UNIT, normal20
from pg536_bootstrap_execution_contract import record


def current_gc_after_known20(preserved, current):
    if not normal20(preserved) or not isinstance(current, dict):
        return False
    expected={**preserved, 'InvocationID':'', 'ExecMainCode':'0', 'ExecMainStatus':'0',
              'ExecMainStartTimestampMonotonic':'0', 'ExecMainExitTimestampMonotonic':'0'}
    return current==expected


def configuration_after_gc(preserved, current, actor):
    if not (isinstance(preserved, dict) and isinstance(current, dict)
            and set(preserved)==set(current) and 'ExecStart' in preserved
            and all(isinstance(v,str)for v in [*preserved.values(),*current.values()])
            and all(preserved[k]==current[k]for k in preserved if k!='ExecStart')
            and isinstance(actor,dict) and set(actor)=={'pid','ticks','invocation','zeroCapabilities'}
            and actor['zeroCapabilities'] is True):
        return False
    old,new=record(preserved['ExecStart']),record(current['ExecStart'])
    return (old is not None and new is not None and old[:3]==new[:3]
            and old[3] not in ('','n/a') and old[4] not in ('','n/a')
            and old[5:]==(actor['pid'],'exited','20')
            and new[3:]==('n/a','n/a','0','(null)','0/0'))


def unchanged_after_gc(preserved, current, actor):
    if not (isinstance(preserved,dict) and isinstance(current,dict)
            and set(preserved)==set(current) and {'units','configuration'}<=set(preserved)):
        return False
    if any(preserved[k]!=current[k]for k in preserved if k not in ('units','configuration')):
        return False
    for key in ('units','configuration'):
        old,new=preserved[key],current[key]
        if not isinstance(old,dict) or not isinstance(new,dict) or set(old)!=set(new) or UNIT not in old:
            return False
        if any(old[u]!=new[u]for u in old if u!=UNIT):
            return False
    return (current_gc_after_known20(preserved['units'][UNIT],current['units'][UNIT])
            and configuration_after_gc(preserved['configuration'][UNIT],current['configuration'][UNIT],actor)
            and actor['invocation']==preserved['units'][UNIT]['InvocationID'])
