"""Independent Login normal admission: synthetic values only, strict current compile/static/byte binding."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';U=R.parent/'pgpt-runs/PG379/pg26524-login-pure-main-subset-v1';O=B/'evidence/PG26528-login-pure-preflight-v1';assert not O.exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
pc=B/'evidence/PG26524-login-pure-main-subset-v1/manifest.json';m=load(pc);ps=B/'evidence/PG26526-login-pure-static-v1';s=load(ps/'manifest.json');assert m['actualExit']==0 and m['expectedTests']==154 and len(m['expectedCases'])==154;assert m['inputHashes']==s['inputHashes'] and m['dependencies']==s['dependencies'];assert all(sha(R/p)==h for p,h in m['inputHashes'].items());assert m['compilerConfiguration']=='EXACT_ROOT_PLUGIN_RELEASE25_NULLAWAY_0141_ERRORPRONE2500'
for label,t in m['stages'].items():
 assert t['actualExit']==0 and not t['timedOut']
 for stream in ['stdout','stderr']:assert sha(pc.parent/(label+'.'+stream))==t[stream+'Sha256']
assert m['mainClassHashes']=={str(p.relative_to(U/'target/classes')):sha(p) for p in (U/'target/classes').rglob('*.class')};assert len(m['mainClassHashes'])==12
assert m['testClassHashes']=={str(p.relative_to(U/'test-classes')):sha(p) for p in (U/'test-classes').rglob('*.class')}
normal=B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';n=load(normal);matches={p:h==n['normalPhysicalClassHashes']['web:'+p] for p,h in m['mainClassHashes'].items()};assert all(matches.values())
style=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';st=load(style);assert st['actualExit']==st['applicableViolations']==st['unclassified']==st['checkstyle']==0;art=style.parent/'artifacts.json';assert sha(art)==st['files']['artifacts.json'];rows={x['path']:x for x in load(art)}
for p in m['mainSources']+m['packageSources']:assert rows[p]['sha256']==sha(R/p)==n['begin']['inputHashes'][p]
ns={'m':'http://maven.apache.org/POM/4.0.0'}
def compiler(p):return next(x for x in ET.parse(p).findall('.//m:plugin',ns) if x.findtext('m:artifactId',namespaces=ns)=='maven-compiler-plugin')
assert ET.tostring(compiler(R/'pom.xml'))==ET.tostring(compiler(U/'pom.xml'))
sb=ET.parse(ps/'spotbugs.xml').getroot();assert not any(sb.findall('.//'+t) for t in ['BugInstance','MissingClass','Error']);stats={x.get('class') for x in sb.findall('.//ClassStats')};assert stats=={x.removesuffix('.class').replace('/','.') for x in m['mainClassHashes']};assert s['stages']['spotbugs']['actualExit']==s['stages']['checkstyle']['actualExit']==0
rt=ET.parse(ps/'pmd.xml').getroot();assert not any(x.tag.rpartition('}')[2] in ['error','configerror'] for x in rt.iter());assert not ET.parse(ps/'checkstyle.xml').findall('.//error');test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginClientTest.java';text=(R/test).read_text();lines=text.splitlines();occ=[]
reasons={'DoNotUseThreads':'Standalone normal JUnit explicitly owns both pools; finite latches/Futures, finally shutdownNow/await5 asserted on both exits, interrupt flag deliberately set and cleared in finally for negative test. No application/container worker creation.', 'CloseResource':'Both fixture pool owners close in explicit finally with shutdownNow and awaitTermination5 terminal assertion, avoiding unbounded ExecutorService.close. Actual job exit is also required.', 'AvoidSynchronizedStatement':'Original standalone 100-request fixture retains a single coordinator monitor; production service does not synchronize on it, no provider/external resources or application locking policy, original six assertions/oracle preserved.'}
for f in rt:
 if f.tag.rpartition('}')[2]!='file':continue
 assert Path(f.get('name'))==R/test
 for x in f:
  if x.tag.rpartition('}')[2]!='violation':continue
  rule=x.get('rule');assert rule in reasons,(rule,x.attrib);i=int(x.get('beginline'));occ.append(dict(path=test,line=i,sourceLine=lines[i-1],rule=rule,classification='CONTEXTUAL_NONAPPLICABLE',reason=reasons[rule]))
assert len(occ)==15 and text.count('workers.awaitTermination(5, TimeUnit.SECONDS)')==2 and 'try (var workers' not in text
mfg=B/'evidence/PG26522-login-test-manufacture-v1/manifest.json';mf=load(mfg);assert mf['originalSixInverseExactBeforeFormatting'] and mf['newDefinitions']==1 and mf['fixedOwnerSites']==2 and mf['afterSha256']==sha(R/test)
for token in ['assertSame(failure, actual)','new NullPointerException("synthetic-provider-fault")','new AssertionError("synthetic-provider-fault")','assertArrayEquals(new char[1], nextPassword)','assertArrayEquals(new byte[640], handed.get())','UUID next = new UUID(0, 2)']:assert token in text
helpers=load(B/'evidence/PG26456-jms-client-nineteen-unit-v1/begin.json')
for p,h in helpers['inputHashes'].items():
 if '/src/test/java/' in p:assert sha(R/p)==h
assert all('artemis' not in p for p in m['dependencies']);login=(R/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginClient.java').read_text();assert 'InetAddress.ofLiteral(address)' in login and 'getByName' not in login
O.mkdir();write(O/'static-contextual-fifteen.json',occ);v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],compileManifestSha256=sha(pc),staticManifestSha256=sha(ps/'manifest.json'),expectedTests=154,newDefinitions=1,wholeOriginalSixPreserved=True,independentUnknownKinds=2,finiteOwnerSites=2,freshNullAway=True,freshSpotbugsExactPhysical12=True,spotbugsBugs=0,spotbugsMissing=0,spotbugsErrors=0,rawPmd=15,applicableStaticViolations=0,unclassified=0,checkstyleFindings=0,processingErrors=0,allMain12ByteIdenticalNormal=True,MainChanged=False,syntheticPasswordOnly=True,literalIpNoDns=True,actualAuthSessionDbKeyProviderRootVmNativeOperations=False,heldActualClassFilesRead=False,whole451Accepted=False,formalUpdated=False,newAcceptance=0,productTestsExecuted=0,files={p.name:sha(p) for p in O.iterdir()});write(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,expectedTests=154,staticApplicable=0,rawContextual=15,allMain12Normal=True,manifestSha256=sha(O/'manifest.json'))))
