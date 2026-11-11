"""Current byte/independent fixture/reference audit; no Java execution or coverage merging."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; O=B/'evidence/PG26068-protocol-three-contracts-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
normal=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG24642-protocol-whole120-independent-v1/manifest.json'
assert sha(normal)=='8ebe6365bc701ba6432b1b55275004024dc71bc452d31b66d31c53894e3ae128'
m=load(normal);pf=load(normal.parent/'preflight-manifest.json');assert m['tests']==120 and m['failures']==m['errors']==m['skipped']==m['aborted']==0
w=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json'); owners=[]
for row in w['tasks']:
 if row['id'] not in ['WBS-P001-01','WBS-P001-02','WBS-P002-03']:continue
 pins={}
 for name in row['ownedArtifacts']:
  assert sha(R/name)==pf['inputHashes'][name];pins[name]=sha(R/name)
 counters={}
 for v in m['perSourceCounters']:
  path='src/schubert-nk-protocol/src/main/java/'+v['package']+'/'+v['name']
  if path in pins:
   for k,c in v['counters'].items():
    a=counters.setdefault(k,dict(covered=0,missed=0));a['covered']+=c['covered'];a['missed']+=c['missed']
 assert all(c['missed']==0 for c in counters.values())
 owners.append(dict(id=row['id'],ownedSourcePins=pins,requirementIds=row['requirementIds'],relatedRD=row['rd'],relatedUI=row['ui'],designFiles=row['evidencePlan']['designFiles'],originalAcceptanceSource=row['acceptance']['source'],dependencies=row['dependencies'],referenceCounters=counters,newAcceptance=0,currentAcceptance=False,missing=['All individual branch/exception/independent-oracle attribution and final owner/451 endings not established by aggregate measured counters.']))
assert sorted(len(a['ownedSourcePins']) for a in owners)==[5,6,20]
refs=[('PG24678-header-method30-trace-independent-v1','ae51094f0453b0f361064b3d5186b4badafac04204b044f75ee01482cd6c89f4'),('PG24732-typecatalog-method12-trace-independent-v1','92e415a1fc5c04e21a5c97ba636c399ee39acff1a0fdbf037c4de2a007e82ec4'),('PG24808-headercodec5-method14-trace-independent-v1','dd40ac9440700fbb1753b0f15c8c6753372fae2488b54b6c939b863be1454e87')]
proofs=[]
for d,h in refs:
 p=B/'evidence'/d/'manifest.json';assert sha(p)==h;proofs.append(dict(path=str(p.relative_to(R)),sha256=h))
tests={n:h for n,h in pf['inputHashes'].items() if n.endswith(('HeaderModelTest.java','LayoutFieldCatalogTest.java','LayoutMetadataTest.java','MessageCodecTest.java','JstWireTimestampTest.java','layouts-ui233.tsv','fields-ui234-236.tsv'))}
assert len(tests)==7
for n,h in tests.items():assert sha(R/n)==h
before=B/'evidence/PG26070-null-contract-spec-before-v1/manifest.json';bm=load(before);assert bm['primarySpecsSearched']==20 and len(bm['hits'])==8
changed=[];allSpecs=sorted((R/'evidence/01_PT').glob('*/001_*.md'));assert len(allSpecs)==20
for p in allSpecs:
 name=str(p.relative_to(R));old=subprocess.check_output(['git','show','HEAD:'+name]);current=p.read_bytes()
 if old!=current:
  assert name in bm['sourcePins'] and hashlib.sha256(old).hexdigest()==bm['sourcePins'][name]
  a=old.decode().splitlines();b=current.decode().splitlines();assert len(a)==len(b)
  deltas=[dict(line=i+1,before=x,after=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  assert len(deltas)==(2 if '001_NK-PRO-001/' in name else 1)
  changed.append(dict(path=name,beforeSha256=hashlib.sha256(old).hexdigest(),afterSha256=sha(p),changes=deltas))
assert len(changed)==2
p1=(R/changed[0]['path']).read_text();p2=(R/changed[1]['path']).read_text()
assert 'Java内部の九参照null' in p1 and 'LayoutValidationException' in p1 and '偶発NPEやNPEの正常業務結果へのcatch/変換を許さない' in p1
assert 'parseはvalue、formatはinstant' in p2 and '外部wire失敗と区別しNPEを正常結果へ変換しない' in p2
assert '旧H03' in (R/'evidence/01_PT/001_NK-PRO-001/104_Header契約個別照合・独立反例仕様.md').read_text()
assert 'WBS65-NULL-20261112' in (R/'documents/400_PGPT/440_判断/441_実装判断記録.md').read_text()
assert not O.exists();O.mkdir()
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',owners=owners,sourceCount=31,testAndIndependentFixturePins=tests,existingNormalProof=dict(path=str(normal.relative_to(R)),sha256=sha(normal)),methodReferenceProofs=proofs,nullSpecSynchronization=dict(bug='BUG-2629',ykt='YKT-2310',beforeManifestSha256=sha(before),searchedPrimarySpecs=20,matchingOriginalLines=8,changedSpecs=changed,otherPrimarySpecsUnchanged=18,behaviorOrExpectedExceptionChanged=False,upperDesignChanged=False),testIds=['PT-PRO-001-H01','PT-PRO-001-H02','PT-PRO-001-H03','HDR3266-001','PT-PRO-001-L01','PT-PRO-001-L02','PT-PRO-001-L03','PT-PRO-003-T02'],productTestsExecuted=0,newCoverageMeasurements=0,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceCount=31,specsChanged=2,statementsChanged=3,otherSpecsUnchanged=18,productTestsExecuted=0,newAcceptance=0,sha256=sha(O/'manifest.json'))))
