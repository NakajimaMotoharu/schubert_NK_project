"""SSC191/DEPLOY006..008: ordinary Java TERM is stop data, never a successful Unit/old close.
Independent strict journal oracle; no process action, mutation, or Production method expected.
"""
import hashlib,json
FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
BOOT='e07aa7061acd4e65b309d7f330f79d54'
def require(b):
    if not b:raise ValueError('ordinary TERM evidence rejected')
def unique(pairs):
    result={}
    for k,v in pairs:
        require(k not in result);result[k]=v
    return result
def witness(role,before,after,raw,pid,uid):
    require(role in ('API','WEB') and isinstance(pid,str) and pid.isdigit() and int(pid)>0 and isinstance(uid,str) and uid.isdigit())
    require(isinstance(before,dict) and isinstance(after,dict) and set(before)==FIELDS and set(after)==FIELDS)
    require(all(isinstance(v,str) for v in (*before.values(),*after.values())))
    unit=f'schubert-nk-{role.lower()}.service'
    require(before['Id']==after['Id']==unit and before['LoadState']==after['LoadState']=='loaded')
    require(before['MainPID']==pid and before['ControlPID']=='0' and before['Job']=='' and before['ActiveState']=='active' and before['SubState']=='running' and before['Result']=='success')
    require(before['ExecMainCode']==before['ExecMainStatus']==before['ExecMainExitTimestampMonotonic']=='0')
    invocation=before['InvocationID'];require(len(invocation)==32 and all(c in '0123456789abcdef' for c in invocation) and after['InvocationID']==invocation)
    require(after['ActiveState']=='failed' and after['SubState']=='failed' and after['Result']=='exit-code' and after['ExecMainCode']=='1' and after['ExecMainStatus']=='143')
    require(after['MainPID']==after['ControlPID']=='0' and after['Job']=='')
    for k,v in {'Type':'simple','Restart':'on-failure','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no'}.items():require(before[k]==after[k]==v)
    require(before['ExecMainStartTimestampMonotonic'].isdigit() and after['ExecMainExitTimestampMonotonic'].isdigit())
    start=int(before['ExecMainStartTimestampMonotonic']);end=int(after['ExecMainExitTimestampMonotonic'])
    require(start>0 and end>=start and after['ExecMainStartTimestampMonotonic']==before['ExecMainStartTimestampMonotonic'])
    require(isinstance(raw,bytes) and 0<len(raw)<=4194304)
    text=raw.decode('utf-8',errors='strict');require(text.endswith('\n'))
    rows=[json.loads(line,object_pairs_hook=unique) for line in text.splitlines()];require(rows)
    cursors=set();markers=[]
    for index,row in enumerate(rows):
        require(isinstance(row,dict))
        for k in ('__CURSOR','__MONOTONIC_TIMESTAMP','_BOOT_ID','_SYSTEMD_UNIT','_SYSTEMD_INVOCATION_ID','_PID','_UID','PRIORITY','MESSAGE'):require(isinstance(row.get(k),str))
        cursor=row['__CURSOR'];require(cursor and len(cursor)<=512 and cursor not in cursors);cursors.add(cursor)
        require(row['_BOOT_ID']==BOOT and row['_SYSTEMD_UNIT']==unit and row['_SYSTEMD_INVOCATION_ID']==invocation and row['_PID']==pid)
        require(row['PRIORITY'] in ('4','5','6','7') and row['__MONOTONIC_TIMESTAMP'].isdigit() and start<=int(row['__MONOTONIC_TIMESTAMP'])<=end)
        require(row['MESSAGE'] not in (f'{role} cleanup unconfirmed',f'{role} process failed'))
        if row['MESSAGE'] in (f'{role} cleanup complete',f'{role} process stopped'):
            require(row['_UID']==uid);markers.append((index,int(row['__MONOTONIC_TIMESTAMP']),row['MESSAGE']))
    require(len(markers)==2 and markers[0][2]==f'{role} cleanup complete' and markers[1][2]==f'{role} process stopped' and markers[0][1]<=markers[1][1])
    return {'rows':len(rows),'sha256':hashlib.sha256(raw).hexdigest(),'ordinaryStopData':True,'unitSuccess':False,'oldToolCloseSuccess':False}
