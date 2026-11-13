"""Independent exact inverse + actual local source checks; retain haruka permission hold, no retry."""
from pathlib import Path
import json,hashlib,datetime,subprocess,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG30590-gate12-source-proof-and-haruka-permission-hold-v1';assert not e.exists();e.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
t=r/'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java';old=(b/'evidence/PG30584-gate12-worker-source-repair-v1/GateCliTest.before.java.txt').read_text();new=t.read_text()
header='    var executor = Executors.newVirtualThreadPerTaskExecutor();\n    try {\n'
cleanup='      first.get(5, TimeUnit.SECONDS);\n    } finally {\n      releaseSerialization.countDown();\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }\n'
assert new.count(header)==new.count(cleanup)==1
inverse=new.replace(header,'    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {\n').replace(cleanup,'      first.get(5, TimeUnit.SECONDS);\n    }\n');assert inverse==old
assert len(re.findall(r'@Test\b',new))==12
main=r/'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java'
assert sha(main)==json.loads((b/'evidence/PG30584-gate12-worker-source-repair-v1/manifest.json').read_text())['mainSha256']
tc=r.parent/'toolchain';commands=[]
for label,args in [('format-source-only',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(t)]),('checkstyle-source-only',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),str(t)])]:
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:code=subprocess.run(args,stdout=out,stderr=err,timeout=60,check=False).returncode
 commands.append(dict(label=label,command=args,actualExit=code));assert code==0
l=r/'documents/900_OTHER/910_台帳';p=l/'915_障害表.md';assert max(map(int,re.findall(r'^## BUG-(\d+)\b',p.read_text(),re.M)))==2873
p.write_text(p.read_text()+'''\n\n## BUG-2874 PT 2026-11-14 haruka direct-OS toolchain admission / NK-CHR-001 Gate原12・必要common58

重要度中・優先高。期待: server.info haruka/mini・PMO専用knownHostsで認証後、PMO構築済み専用JDK25.0.4を同利用者が読取/実行でき、個別PGPTのresource/source/owner前提を検証できる。実際: PG30588 SSH真正exit1、auth一回・strict pin、Python読取inventoryで /opt/schubert-nk-test-tools/jdk-25.0.4/bin/java にPermissionError。試験/compile/job/source upload/DB/VM/Root/サービス/権限変更0。再現: 当read-only inventory原run公開terminal/failure、追加probeで再現しない。原因: access拒否は確認、ディレクトリowner/mode/ACLや他toolの共通原因は未確認、推定で埋めない。影響: Gate12/common58のharuka専用実行前提未成立、disk/memory/所有の完全inventory未回収。BUG2873/SS355/451/WBS-F03/F04、環境資格で業務仕様変更不要。PG30586は初producerが非0詳細を保存せずUNKNOWN、PG30588の原因を旧runへ転用しない。YKT2410。修正なし/修正commitなし/再試験なし、証跡PG30588・PG30590。状態OPEN、完了日未、権限/別path/別user/別hostで迂回せず既存許可済み独立PGPT継続。\n''')
p=l/'916_横展開管理台帳.md';assert max(map(int,re.findall(r'^## YKT-(\d+)\b',p.read_text(),re.M)))==2409
p.write_text(p.read_text()+'''\n\n## YKT-2410 BUG2874 haruka dedicated toolchain access prerequisite

共通原因は未確定。検索条件=PMO HARUKA_EXECUTION_ENVIRONMENT.json専用tool pathとPGPT miniアクセス要件。対象: JDK javaはPermissionError実測、javac/Maven/親directory/ACLは未確認、JDKを使うGate12/common58の開始は保留。DB/Artemis/Caddy/原本/他hostは当read-only runで読取/操作しておらず非該当と断定しない。修正・追加品質checkは正規のowner/permission契約確定後だけ、勝手chmod/sudo/alternate path/userや再probeなし。関係commit未、元PG30588 terminal/failure・PG30590独立source/保留を参照。全対象の是正又は非該当根拠と必要再発防止確認が未、状態OPEN。\n''')
full=[main,t,r/'pom.xml',r/'program/characterization/pom.xml']
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='689c5ffff95dd73cb717f2709bd5e4d384001dee',bug='BUG-2873',exactInverseAllOtherBytes=True,originalWhole12Retained=True,newTestDefinitions=0,mainUnchanged=True,commands=commands,reviewedSources=[dict(**ref(q),lines=len(q.read_text().splitlines())) for q in full],sourceReview=dict(allGateMain667=True,wholeTestHelpersReviewed=True,reachableNetworkDbProcessExecution=False,realCurrentCapture=False,baselinePromotionOnlyNewFixture=True,originalBaselineReadOnly=True,dummyJavaCaddyPgCtlNeverExecuted=True,expectedFromIndependentLiteralsAndApprovedPublicReports=True,realHighDiskGiB=20,lowTempDiskGiBLessThan=20,commonBundleNeeded58=True,old46NotReplayed=True),hostAttempt1=ref(b/'evidence/PG30586-haruka-readonly-gate-eligibility-v1/manifest.json'),hostAttempt2Terminal=ref(b/'evidence/PG30588-haruka-readonly-gate-eligibility-recorded-v2/terminal.json'),hostAttempt2Failure=ref(b/'evidence/PG30588-haruka-readonly-gate-eligibility-recorded-v2/failure.json'),hostEligibility='HOLD_BUG2874_PERMISSION_PREREQUISITE_INCOMPLETE',hostCurrentResources=None,hostCurrentOwnedJobs=None,harukaActualTestExecutions=0,sourceUploads=0,newRuntimeJobs=0,permissionChanges=0,alternatePathOrUserRetry=0,aruOperations=0,existingHoldsReleased=False,testsExecuted=0,coverage=None,formalAccepted=False,newAcceptance=0,bugsOpen=['BUG-2873','BUG-2874'],horizontalOpen=['YKT-2387','YKT-2410'])
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceInverse=True,sourceChecks0=True,newBug='BUG-2874',horizontal='YKT-2410',normalWhole12NotRun=True,harukaEligibility='HOLD')))
