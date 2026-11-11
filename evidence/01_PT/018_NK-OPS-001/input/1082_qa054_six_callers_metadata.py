"""Six whole-suite HOLD decisions from explicit source witnesses; no compilation or application run."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,re,subprocess
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26034-qa054-six-callers-source-v1'
P=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
table=P/'QA054六呼出元の作業票.tsv';assert sha(table)=='40db14c9ce854d7fb153c3c43ee16485a35cbd37c270f1a7e108d96acde5aa53'
rows=list(csv.DictReader(table.open(encoding='utf-8-sig'),delimiter='\t'));assert len(rows)==6
post=E/'PG25760-weblog-codec-whole9-independent-v1/manifest.json';assert sha(post)=='2a9228374b8ed2b84f4976c8eee4575c650cf2ed62e603e8da242548f1d89596'
proof=load(post);pf=load(R/proof['preflight']['path']);assert sha(R/proof['preflight']['path'])==proof['preflight']['sha256']
golden='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogPayloadCodecTest.java'
assert sha(R/golden)==pf['inputHashes'][golden]
gold=(R/golden).read_text();assert 'ascii(wire, 256 + 41, "HTTP_REQUEST_COMPLETED");' in gold and 'new byte[2_336]' in gold and '"HTTP_COMPLETED"' not in gold
vector=E/'PG25794-weblog-current-public-vector-v1/manifest.json';v=load(vector)
assert v['actualExit']==0 and v['approvedAction']=='HTTP_REQUEST_COMPLETED' and v['plaintextBytes']==2336 and v['wireSha256']=='2f1a567b2de4217dbb6a050f01b14d0e537c2b9b887b6c5895a9aa8a95abb74c'
root='src/schubert-nk-web/src/';sender=root+'main/java/dev/codex/schubert/nk/web/logging/WebLogMessageSender.java'
dispatcher=root+'main/java/dev/codex/schubert/nk/web/logging/WebLogDispatcher.java'
database=root+'test/java/dev/codex/schubert/nk/web/logging/WebLogDatabaseFixture.java'
witnessFiles={p:(R/p).read_text() for p in [sender,dispatcher,database]}
assert 'WebStartupException.preserveFatal(failure)' in witnessFiles[sender]
assert 'WebStartupException.attachSecondary' in witnessFiles[dispatcher]
assert 'ProcessBuilder builder' in witnessFiles[database] and '"initdb"' in witnessFiles[database]
textByName={};bindings={}
for r in rows:
 path=r['停止HEADの元ファイル'];blob=subprocess.check_output(['git','rev-parse','HEAD:'+path],text=True).strip();assert blob==r['Git blob']
 text=(R/path).read_text();assert 'WebLogPayloadCodecTest.goldenWire()' in text and '"HTTP_COMPLETED"' not in text
 textByName[r['呼出元試験']]=text;bindings[path]=dict(sha256=sha(R/path),gitBlob=blob)
callers=[]
for r in rows:
 name=r['呼出元試験'];t=textByName[name];p=r['停止HEADの元ファイル']
 if name=='JmsSecondary330Test':
  needles=['new WebLogMessageSender(codec, this::open).send(row)','codec.encrypt(identity, WebLogPayloadCodecTest.goldenWire())']
  hold=['Shared WebLogMessageSender calls held WebStartupException; original suite also tests ArtemisRequestSender. In-memory JMS proxies are not authorization to initialize held helpers.']
 elif name=='HttpRequestLoggingValveTest':
  needles=['new WebLogDatabaseFixture(root)','WebLogPayloadCodecTest.goldenWire()']
  hold=['Whole-suite database setup invokes initdb/ProcessBuilder/JDBC via WebLogDatabaseFixture; DB HOLD. No extraction of the pure codec subcase.']
 else:
  needles=['WebLogMessageSenderTest.broker(', 'WebLogPayloadCodecTest.goldenWire()'] if name!='WebLogMessageSenderTest' else ['EmbeddedActiveMQ','new EmbeddedActiveMQ().setConfiguration(configuration).start()','WebLogPayloadCodecTest.goldenWire()']
  hold=['Whole-suite embedded broker or DB actions and/or shared held WebStartupException; dynamic invocation/compile HOLD. No subset, helper substitution or alternative execution.']
 assert all(n in t for n in needles),(name,needles)
 evidence=[dict(path=p,line=i+1,text=line.strip()) for i,line in enumerate(t.splitlines()) if any(n in line for n in needles)]
 methods=re.findall(r'@Test\s+(?:final\s+)?void\s+([A-Za-z0-9_]+)',t)
 callers.append(dict(name=name,testSource=bindings[p],path=p,owner=r['既存の個別契約に登録された名義'],candidateSource='7aed8eace7c844c2f79f2e39db766faf914890d5',fixtureAction='HTTP_REQUEST_COMPLETED',fixtureSha256=sha(R/golden),compatibility='SOURCE_EXPECTATION_CONSISTENT_DYNAMIC_UNVERIFIED',actionInterpretation=('API SS312 fixture already rewrites Action to the same approved literal; no additional Action difference. Details projectionStatus override retained.' if name=='WebApiLogReplayIntegrationTest' else 'Shared transport/ciphertext byte comparisons use the current golden dynamically; no stale hardcoded HTTP_COMPLETED literal.'),testMethods=methods,goldenCallSites=t.count('WebLogPayloadCodecTest.goldenWire()'),sourceWitnesses=evidence,operation='COMPLETE_ORIGINAL_SUITE',decision='NOT_RUN_HOLD',requiredConditions=hold,executedTests=0,coverage=None,independentStaticAnalysisPassClaimed=False,fullPgReviewClaimed=False,extraBudgetAddedPp=0,nextWorkOwner='Existing individual B contract; restrictions must be resolved independently. No automatic HOLD release.'))
t=textByName['WebApiLogReplayIntegrationTest'];assert 'Arrays.fill(wire, 297, 361' in t and '"HTTP_REQUEST_COMPLETED".getBytes' in t and '"{\\"projectionStatus\\":\\"PENDING\\"}"' in t
assert 256+41==297 and 361-297==64 and len('HTTP_REQUEST_COMPLETED'.encode('ascii'))==22
assert not O.exists();O.mkdir();out=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',golden=dict(path=golden,sha256=sha(R/golden),changedAction='HTTP_COMPLETED -> HTTP_REQUEST_COMPLETED',absoluteFieldStart=297,fieldLength=64,actionBytes=22,paddingBytes=42,wireBytes=2336),vectorReference=dict(path=str(vector.relative_to(R)),sha256=sha(vector),reexecuted=False),planTable=dict(path=str(table),sha256=sha(table)),callers=callers,witnessDependencies={p:sha(R/p) for p in witnessFiles},callerConclusions=6,sourceConsistentCallers=6,dynamicHeldCallers=6,productTestsExecuted=0,normalCompilerOrJavaParsingExecuted=False,actualDbBrokerOrHeldCalls=0,bug2615Closed=False,ykt2303Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,fullPgReviewClaimed=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,callerConclusions=6,sourceExpectationsConsistent=6,dynamicHeld=6,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
