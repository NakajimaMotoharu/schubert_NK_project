"""BUG750 handwritten Caddy/oneshot states; pure refusal checks, no service action."""
from pg469_owned_stop import normal_terminal
count=0
def check(ok):
 global count
 count+=1
 if not ok:raise AssertionError('normal terminal vector '+str(count))
before={'Id':'caddy.service','LoadState':'loaded','ActiveState':'active','SubState':'running','Job':'','MainPID':'42','ControlPID':'0','InvocationID':'a'*32,'Type':'notify','Restart':'on-failure','RemainAfterExit':'no','Result':'success','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
after={**before,'ActiveState':'inactive','SubState':'dead','MainPID':'0','ExecMainCode':'1','ExecMainStatus':'0','ExecMainExitTimestampMonotonic':'200'}
check(normal_terminal(before,after));check(not normal_terminal(None,after));check(not normal_terminal(before,None))
for key in before:
 for side in ('before','after'):
  for mode in ('missing','null','foreign'):
   b=before.copy();a=after.copy();target=b if side=='before' else a
   if mode=='missing':del target[key]
   else:target[key]=None if mode=='null' else 'foreign'
   check(not normal_terminal(b,a))
for unit in ['schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service']:
 b={**before,'Id':unit,'MainPID':'0','Type':'oneshot','RemainAfterExit':'yes','SubState':'exited','ExecMainCode':'1','ExecMainStatus':'0','ExecMainExitTimestampMonotonic':'150'}
 a={**b,'ActiveState':'inactive','SubState':'dead'};check(normal_terminal(b,a))
 for key in ('SubState','ExecMainCode','ExecMainStatus','ExecMainExitTimestampMonotonic'):
  bad=a.copy();bad[key]='foreign';check(not normal_terminal(b,bad))
for value in ['100','101']:
 a={**after,'ExecMainExitTimestampMonotonic':value};check(normal_terminal(before,a))
for value in ['99','-1','']:
 a={**after,'ExecMainExitTimestampMonotonic':value};check(not normal_terminal(before,a))
print('PG469_NORMAL_TERMINAL_ORACLE independentAssertions='+str(count)+' nativeMutation0=true productionPT0=true')
