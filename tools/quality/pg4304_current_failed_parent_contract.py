"""Data-only failed parent certificate. Never normalizes .done data or grants stop authority."""
import datetime
import hashlib
import re
import uuid

SOURCE='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
BOM='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'
UNIT='schubert-nk-morning-controller.service'


def require(value):
    if value is not True:raise ValueError('current failed-parent evidence refused')


def instant(value):
    require(type(value)is str and value.endswith('Z'))
    try:r=datetime.datetime.fromisoformat(value[:-1]+'+00:00')
    except ValueError:raise ValueError('current failed-parent evidence refused')from None
    require(r.tzinfo is not None);return r


def classify(source,bom,boot,binding,state,rows,done):
    require(source==SOURCE and bom==BOM and boot==BOOT)
    require(type(binding)is dict and set(binding)=={'boot','invocation','job','start','run','cutoff','activation','rootPid'})
    require(binding['boot']==BOOT.replace('-','')and type(binding['start'])is int and binding['start']>0 and type(binding['rootPid'])is int and binding['rootPid']>1)
    require(type(binding['invocation'])is str and re.fullmatch('(?!0{32}$)[0-9a-f]{32}',binding['invocation'])is not None)
    require(type(binding['job'])is str and re.fullmatch('[1-9][0-9]*',binding['job'])is not None)
    for key in ['run','activation']:
        value=binding[key];require(type(value)is str)
        try:require(str(uuid.UUID(value))==value and uuid.UUID(value).int!=0)
        except ValueError:raise ValueError('current failed-parent evidence refused')from None
    cutoff=instant(binding['cutoff'])
    expected={'Id':UNIT,'LoadState':'loaded','ActiveState':'failed','SubState':'failed','InvocationID':binding['invocation'],
       'MainPID':'0','ControlPID':'0','Job':'','Result':'timeout','ExecMainCode':'1','ExecMainStatus':'143','ExecMainStartTimestampMonotonic':str(binding['start'])}
    require(type(state)is dict and set(state)==set(expected)|{'ExecMainExitTimestampMonotonic'}and all(type(v)is str for v in state.values())and all(state[k]==v for k,v in expected.items()))
    end=state['ExecMainExitTimestampMonotonic'];require(re.fullmatch('[1-9][0-9]*',end)is not None)
    end=int(end);require(1800000000<=end-binding['start']<=1810000000)
    require(type(done)is bytes and 0<len(done)<=512 and done.endswith(b'\n')and b'\r'not in done)
    try:fields=done.decode('ascii').splitlines()
    except UnicodeDecodeError:raise ValueError('current failed-parent evidence refused')from None
    require(len(fields)==6 and fields[:4]==['NKDONE1',binding['run'],binding['cutoff'],binding['activation']]and fields[5]in {'0','10'})
    require(cutoff<=instant(fields[4])and(instant(fields[4])-cutoff).total_seconds()<=1800)
    require(type(rows)is list and 2<=len(rows)<=32);starts=[];failures=[];seen=set()
    for row in rows:
        require(type(row)is dict and all(type(k)is str and type(v)is str for k,v in row.items()))
        require(all(row.get(k)==v for k,v in {'UNIT':UNIT,'INVOCATION_ID':binding['invocation'],'_PID':'1','_UID':'0','_BOOT_ID':binding['boot']}.items()))
        stamp=row.get('__MONOTONIC_TIMESTAMP');require(type(stamp)is str and re.fullmatch('[1-9][0-9]*',stamp)is not None)
        at=int(stamp);require(binding['start']<=at<=end+10000000 and at not in seen);seen.add(at)
        require('JOB_RESULT'not in row or row['JOB_RESULT']=='failed')
        if row.get('MESSAGE_ID')=='7d4958e842da4a758f6c1cdc7b36dcc5':
            require(row.get('JOB_ID')==binding['job']and row.get('JOB_TYPE')=='start'and 'JOB_RESULT'not in row and at<=binding['start']+1000000);starts.append(at)
        elif row.get('MESSAGE_ID')=='be02cf6855d2428ba40df7e9d022f03d':
            require(row.get('JOB_ID')==binding['job']and row.get('JOB_TYPE')=='start'and row.get('JOB_RESULT')=='failed'and at>=end);failures.append(at)
        else:require(not({'JOB_ID','JOB_TYPE','JOB_RESULT'}&set(row)))
    require(len(starts)==len(failures)==1 and starts[0]<failures[0])
    return {'failedParent143Confirmed':True,'actualPid1StartFailed':True,'doneCodeDataOnly':int(fields[5]),'doneSha256':hashlib.sha256(done).hexdigest(),
      'parentNormal':False,'genuineRootDone':False,'normalUnit0or10':False,'recoveryAuthorityIssued':False,'stopAuthority':False,
      'formalAccepted':False,'elapsedSeconds':(end-binding['start'])/1000000}
