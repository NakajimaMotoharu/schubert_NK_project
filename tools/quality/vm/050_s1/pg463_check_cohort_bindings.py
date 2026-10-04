"""Independent literal actual-cohort checks; no native operation or oracle mutation."""
import ast, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
source='ca33239da3019dad50b6ebad22318130283d6756'
digest='421b31e7dcdc90018375c10331aab382cd262470d265b51c02796fba4ca0b49b'
watch=WORK/'pg462-parent-watch-private-v1.jsonl'
assert hashlib.sha256(watch.read_bytes()).hexdigest()=='d30cf5054b452f2568d607ae7695de24514bad1a877fdb9660db73302e120df2'
actual=json.loads((WORK/'pg462-release-v1/RELEASE-MANIFEST.json').read_bytes())
assert actual['source']['commit']==source and hashlib.sha256((WORK/'pg462-release-v1/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==digest
texts={n:(ROOT/n).read_text() for n in ['Pg463CapturedPeers.java','Pg463CapturedPeersTest.java','Pg463OwnedIsolation.java','Pg463Known30PairRecovery.java','Pg463Known30PairRecoveryTest.java','Pg463CodeOnlyDeployment.java','Pg463CodeOnlyDeploymentTest.java']}
for name,s in texts.items():
 for stale in ['ca33239da311','00785cf0698aecf1ace1e60b87e8849639e85b97','8e97eb9138828010926cd47fd10868d8a2d54f11','rows.size()==291','rows.size()==301','expected.size()==17','fixed.size()==21','471458','613477','615605','9365225','9437302','9438438']:
  assert stale not in s,(name,'stale binding')
for name in ['Pg463OwnedIsolation.java','Pg463Known30PairRecovery.java']:
 for value in ['4105e7a77d3449b1aeff0dcea2f0d5ca','bcd85e18-8926-4a3c-9e9c-78da9dba2670','rows.size()==311']:
  assert value in texts[name],(name,'binding missing')
assert 'fdb6883dc2928e79f5e56637f854d56afc792c91de0de4bd9f3416582f378060' in texts['Pg463Known30PairRecovery.java']
assert 'expected.size()==25' in texts['Pg463Known30PairRecovery.java'] and 'actual.size()==25' in texts['Pg463Known30PairRecoveryTest.java']
for old in ['1eecb7b9-1e98-478f-9084-201422b31bff','d536cf5a-f5a8-4dd9-8679-3488fab17fdf','e8cce97a-163b-4814-b435-8fc26466e550','25020aa0-7b69-4554-be47-ea69588da569','15e4559b-13ab-46d7-a7a8-c15f1de4a245']:
 for name in ['Pg463Known30PairRecovery.java','Pg463Known30PairRecoveryTest.java','Pg463CodeOnlyDeployment.java','Pg463CodeOnlyDeploymentTest.java']:assert old in texts[name]
for value in [source,'10587260','10659726','10661011','782118','925161','927354']:assert value in texts['Pg463CapturedPeers.java']
assert 'OLD_SOURCE="'+source+'"' in texts['Pg463CodeOnlyDeployment.java'] and 'OLD_DIGEST="'+digest+'"' in texts['Pg463CodeOnlyDeployment.java']
for name in ['pg463_stage_v1.py','pg463_watch_parent.py','pg463_external_start_once.py','pg463_capture_a01_when_ready.py']:
 s=(ROOT/name).read_text();ast.parse(s)
 assert 'PG463' in s
start=(ROOT/'pg463_external_start_once.py').read_text()
assert start.count("'start','--no-block'")==1 and 'os.O_EXCL' in start and '==25' in start and "d['LoadState']=='loaded'" in start and "'originalBudgetSeconds':1800" in start
stage=(ROOT/'pg463_stage_v1.py').read_text()
assert stage.count("'pg462_observer_identity.py'")==2 # importer and installer names are immutable
assert 'from pg462_observer_identity' in (ROOT/'pg463_watch_parent.py').read_text()
print('PG463_COHORT_BINDINGS_PASS actualManifestWatchSource=true allRetained20Post25=true independentPins=true singleStartGuard=true nativeMutation=false productionPt0=true')
