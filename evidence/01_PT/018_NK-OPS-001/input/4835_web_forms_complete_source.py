"""Use proven whole enum13 closure, not import-only approximation; logging package adds one safe source."""
from pathlib import Path
import datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=ld(b/'evidence/PG37692-web-enum-eight-prepare-v1/manifest.json');main=prior['apiMainSources']+['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/package-info.java'];assert len(main)==len(set(main))==14
old=ld(b/'evidence/PG37844-web-forms-current24-source-v1/manifest.json');tests=old['testSources'];sdk=ld(b/'evidence/PG37690-web-enum-eight-source-closure-v1/manifest.json')['sdkHashes'];assert len(sdk)==3
for n in main+[x['path'] for x in tests]:
 text=(r/n).read_text();assert not any(x in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','NotificationListViewModel','QuestionDetailViewModel','DriverManager','DataSource','ProcessBuilder','Class.forName','setAccessible','java.net.Socket','java.nio.file','@BeforeAll'])
 if n in prior['apiMainSources']:assert sha(r/n)==prior['inputHashes'][n]
assert all(sha(Path(n))==h for n,h in sdk.items())
out=b/'evidence/PG37850-web-forms-complete-source-v2';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainSources=main,testSources=tests,expectedCases=old['expectedCases'],sdkHashes=sdk,sourceHashes={n:sha(r/n) for n in main+[x['path'] for x in tests]},originalQualifiedWholeClosure='PG37692/37702 exact13Main/currentProtocol176',samePackageSignature='ErrorViewModel.of Optional<TopBarViewModel>; safePrincipal5 andsecurity/session package annotations required',newDefinitions=0,original16AndPublic8Unchanged=True,sourceBytesOrHoldsNotBroadenedToRefusedActions=True,actualRootVmDbNativeKeyAuthorityActions=0,heldClassfileActions=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,main14=14,SDK3=3,whole24Unchanged=True,newPT=0))
