"""Independent set/count/hash/ownership audit; no production execution or qualification inflation."""
from pathlib import Path
import datetime,difflib,hashlib,json,re,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'));import trace_owner_join
b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG36800-current-protocol-source-layout-trace-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));m=ld(e/'manifest.json');assert m['actualExit']==0
for name,h in m['files'].items():assert sha(e/name)==h
main=ld(e/'source-class-owner-requirement-cases.json');layouts=ld(e/'layout64-fields389-types69.json');pm=ld(e/'physical175-method1438-owner-counters.json');reuse=ld(e/'current-source-reuse.json');design=ld(e/'design-current-pins.json');canary=ld(e/'requirement-scope-and-parser-canaries.json');inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');logical={x['path']:x for x in inv['artifacts']};assert len(main)==len({x['sourcePath'] for x in main})==165
canonical=[]
for x in main:
 p=x['sourcePath'];assert sha(r/p)==x['currentSha256']==hashlib.sha256(subprocess.check_output(['git','show',m['sourceCore']+':'+p])).hexdigest();owner=trace_owner_join.canonical(p,logical);assert x['canonicalOwner']==owner['canonicalOwner'] and owner['canonicalCostOwner'];canonical.append(dict(path=p,currentSha256=x['currentSha256'],**owner,auditOwner='WBS-G13.01',productionChangeOwner=None,productionChangedByAudit=False,additionalSharedCostPp=0))
assert len(pm['physicalSource'])==len(pm['classHashes'])==175 and set(pm['physicalSource'].values())=={x['sourcePath'].split('/src/main/java/')[1][:-5] for x in main};methodKeys=[(x['className'],x['name'],x['descriptor']) for x in pm['methods']];assert len(methodKeys)==len(set(methodKeys))==1438
assert all(x['owner']==logical[x['source']]['owner'] for x in pm['methods']);assert sum(x['rawCounters']['METHOD']['missed'] for x in pm['methods'])==4 and sum(x['rawCounters']['BRANCH']['missed'] for x in pm['methods'])==58;assert all(x['knownQualityGap']=='BUG3111/YKT2583' for x in pm['methods'] if x['rawCounters']['METHOD']['missed'] or x['rawCounters']['BRANCH']['missed'])
assert len(layouts)==len({x['layout'] for x in layouts})==64;types={t['name'] for x in layouts for t in x['types']};assert len(types)==69;fields=[row for x in layouts for area in x['areas'].values() for row in area['oracleFields']];assert len(fields)==389
caseSet=set()
for p,h in reuse['allOriginalInputHashes'].items():assert sha(r/p)==h
cfg=ld(b/'input/4425_ssc447_profile.json');prep=ld(r/cfg['slots']['prepare']/'manifest.json');caseSet={x['classname']+'#'+x['name'] for x in prep['expectedCases']};assert len(caseSet)==152
for x in main:assert set(x['actualCaseScopeLinks'])<=caseSet and (x['actualCaseScopeLinks'] or x['rawCodeMethods']==0)
for x in layouts:
 assert set(x['actualJUnitCases'])<=caseSet and len(x['actualJUnitCases'])==6
 for area in x['areas'].values():assert [(a['start'],a['length'],a['wire'],a['presence']) for a in area['uiFields']]==[(a['start'],a['length'],a['wire'],a['presence']) for a in area['oracleFields']]
 for t in x['types']:assert logical[t['path']]['owner']==t['owner'] and t['path'] in {v['sourcePath'] for v in main}
for p,h in design['documents'].items():assert hashlib.sha256(subprocess.check_output(['git','show',design['originMain']+':'+p])).hexdigest()==h
# A separately written UI233 table scan reconciles all four numeric shape columns.
uiName=next(p for p in design['documents'] if '/233_' in p);text=subprocess.check_output(['git','show',design['originMain']+':'+uiName],text=True);scan={}
for line in text.splitlines():
 if not line.startswith('|'):continue
 parts=[v.strip() for v in line.strip('|').split('|')]
 if len(parts)<9:continue
 keys=re.findall(r'`([A-Z0-9]{8})`',parts[1])
 if not keys:continue
 assert len(keys)==1 and keys[0] not in scan;scan[keys[0]]=list(map(lambda v:int(v.replace(',','')),parts[3:7]))
assert len(scan)==64
for x in layouts:assert scan[x['layout']]==[x['ui'][k] for k in ['data','record','maximum','total']]==x['ss']['lengths']
assert len(canary['parserCanaries'])==6 and all(v['passed'] for v in canary['parserCanaries']);assert {x['id'] for x in canary['requirements']}=={'SYS-011','SCP-001','SCP-002','SCP-003','SCP-006'}
# Only the necessary F01 dependency is reviewed; the other historical16 are not requalified.
policy='documents/400_PGPT/410_工程標準/411_コーディング規約.md';old=subprocess.check_output(['git','show','7fffab57a567914956b66452e5e54388642efdec:'+policy],text=True);current=(r/policy).read_text();changes=list(difflib.SequenceMatcher(a=old.splitlines(),b=current.splitlines(),autojunk=False).get_opcodes());removed=[line for tag,a,z,_,_ in changes if tag in ['delete','replace'] for line in old.splitlines()[a:z] if line.strip()];assert not removed;assert all(token in current for token in ['Java 25','命名','Module依存','Null','transaction','redaction','SQL','固定長codec','並行','Testability','静的解析','禁止事項']);assert sha(r/policy)==hashlib.sha256(subprocess.check_output(['git','show',m['sourceCore']+':'+policy])).hexdigest()
out=b/'evidence/PG36802-current-protocol-trace-independent-post-v1';out.mkdir();(out/'canonical-owner-cost-join165.json').write_text(json.dumps(canonical,ensure_ascii=False,indent=2)+'\n');f01=dict(actualExit=0,currentSource=m['sourceCore'],policy=dict(path=policy,sha256=sha(r/policy)),oldAcceptedSource='7fffab57a567914956b66452e5e54388642efdec',policyDelta='Existing base rules unchanged; additive guard/trace/static/TYPE_USE clarifications reviewed, no waiver',mandatoryTopicDefinitionsPresent=True,neededExternalDependency='WBS-F01',newAcceptanceCredit=0,oldOther16Requalified=False,F03Accepted=False,productQualityNotInferred=True);(out/'f01-needed-policy-dependency-only.json').write_text(json.dumps(f01,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=m['sourceCore'],originalUnit=m['originalUnit'],traceEvidence=ref(e/'manifest.json'),derivedCounts=dict(main=len(main),physical=len(pm['physicalSource']),methods=len(methodKeys),layouts=len(layouts),fields=len(fields),types=len(types),caseScope=len(caseSet)),canonicalOwnerAndCostPairsExact=True,productionChangeOwnerNotInvented=True,allSourceCurrentAndCoreHashExact=True,layoutNumericSourceIndependentlyReparsed=True,fieldShapeSet389Reconciled=True,allClassAndMethodCounterOwnersKnown=True,rawMissedMethods=4,rawMissedBranches=58,qualityGapsNotClosed=True,parserCanaries=6,F01RequiredPolicyReviewed=True,scopeReadStaticDocumentOnly=True,productTestsExecuted=0,old152Replayed=0,currentG1301ScopeTraceAccepted=True,originalG13ParentAccepted=False,newOriginalAcceptance=0,formalUpdated=False,effortRate=None,files={p.name:sha(p) for p in out.iterdir() if p.is_file()},verifier=ref(Path(__file__).resolve()),canonicalJoinTool=ref(r/'tools/quality/trace_owner_join.py'));(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,counts=value['derivedCounts'],G1301LocalTrace=True,originalG13Parent=False,old152Replayed=0,newOriginalAcceptance=0)))
