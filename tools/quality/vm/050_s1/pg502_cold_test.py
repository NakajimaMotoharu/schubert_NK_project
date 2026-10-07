"""Independent literal cold/epoch/boundary vectors. No native authority/Production PT."""
import ast,copy,pathlib,re
source=ast.parse(pathlib.Path(__file__).with_name('pg502_cold_refs.py').read_text())
names={'bounded','cold','epoch_valid'}
definitions=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in names]
env={'re':re,'BOOT':'cc9ed874-7f4f-450e-a188-8de1e42c8441',
 'FIELDS':set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())}
exec(compile(ast.Module(body=definitions,type_ignores=[]),'fixed cold pure guards','exec'),env)
checks=0
def check(actual,expected):
 global checks
 assert actual is expected;checks+=1
for code,size,limit,expected in [(0,0,0,True),(0,21337529,33554432,True),(0,33554432,33554432,True),
 (0,33554433,33554432,False),(1,0,33554432,False),(None,1,1,False),(False,1,1,False),
 (0,-1,1,False),(0,1,-1,False),(0,None,1,False),(0,1,None,False)]:check(env['bounded'](code,size,limit),expected)
v={'Id':'schubert-nk-api.service','LoadState':'loaded','ActiveState':'inactive','SubState':'dead',
 'Job':'','MainPID':'0','ControlPID':'0','InvocationID':'','Type':'simple','Restart':'on-failure',
 'RemainAfterExit':'no','Result':'success','ExecMainCode':'0','ExecMainStatus':'0',
 'ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0','KillMode':'control-group','SendSIGKILL':'no'}
check(env['cold'](v),True);check(env['cold'](None),False);check(env['cold']({}),False)
for key in v:
 p=copy.deepcopy(v);del p[key];check(env['cold'](p),False)
 p=copy.deepcopy(v);p[key]=None;check(env['cold'](p),False)
for key in ['ActiveState','SubState','Job','MainPID','ControlPID','InvocationID','Result','ExecMainCode','ExecMainStatus',
            'ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','KillMode','SendSIGKILL']:
 p=copy.deepcopy(v);p[key]='foreign';check(env['cold'](p),False)
# Golden constructed independently from SS343 canonical ASCII, not a Production encoder.
active=b'NKACT1\n91a748b4-1abe-484c-9682-44f46429b324\n2026-10-06T15:00:00.000000Z\n11111111-2222-4333-8444-555555555555\n'
gold=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=91a748b4-1abe-484c-9682-44f46429b324\ncutoff_utc=2026-10-06T15:00:00.000000Z\nactivation_id=11111111-2222-4333-8444-555555555555\npermit_sha256=-\n'
check(env['epoch_valid'](gold,active),True)
for raw,original in [(None,active),(gold,None),(b'\xff',active),(gold,b'\xff'),(gold[:-1],active),
 (gold.replace(b'INVALID',b'ISSUED'),active),(gold.replace(b'cc9ed874',b'e07aa706'),active),
 (gold.replace(b'epoch_id=11111111-2222-4333-8444-555555555555',b'epoch_id=00000000-0000-0000-0000-000000000000'),active),
 (gold.replace(b'permit_sha256=-',b'permit_sha256=foreign'),active),(gold.replace(b'\n',b'\r\n'),active),
 (gold+b'state=INVALID\n',active),(gold,active.replace(b'91a748b4',b'00000000'))]:check(env['epoch_valid'](raw,original),False)
print('PG502_COLD_ORACLE independentAssertions='+str(checks)+' productionPT0=true nativeMutation0=true')
