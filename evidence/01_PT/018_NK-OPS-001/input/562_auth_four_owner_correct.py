"""Fix exact authentication responsibilities and derive a separate current ownership view."""
from pathlib import Path
from collections import defaultdict
import datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/560_auth_four_owner_scope.json';O=B/'evidence/PG23880-auth-four-owner-correction-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C);assert not O.exists();wp=R/cfg['wbsBefore']['path'];pp=R/cfg['planBefore']['path'];assert sha(wp)==cfg['wbsBefore']['sha256'] and sha(pp)==cfg['planBefore']['sha256'];wb=load(wp);plan=load(pp);tasks={v['id']:v for v in plan['tasks']};artifact={v['path']:v for v in wb['artifacts']};assert len(artifact)==len(wb['artifacts'])==1061
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['source']==cfg['source'] and normal['actualExit']==0
recipes={'LoginApplicationAssembly.java':['Production Login transaction graph','return new LoginInboxService(','new LoginReplayService('],'LogoutApplicationAssembly.java':['Existing Logout transaction participants','return new LogoutInboxService(','new LogoutReplayService('],'LoginResult.java':['Disjoint success/failure shape','sealed interface LoginResult','record Success(','record Failure('],'LoginUsername.java':['Display/input is 64 UTF-8 bytes','record LoginUsername(','Normalizer.normalize','value.toLowerCase(Locale.ROOT)']}
changes=[]
for n,owner in cfg['ownerCorrections'].items():
 assert n in artifact and artifact[n]==cfg['beforeRows'][n] and artifact[n]['owner']==artifact[n]['costOwner']=='WBS-P018-09'
 assert sha(R/n)==cfg['sourcePins'][n]==normal['begin']['inputHashes'][n] and owner in tasks
 text=(R/n).read_text();assert all(v in text for v in recipes[Path(n).name])
 before=artifact[n].copy();artifact[n]['owner']=artifact[n]['costOwner']=owner
 artifact[n]['basis']='PG23880: explicit SS314 authentication/inbox/logout responsibility; broad Log substring selector is not authoritative. Previous row retained in PG23884.'
 changes.append(dict(path=n,before=before,after=artifact[n].copy(),sourceSha256=sha(R/n),responsibilityEvidence=recipes[Path(n).name],ownerTitle=tasks[owner]['title']))
candidates=[dict(path=v['path'],owner=v['owner'],costOwner=v['costOwner']) for v in wb['artifacts'] if any(t in Path(v['path']).name for t in ('Login','Logout'))]
assert len(candidates)==35 and not any(v['owner']=='WBS-P018-09' for v in candidates)
projection=defaultdict(list);reverse={}
for v in wb['artifacts']:
 n=v['path'];owner=v['owner'];cost=v['costOwner'];assert owner in tasks and cost in tasks and n not in reverse
 projection[owner].append(n);reverse[n]=dict(owner=owner,costOwner=cost)
projection={k:sorted(v) for k,v in sorted(projection.items())};assert sum(map(len,projection.values()))==len(reverse)==1061
key='currentRegisteredArtifactOwnershipProjection20261108';assert key not in plan
O.mkdir()
for name,value in [('four-owner-changes.json',changes),('auth-name-horizontal-candidates.json',candidates),('current-owner-to-artifacts.json',projection),('current-artifact-to-owner.json',reverse)]:
 (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
files={n:sha(O/n) for n in ('four-owner-changes.json','auth-name-horizontal-candidates.json','current-owner-to-artifacts.json','current-artifact-to-owner.json')}
plan[key]=dict(source=cfg['source'],registeredLogicalArtifacts=1061,scope='CURRENT_CANONICAL_OWNER_VIEW_OF_REGISTERED_LOGICAL_ARTIFACTS_NOT_CURRENT_FILE_EXISTENCE_TEST_OR_ACCEPTANCE',ownerToArtifacts=dict(path=str((O/'current-owner-to-artifacts.json').relative_to(R)),sha256=files['current-owner-to-artifacts.json']),artifactToOwner=dict(path=str((O/'current-artifact-to-owner.json').relative_to(R)),sha256=files['current-artifact-to-owner.json']),correctedAuthenticationRows=4,historicalOwnedArtifactsEvidencePlansAndBudgetsUnchanged=True,artifactOwnersMayBeResponsibilityParentsNotExecutionCostLeaves=True,newAcceptance=0,newProductTests=0,effortRate=None,wholeG13Accepted=False,whole451Accepted=False)
pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),wbsBefore=cfg['wbsBefore'],planBefore=cfg['planBefore'],wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),planAfter=dict(path=str(pp.relative_to(R)),sha256=sha(pp)),overlayKey=key,correctedOwnerRows=4,authFilenameCandidates=35,nonChangedFilenameCandidates=31,registeredLogicalArtifacts=1061,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,assembliesInvoked=False,originalBudgetAndAcceptanceUnchanged=True,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,files=files,bugs=['BUG-2507'],ykts=['YKT-2245'],tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,ownerCorrections=4,authCandidates=35,logicalArtifactProjection=1061,manifestSha256=sha(O/'manifest.json'))))
