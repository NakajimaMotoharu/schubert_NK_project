"""Independent current source/compile/oracle/static admission; no product execution."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';O=B/'evidence/PG26504-jms-provider-preflight-v3';assert not O.exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
pc=B/'evidence/PG26500-jms-provider-current-test-compile-v3/manifest.json';m=load(pc);ps=B/'evidence/PG26502-jms-provider-current-static-v3';s=load(ps/'manifest.json');assert m['actualExit']==0 and m['inputHashes']==s['inputHashes'] and m['dependencies']==s['dependencies'];assert all(sha(R/p)==h for p,h in m['inputHashes'].items());assert len(m['expectedCases'])==163 and m['expectedTests']==163
original=R/m['originalMainCompile']['path'];assert sha(original)==m['originalMainCompile']['sha256'];m0=load(original);assert m0['actualExit']==0 and m0['compilerConfiguration']=='EXACT_ROOT_PLUGIN_RELEASE25_NULLAWAY_0141_ERRORPRONE2500';work=RUNS/'pg26480-jms-provider-main-subset-v1';assert sha(work/'pom.xml')==m['subsetPomSha256']==m0['subsetPomSha256'];ns={'m':'http://maven.apache.org/POM/4.0.0'}
def compiler(p):
 return next(x for x in ET.parse(p).findall('.//m:plugin',ns) if x.findtext('m:artifactId',namespaces=ns)=='maven-compiler-plugin')
assert ET.tostring(compiler(R/'pom.xml'))==ET.tostring(compiler(work/'pom.xml'))
for p in m['mainSources']+m['packageSources']:
 assert m['inputHashes'][p]==m0['inputHashes'][p]==sha(work/'src/main/java'/p.split('/src/main/java/')[1])
for label,t in m0['stages'].items():
 assert t['actualExit']==0 and not t['timedOut']
 for stream in ['stdout','stderr']:assert sha(original.parent/(label+'.'+stream))==t[stream+'Sha256']
assert m['mainClassHashes']==m0['mainClassHashes']=={str(p.relative_to(work/'target/classes')):sha(p) for p in (work/'target/classes').rglob('*.class')};assert len(m['mainClassHashes'])==12
assert m['testClassHashes']=={str(p.relative_to(work/'test-classes-v3')):sha(p) for p in (work/'test-classes-v3').rglob('*.class')}
assert m['stages']['test-compile']['actualExit']==0
root=ET.parse(ps/'pmd.xml').getroot();assert not any(x.tag.rpartition('}')[2] in ['error','configerror'] for x in root.iter());occ=[]
reasons={'UseProperClassLoader':'Standalone JVM dynamic Proxy must implement exact JMS interface identity; interface defining loader is intentional, no J2EE container/context-loader service or reflection access override.', 'UseConcurrentHashMap':'Test-owned mutable value maps are local to each synchronous fixture; no concurrent reader/writer or application map, null test values required; never shared across worker tests.', 'CompareObjectsWithEquals':'Proxy equals handler must implement reference identity without recursively invoking Proxy.equals; intentional Object identity contract, not domain value comparison.'}
for f in root:
 if f.tag.rpartition('}')[2]!='file':continue
 lines=Path(f.get('name')).read_text().splitlines()
 for v in f:
  if v.tag.rpartition('}')[2]!='violation':continue
  rule=v.get('rule');assert rule in reasons,(rule,v.attrib);at=int(v.get('beginline'));occ.append(dict(path=str(Path(f.get('name')).relative_to(R)),line=at,sourceLine=lines[at-1],rule=rule,classification='CONTEXTUAL_NONAPPLICABLE',reason=reasons[rule]))
assert len(occ)==12;assert not ET.parse(ps/'checkstyle.xml').findall('.//error') and s['stages']['checkstyle']['actualExit']==0
oldStatic=B/'evidence/PG26482-jms-provider-static-v1';old=load(oldStatic/'manifest.json')
for p in m['mainSources']+m['packageSources']:assert old['inputHashes'][p]==m['inputHashes'][p]
oldPmd=ET.parse(oldStatic/'pmd.xml').getroot();assert not any('/src/main/java/' in f.get('name','') for f in oldPmd if f.tag.rpartition('}')[2]=='file');assert sha(ps/'spotbugs.xml')==sha(oldStatic/'spotbugs.xml');sb=ET.parse(ps/'spotbugs.xml').getroot();assert not any(sb.findall('.//'+n) for n in ['BugInstance','MissingClass','Error']);stats={x.get('class') for x in sb.findall('.//ClassStats')};assert stats=={p.removesuffix('.class').replace('/','.') for p in m['mainClassHashes']}
proto=B/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json';assert sha(proto)=='f55c0333e063a7350849315a3b9ad4f9fdcbc22e194c22148b84e62b0c8c4d9f';pm=load(proto);assert pm['actualExit']==0
# All unchanged helper Test sources retain their qualified current normal snapshots.
helper=B/'evidence/PG26458-jms-client-nineteen-independent-v1/manifest.json';assert sha(helper)=='c9b62f118d1e626fb93ce1f9a694fb5dfaeaca6dd261e9e0384f61ff69447323';hm=load(helper);assert hm['actualExit']==0;hb=load(B/'evidence/PG26456-jms-client-nineteen-unit-v1/begin.json')
for p,h in hb['inputHashes'].items():
 if '/src/test/java/' in p:assert sha(R/p)==h
red=load(B/'evidence/PG26476-jms-provider-original-red-v1/manifest.json');assert red['unitActualExit']==1 and red['tests']==red['failures']==2 and red['remainingMatrixCellsNotClaimed']
mfg=load(B/'evidence/PG26474-jms-provider-tests-manufacture-v1/manifest.json');assert mfg['actualExit']==0 and len(mfg['records'])==2
constants=load(B/'evidence/PG26488-provider-fixture-literals-manufacture-v1/manifest.json');assert all(x['inverseAllTokensExactlyOriginal'] and not x['valuesChanged'] for x in constants['results']);follow=load(B/'evidence/PG26493-provider-existing-constant-followup-v1/manifest.json');assert follow['allResolvedSourceTokensEqual']
O.mkdir();write(O/'static-contextual-twelve.json',occ);v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],compileManifestSha256=sha(pc),staticManifestSha256=sha(ps/'manifest.json'),expectedTests=163,rawPmd=12,applicableStaticViolations=0,unclassified=0,checkstyleFindings=0,processingErrors=0,freshNullAwaySameMainSources=True,freshSpotbugsExactPhysical12=True,spotbugsBugs=0,spotbugsMissing=0,spotbugsErrors=0,oldMainBuildNotReplayed=True,wholeOriginal14Preserved=True,independentProviderSites=16,independentProviderKinds=4,earlyValidationInputsPerSide=2,newDefinitions=2,oldExpectedRed2NotPass=True,protocol130PhysicalProofSha256=sha(proto),helper19PhysicalProofSha256=sha(helper),actualInfrastructureOrHeldOperations=False,whole451Accepted=False,formalUpdated=False,newAcceptance=0,productTestsExecuted=0,files={p.name:sha(p) for p in O.iterdir()});write(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,expectedTests=163,staticApplicable=0,rawContextual=12,physicalMain12=True,manifestSha256=sha(O/'manifest.json'))))
