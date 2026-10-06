"""Read-only field-delta diagnosis; no refs/start/stop/DB/namespace mutation."""
import ast,pathlib,json,subprocess
from pg466_term_witness import FIELDS
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-tools-v2')
tree=ast.parse((TOOLS/'pg477_partial_handoff.py').read_text())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','command','policy']]
all_node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALL' for t in n.targets))
env={'ast':ast,'pathlib':pathlib,'json':json,'subprocess':subprocess,'FIELDS':FIELDS,'TOOLS':TOOLS}
exec(compile(ast.Module(body=[all_node,*functions],type_ignores=[]),'<fixed read-only inspection>','exec'),env)
policy=env['policy']()
proof=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/refs-activate-before.private.json').read_text())
for unit in env['ALL']:
 current=policy['show'](unit);old=proof['stopped'][unit]
 delta=[k for k in set(current)|set(old) if current.get(k)!=old.get(k)]
 config=policy['show'](unit,policy['CONFIG']);before=proof['configuration'][unit]
 changed=[k for k in set(config)|set(before) if config.get(k)!=before.get(k)]
 print(unit,'stateDelta='+','.join(sorted(delta)),'configDelta='+','.join(sorted(changed)))
 if unit=='caddy.service':print('EXEC_BEFORE',before['ExecStart']);print('EXEC_AFTER',config['ExecStart'])
