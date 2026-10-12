"""Exact observed failed-manager normal-WARNING original profile, not success."""

EXPECTED={
    'MainPID':'0','ControlPID':'0','Job':'','ActiveState':'failed','SubState':'failed',
    'Result':'exit-code','ExecMainCode':'1','ExecMainStatus':'10',
    'InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f',
    'ExecMainStartTimestampMonotonic':'81404764713',
    'ExecMainExitTimestampMonotonic':'83018952135',
}


def qualify_warning_parent(fields,configuration=False):
    if type(fields)is not dict or type(configuration)is not bool:raise ValueError('typed complete parent required')
    if any(type(fields.get(k))is not str or fields[k]!=v for k,v in EXPECTED.items()):raise ValueError('same actual retained failure required')
    if configuration and (fields.get('Type')!='oneshot'or fields.get('SuccessExitStatus')!=''):raise ValueError('actual old signed Unit contract required')
    return {'managerFailureRetained':True,'genuinePid1StartDone':False,'stopAuthority':False}
