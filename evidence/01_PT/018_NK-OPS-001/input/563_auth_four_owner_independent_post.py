"""Independent exact delta and full registered-logical-artifact owner projection checks."""
from pathlib import Path
import copy,datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG23880-auth-four-owner-correction-v1';O=B/'evidence/PG23882-auth-four-owner-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='9c88eeb85104e6e07e8c4445fa1ee3198d682c40a801431914c3d8ec2ec93acd'
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(P/n)==h
wp=R/m['wbsAfter']['path'];pp=R/m['planAfter']['path'];assert sha(wp)==m['wbsAfter']['sha256'] and sha(pp)==m['planAfter']['sha256'];wb=load(wp);plan=load(pp)
old=[]
for ref in (cfg['wbsBefore'],cfg['planBefore']):
 raw=subprocess.check_output(['git','show',cfg['observerHead']+':'+ref['path']],cwd=R);assert hashlib.sha256(raw).hexdigest()==ref['sha256'];old.append(json.loads(raw))
oldWbs,oldPlan=old;assert oldPlan=={k:v for k,v in plan.items() if k!=m['overlayKey']}
assert {k:v for k,v in oldWbs.items() if k!='artifacts'}=={k:v for k,v in wb.items() if k!='artifacts'}
oldRows={v['path']:v for v in oldWbs['artifacts']};current={v['path']:v for v in wb['artifacts']};assert len(oldRows)==len(current)==len(wb['artifacts'])==1061
base='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'
expected={base+'LoginApplicationAssembly.java':'WBS-P007-04',base+'LogoutApplicationAssembly.java':'WBS-P007-05',base+'LoginResult.java':'WBS-P007-01',base+'LoginUsername.java':'WBS-P007-01'}
assert expected==cfg['ownerCorrections']
for n,old in oldRows.items():
 if n not in expected:assert old==current[n]
 else:
  assert old==cfg['beforeRows'][n] and old['owner']==old['costOwner']=='WBS-P018-09'
  assert {k:v for k,v in old.items() if k not in ('owner','costOwner','basis')}=={k:v for k,v in current[n].items() if k not in ('owner','costOwner','basis')}
  assert current[n]['owner']==current[n]['costOwner']==expected[n] and sha(R/n)==cfg['sourcePins'][n]
sourceWitnesses={'LoginApplicationAssembly.java':['Login transaction graph','LoginInboxService create(','new LoginInboxService(','new LoginReplayService('],'LogoutApplicationAssembly.java':['Logout transaction participants','LogoutInboxService create(','new LogoutInboxService('],'LoginResult.java':['sealed interface LoginResult','ResultCode resultCode();','int retryAfterSeconds();'],'LoginUsername.java':['record LoginUsername(String value)','Display/input is 64 UTF-8 bytes','value.toLowerCase(Locale.ROOT)']}
for n in expected:
 text=(R/n).read_text();assert all(token in text for token in sourceWitnesses[Path(n).name])
candidates=load(P/'auth-name-horizontal-candidates.json');actualCandidates=[dict(path=v['path'],owner=v['owner'],costOwner=v['costOwner']) for v in wb['artifacts'] if any(t in Path(v['path']).name for t in ('Login','Logout'))]
assert candidates==actualCandidates and len(candidates)==35 and not any(v['owner']=='WBS-P018-09' for v in candidates)
forward=load(P/'current-owner-to-artifacts.json');reverse=load(P/'current-artifact-to-owner.json')
def valid(rows,fwd,rev):
 try:
  assert len(rows)==len({v['path'] for v in rows})==1061
  index={v['path']:v for v in rows};assert set(index)==set(rev)
  for n,owner in expected.items():assert index[n]['owner']==index[n]['costOwner']==owner
  assert sum(map(len,fwd.values()))==1061
  for n,v in index.items():
   assert rev[n]==dict(owner=v['owner'],costOwner=v['costOwner'])
   assert v['owner'] in fwd and fwd[v['owner']].count(n)==1
  assert set(n for group in fwd.values() for n in group)==set(index)
  return True
 except (AssertionError,KeyError,TypeError):return False
assert valid(wb['artifacts'],forward,reverse)
negative=[]
for label,change in [('reclassify-as-log',lambda v:v.update(owner='WBS-P018-09',costOwner='WBS-P018-09')),('cost-owner-only-log',lambda v:v.update(costOwner='WBS-P018-09'))]:
 altered=copy.deepcopy(wb['artifacts']);v=next(v for v in altered if v['path'] in expected);change(v);assert not valid(altered,forward,reverse);negative.append(label)
altered=copy.deepcopy(forward);key=next(iter(altered));altered[key].append(altered[key][0]);assert not valid(wb['artifacts'],altered,reverse);negative.append('duplicate-forward-edge')
altered=copy.deepcopy(reverse);del altered[next(iter(altered))];assert not valid(wb['artifacts'],forward,altered);negative.append('missing-reverse-edge')
altered=copy.deepcopy(forward);owner=expected[base+'LoginResult.java'];altered[owner].remove(base+'LoginResult.java');assert not valid(wb['artifacts'],altered,reverse);negative.append('missing-corrected-owned-artifact')
overlay=plan[m['overlayKey']];assert overlay['registeredLogicalArtifacts']==1061 and overlay['newAcceptance']==overlay['newProductTests']==0 and overlay['historicalOwnedArtifactsEvidencePlansAndBudgetsUnchanged'] is True and overlay['wholeG13Accepted'] is False and overlay['whole451Accepted'] is False
assert plan['tasks']==oldPlan['tasks'] and len(plan['tasks'])==190
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),wbsAfter=m['wbsAfter'],planAfter=m['planAfter'],correctedOwnerRows=4,authFilenameCandidates=35,unchangedNonTargetFilenameCandidates=31,registeredLogicalArtifacts=1061,historical190TaskDefinitionsBudgetsAcceptanceUnchanged=True,independentMetadataNegativeChecks=len(negative),negativeLabels=negative,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,assembliesInvoked=False,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,bugs=['BUG-2507'],ykts=['YKT-2245'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,corrected=4,authFilenameCandidates=35,projectionArtifacts=1061,negativeChecks=len(negative),manifestSha256=sha(O/'manifest.json'))))
