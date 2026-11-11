"""Independent public-only post of owner proof and column-contract negative checks; no product PT."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26254-header-field-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'evidence/PG26250-header-layout-field-current-criteria-v1/manifest.json';assert sha(p)=='74f615ceb33c98fcea90f20ff0fd72c929c7afac61d648f47bb034aaf0686bc7';m=load(p)
for name,h in m['files'].items():assert sha(p.parent/name)==h
assert m['criteriaVerified']==m['criteriaTotal']==9 and m['canonicalLayoutRows']==64 and m['canonicalPhysicalFieldRows']==389 and m['productTestsReexecuted']==m['newOriginal190Acceptance']==0
f=R/m['sameSourceRunManifest']['path'];assert sha(f)==m['sameSourceRunManifest']['sha256'];full=load(f);assert full['actualExit']==0 and full['tests']==124 and full['source']==m['source'] and full['singleSession']==m['run'];assert all(full[k]==0 for k in ['failures','errors','skipped','aborted']);assert sha(f.parent/'coverage.xml')==full['files']['coverage.xml']
xml={x.get('name'):x for x in E.parse(f.parent/'coverage.xml').findall('.//class')};expected={'WBS-P001-01':(6,6,137,30,5,88),'WBS-P001-02':(20,29,564,84,22,170),'WBS-P002-01':(43,43,457,121,39,188)}
rows=load(p.parent/'source-physical-counters.json'); owners=load(p.parent/'owner-scopes.json');assert len(rows)==78
for x in owners:
 a,b,l,method,c,branch=expected[x['owner']];assert (x['sourceArtifacts'],x['physicalClasses'])==(a,b)
 for k,n in [('LINE',l),('METHOD',method),('CLASS',c),('BRANCH',branch)]:assert x['coverage'][k]=={'covered':n,'missed':0}
 for row in rows:
  if row['owner']!=x['owner']:continue
  assert sha(R/row['path'])==row['sourceSha256'];node=xml.get(row['physicalClass']);v={q.get('type'):dict(covered=int(q.get('covered')),missed=int(q.get('missed'))) for q in node.findall('counter')} if node is not None else {};assert v==row['counters']
assert next(x for x in owners if x['owner']=='WBS-P002-01')['dependencies']==['WBS-P001-01','WBS-P001-02'];assert next(x for x in owners if x['owner']=='WBS-P002-01')['sharedClassReferences']==['dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator']
# Physical columns always exact; prose-only variation needs explicit disposition and independent QA054 proof.
def validate(left,right,disposition,proof_cases):
 assert left[:5]==right[:5]
 if left[5]!=right[5]:assert disposition=='EXPLICIT_CANONICAL_QA054_RULE_REVIEW' and proof_cases==13
base=['Action','42','64','X','O','REQUEST HTTP_REQUEST_COMPLETED; ACTION MENU_VIEWED'];short=base[:5]+['Bounded action code'];validate(base,base,None,0);validate(base,short,'EXPLICIT_CANONICAL_QA054_RULE_REVIEW',13)
neg=[(base[:1]+['43']+base[2:],base,None,0),(base,short,None,13),(base,short,'EXPLICIT_CANONICAL_QA054_RULE_REVIEW',12)]
for args in neg:
 try:validate(*args)
 except AssertionError:pass
 else:raise AssertionError('invalid column/prose contract accepted')
O.mkdir();data=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],ownerCriteriaVerified=9,currentHostOwnerCount=3,sourceArtifacts=69,physicalClasses=78,canonicalRows=dict(layout=64,field=389),proseDispositions=2,metadataPositiveChecks=2,metadataNegativeChecks=3,bug='BUG-2647',ykt='YKT-2327',newOriginal190Acceptance=0,productTestsExecuted=0,formalUpdated=False,whole451Accepted=False,backendNativeOrVmUsed=False,effortRate=None,parentManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,criteria=9,negativeChecks=3,manifestSha256=sha(O/'manifest.json'))))
