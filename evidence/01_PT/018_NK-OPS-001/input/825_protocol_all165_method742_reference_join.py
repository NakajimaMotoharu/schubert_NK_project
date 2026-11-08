"""Join existing public reference proofs against the original normal XML, no Product execution."""
from pathlib import Path
from collections import Counter
import hashlib,json,datetime,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24854-protocol-all165-method742-reference-join-v1';assert not O.exists()
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(B/'input/820_protocol_remaining13_method_trace_scope.json');normal=load(R/cfg['normalProof']['path']);assert sha(R/cfg['normalProof']['path'])==cfg['normalProof']['sha256'];parent=(R/cfg['normalProof']['path']).parent
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
assert normal['actualExit']==0 and normal['tests']==120 and normal['productionCoreMain']==cfg['source'] and normal['source']==cfg['testSource']
xml=E.parse(parent/'coverage.xml').getroot();expected={c.get('name')+'#'+m.get('name')+m.get('desc'):m for c in xml.findall('.//class') for m in c.findall('method')};assert len(expected)==742
actual={t.get('classname')+'#'+t.get('name') for t in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')};assert len(actual)==120
pins=[(24662,'a8bd6f0efaae5b85a2824e65563a8603d905844ddeb5334008c6b98d221601e2'),(24678,'ae51094f0453b0f361064b3d5186b4badafac04204b044f75ee01482cd6c89f4'),(24694,'bc08487b765315335c646f1360a7873e3cf033e5f3eaf75b73404781dfcc8884'),(24706,'744f86cebafd04bdfa03e84abce393f467fc1a810dff4ade560fff5e20b1ca29'),(24718,'e272cdbeb727ed25ef38528fb683257f3ecd5be8bfd53dccc50ceab0795e031a'),(24732,'92e415a1fc5c04e21a5c97ba636c399ee39acff1a0fdbf037c4de2a007e82ec4'),(24762,'44ee25e75715c66e61557255771287da10bb2d0dbb59d36fc5536bc8bed490ac'),(24776,'33c2166b9c54d75ae97144113934e6ab1ed49ae6efd96669c1c58b03d785ddf6'),(24790,'344b9391c1a6c390f29a238ba79aa6e85300e57ff5c1d8feacc7ea0d3a0bd24f'),(24808,'dd40ac9440700fbb1753b0f15c8c6753372fae2488b54b6c939b863be1454e87'),(24824,'fd64441513f3fe65bd21c4a3e44a18112a26a121d0faa0065e877f7ccae231c3'),(24840,'ce5f3700a924c67ce8660dae5d8d3c9ce623edad5459f8220c62c6161e4aa250')]
# Frozen typecatalog's historical295 prose must carry the independently established296 supplement.
cp=B/'evidence/PG24752-component296-correction-independent-v1/manifest.json';assert sha(cp)=='880fd317272f3712321d7017cbc38b53e7f6dd6aa30d2947f48f70a08348f811' and load(cp)['actualExit']==0
for k in ['metadataInventory','descriptorInventory','physicalIndex']:assert sha(R/cfg[k]['path'])==cfg[k]['sha256']
meta=[r for r in load(R/cfg['metadataInventory']['path']) if r['physicalKey'].startswith('protocol:')];desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if '/schubert-nk-protocol/' in r['path']};ix=load(R/cfg['physicalIndex']['path']);assert len(meta)==176 and len(desc)==165
rows=[];classes=[];proofs=[];sources=set();perGroup=[]
for number,digest in pins:
 choices=list((B/'evidence').glob('PG'+str(number)+'-*/manifest.json'));assert len(choices)==1;mp=choices[0];assert sha(mp)==digest;m=load(mp);assert m['actualExit']==0 and m['source']==cfg['source'] and m['testSource']==cfg['testSource'] and m['newAcceptance']==0 and m['formalUpdated'] is False and m['effortRate'] is None
 ref=m['producerManifest'];pp=R/ref['path'];assert sha(pp)==ref['sha256'];pm=load(pp);assert pm['normalProof']==cfg['normalProof'] and pm['source']==cfg['source'] and pm['testSource']==cfg['testSource']
 for n,h in pm['files'].items():assert sha(pp.parent/n)==h
 rs=load(pp.parent/'method-trace.json');cs=load(pp.parent/'class-trace.json');ss={c['path'] for c in cs};assert not sources&ss;sources|=ss;rows+=rs;classes+=cs;proofs.append(dict(path=str(mp.relative_to(R)),sha256=digest));perGroup.append(dict(proof=number,sources=len(ss),methods=len(rs)))
assert len(rows)==742 and len(classes)==176 and sources==set(desc)
got={r['symbol']:r for r in rows};assert len(got)==len(rows) and got.keys()==expected.keys()
for symbol,x in expected.items():
 r=got[symbol];d=desc[r['sourcePath']];assert r['sourceSha256']==d['sha256'] and r['owner']==r['costOwner']==d['owner']==d['costOwner'] and r['firstExecutableLine']==int(x.get('line')) and r['actualCaseKeys'] and set(r['actualCaseKeys'])<=actual and r['perCaseProbeAttribution'] is None
 assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in x.findall('counter')}
for c in classes:
 assert c['sourceSha256']==desc[c['path']]['sha256'] and c['classSha256']==ix[c['className']]['sha256'] and c['crc64']==ix[c['className']]['crc64']
assert {c['className'] for c in classes}=={r['physicalKey'].split(':',1)[1][:-6] for r in meta}
# Per-class existing counters, not sums of overlapping source line ranges.
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for c in classes:
 for k in total:
  for v in ['covered','missed']:total[k][v]+=c.get('counters',{}).get(k,{}).get(v,0)
assert total=={k:dict(covered=n,missed=0) for k,n in dict(LINE=3478,METHOD=742,CLASS=159,BRANCH=1014,INSTRUCTION=17460).items()}
ownerMethods=Counter(r['owner'] for r in rows);ownerSources=Counter(d['owner'] for d in desc.values());caseKeys=sorted({k for r in rows for k in r['actualCaseKeys']})
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],normalProof=cfg['normalProof'],referenceProofs=proofs,mandatoryComponent296Supplement=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),sourceArtifacts=len(sources),physicalClasses=len(classes),officialMeasuredMethods=len(rows),sourceOwnerCounts=dict(ownerSources),measuredMethodOwnerCounts=dict(ownerMethods),existingActualCaseRefs=len(caseKeys),coverageReferences=total,perGroup=perGroup,allSourceAndXmlMethodKeysExactlyOnce=True,methodReferencesCompleteOnly=True,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False,newProductTests=0,productTestsExecuted=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sources=len(sources),methods=len(rows),caseRefs=len(caseKeys),manifestSha256=sha(O/'manifest.json'))))
