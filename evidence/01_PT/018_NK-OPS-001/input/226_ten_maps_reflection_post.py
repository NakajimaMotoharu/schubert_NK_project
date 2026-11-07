"""Independent method-range/owner checks using a prequalified JDK parse-only tool."""
from pathlib import Path
import datetime,hashlib,json,subprocess,copy,re
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22576-ten-maps-one-reflection-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22578-ten-maps-one-reflection-independent-v1';SLOT=RUNS/'pg22578-ten-maps-one-reflection-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def profile(row,text,body):
 if any(w not in text for w in row['witnesses']) or not row['reason']:return False
 a=row['originalAttributes'];p=row['profile'];v=a.get('variable','')
 if p=='FIXED_OWN_PRIVATE_RECORD_REDACTION_TEST':return body.count('constructor.setAccessible(true);')==1 and body.count('Class.forName(')==1 and 'Class.forName("dev.codex.schubert.nk.batch.repository.BatchRunRepository$History")' in body and 'assertFalse(history.toString().contains(FOREIGN.toString()));' in body and 'assertFalse(history.toString().contains(BASE.toString()));' in body
 if p=='LOCAL_COPY_TO_IMMUTABLE_SNAPSHOT':return 'data.put(field, value);' in body and 'return new ExpiryAuditRepository.Snapshot(' in body and 'return data;' not in body
 if p=='LOCAL_EXPECTED_HTTP_HEADERS':return 'assertEquals(headers, reply.headers);' in body and 'return headers;' not in body
 if p=='LOCAL_EXPECTED_COPY':return 'new HashMap<>(fixture.bindings)' in body and 'values.remove(10);' in body and 'return values;' in body
 if p=='LOCAL_EXPECTED_HANDLE_VECTOR':return 'values.put(first, 7L);' in body and 'return values;' in body and 'expected.put(5, null);' in text
 if p=='LOCAL_ROW_VECTOR_RETURNED_ONLY_TO_SYNCHRONOUS_TEST':return 'values.put("id", id);' in body and 'return values;' in body and not re.search(r'\b(?:ExecutorService|Executors|Thread|CompletableFuture)\b|\.parallel\(',text)
 if p=='WORKER_OWN_REQUEST_FRAME':return 'var frame = new Frame(' in body and 'workers.submit(' in body and 'get(10, java.util.concurrent.TimeUnit.SECONDS)' in body
 if p=='WORKER_OWN_JDBC_FIXTURE':return 'var f = new Jdbc();' in body and not re.search(r'static\s+(?:final\s+)?Map\b',text)
 return False

def main():
 assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==0;sites=load(P/'sites.json');assert len(sites)==11 and sum(x['originalAttributes']['rule']=='UseConcurrentHashMap' for x in sites)==10
 for p,h in m['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+p],cwd=R)).hexdigest()
 prior=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22410-ordinary-thread158-independent-v1/manifest.json';assert sha(prior)=='b7a9022920798dd9c82e80a3e5165fca4a19a82de4d700568c46382c86f929f4';tool=load(prior)['tool'];owned=RUNS/'pg22410-ordinary-thread158-independent-v1';assert sha(R/tool['path'])==tool['sha256']==sha(owned/'source/TestMethodScopeAstCheck.java');classes={p.name:sha(p) for p in (owned/'classes').glob('*.class')};assert set(classes)=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};SLOT.mkdir();c.SLOT=SLOT;stage=c.step('parse',[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',str(owned/'classes'),'TestMethodScopeAstCheck',str(R),*sorted(m['inputHashes'])],R,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];methods={}
 for line in (SLOT/'parse.stdout').read_text().splitlines():
  p,cl,method,lo,hi=line.split('\t');methods.setdefault((p,cl,method),[]).append((int(lo),int(hi)))
 checked=[]
 for row in sites:
  a=row['originalAttributes'];text=(R/row['path']).read_text();assert text.splitlines()[row['currentDeclarationLine']-1].strip()==row['declaration'];owner=a['class'];method=a.get('method');p=row['path'];name=Path(p).name
  if method:key=(p,owner,method)
  elif name=='UserCriticalAuditPortTest.java':key=(p,'UserCriticalAuditPortTest','writeOne')
  elif name=='WebLogOutboxPortTest.java':key=(p,'WebLogOutboxPortTest','readWorker')
  elif name=='CsrfDeniedHandlerPortTest.java':key=(p,'CsrfDeniedHandlerPortTest','twoWorkerThreadLocalActorsAndRequestAuditsRemainIndependent')
  elif name=='CsrfFilterFactoryPortTest.java':key=(p,'CsrfFilterFactoryPortTest','sharedConfiguredFilterKeepsEightConcurrentSuppliedTokensRequestLocal')
  else:raise ValueError('unregistered owner')
  spans=methods[key];assert len(spans)==1;lo,hi=spans[0];body='\n'.join(text.splitlines()[lo-1:hi]);assert profile(row,text,body),(name,a.get('variable'));checked.append(dict(path=p,owner=owner,method=key[2],range=[lo,hi],profile=row['profile']))
 mw=m['mainWitness'];assert sha(R/mw['path'])==mw['sha256'] and all(x in (R/mw['path']).read_text() for x in mw['witnesses']);sample=sites[0];bad=copy.deepcopy(sample);bad['profile']='UNKNOWN';assert not profile(bad,(R/sample['path']).read_text(),'');bad=copy.deepcopy(sample);bad['witnesses']=['MISSING_OWNERSHIP_WITNESS'];assert not profile(bad,(R/sample['path']).read_text(),'');assert classes=={p.name:sha(p) for p in (owned/'classes').glob('*.class')};OUT.mkdir();files={}
 for name in ['parse.stdout','parse.stderr','parse-exit.safe.json']:(OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),targetSites=11,newIndividualClassifications=11,selectedMapSites=10,selectedReflectionSites=1,currentRawSitesRetained=346,subsetClassifiedBefore=283,subsetClassifiedAfter=294,subsetUnclassifiedBefore=63,subsetUnclassifiedAfter=52,remainingMapSites=52,remainingReflectionSites=0,verifiedOwnershipSites=checked,negativeMetadataGuards=2,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,dynamicBehaviourRequalified=False,effortRate=None,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,stage=stage,files=files,reusedToolPhysical=classes,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=11,remaining=52)))
if __name__=='__main__':main()
