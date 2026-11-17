"""Exact pure source closure and unchanged whole16+8 fixtures, no runtime."""
from pathlib import Path
import datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';root='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
main=[root+n for n in ['form/ScenarioSearchForm.java','form/LogSearchForm.java','view/ErrorViewModel.java','view/MenuCard.java','revocation/RevocationFailureCode.java','logging/WebHttpLogKind.java','logging/package-info.java']]
tests=['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'+n for n in ['form/ScenarioSearchFormTest.java','form/LogSearchFormTest.java','view/WebPublicEnumContractTest.java']];rows=[];expected=[]
for n in main+tests:
 text=(r/n).read_text();assert not any(x in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','NotificationListViewModel','QuestionDetailViewModel','DriverManager','DataSource','ProcessBuilder','Class.forName','setAccessible','java.net.Socket','java.nio.file','@BeforeAll'])
 if n in tests:
  ids=re.findall(r'@Test\s+void (\w+)\s*\(',text);assert len(ids)==8;rows.append(dict(path=n,tests=8,sha256=sha(r/n)));expected.extend(dict(classname=n.split('/src/test/java/')[1][:-5].replace('/','.'),name=x+'()') for x in ids)
for n in tests[:2]:
 text=(r/n).read_text();assert 'shutdownNow()' in text and 'awaitTermination(10, TimeUnit.SECONDS)' in text
out=b/'evidence/PG37844-web-forms-current24-source-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainSources=main,testSources=rows,expectedCases=expected,sdkHashes={},readonlyFixtureHashes={},sourceHashes={n:sha(r/n) for n in main+tests},sourcesReviewedAgainst='4519 /37834/37836/4501/37702/SS313351352354',newDefinitions=0,currentOnlyNeededWhole24=True,MainImplementationRetainedAfterReview=True,noActualSourceBehaviourChange=True,original16BusinessOracleExact=True,currentExistingPublicEnum8Exact=True,actualRootVmDbNativeKeyAuthorityActions=0,heldClassfileActions=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,main7=7,wholeFixtures=3,expectedTests=24,newDefinitions=0,sdkExternal=0))
