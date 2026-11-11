"""Four P020 child spec IDs, current byte reuse and explicit missing/end dependencies; no executions."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';C=R/'evidence/01_PT/020_NK-CHR-001';O=B/'evidence/PG26060-p0200101-contract-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
prefix='program/characterization/';java=prefix+'src/main/java/dev/codex/schubert/characterization/';test=prefix+'tests/java/dev/codex/schubert/characterization/'
adapter=C/'evidence/PG18716-gate-definitions-thirtyfive-v1/manifest.json';old=load(adapter);assert old['actualExit']==0 and old['tests']==35 and all(old[k]==0 for k in ['failures','errors','skipped','aborted'])
targetInputs={}
for path in [java+'TargetAdapter.java',test+'TargetAdapterTest.java',prefix+'tests/resources/cases/catalog.json']:
 raw=subprocess.check_output(['git','show',old['source']+':'+path]);assert raw==(R/path).read_bytes();targetInputs[path]=sha(R/path)
assert 'TargetAdapter.java' in old['fourCountersWholeSourceQualified'] and old['noOldExecUnion'] is True
targetMethods=[v for v in old['testSourceMethods'] if v[0].endswith('.TargetAdapterTest')];assert len(targetMethods)==3
for name in ['dev/codex/schubert/characterization/TargetAdapter','dev/codex/schubert/characterization/TargetAdapter$Target']:
 assert all(v['missed']==0 for v in old['coverage'][name].values())
cliNamed=old['partiallyCoveredNotQualified'];assert 'GateCli.java' not in old['fourCountersWholeSourceQualified']
gate=C/'evidence/PG21140-gate-synthetic-sixty-v1/manifest.json';assert sha(gate)=='1d672d4a736b9b14b684a73822ef1602ee4065b18aa171c37001bfaef7f360cd';g=load(gate)
assert g['actualExit']==0 and g['tests']==60 and all(g[k]==0 for k in ['failures','errors','skipped'])
gateProductPins={p:h for p,h in g['inputHashes'].items() if p.endswith(('.java','.json'))}
for p,h in gateProductPins.items():assert sha(R/p)==h
post=C/'evidence/PG21146-gate-independent-post-v1/manifest.json';assert sha(post)=='9183fc62c812cf8e8050c1122e5b876177bc9e0da1d0ed86eb52d5af03409408';ind=load(post);assert ind['actualExit']==0 and ind['tests']==60 and ind['realChrExecution'] is False and ind['productTestsReexecuted']==0
treePath='program/characterization/baseline/current';oldTree=subprocess.check_output(['git','rev-parse','843de94:'+treePath],text=True).strip();currentTree=subprocess.check_output(['git','rev-parse','HEAD:'+treePath],text=True).strip();assert oldTree==currentTree=='cd377044e4ca058ea219ca6a2fec82159559c72c'
assert subprocess.check_output(['git','status','--porcelain','--',treePath],text=True)==''
spec=C/'001_NK-CHR-001_単体テスト仕様書.md';text=spec.read_text();ids=['PT-CHR-NK-001','PT-CHR-G04-001','PT-CHR-G04-002','PT-CHR-CLI-002'];assert all(k in text for k in ids)
matrix=[dict(id=ids[0],main=java+'TargetAdapter.java',tests=test+'TargetAdapterTest.java',independentExpected='Exactly24 shared catalog IDs; CURRENT23 exceptNK-onlyN01, NK24; explicit normalized HTTPS URI/path/artifact and null/unknown/overwrite rejection.',existingEvidence=dict(path=str(adapter.relative_to(R)),sha256=sha(adapter)),scope='All original three TargetAdapter methods and wholeSource counters existing; exact current Main/Test/catalog bytes matched.',decision='CURRENT_BYTE_REUSE_REFERENCE_NOT_NEW_PT'),dict(id=ids[1],main=java+'GateContractValidator.java',tests=test+'GateContractTest.java',independentExpected='Pinned environment/counts/tree/source manifest and same two run schema.',existingEvidence=dict(path=str(gate.relative_to(R)),sha256=sha(gate)),scope='Current Product inputs of synthetic Gate60 matched; original GateContractTest seven-method whole suite is not represented by this selected method set.',decision='SYNTHETIC_GATE_SUBSET_REFERENCE_ORIGINAL_WHOLE_GAP'),dict(id=ids[2],main=java+'GateContractValidator.java',tests=test+'GateContractValidatorNegativeTest.java',independentExpected='Arbitrary legacy placeholder/tree/manifest/env modifications reject; trusted843 baseline tree identity required.',existingEvidence=dict(path=str(post.relative_to(R)),sha256=sha(post)),scope='Existing synthetic gate methods include exact acceptsActualBaselineCommit/rejectsAlteredBaseline cases; no new actual baseline data access.',decision='EXISTING_CURRENT_INPUT_SYNTHETIC_REF_NOT_NEW_RUN'),dict(id=ids[3],main=java+'GateCli.java',tests=test+'GateCliTest.java',independentExpected='Temporary output atomically written; existing baseline overwrite rejects; no part residue.',existingEvidence=None,scope='Source witness baselinePromotionIsImmutableCommitBoundAndSymlinkSafe; no current complete GateCli wholeSource four-counter qualification established by referenced adapter/gate evidence.',decision='SOURCE_REVIEW_ONLY_DYNAMIC_QUALITY_GAP')]
budget=load(R/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json')
def find(v):
 if isinstance(v,dict):
  if v.get('id')=='WBS-P020-01.01':return v
  for a in v.values():
   r=find(a)
   if r:return r
 if isinstance(v,list):
  for a in v:
   r=find(a)
   if r:return r
 return None
leaf=find(budget);assert leaf['externalDependencies']==['WBS-F02'] and leaf['acceptance']['status']=='NOT_ACCEPTED'
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',mainCandidates=[java+n+'.java' for n in ['TargetAdapter','GateContractValidator','GateCli']],targetInputs=targetInputs,gateProductPins=gateProductPins,specification=dict(path=str(spec.relative_to(R)),sha256=sha(spec)),matrix=matrix,baseline=dict(originalCommit='843de94',gitTree=oldTree,currentGitTree=currentTree,workingDiff='',actualBaselineFilesRead=False,written=False),existingAdapterMethodsReferenced=3,existingGateTestsReferenced=60,sourceDeclarationsDifferFromProductionCoreAndNotCombined=True,gateCliCompleteSourceQualified=False,missing=['Complete original GateCli wholeSource quality/oracle/source evidence, without executing unknown or actual backend paths.','F02 external ending dependency NOT_ACCEPTED; child acceptance blocked but independent work continues.'],decision='NOT_ACCEPTED',externalDependency='WBS-F02',productTestsExecuted=0,newCoverageMeasurements=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,specIds=4,baselineTreeUnchanged=True,childAccepted=False,newPt=0,manifestSha256=sha(O/'manifest.json'))))
