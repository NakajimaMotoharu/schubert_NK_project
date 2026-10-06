"""Independent terminal/argument/order oracle, no authority/VM actions/Production PT."""
import ast,pathlib,re
root=pathlib.Path(__file__).parent;source=(root/'pg482_bootstrap_existing.py').read_text();parsed=ast.parse(source);env={'re':re,'UNIT':'schubert-nk-bootstrap-admin.service','FIELDS':set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))}
node=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='normal20');exec(compile(ast.Module(body=[node],type_ignores=[]),'fixed pure terminal','exec'),env)
n=0
def check(v):
 global n
 n+=1
 if not v:raise AssertionError('bootstrap vector '+str(n))
literal={'Id':'schubert-nk-bootstrap-admin.service','LoadState':'loaded','ActiveState':'inactive','SubState':'dead','Job':'','MainPID':'0','ControlPID':'0','InvocationID':'a'*32,'Type':'oneshot','Restart':'no','RemainAfterExit':'no','Result':'success','ExecMainCode':'1','ExecMainStatus':'20','ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'200','KillMode':'control-group','SendSIGKILL':'no'}
check(env['normal20'](literal))
for key in literal:
 for value in [None,'foreign']:
  v=dict(literal);v[key]=value;check(not env['normal20'](v))
 v=dict(literal);del v[key];check(not env['normal20'](v))
for bad in [None,{},[],{**literal,'extra':'foreign'}]:check(not env['normal20'](bad))
for start,end,expected in [('0','1',False),('100','99',False),('100','30000100',True),('100','30000101',False),('100','100',True)]:check(env['normal20']({**literal,'ExecMainStartTimestampMonotonic':start,'ExecMainExitTimestampMonotonic':end})==expected)
check(source.count("'start','--no-block',UNIT")==1 and "'start-reserved.private.json'" in source)
java=(root/'Pg482BootstrapExisting.java').read_text();start=java.index('try(var database=open())');close=java.index('PREPARE_DATABASE_SCOPE_CLOSE',start);run=java.index('refs.check("run")',close);post=java.index('try(var database=open())',run);retire=java.index('refs.check("retire:',post);check(start<close<run<post<retire)
check('pgpt_bootstrap_482_synthetic' in source and 'secrets.token_urlsafe(32)' in source and 'pg468-active-account.private.json' not in source)
check('bootstrap-admin-username' in source and 'bootstrap-admin-password' in source and 'os.rename(CREDS/n,SAVE/' in source)
print('PG482_BOOTSTRAP_ORACLE independentAssertions='+str(n)+' nativeMutation0=true productionPT0=true')
