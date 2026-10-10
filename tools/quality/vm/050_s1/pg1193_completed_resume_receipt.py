"""Current GC state is data only; genuine new PID1/DONE receipt remains mandatory."""
import ast
import inspect
from pg1186_current_resume_done_probe import payload as previous, BINDING
import pg1117_current_done_probe as transport

GC = {'ActiveState':'inactive','SubState':'dead','MainPID':'0','Job':'','InvocationID':'',
      'Result':'success','ExecMainCode':'0','ExecMainStatus':'0',
      'ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}


def qualify_current(state):
    if type(state) is not dict or set(state) != set(GC):raise ValueError('complete current idle state required')
    if state == GC:return 'GC_CURRENT_NOT_COMPLETION_PROOF'
    expected = dict(GC, InvocationID=BINDING['invocation'],ExecMainCode='1',ExecMainStartTimestampMonotonic=str(BINDING['start']))
    exit_value=state.get('ExecMainExitTimestampMonotonic')
    if type(exit_value) is not str or not exit_value.isdigit():raise ValueError('retained current exit refused')
    expected['ExecMainExitTimestampMonotonic']=exit_value
    if state != expected or not BINDING['start'] <= int(exit_value) <= BINDING['start']+1_800_000_000:
        raise ValueError('current retained normal state refused')
    return 'RETAINED_CURRENT_SEPARATE_FROM_PID1'


def payload():
    s = previous()
    old = "if not(state['ActiveState']=='inactive'and state['SubState']=='dead'and state['MainPID']=='0'and not state['Job']and state['Result']=='success'and state['ExecMainCode']=='1'and state['ExecMainStatus']=='0'and state['InvocationID']==BINDING['invocation']and int(state['ExecMainStartTimestampMonotonic'])==BINDING['start']):raise ValueError('current parent not terminal-success')"
    if s.count(old)!=1:raise ValueError('fixed separate current receipt insertion refused')
    s = s.replace(old, 'currentStateClass=qualify_current(state)')
    function=ast.parse(inspect.getsource(qualify_current)).body
    snippet=ast.unparse(ast.Module(body=function,type_ignores=[]))
    s='GC='+repr(GC)+'\n'+snippet+'\n'+s
    s=s.replace("'scope':'RECEIPT_ONLY'", "'scope':'RECEIPT_ONLY','currentStateClass':currentStateClass,'currentGcNotUsedAsCompletionProof':True")
    ast.parse(s);return s


def main():
    s=inspect.getsource(transport.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1183-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1193-completed-resume-receipt-v1').replace('PG1117-current-done-receipt-v1','PG1193-completed-resume-receipt-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(s,'<completed new resume independent receipt>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
