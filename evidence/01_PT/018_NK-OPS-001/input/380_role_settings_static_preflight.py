"""Independent literal table and passive static/SDK review, no role or authorization operation."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());test='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/RoleSettingsProjectionPortTest.java';text=(R/test).read_text();old=(B/'evidence/PG23250-role-prefix-before-v1/before.java').read_text();tok=lambda s:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',s);restored=tok(text)
for name,literal in [('JSON_NAME_PREFIX','"\\\"name\\\":\\\""'),('JSON_SEND_PREFIX','"\\\"send\\\":"')]:
 declaration=['private','static','final','String',name,'=',literal,';'];positions=[i for i in range(len(restored)) if restored[i:i+len(declaration)]==declaration];assert len(positions)==1;i=positions[0];del restored[i:i+len(declaration)];assert restored.count(name)==4;restored=[literal if x==name else x for x in restored]
assert restored==tok(old) and len(re.findall(r'@Test\b',text))==4
literal=r'"(?:\\.|[^"\\])*"'
def table(s):
 body=s[s.index('private static final Map<String, String> GRANTS'):s.index('@Test')];out={}
 for name,expr in re.findall(r'Map.entry\(\s*(REQUEST|'+literal+r')\s*,\s*((?:'+literal+r'\s*(?:\+\s*)?)+)\s*\)',body,re.S):
  key='nk.sync.request' if name=='REQUEST' else json.loads(name);assert key not in out;out[key]=''.join(json.loads(v) for v in re.findall(literal,expr))
 return out
expected={
 'nk.sync.request':'nk_web:send;nk_api:consume;nk_ops:browse',
 'nk.sync.reply.web':'nk_web:consume;nk_api:send;nk_ops:browse',
 'nk.async.work':'nk_api:send,consume;nk_ops:send,browse',
 'nk.web.log':'nk_web:send;nk_api:consume;nk_ops:browse',
 'nk.dead.letter':'nk_web:send;nk_api:send;nk_ops:consume,browse,manage',
 'nk.expiry':'nk_mq_maintenance:consume,browse;nk_ops:consume,browse,manage',
 'activemq.management.#':'nk_ops:send,consume,manage,createAddress,deleteAddress,createNonDurableQueue,deleteNonDurableQueue;nk_mq_maintenance:send,consume,manage,createAddress,deleteAddress,createNonDurableQueue,deleteNonDurableQueue',
 'mops.#':'nk_ops:manage,view,edit',
 'mops.queue.nk.expiry.q.countMessages':'nk_ops:manage,view;nk_mq_maintenance:manage,view',
 'mops.queue.nk.expiry.q.getMessageCount':'nk_ops:manage,view;nk_mq_maintenance:manage,view',
 'mops.queue.nk.expiry.q.getPersistentSize':'nk_ops:manage,view;nk_mq_maintenance:manage,view',
 'mops.queue.nk.expiry.q.removeMessages':'nk_ops:manage,edit;nk_mq_maintenance:manage,edit'}
assert table(text)==expected;assert table(text.replace('nk_web:send;nk_api:consume;nk_ops:browse','nk_web:consume;nk_api:consume;nk_ops:browse',1))!=expected
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';nm=load(normal);cfg=load(B/'input/379_role_settings_scope.json');assert all(sha(R/n)==nm['begin']['inputHashes'][n] for n in cfg['mainPaths']);pm=load(RUNS/'pg23256-role-settings-port-compile-v1/manifest.json');sm=load(RUNS/'pg23258-role-settings-port-static-v1/manifest.json');assert pm['actualExit']==0 and pm['inputHashes'][test]==sm['inputHashes'][test]==sha(R/test);assert sm['reports']['checkstyle']['items']==[] and not sm['reports']['pmd']['processingErrors'];items=sm['reports']['pmd']['items'];assert len(items)==1 and items[0]['rule']=='UseProperClassLoader' and items[0]['method']=='unusedSession';assert 'ClientSession.class.getClassLoader()' in text.splitlines()[int(items[0]['beginline'])-1]
prior=B/'evidence/PG23232-address-settings-static-preflight-v1/manifest.json';pr=load(prior);rvpath=B/'input/011_acceptor_parser_port_sdk_review.json';assert sha(rvpath)==pr['sdkReview']['sha256'];rv=load(rvpath);assert 'readJsonArray(String)' in rv['parserMethodClosure'] and rv['staticallyDisassembledJsonClasses']==157
for p,h in rv['staticArtifacts'].items():assert sha(R/p)==h
for p,h in pm['dependencies'].items():assert sha(p)==h
for bad in ['TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec','Root','Files.','ProcessBuilder','DriverManager','EmbeddedActiveMQ','ActiveMQClient.create']:assert bad not in text
assert 'unconnected.verify(null)' in text and 'borrowed session must remain untouched' in text
ref='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md';commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=R,text=True).strip();design=hashlib.sha256(subprocess.check_output(['git','show',commit+':'+ref],cwd=R)).hexdigest();O=B/'evidence/PG23260-role-settings-static-preflight-v1';assert not O.exists();O.mkdir();(O/'independent-role-grants.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),inputHashes=pm['inputHashes'],normalManifestSha256=sha(normal),compileManifestSha256=sha(RUNS/'pg23256-role-settings-port-compile-v1/manifest.json'),staticManifestSha256=sha(RUNS/'pg23258-role-settings-port-static-v1/manifest.json'),pmdRaw=1,pmdApplicable=0,checkstyle=0,unclassified=0,sourceRemedyInverseTokens=True,jsonPrefixReplacementSites=8,independentGoldenMatches=12,independentGoldenRoles=27,independentGoldenBooleanValues=324,goldenSha256=sha(O/'independent-role-grants.json'),goldenNegativeChecks=1,designRefs=[dict(commit=commit,path=ref,sha256=design)],pmdClassifications=[dict(finding=items[0],disposition='NOT_APPLICABLE',reason='Exact public interface defining loader for a standalone JUnit proxy, no J2EE owner. Every session method raises; no provider/session/network operation. Context loader replacement introduces ambient type resolution.')],sdkReview=dict(path=str(rvpath.relative_to(R)),sha256=sha(rvpath),parentObjectPreflightSha256=sha(prior),parserClosure=rv['parserMethodClosure']),expectedTests=4,originalTestsCompiled=0,productTestsExecuted=0,actualBackendActions=0,heldFourInitializationsAllowed=False,formalUpdated=False,newAcceptance=0,whole451Accepted=False,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,compile=0,pmdRaw=1,pmdApplicable=0,checkstyle=0,goldenRoles=27,expectedTests=4)))
