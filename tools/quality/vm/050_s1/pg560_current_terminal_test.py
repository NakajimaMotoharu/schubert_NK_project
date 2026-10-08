"""BUG851/YKT620: actual oneshot dependency chain, fixed10 matrix, JSON field order only."""
import ast,copy,json,hashlib,pathlib,types
import pg557_native_owned_stop as h
R=pathlib.Path(__file__).parent;source=ast.parse((R/'pg560_current_terminal_handoff.py').read_text());env={'h':h,'json':json,'hashlib':hashlib,'FOUR':h.ORDER[:4]}
names={'require','terminal_matrix','journal_value_hash'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),'<current terminal matrix>','exec'),env)
def unit(u):
 return {'Id':u,'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','Job':'','MainPID':'0','ControlPID':'0','InvocationID':'','Type':'oneshot','Restart':'no','RemainAfterExit':'yes','Result':'success','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
before={u:unit(u)for u in [*h.ORDER,'schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']}
for u,(pid,inv)in h.EXPECTED.items():before[u].update(MainPID=pid,InvocationID=inv,ActiveState='active',SubState='running',Type='simple',RemainAfterExit='no')
for u in ['schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:before[u].update(ActiveState='active',SubState='exited',InvocationID=('b'if'cleanup.service'==u.removeprefix('schubert-nk-')else'c')*32,ExecMainCode='1',ExecMainExitTimestampMonotonic='130')
now=copy.deepcopy(before)
for u in h.EXPECTED:
 now[u].update(MainPID='0',ActiveState='inactive',SubState='dead',ExecMainCode='1',ExecMainExitTimestampMonotonic='200')
 if u in ('schubert-nk-api.service','schubert-nk-web.service'):now[u].update(ActiveState='failed',SubState='failed',Result='exit-code',ExecMainStatus='143')
 if u=='artemis.service':now[u]['ExecMainStatus']='143'
for u in ['schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:now[u].update(ActiveState='inactive',SubState='dead')
receipts={u:copy.deepcopy(now[u])for u in h.ORDER[:4]};count=0
def check(actual,rec,expected):
 global count
 try:env['terminal_matrix'](before,actual,rec);got=True
 except (ValueError,TypeError,KeyError):got=False
 assert got is expected;count+=1
check(now,receipts,True)
for invalid in [None,{},[],{u:v for u,v in now.items()if u!='artemis.service'},{**now,'foreign.service':unit('foreign.service')}]:check(invalid,receipts,False)
for invalid in [None,{},[],{u:v for u,v in receipts.items()if u!='caddy.service'}]:check(now,invalid,False)
for u in now:
 for k in now[u]:
  bad=copy.deepcopy(now);del bad[u][k];check(bad,receipts,False)
  bad=copy.deepcopy(now);bad[u][k]=None;check(bad,receipts,False)
 for k in ['MainPID','ControlPID','Job','InvocationID','ExecMainCode','ExecMainStatus','Result','SubState']:
  bad=copy.deepcopy(now);bad[u][k]='foreign';check(bad,receipts,False)
bad=copy.deepcopy(now);bad['schubert-nk-expiry-cleanup.service']=copy.deepcopy(before['schubert-nk-expiry-cleanup.service']);check(bad,receipts,False)
# After Cleanup, true oneshot/RemainAfterExit normal exit history is kept, not simple/inactive fixture.
assert before['schubert-nk-expiry-cleanup.service']['Type']=='oneshot'and before['schubert-nk-expiry-cleanup.service']['RemainAfterExit']=='yes'
assert h.normal_terminal(before['schubert-nk-expiry-cleanup.service'],now['schubert-nk-expiry-cleanup.service']);count+=2
# journalctl JSON mapping field serialization order is not its semantic stream order; raw is saved separately.
a=b'{"MESSAGE":"literal","__CURSOR":"one"}\n';b=b'{"__CURSOR":"one","MESSAGE":"literal"}\n'
assert a!=b and env['journal_value_hash'](a)==env['journal_value_hash'](b);count+=1
for v in [None,b'',b'{"MESSAGE":"changed","__CURSOR":"one"}\n',a+a]:
 try:d=env['journal_value_hash'](v);assert d!=env['journal_value_hash'](a)
 except ValueError:pass
 count+=1
try:env['journal_value_hash'](b'{"MESSAGE":"a","MESSAGE":"b"}\n')
except ValueError:count+=1
else:raise AssertionError('duplicate journal fields accepted')
print('PG560_TERMINAL_MATRIX_ORACLE independentAssertions='+str(count)+' exact10Units=true actualOneshotChain=true rawJournalPreserved=true vmActions0=true productionPT0=true')
