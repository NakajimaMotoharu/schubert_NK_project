"""Hand-written twelve-source oracle and whole-token negatives; no Production execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,subprocess,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG23862-monitoring112-declared-rd-join-v1';O=B/'evidence/PG23864-monitoring112-declared-rd-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='ca38464f11bb3ce52601a5a3dd78240932fa8bc30333d53627c9c0d7a883734b'
assert m['actualExit']==m['newAcceptance']==0 and m['wholeG13Accepted'] is False
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
obs=R/cfg['observations']['path'];assert sha(obs)==cfg['observations']['sha256'];observations={v['path']:v for v in load(obs)}
for n,h in m['files'].items():assert sha(P/n)==h
wp=R/m['wbsAfter']['path'];assert sha(wp)==m['wbsAfter']['sha256'];wb=load(wp)
raw=subprocess.check_output(['git','show',m['observerHead']+':'+cfg['wbsBefore']['path']],cwd=R);assert hashlib.sha256(raw).hexdigest()==cfg['wbsBefore']['sha256'];old=json.loads(raw)
assert old=={k:v for k,v in wb.items() if k!=m['overlayKey']}
rd=R/cfg['rd']['path'];assert sha(rd)==cfg['rd']['sha256'] and rd.read_bytes()==subprocess.check_output(['git','show','origin/main:'+cfg['rd']['path']],cwd=R)
requirements={v['id']:v for v in wb['requirements'] if v['id'].startswith('MON-')};valid=set(requirements);assert len(valid)==13
prefix='dev/codex/schubert/nk/batch/monitoring/'
six=['MON-005','MON-006','MON-007','MON-008','MON-009','MON-013']
nine=['MON-005','MON-006','MON-007','MON-008','MON-009','MON-010','MON-011','MON-012','MON-013']
four=['MON-010','MON-011','MON-012','MON-013']
# Independent literal expected links, written from approved declarations before post execution.
expected={prefix+'AlertLifecycle.java':six,prefix+'AlertRegistry.java':six,prefix+'AlertThresholds.java':six,prefix+'ContinuousConditionWindow.java':nine,prefix+'MetricContract.java':['MON-005','MON-006','MON-009','MON-013'],prefix+'MonitoringModePolicy.java':four,prefix+'MonitoringPolicyEngine.java':nine,prefix+'MonitoringStatusText.java':nine,prefix+'ObservationContext.java':nine,prefix+'TimedFilesystemMonitor.java':nine,prefix+'package-info.java':four,'dev/codex/schubert/nk/web/monitoring/HttpMetricContract.java':nine}
expectedTokens={n:('MON005..009/013' if n.rsplit('/',1)[-1] in ('AlertLifecycle.java','AlertRegistry.java','AlertThresholds.java') else 'MON005/006/009/013' if n.endswith('/MetricContract.java') else 'MON010..013' if n.endswith(('/MonitoringModePolicy.java','/package-info.java')) else 'MON005..013') for n in expected}
rows=load(P/'source-declared-refs.json');assert len(rows)==112 and len({v['path'] for v in rows})==112 and {v['path'] for v in rows}==set(cfg['selectedSourcePaths'])
reverse={k:[] for k in requirements};links=0;known=0
for row in rows:
 n=row['path'];key=n.split('/src/main/java/')[1];ids=expected.get(key,[]);o=observations[n]
 assert row['sourceSha256']==o['sourceSha256'] and row['classDeclaration']==o['classDoc']
 assert row['parsed']['ids']==ids and row['parsed']['unparsedNumericTokens']==[] and row['canonicalRequirementRows']=={k:requirements[k] for k in ids}
 assert row['status']==('EXACT_DECLARED_REFERENCE_ONLY' if ids else 'DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING')
 assert row['implementationAccepted'] is False and row['ptEvidenceInferred'] is False and row['coverageQualified'] is False
 tokens=row['parsed']['tokens'];assert len(tokens)==(1 if ids else 0)
 if ids:
  t=tokens[0];assert t['token']==expectedTokens[key] and row['classDeclaration'][t['start']:t['end']]==t['token'] and t['ids']==ids and t['problem'] is None
  known+=1;links+=len(ids)
 for ident in ids:reverse[ident].append(n)
assert known==12 and links==84 and len([k for k,v in reverse.items() if v])==9
assert reverse==load(P/'requirement-reverse-refs.json')
before=B/'evidence/PG23868-mon-whole-token-before-v1';bm=load(before/'manifest.json');assert sha(before/'557_monitoring112_declared_rd_join.py')==bm['beforeSourceSha256']==m['tool']['sha256']
current=R/m['tool']['path'];assert sha(current)!=m['tool']['sha256']
spec=importlib.util.spec_from_file_location('own_declared_reference_guard',current);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# Corrected parser is tested; original valid112 data remains immutable and separately qualified.
for row in rows:assert mod.references(row['classDeclaration'] or '',valid)==row['parsed']
bad=['MON005.006','MON005/006.1','MON005..013x','MON005006','MON005..999','MON013..005','MON005..','MON005-006','MON-999']
for text in bad:
 result=mod.references(text,valid);assert not result['ids'] and (result['unparsedNumericTokens'] or any(v['problem'] for v in result['tokens']))
positive=[('MON005..009/013',six),('MON005/006/009/013',['MON-005','MON-006','MON-009','MON-013']),('MON010..013.',four),('MON-005/MON-006',['MON-005','MON-006']),('MON005..013;',nine)]
for text,ids in positive:
 result=mod.references(text,valid);assert result['ids']==ids and not result['unparsedNumericTokens'] and not any(v['problem'] for v in result['tokens'])
for text in ['PT-OPS-MONMODE-001..007','MONWINDOW001..008','NK-MON-005','MONSTATUS-001..006']:
 assert mod.references(text,valid)==dict(ids=[],tokens=[],unparsedNumericTokens=[])
overlay=wb[m['overlayKey']];assert overlay['withExplicitCanonicalReferences']==12 and overlay['uniqueSourceRequirementLinks']==84 and overlay['docContextOnlyPreciseMappingPending']==100 and overlay['implementedRequirementsInferred'] is False
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json'),originalToolSha256=m['tool']['sha256'],originalDataUnmodified=True,originalProducerRerun=False),correctedParser=dict(path=str(current.relative_to(R)),sha256=sha(current)),wbsAfter=m['wbsAfter'],sourcePrograms=112,explicitReferenceSources=12,sourceRequirementLinks=84,distinctRequirementIds=9,docContextOnlyPreciseMappingPending=100,unknownNumericTokensInOriginalDataset=0,independentLiteralSourceOracleCount=12,malformedWholeTokenNegatives=9,positiveGrammarVectors=5,nonRequirementFamilyVectors=4,original112DatasetUnaffectedByParserBoundaryFix=True,sourceBodiesReread=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,environment=dict(os=os.uname().sysname,release=os.uname().release,python=sys.version.split()[0]),command='PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/558_monitoring112_declared_rd_independent_post.py',bugs=['BUG-2505'],ykts=['YKT-2243'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sources=112,literalOracles=12,links=84,pending=100,malformedNegatives=9,positiveVectors=5,familyVectors=4,manifestSha256=sha(O/'manifest.json'))))
