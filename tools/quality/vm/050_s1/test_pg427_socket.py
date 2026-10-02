"""Independent Linux proc TCP literal matrix, no VM/Production entry or PT numerator."""
import ast, pathlib
count = 0
for tool in ['pg424_watch_api.py', 'pg425_watch_api.py', 'pg427_watch_owned_api.py']:
  source = pathlib.Path(__file__).with_name(tool).read_text()
  tree = ast.parse(source)
  node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'listens')
  namespace = {}
  exec(compile(ast.Module(body=[node], type_ignores=[]), '<tested socket function>', 'exec'), namespace)
  listens = namespace['listens']
  for address in ['0100007F:1F9B', '0000000000000000FFFF00000100007F:1F9B']:
    row = ['0:', address, '00000000:0000', '0A', '0:0', '00:0', '0', '999', '0', '12345']
    assert listens([' '.join(row)], {'12345'}, address); count += 1
    assert not listens([' '.join(row)], {'12346'}, address); count += 1
    for field, value in [(1, '00000000:1F9B'), (1, '00000000000000000000000000000000:1F9B'),
                         (1, '00000000000000000000000001000000:1F9B'), (1, '0100007F:1F9A'),
                         (1, '0200007F:1F9B'), (3, '01'), (9, 'unknown')]:
        changed = list(row); changed[field] = value
        assert not listens([' '.join(changed)], {'12345'}, address); count += 1
    for unknown in ['', 'malformed', ' '.join(row[:9])]:
        assert not listens([unknown], {'12345'}, address); count += 1
    assert not listens([], {'12345'}, address); count += 1
  info = next(n.value for n in tree.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == 'INFO' for t in n.targets))
  versions = {ast.literal_eval(k): ast.literal_eval(v) for k, v in zip(info.keys, info.values)
              if ast.literal_eval(k) != 'commit'}
  assert versions == {'app':'0.1.0-SNAPSHOT','config':'1','schema':'025','protocol':'0.1.0-SNAPSHOT'}
  count += 1
print('PG427_SOCKET_TOOL independentAssertions=' + str(count) + ' success=true productionTestCount=0')
