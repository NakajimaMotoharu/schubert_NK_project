"""Independent post oracle: captured normal20 is prerequisite, never inferred from GC."""
def current_normal_or_gc(captured,current):
 if type(captured)is not dict or type(current)is not dict or set(captured)!=set(current):return False
 if captured.get('ExecMainCode')!='1'or captured.get('ExecMainStatus')!='20'or captured.get('InvocationID')in(None,''):return False
 if current==captured:return True
 empty={**captured,'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
 return current==empty
