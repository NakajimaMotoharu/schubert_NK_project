"""Fixed release/run/source/budget oracle; does not invoke SSH/start or guest payload."""
import ast,pathlib
r=pathlib.Path(__file__).parent
source=(r/'pg478_external_start_once.py').read_text();tree=ast.parse(source)
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
guest=ast.parse(payload);checks=0
def check(v):
 global checks
 checks+=1;assert v
for token in ['pg477-six-full-v1.source','pg477-six-full-v1.exit','0.1.0-PG477','pg478-newrun-preflight-v2','cleanup-oracle.private.json','originalBudgetSeconds\':1800','O_EXCL','len(list(startup.iterdir()))==65','priorGuardRequiresReattachment']:
 check(token in source)
fixed=[n for n in ast.walk(guest) if isinstance(n,ast.Constant) and isinstance(n.value,bytes)]
check(any(n.value==b'allNewScopesReturnedNormally=true\npartialDeploymentAcceptedSeparately=true\noldCloseUnknown=true\nstarts0=true\ndeployReplay0=true\npermits0=true\nddl0=true\n' for n in fixed))
check(source.count("'start','--no-block','schubert-nk-morning-controller.service'")==1)
for name in ['pg478_prepare_observer_v1.py','pg478_parent_observer_v1.sh','pg478_watch_parent.py']:
 text=(r/name).read_text();check('PG475' not in text and 'pg475' not in text)
 for old in ['979c5ac3e9c28ae76363adacdf9f0736f5a59df1','9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806']:check(old not in text)
check('cce61f63900b1479f9f8dbdc338e222b1c8c38a3' in (r/'pg478_parent_observer_v1.sh').read_text())
check('len(data[\'oldExec\'])==27' in (r/'pg478_prepare_observer_v1.py').read_text())
print('PG478_SOURCE_BINDING_TEST independentAssertions='+str(checks)+' starts0=true productionPT0=true')
