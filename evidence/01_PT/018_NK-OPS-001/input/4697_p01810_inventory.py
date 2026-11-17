"""Public Java-only boundary inventory and explicit source/Test expectations; zero dynamic operation."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';out=b/'evidence/PG37334-p01810-source-inventory-v1';assert not out.exists();out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));ss='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md';canonical=subprocess.check_output(['git','show','origin/main:'+ss]);assert canonical==(r/ss).read_bytes()
nodes=[]
def walk(n):
 if isinstance(n,dict):
  if n.get('id','').startswith('WBS-') and n.get('ownedArtifacts'):nodes.append(n)
  for v in n.values():walk(v)
 elif isinstance(n,list):
  for v in n:walk(v)
walk(ld(r/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json'));owners={}
for n in nodes:
 for path in n['ownedArtifacts']:owners.setdefault(path,[]).append(n['id'])
patterns={
 'LOCAL_JSON_SINK':re.compile(r'logger\.log\(|System\.getLogger\('),
 'PROCESS_BOUNDARY':re.compile(r'new ProcessBuilder\('),
 'STDIO_BOUNDARY':re.compile(r'System\.(?:out|err)\.'),
 'EXPLICIT_REDACTED_DIAGNOSTIC':re.compile(r'<redacted>|\[redacted\]'),
 'DIRECT_MESSAGE_DIAGNOSTIC':re.compile(r'\.getMessage\(\)'),
 'METRIC_LABEL_API':re.compile(r'\.labelValues\(|\.labelNames\(')}
inventory=[];pins={};modules=['protocol','storage','bootstrap','api','web','batch']
for m in modules:
 for p in sorted((r/('src/schubert-nk-'+m)/'src/main/java').rglob('*.java')):
  rel=str(p.relative_to(r));text=p.read_text();pins[rel]=sha(p);hits=[dict(category=k,line=i+1,sourceAnchor=line.strip()) for i,line in enumerate(text.splitlines()) for k,pattern in patterns.items() if pattern.search(line)]
  if hits:inventory.append(dict(path=rel,module=m,sourceSha256=pins[rel],logicalOwners=owners.get(rel,[]),sourceOnly=True,hits=hits,proofStatus='INVENTORY_NOT_EXECUTION_OR_SAFETY_PASS'))
assert len(pins)==1022
testroot={m:r/('src/schubert-nk-'+m)/'src/test/java' for m in modules}
roles=[
 ('WEB-REQUEST-LOCAL','web/logging/WebRequestLogProducer','web/logging/WebRequestLogProducerTest','SS351 3.1/3.2/3.3: fixed JSON keys, closed route/method, no raw URI/query/headers/body/context; PENDING/FAILED same event; fatal retained','HOLD: imports WebStartupException; actual producer whole Test has DB/JCE fixture, no execution under this inventory'),
 ('WEB-ROUTE-METADATA','web/logging/WebRequestTrace','web/logging/WebRequestTraceTest','SS351 3.3: registered template only or /**, first business ID/one request lifetime, safe display actor','Existing source/whole proof must be located and class/source independently bound before any new test'),
 ('WEB-SECURITY-LOCAL','web/logging/WebSecurityAudit','web/logging/WebSecurityAuditTest','SS351 4/10: closed SECURITY action/reason and fixed literal JSON; password/context/cookie/CSRF/credential values absent','Whole six source-defined ordinary tests are candidates, not executed/currently qualified here'),
 ('WEB-MEDIA-LOCAL','web/logging/WebMediaAudit','web/logging/MediaAuditContractTest','SS351 3/4: closed media audit metadata, no payload/raw path/provider exception','Source contract audit, shared media owner; existing qualification before any repeat'),
 ('API-DETAILS-ALLOWLIST','api/logging/RequestLogDetails','api/logging/RequestLogDetailsTest','SS351 3.3: only responseBytes N12/userAgentFamily ASCII1..32/truncated boolean/PENDING or FAILED; duplicate/unknown/null/trailing/nonobject invalid with fixed safe exception and no cause; role supplied separately','Candidate pure memory parser: no DB/threads/process or held four class dependency in original two Test methods; inspect actual raw deficits before new PG/PT'),
 ('API-LOG-INGEST','api/logging/WebLogIngestService','api/logging/WebLogIngestServiceTest','SS351 2/3.3: source_message_id duplicate projection no repeated event; critical audit rollback, screen DB remains truth','Actual DB/transaction dependent, preserve HOLD; source-only audit not replacement PT'),
 ('WEB-FATAL-BOUNDARY','web/logging/WebRequestLogProducer','web/logging/LocalAuditGraph331Test','SSC331: cause/suppressed/SQL/JMS graph, direct Error precedence, ordinary callback fixed catalog no raw throwable text','HOLD inherited WebStartupException/producer graph; do not extract rejected/unknown operation'),
 ('BATCH-VALUE-DIAGNOSTIC','batch/file/RootServiceFacts','batch/file/ObservationValueRedactionTest','SS351 10.2: configuration/YAML/path/binding/journal data absent from fixed diagnostic, field access retains literal input','Four public-value source methods exist; actual Root/DB/Broker observation remains held; reuse proven historical exact bytes only')]
matrix=[]
for key,src,tst,expected,remaining in roles:
 module=src.split('/')[0];p=r/('src/schubert-nk-'+module)/'src/main/java/dev/codex/schubert/nk'/(src+'.java');test=r/('src/schubert-nk-'+module)/'src/test/java/dev/codex/schubert/nk'/(tst+'.java');assert p.is_file() and test.is_file(),(key,p,test);text=test.read_text();names=re.findall(r'@Test\s+void\s+(\w+)',text);assert names
 matrix.append(dict(boundaryId=key,main=ref(p),logicalOwner=owners.get(str(p.relative_to(r)),[]),testSource=ref(test),testIds=names,independentExpected=expected,unresolved=remaining,result='SOURCE_MAPPING_ONLY_NOT_PT_PASS'))
genericForbidden=['password/password hash','raw/hash/ciphertext session/context','cookie/Authorization/CSRF','HMAC/AES/private key','question/answer/fixed wire body','absolute path','provider exception/SQL bind text'];cross=[dict(category='PROCESS_BOUNDARY',expected='Only validated finite argument schema/fixed diagnostic; no command stdout/stderr/raw arguments in public logs; inspect each existing command owner before any permitted pure fixture',sourcePaths=[x['path'] for x in inventory if any(h['category']=='PROCESS_BOUNDARY' for h in x['hits'])],actualProcessOperations=0),dict(category='EXPLICIT_REDACTED_DIAGNOSTIC',expected='Each exact diagnostic target needs its own raw same-source proof, accessors/mutation/null contract and independent nonsecret canaries; marker text alone is not success',sourcePaths=[x['path'] for x in inventory if any(h['category']=='EXPLICIT_REDACTED_DIAGNOSTIC' for h in x['hits'])],allTargetsAccepted=False),dict(category='METRIC_LABEL_API',expected='Use MON catalog/low cardinality enums, no username/IP/token/path/question in labels; P01809 shared proof must stay source-bound',sourcePaths=[x['path'] for x in inventory if any(h['category']=='METRIC_LABEL_API' for h in x['hits'])],currentAllProducersAccepted=False)]
(out/'boundary-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n');(out/'source-test-expected-matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n');(out/'common-forbidden-inputs-and-remaining.json').write_text(json.dumps(dict(forbiddenFields=genericForbidden,targets=cross),ensure_ascii=False,indent=2)+'\n')
old=ld(b/'evidence/provisional/PG6930-current4222-cases/qualification.json');target='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/RequestLogDetails.java';assert old['allSourceHashes'][target]==pins[target];xml=b/'evidence/provisional/PG6930-current4222-cases/coverage/api/site/jacoco/jacoco.xml'
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='91c55386a79a59b9766fb1cc9447d7451c71c083',canonicalSS351Sha256=hashlib.sha256(canonical).hexdigest(),mainSourceInventory=1022,moduleCount=6,categoryCounts={k:sum(any(h['category']==k for h in x['hits']) for x in inventory) for k in patterns},inventorySources=len(inventory),specificSourceOracleMappings=len(matrix),originalTestsSelectedOrExecuted=0,protectedFilesOrPrivateLogsRead=False,heldClassfilesGeneratedOrRead=False,sourceOnlyWholeGateAccepted=False,original190NewAcceptance=0,effortCompletionRate=None,completedOriginalInventoryPricePp=.35,remainingOriginalDetailPp='1090.998',additionalPricePp=0,requestDetailsHistoricalSourceSame=True,historical4222OnlyNotCurrentProof=True,currentMissingNext='Inspect only exact permitted RequestLogDetails class/coverage metadata, no four held classfiles. Original independent memory Test2 alone does not prove all unfiltered private/compiler paths. If a genuine raw/code gap is found, record before repair and select necessary ordinary pure-parser PG/PT with no DB/keys/authority.',files={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()})
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,allMainSources=1022,boundarySources=len(inventory),categoryCounts=v['categoryCounts'],explicitMappings=len(matrix),newAcceptance=0)))
