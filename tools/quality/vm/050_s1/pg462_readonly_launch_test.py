"""Independent root-local-import cache and new-source launcher fixed-contract tests.

Host temporary fixture only, no SSH/start/stop/permit/DB/application operation.
"""
import ast,pathlib,shutil,subprocess,sys,tempfile
base=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='pg462-readonly-import-') as name:
 fixture=pathlib.Path(name)
 required={'pg457_stable_actor.py','pg462_observer_identity.py'}
 for member in required:shutil.copy2(base/member,fixture/member)
 r=subprocess.run([sys.executable,'-B','-c','import pg457_stable_actor, pg462_observer_identity'],cwd=fixture,capture_output=True)
 assert r.returncode==0 and {p.name for p in fixture.iterdir()}==required
 assert all((base/member).read_bytes()==(fixture/member).read_bytes() for member in required)
source=(base/'pg462_external_start_once.py').read_text();tree=ast.parse(source)
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
ast.parse(payload)
assert payload.count("'/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'")==1
assert 'os.O_EXCL' in payload and '==21' in payload and '==17' not in payload
assert "save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg462-code-only')" in payload
assert 'originalBudgetSeconds' in payload and '1800' in payload and 'allOwnedScopesReturnedNormally=true' in payload
wait=(base/'pg462_capture_a01_when_ready.py').read_text();ast.parse(wait)
assert 'PG462-native-a01-patched-v1' in wait and 'pg462-parent-watch-private-v1.jsonl' in wait
assert 'ca33239da3019dad50b6ebad22318130283d6756' in wait
assert '.open(\'xb\')' in wait and "wholeParentAccepted':False" in wait
print('PG462_READONLY_LAUNCH independentImports2=true noBytecodeCache=true oneStartExclusiveGuard=true namespace21=true budget1800=true newSourceNewA01=true networkVmMutation=false')
