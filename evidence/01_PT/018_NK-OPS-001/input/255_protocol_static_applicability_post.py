"""Independent raw-site completeness and current-source witnesses; no dynamic acceptance inference."""
from pathlib import Path
import copy,datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22766-protocol-static-applicability-v1/manifest.json';O=B/'evidence/PG22768-protocol-static-applicability-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def valid(row,raw,inputs):
 f=row['finding'];return f in raw and row['classification']=='NOT_APPLICABLE' and bool(row['reason'].strip()) and row['sourceSha256']==inputs.get(f['path'])
def main():
 assert not O.exists();m=load(P);assert m['actualExit']==0 and sha(R/m['originalManifest']['path'])==m['originalManifest']['sha256'];rawmanifest=load(R/m['originalManifest']['path']);raw=rawmanifest['reports']['pmd']['rawItems'];post=load(R/m['independentRawPost']['path']);assert post['actualExit']==0 and sha(R/m['independentRawPost']['path'])==m['independentRawPost']['sha256'];assert m['inputHashes']==post['inputHashes'] and len(m['inputHashes'])==25
 for n,h in m['inputHashes'].items():assert sha(R/n)==h
 rows=m['individualClassifications'];assert len(rows)==len(raw)==11;assert sorted(json.dumps(x['finding'],sort_keys=True) for x in rows)==sorted(json.dumps(x,sort_keys=True) for x in raw);assert all(valid(x,raw,m['inputHashes']) for x in rows)
 counts={'DoNotUseThreads':0,'UseConcurrentHashMap':0,'NullAssignment':0};pending=0
 for row in rows:
  f=row['finding'];text=(R/f['path']).read_text();counts[f['rule']]+=1
  if f['rule']=='UseConcurrentHashMap':
   assert f['class']=='IndependentNamedFieldOracle';assert f['method'] in ['verifyAll','verifyType'];assert f['variable'] in ['accessors','areas','reviewed','absent'];assert row['witnesses'] and row['witnesses'][0]['declaration'][4]==f['variable'];assert row['witnesses'][0]['declaration'][3]==f['method'];assert not any(v in text for v in ['new Thread','Executors.','submit(','parallelStream('])
  elif f['rule']=='NullAssignment':
   assert f['class'] in ['IndependentNamedFieldOracle','WebLogActionContractTest'];assert 'assertThrows(InvocationTargetException.class' in text and 'assertInstanceOf(NullPointerException.class' in text;assert ('Object[] bad = arguments.toArray();' in text and 'bad[n] = null;' in text) or ('Object[] invalid = args.clone();' in text and 'invalid[i] = null;' in text)
  elif f['class']=='PayloadGoldenVectorTest':
   ref=row['witnesses'][0];p=R/ref['path'];assert sha(p)==ref['sha256'];g=load(p);assert g['actualExit']==0 and g['tests']==3 and g['inputHashes'][f['path']]==row['sourceSha256']
  else:
   assert f['class']=='WebLogActionContractTest' and row['separatePendingDefect']=='BUG-2450';assert 'workers = Executors.newFixedThreadPool(2)' in text and text.count('workers.submit(')==2 and 'first.get()' in text and 'second.get()' in text;pending+=1
 assert counts=={'DoNotUseThreads':5,'UseConcurrentHashMap':4,'NullAssignment':2} and pending==3 and m['pendingDefects']==['BUG-2450']
 negatives=[]
 for key,value in [('classification','PASS'),('reason',''),('sourceSha256','0'*64)]:
  b=copy.deepcopy(rows[0]);b[key]=value;assert not valid(b,raw,m['inputHashes']);negatives.append(key)
 b=copy.deepcopy(rows[0]);b['finding']['beginline']='0';assert not valid(b,raw,m['inputHashes']);negatives.append('findingIdentity')
 assert not m['moduleQualityAccepted'] and not m['wholeF03Accepted'] and not m['whole451Accepted'] and m['productTestsExecuted']==m['newAcceptance']==0
 O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],classificationManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),checkedSources=25,pmdRaw=11,individuallyClassified=11,applicableStaticFindings=0,unclassifiedStaticFindings=0,classificationCounts=counts,checkstyleRaw=0,formatDifferences=0,processingErrors=0,pendingDefects=['BUG-2450'],moduleQualityAccepted=False,metadataNegativeGuards=negatives,wholeF03Accepted=False,whole451Accepted=False,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,inputHashes=m['inputHashes'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=11,pending='BUG-2450',metadataNegativeGuards=4,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
