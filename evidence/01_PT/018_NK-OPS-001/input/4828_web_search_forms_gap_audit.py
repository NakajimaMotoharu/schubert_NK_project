"""Source/public proof only; no JUnit/compiler/new analyzer or held source access."""
from pathlib import Path
import datetime,hashlib,json,re,shutil
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
oldpath=b/'evidence/provisional/PG14272-web-three-forms-whole-twenty-four-post-v1/manifest.json';old=ld(oldpath);newpath=b/'evidence/PG37702-web-enum-eight-independent-v1/manifest.json';new=ld(newpath);unionpath=b/'evidence/PG37782-pure-protocol-web-maxlow-prepare-v1/manifest.json';union=ld(unionpath)
assert old['actualExit']==0 and old['tests']==24 and old['failures']==old['errors']==old['skipped']==0 and old['singleSession'] is True
names=sorted(n for n in old['physicalClasses'] if 'SearchForm' in n);assert len(names)==6 and all(union['physicalClassHashes'][n+'.class']==old['physicalClasses'][n] for n in names)
methods=[x for x in new['allMeasuredMethods'] if x['className'] in names];assert len(methods)==52
source=[f'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/{stem}.java' for stem in ['ScenarioSearchForm','LogSearchForm']];tests=[n.replace('/main/','/test/').replace('.java','Test.java') for n in source]
fixture=[]
for n in tests:
 text=(r/n).read_text();ids=re.findall(r'@Test\s+void (\w+)\s*\(',text);assert len(ids)==8
 assert all(x not in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','DriverManager','DataSource','ProcessBuilder','Class.forName','setAccessible','@BeforeAll'])
 assert 'shutdownNow()' in text and 'awaitTermination(10, TimeUnit.SECONDS)' in text and 'get(10, TimeUnit.SECONDS)' in text
 fixture.append(dict(path=n,sha256=sha(r/n),wholeTestIds=ids,count=8,finiteCleanupVerified=True))
closure=[]
for n in source:
 text=(r/n).read_text();assert all(x not in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','DriverManager','DataSource','java.net.Socket','ProcessBuilder'])
 closure.append(dict(path=n,sha256=sha(r/n),imports=[x for x in text.splitlines() if x.startswith('import ')]))
standard=sum(old['fullSourceUnits'][n]['totals']['METHOD']['covered'] for n in ['dev/codex/schubert/nk/web/form/LogSearchForm','dev/codex/schubert/nk/web/form/ScenarioSearchForm']);assert standard==36
out=b/'evidence/PG37834-web-search-forms-gap-audit-v1';assert not out.exists();out.mkdir();index=r.parent/'pgpt-runs/PG379/pg37834-form-followup-index.json';shutil.copyfile(index,out/'followup-index.json');assert ld(out/'followup-index.json')['acceptanceInferred'] is False
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',oldWhole24=ref(oldpath),currentPublicEnum8=ref(newpath),currentByteUnion251=ref(unionpath),sourceInputs=closure,wholeFixtures=fixture,oldSource='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',sixCurrentByteHashesExactOld=True,physicalClasses6=names,oldStandardMethodCovered=36,actualJvmCodeMethods=52,filteredMethodDifference=16,methodMetadata=methods,completeCurrent52SingleRunNotYetQualified=True,separateEnumExecCannotBeMerged=True,necessaryNextWhole=dict(originalTwoFixtures16=16,existingPublicEnumWhole8=8,total=24,newDefinitions=0,sourceClasses=3,QuestionOld8NotRepeated=True),independentOracles=['UI222223225234235/SS313352: input parameter allowlist/count, originalNFC é andUTF8 limits, page1..999999/default1, request size100','UI235/SS313: JST→fixedUTC,31days±1ms,strict leap/year/time format, no producer/DB operation','Originalfixtures: null key/list/item rejection, immutable defensive copies, fixed redacted string;64tasks each with finite get/cleanup'],newCompileOrProductRunOrAnalyzer=False,heldSourceOrBinaryActions=0,actualRootVmDbNativeKeyAuthorityActions=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,bug='BUG3192',crossDeployment='YKT2659',metadataRecovery='Bare14272 dirname absent; rg filename index identified actual provisional path, no job reissued.')
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,old6ByteExact=True,standard36=36,actualCode52=52,unqualifiedCurrentSingleRun=True,newPT=0))
