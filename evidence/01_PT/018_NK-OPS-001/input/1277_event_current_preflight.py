"""Source-fixed170 admission; reuse successful same14 Main analysis, refresh only changed whole Test."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';U=R.parent/'pgpt-runs/PG379/pg26578-event-main-subset-v1';O=B/'evidence/PG26598-event-current-preflight-v2';assert not O.exists();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
prior=B/'evidence/PG26582-event-preflight-v1/manifest.json';assert sha(prior)=='902bc2c3c375bc75f707caa8596384ac361e0fc6a60e5ddfb2c1c663c6cb21f3';p=load(prior);assert p['actualExit']==0 and p['applicableStaticViolations']==p['unclassified']==p['checkstyleFindings']==p['processingErrors']==0
oldCompile=B/'evidence/PG26578-event-main-subset-v1/manifest.json';old=load(oldCompile);pc=B/'evidence/PG26594-event-current-test-compile-v2/manifest.json';m=load(pc);ps=B/'evidence/PG26596-event-current-static-v2';s=load(ps/'manifest.json');assert m['actualExit']==0 and m['expectedTests']==len(m['expectedCases'])==170;assert m['inputHashes']==s['inputHashes'] and m['dependencies']==s['dependencies']==old['dependencies'];assert all(sha(R/q)==h for q,h in m['inputHashes'].items());assert m['originalMainCompile']['sha256']==sha(oldCompile)
assert m['mainClassHashes']==old['mainClassHashes']=={str(q.relative_to(U/'target/classes')):sha(q) for q in (U/'target/classes').rglob('*.class')};assert len(m['mainClassHashes'])==14
for q in m['mainSources']+m['packageSources']+['pom.xml']:assert m['inputHashes'][q]==old['inputHashes'][q]
for label,t in old['stages'].items():
 assert t['actualExit']==0 and not t['timedOut']
 for stream in ['stdout','stderr']:assert sha(oldCompile.parent/(label+'.'+stream))==t[stream+'Sha256']
assert m['testClassHashes']=={str(q.relative_to(U/'test-classes-v2')):sha(q) for q in (U/'test-classes-v2').rglob('*.class')}
test='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/InboundTransactionPortTest.java';changed={q for q,h in old['inputHashes'].items() if '/src/test/' in q and sha(R/q)!=h};assert changed=={test}
mf=load(B/'evidence/PG26592-inbound-identity-guard-manufacture-v1/manifest.json');assert mf['originalSixAllTokensInverseExact'] and mf['newDefinitions']==1 and mf['independentSameInstanceInputs']==2 and mf['afterSha256']==sha(R/test) and not mf['MainChanged']
root=ET.parse(ps/'pmd.xml').getroot();assert not any(x.tag.rpartition('}')[2] in ['error','configerror'] for x in root.iter());assert not ET.parse(ps/'checkstyle.xml').findall('.//error');assert s['stages']['checkstyle']['actualExit']==s['stages']['spotbugs']['actualExit']==0;occ=[];lines=(R/test).read_text().splitlines();reasons={'UseConcurrentHashMap':'Fixture-local synchronous maps only, deliberately null/missing provider data; no concurrent state.', 'UseProperClassLoader':'Standalone JMS interface Proxy uses defining loader for exact type identity; no J2EE server/context-loader service or access override.'}
for f in root:
 if f.tag.rpartition('}')[2]!='file':continue
 assert Path(f.get('name'))==R/test
 for x in f:
  if x.tag.rpartition('}')[2]!='violation':continue
  rule=x.get('rule');assert rule in reasons,(rule,x.attrib);at=int(x.get('beginline'));occ.append(dict(path=test,line=at,sourceLine=lines[at-1],rule=rule,classification='CONTEXTUAL_NONAPPLICABLE',reason=reasons[rule]))
assert len(occ)==4
oldContext=load(B/'evidence/PG26582-event-preflight-v1/static-contextual-thirty.json');unaffected=[x for x in oldContext if x['path']!=test];assert len(unaffected)==26
for x in unaffected:assert sha(R/x['path'])==old['inputHashes'][x['path']]
assert sha(ps/'spotbugs.xml')==sha(B/'evidence/PG26580-event-static-v1/spotbugs.xml');sb=ET.parse(ps/'spotbugs.xml').getroot();assert not any(sb.findall('.//'+v) for v in ['BugInstance','MissingClass','Error']);assert {x.get('class') for x in sb.findall('.//ClassStats')}=={x.removesuffix('.class').replace('/','.') for x in m['mainClassHashes']}
incomplete=B/'evidence/PG26586-event-independent-v1/manifest.json';im=load(incomplete);assert im['actualExit']==1 and im['unitActualExit']==0 and im['tests']==169 and im['coverage']['BRANCH']==dict(covered=1116,missed=2) and not im['wholeClosureAccepted']
O.mkdir();write(O/'current-static-contextual-thirty.json',unaffected+occ);v=dict(p,inputHashes=m['inputHashes'],dependencies=m['dependencies'],compileManifestSha256=sha(pc),staticManifestSha256=sha(ps/'manifest.json'),expectedTests=170,newDefinitions=4,originalEvent9Writer3Inbound6Preserved=True,newIdentityFailureGuardInputs=2,old169SuccessBranchIncompleteRetained=True,old169CoverageNotCombined=True,originalPreflightSha256=sha(prior),currentChangedTestRawFindings=4,unchangedOtherFixturesContextualFindings=26,rawPmd=30,wholeSourceStaticCurrent=True,freshNullAwaySame14MainNotReplayed=True,freshSpotbugsSame14MainNotReplayed=True,files={q.name:sha(q) for q in O.iterdir()});write(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,expectedTests=170,staticApplicable=0,currentTestRaw=4,unchangedRaw=26,Main14NotReplayed=True,manifestSha256=sha(O/'manifest.json'))))
