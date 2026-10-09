"""Fixed stopped declaration and authenticated auxiliary history; never infers GC success."""


def accepted(before,after,manager,closed):
    if not isinstance(before,tuple)or not isinstance(after,tuple)or len(before)!=8 or len(after)!=8:return False
    if before[:3]!=after[:3]:return False
    if before==after:return True
    if after[3:]==('n/a','n/a','0','(null)','0/0'):
        return isinstance(manager,dict)and manager.get('MainPID')==manager.get('ControlPID')=='0'and manager.get('Job')==''and manager.get('InvocationID')==''and all(manager.get(k)=='0'for k in ('ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic'))
    return isinstance(manager,dict)and isinstance(closed,dict)and manager==closed and manager.get('MainPID')==manager.get('ControlPID')=='0'and manager.get('Job')==''and manager.get('Result')in ('success','exit-code','timeout')and manager.get('ExecMainCode')=='1'and before[3]==after[3]and before[5]==after[5]and after[6]=='exited'and after[7]==manager.get('ExecMainStatus')and after[4]not in ('','n/a')
