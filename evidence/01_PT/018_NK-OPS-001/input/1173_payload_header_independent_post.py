"""Independently validate public same-run six-criterion join, without reexecuting PT."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26260-payload-header-independent-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
p=B/'evidence/PG26258-payload-header-current-criteria-v1/manifest.json';assert sha(p)=='d69badfb266b4ed6714022389ee5f768586807985faf11a62ecc6713b4ee9068';m=load(p)
for n,h in m['files'].items():assert sha(p.parent/n)==h
assert m['criteriaVerified']==m['criteriaTotal']==6 and m['canonicalGoldenHashComparisons']==287 and m['productTestsReexecuted']==m['newOriginal190Acceptance']==0
f=R/m['sameSourceRunManifest']['path'];assert sha(f)==m['sameSourceRunManifest']['sha256'];full=load(f);assert full['source']==m['source'] and full['singleSession']==m['run'] and full['actualExit']==0 and full['tests']==124;assert all(full[k]==0 for k in ['failures','errors','skipped','aborted']);dep=R/m['sameSourceDependencyProof']['path'];assert sha(dep)==m['sameSourceDependencyProof']['sha256'];d=load(dep);assert d['source']==m['source'] and d['run']==m['run'] and d['ownerCriteriaVerified']==9
expected={'WBS-P002-02':(2,3,491,61,2,347),'WBS-P002-03':(5,5,113,14,5,36)}
for own in m['ownerSummaries']:
 a,b,l,me,c,br=expected[own['owner']];assert (own['sourceArtifacts'],own['physicalClasses'])==(a,b)
 for k,v in [('LINE',l),('METHOD',me),('CLASS',c),('BRANCH',br)]:assert own['coverage'][k]=={'covered':v,'missed':0}
rows=load(p.parent/'source-physical-counters.json');assert len(rows)==8
for row in rows:assert sha(R/row['path'])==row['sourceSha256']
fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv';gold={q[0]:q[1:] for l in fixture.read_text().splitlines() if l and not l.startswith('#') for q in [l.split('\t')]};vectors=load(p.parent/'independent287-fixed-golden-hashes.json');assert len(vectors)==287;assert len({(v['layout'],v['area'],v['profile']) for v in vectors})==287
for v in vectors:
 at=4 if v['profile']=='generic-error' else (2 if v['area']=='RECORD' else 0)+(v['profile']=='max');assert v['expectedSha256']==v['fixtureSha256']==gold[v['layout']][at]
names={(x.get('classname').rsplit('.',1)[-1],x.get('name').removesuffix('()')) for x in E.parse(f.parent/'testcases.safe.xml').findall('testcase')};matrix=load(p.parent/'individual-oracle-matrix.json');assert len(matrix)==23
for row in matrix:
 cl,case=row['case'].split('#');assert (cl.rsplit('.',1)[-1],case.removesuffix('()')) in names
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],ownerCriteriaVerified=6,sourceArtifacts=7,physicalClasses=8,independentGoldenHashComparisons=287,oracleCases=23,currentRequiredOwnerDependencies=2,productTestsExecuted=0,newOriginal190Acceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,parentManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,criteria=6,hashes=287,oracles=23,manifestSha256=sha(O/'manifest.json'))))
