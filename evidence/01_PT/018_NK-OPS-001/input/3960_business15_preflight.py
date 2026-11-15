"""Admit concrete bounded JUnit sites, exact protocol width, and fresh Root Main13."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG34982-business15-prepare-v1/manifest.json';sp=b/'evidence/PG34984-business15-static-v1/manifest.json';cp=b/'evidence/PG34980-business15-source-v1/manifest.json';m=ld(pp);s=ld(sp);proof=ld(cp);o=b/'evidence/PG34986-business15-preflight-v1';assert not o.exists()
assert m['actualExit']==s['actualExit']==proof['actualExit']==0 and m['expectedTests']==15 and len(m['apiMainSources'])==13 and len(m['apiTestSources'])==1 and proof['original13InverseByteExact'];assert m['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(s,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert s['processingErrors']==[] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','errors','missing'])
wanted={('JmsRequestReplyClient.java','DoNotUseThreads','80'),('ProtectedReadWireClient.java','AvoidLiteralsInIfCondition','211'),('WebBusinessWireClientsTest.java','CloseResource','362'),*{('WebBusinessWireClientsTest.java','DoNotUseThreads',str(n)) for n in [362,368,389,390]}}
assert {(Path(x['path']).name,x['rule'],x['line']) for x in s['rawFindings']}==wanted and len(s['rawFindings'])==7
classified=[]
for x in s['rawFindings']:
 p=Path(x['path']);text=p.read_text();line=text.splitlines()[int(x['line'])-1]
 if p.name=='JmsRequestReplyClient.java':
  assert line.strip()=='Thread.currentThread().interrupt();';reason='Restores current caller interrupt after bounded wait/cancel, no thread creation or swallowing.'
 elif p.name=='ProtectedReadWireClient.java':
  assert line.strip()=='if (bytes.length != 64) {';reason='SS311/352 UI232 fixed authentication-context wire width64, not arbitrary configurable business threshold. Prior SSC418 independent0/63/65/64 vectors retained at PG33750; this group does not rerun or transfer those oldsource executions.'
 else:
  assert 'newFixedThreadPool(8)' in text and 'for (int n = 0; n < 180; n++)' in text and 'task.get(10, TimeUnit.SECONDS)' in text and 'pool.shutdownNow();' in text and 'assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));' in text;reason='Standalone owned JUnit eight-worker pool for180 in-memory immediate-response calls. Each futureget10 and finallyshutdownNow/await10assert, any timeout/termination failure fails whole test. No transport/container/unrelated PID.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(p),disposition='NOT_APPLICABLE_CONCRETE_PROTOCOL_WIDTH_OR_BOUNDED_OWNED_FIXTURE',reason=reason))
w=r.parent/'pgpt-runs/PG379/pg34982-business15-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(w/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==194 and len(m['mainClassHashes'])==18 and {v.replace('.','/')+'.class' for v in s['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(n))==h for n,h in m['dependencies'].items())
jp=r/'evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/manifest.json';j=ld(jp);assert j['decision']=='STATIC_JDK_EXCEPTION_LOG_WRITER_CLOSURE' and j['testsReexecuted']==j['actualBackendActions']==0;assert sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==j['jdkModulesSha256'] and sha(r.parent/'toolchain/jdk-25.0.4/bin/javap')==j['jdkJavapSha256']
for n,h in j['staticArtifacts'].items():assert n.startswith('evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/') and Path(n).suffix in ['.json','.stdout','.stderr'] and sha(r/n)==h
providers={}
for n in m['dependencies']:
 with zipfile.ZipFile(n) as z:providers[n]=[x for x in z.namelist() if x=='META-INF/services/java.sql.Driver']
assert all(not x for x in providers.values())
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),sourceInverse=ref(cp),expectedTests=15,newDefinitions=2,necessaryPriorDefinitions=13,physicalClasses=194,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,pmdRaw7=7,classified=classified,rootNullAwayFresh=True,original13InverseByteExact=True,declaredTargets=proof['targets'],manualSuppressionAdded=False,jdkExceptionStaticReference=ref(jp),sameJdkModuleAndJavapBytes=True,currentClasspathSqlDriverDescriptors=providers,currentUnitInitMustBindAfterRun=True,sdkJvmNativeHostFsActivityUnmeasured=True,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
o.mkdir();(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=15,Main13RootFresh=True,physical=194,staticRaw=7,applicable=0,unclassified=0)))
