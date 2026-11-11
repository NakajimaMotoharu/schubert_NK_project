"""Independent same-run public metadata check; Media Unicode gap explicitly returned."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26266-record-time-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'evidence/PG26262-record-descriptor-time-criteria-v1/manifest.json';assert sha(p)=='53a0d309fc6c0c5f8134369c26fb44e4157981c8a54c65d1d722f4010b157b67';m=load(p)
for n,h in m['files'].items():assert sha(p.parent/n)==h
f=R/m['sameSourceRunManifest']['path'];assert sha(f)==m['sameSourceRunManifest']['sha256'];full=load(f);assert full['actualExit']==0 and full['tests']==124 and full['source']==m['source'] and full['singleSession']==m['run'];assert all(full[k]==0 for k in ['failures','errors','skipped','aborted']);assert sha(f.parent/'coverage.xml')==full['files']['coverage.xml'];xml={x.get('name'):x for x in E.parse(f.parent/'coverage.xml').findall('.//class')};rows=load(p.parent/'source-physical-counters.json');assert len(rows)==12 and len({x['path'] for x in rows})==11
for row in rows:
 assert sha(R/row['path'])==row['sourceSha256'];node=xml.get(row['physicalClass']);c={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in node.findall('counter')} if node is not None else {};assert row['coverage']==c
expected={'WBS-P002-04':(4,2,1,None),'WBS-P003-01':(104,19,4,52),'WBS-P003-02':(103,23,4,79),'WBS-P003-03':(19,3,1,6)}
for own in m['ownerSummaries']:
 for k,v in zip(['LINE','METHOD','CLASS','BRANCH'],expected[own['owner']]):
  if v is None:assert 'BRANCH' not in own['coverage'] and own['branchMetric']=='NATURAL_ZERO_BRANCH_NA_NOT100'
  else:assert own['coverage'][k]==dict(covered=v,missed=0)
assert m['fullyVerifiedOwners']==['WBS-P002-04','WBS-P003-01','WBS-P003-03'] and m['returnedOwner']=='WBS-P003-02' and not m['normalReproductionExecuted']
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],verifiedCurrentHostOwners=m['fullyVerifiedOwners'],fullyVerifiedCriteria=9,mediaScopeVerified=True,mediaContractQualityReturned=True,mediaBug='BUG-2648',mediaActualReproduction='NOT_RUN',sourceArtifacts=11,physicalClasses=12,productTestsExecuted=0,newOriginal190Acceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,parentManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),producerProvenance='Parent assembled by inline Python metadata-only command; persistent independent post verifies every pinned source/physical/XML counter. No unrecorded product execution claimed.',command='python3 -B evidence/01_PT/018_NK-OPS-001/input/1176_record_descriptor_time_post.py',toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,verifiedCriteria=9,returned='P00302',manifestSha256=sha(O/'manifest.json'))))
