"""BUG695/YKT499 independent installed/direct-import closed-set oracle; no stage/network."""
import ast,pathlib
root=pathlib.Path(__file__).parent
tree=ast.parse((root/'pg462_stage_v1.py').read_text());files=None;payload=None
for node in tree.body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name) and target.id=='FILES':files={ast.literal_eval(k) for k in node.value.keys}
   if isinstance(target,ast.Name) and target.id=='PAYLOAD':payload=ast.literal_eval(node.value)
assert files=={'release.tar','manifest.sig','Pg462CodeOnlyDeployment.class','pg462_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}
inner=ast.parse(payload);installed=[]
for node in inner.body:
 if isinstance(node,ast.For) and isinstance(node.target,ast.Name) and node.target.id=='name' and isinstance(node.iter,ast.Tuple):installed=list(ast.literal_eval(node.iter))
assert set(installed)==files-{'release.tar','manifest.sig'} and len(installed)==4
for name in ('pg462_watch_parent.py','pg462_observer_identity.py','pg457_stable_actor.py'):
 modules=[n.module for n in ast.walk(ast.parse((root/name).read_text())) if isinstance(n,ast.ImportFrom)]
 for module in modules:
  if module and module.startswith('pg'):assert module+'.py' in installed
assert "assert {p.name for p in tools.iterdir()}==set(EXPECTED)-{'release.tar','manifest.sig'}" in payload
print('PG462_STAGE_CLOSEDSET independentLiteral6=true installedTools4=true directImportsClosed=true unknownMemberRejected=true networkVmMutation=false')
