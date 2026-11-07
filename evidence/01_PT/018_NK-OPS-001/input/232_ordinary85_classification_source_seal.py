"""Compose pinned individual classifications and exact current source projections; engines never replayed."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];OPS=R/'evidence/01_PT/018_NK-OPS-001/evidence';ADM=R/'evidence/01_PT/010_NK-ADM-001/evidence';WEB=R/'evidence/01_PT/015_NK-WEB-001/evidence';OUT=OPS/'PG22606-ordinary85-classification-source-seal-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
def key(p,a):return (p,json.dumps(a,sort_keys=True))
def stable(row):return (row['path'],json.dumps({k:v for k,v in row['attributes'].items() if k not in ['beginline','endline','begincolumn','endcolumn']},sort_keys=True),row['message'])
def source_for(row,manifest):
 choices=[p for p in manifest['inputHashes'] if '/src/test/java/' in p and p.endswith('.java')];p=row.get('sourcePath')
 if p is None:
  assert len(choices)==1,'source ambiguity';p=choices[0]
 assert p in choices,'unknown source';return p
def main():
 assert not OUT.exists();raw=OPS/'PG22382-ordinary85-test-static-v1';rm=load(raw/'manifest.json');assert sha(raw/'manifest.json')=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';assert sha(raw/'unclassified-sites.json')==rm['files']['unclassified-sites.json'];original=load(raw/'unclassified-sites.json');assert len(original)==347;index={key(x['path'],x['attributes']):x for x in original};assert len(index)==347;binding={};parts=[]
 definitions=[('PG22392-ordinary-proxy-loader93-v1','PG22398-ordinary-proxy-loader93-independent-v2',93),('PG22408-ordinary-thread158-scope-v1','PG22410-ordinary-thread158-independent-v1',158),('PG22418-null-identity14-sites-v1','PG22420-null-identity14-independent-v1',14),('PG22456-close-resource-six-ownership-v1','PG22458-close-resource-six-independent-v1',6)]
 for src,dst,count in definitions:
  p=OPS/src/'manifest.json';m=load(p);q=OPS/dst/'manifest.json';qm=load(q);assert m['actualExit']==qm['actualExit']==0;f=p.parent/'site-classifications.json';assert sha(f)==m['files'][f.name];items=load(f);assert len(items)==count
  for x in items:
   o=x['original'];k=key(o['path'],o['attributes']);assert k in index and k not in binding;binding[k]=ref(q)
  parts.append(dict(collector=ref(p),independentPost=ref(q),count=count))
 p=OPS/'PG22470-question-volatile12-context-v2/manifest.json';m=load(p);q=OPS/'PG22474-question-volatile12-independent-v1/manifest.json';assert m['actualExit']==load(q)['actualExit']==0 and len(m['originalSites'])==12
 for o in m['originalSites']:
  k=key(o['path'],o['attributes']);assert k in index and k not in binding;binding[k]=ref(q)
 parts.append(dict(collector=ref(p),independentPost=ref(q),count=12))
 for src,dst,count in [('PG22584-ten-maps-one-reflection-v2','PG22586-ten-maps-one-reflection-independent-v2',11),('PG22598-remaining52-map-owners-v1','PG22600-remaining52-map-owners-independent-v1',52)]:
  p=OPS/src/'manifest.json';m=load(p);q=OPS/dst/'manifest.json';assert m['actualExit']==load(q)['actualExit']==0;f=p.parent/'sites.json';assert sha(f)==m['files'][f.name];items=load(f);assert len(items)==count
  for x in items:
   k=key(x['path'],x['originalAttributes']);assert k in index and k not in binding;binding[k]=ref(q)
  parts.append(dict(collector=ref(p),independentPost=ref(q),count=count))
 rb=ADM/'PG22444-user-audit-static-source-rebinding-v1/manifest.json';remove=load(rb)['removedApplicableFinding'];removed=key(remove['path'],remove['attributes']);assert len(binding)==346 and set(binding)==set(index)-{removed}
 names=sorted(rm['begin']['inputHashes']);assert len(names)==85 and all('/src/test/java/' in n and not any(t in n for t in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) for n in names);current={n:sha(R/n) for n in names};changed={n for n in names if current[n]!=rm['begin']['inputHashes'][n]};up=ADM/'PG22438-user-audit-cleanup-independent-v1/manifest.json';qp=OPS/'PG22492-question-bounded-wait-independent-v1/manifest.json';wp=WEB/'PG22546-seven-future-independent-v1/manifest.json';um=load(up);qq=load(qp);wm=load(wp);assert all(x['actualExit']==0 for x in [um,qq,wm]);expected={n for n in um['inputHashes'] if '/src/test/java/' in n};expected.add(qq['testPath']);expected|={n for n in wm['inputHashes'] if '/src/test/java/' in n and n.endswith('PortTest.java')};assert len(changed)==len(expected)==9 and changed==expected
 sourceBindings=[]
 for p,m in [(up,um),(wp,wm)]:
  for n,h in m['inputHashes'].items():
   if n in changed:assert h==current[n];sourceBindings.append(dict(path=n,sha256=h,post=ref(p)))
 assert current[qq['testPath']]==qq['testSha256'];sourceBindings.append(dict(path=qq['testPath'],sha256=qq['testSha256'],post=ref(qp)));assert len(sourceBindings)==9
 fresh=[]
 for p in [ADM/'PG22432-user-audit-cleanup-static-applicability-v1/manifest.json',WEB/'PG22518-seven-security-port-static-applicability-v1/manifest.json']:
  m=load(p);assert m['applicableViolations']==m['checkstyle']==m['spotbugs']==m['processingErrors']==0
  for row in m['individualClassifications']:
   if source_for(row,m) in changed:fresh.append(dict(path=source_for(row,m),attributes={k:row[k] for k in ['beginline','endline','begincolumn','endcolumn','rule','ruleset','package','class','method','variable','externalInfoUrl','priority'] if k in row},message=row['message'],freshProjection=ref(p)))
 p=OPS/'PG22488-question-bounded-wait-static-v1';qm=load(p/'manifest.json');assert qm['actualExit']==0 and sha(p/'pmd.xml')==qm['files']['pmd.xml']
 for f in E.parse(p/'pmd.xml').getroot():
  for x in f:
   if x.tag.rsplit('}',1)[-1]=='violation':fresh.append(dict(path=str(Path(f.get('name')).relative_to(R)),attributes=dict(x.attrib),message=' '.join(''.join(x.itertext()).split())[:600],freshProjection=ref(p/'manifest.json')))
 # PMD findings can have optional method/variable attributes: take only actual PMD attributes, not a sample shape.
 extra={'classification','reason','sourcePath','sourceSha256','sourceLineSha256'}
 for row in fresh:row['attributes']={k:v for k,v in row['attributes'].items() if k not in extra}
 oldgroups=collections.defaultdict(list);newgroups=collections.defaultdict(list)
 for x in original:
  if x['path'] in changed and key(x['path'],x['attributes'])!=removed:oldgroups[stable(x)].append(x)
 for x in fresh:newgroups[stable(x)].append(x)
 assert {k:len(v) for k,v in oldgroups.items()}=={k:len(v) for k,v in newgroups.items()}
 rebound={}
 for k,oldrows in oldgroups.items():
  newrows=newgroups[k];order=lambda x:tuple(int(x['attributes'][v]) for v in ['beginline','begincolumn','endline','endcolumn'])
  for oldrow,newrow in zip(sorted(oldrows,key=order),sorted(newrows,key=order)):rebound[key(oldrow['path'],oldrow['attributes'])]=newrow
 rows=[]
 for k,proof in binding.items():
  old=index[k];new=rebound.get(k,old);rows.append(dict(originalOrdinal=old['ordinal'],path=old['path'],originalAttributes=old['attributes'],currentAttributes=new['attributes'],message=old['message'],currentSourceSha256=current[old['path']],classification='NOT_APPLICABLE_INDIVIDUALLY_JUSTIFIED',independentPost=proof,freshProjection=new.get('freshProjection')))
 assert len(rows)==346;OUT.mkdir();write(OUT/'sites.json',sorted(rows,key=lambda x:x['originalOrdinal']));result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',originalRawManifest=ref(raw/'manifest.json'),originalRawSites=347,removedActualDefect=remove,removedDefectPost=ref(up),currentSourceHashes=current,changedSources=sourceBindings,unchangedSources=76,changedSourceCount=9,classificationParts=parts,currentComposedRaw=346,classifiedSites=346,applicableSites=0,unclassifiedSites=0,duplicateSites=0,missingSites=0,reconstructedNotFreshAll85EngineRun=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeF03Accepted=False,whole451Accepted=False,questionDynamicHold=True,ykt2177Closed=False,files={'sites.json':sha(OUT/'sites.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));write(OUT/'manifest.json',result);print(json.dumps(dict(actualExit=0,current=346,changed=9,unchanged=76)))
if __name__=='__main__':main()
