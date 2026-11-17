"""Complete standalone one-class source closure, no backend caller or held type included."""
from pathlib import Path
import datetime,hashlib,json,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pgpt_closed_host_profile as policy
b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException.java';test=main.replace('/src/main/java/','/src/test/java/').replace('.java','ContractTest.java');text=(r/main).read_text();t=(r/test).read_text()
assert text.count('LogProjectionDatabaseException()')==1 and 'super("DB request log projection was not confirmed");' in text and 'extends RuntimeException' in text
assert all(x not in text+t for x in ['@BeforeAll','ProcessBuilder','DataSource','java.net','java.lang.foreign','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
assert t.count('@Test')==1 and 'new LogProjectionDatabaseException()' in t
out=b/'evidence/PG37100-p00405-projection-source-admission-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9',inputHashes={p:sha(r/p) for p in [main,test]},wholeMainClasses=1,wholeTestClasses=1,expectedTests=1,productDependency='JDK RuntimeException only; implicit Object/Throwable/String, no app helper/backend provider',owner='WBS-P004-05',heldClassfilesReadCompileInit=False,productTestsExecuted=0,actualBackendOrAuthorityActions=0,sourceReviewOnly=True)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n')
c=ld(b/'input/4456_ssc448_pure8_profile.json');c.update(id='PG37110-P00405-PROJECTION1',productionCoreMain=v['sourceCore'],oracleSpecs=[ref(b/'4469_P00405固定投影例外の独立契約仕様.md')],closureProofs=[ref(out/'manifest.json')],mainSources=[main],testSources=[dict(path=test,tests=1)],expectedTests=1,newTestDefinitions=1,pomInputs=['pom.xml','src/schubert-nk-api/pom.xml'],productOwnerByMainPath={main:'WBS-P004-05'},physicalClasses=['dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException.class'],targetClasses=['dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException'],slots={k:'evidence/01_PT/018_NK-OPS-001/evidence/PG'+str(n)+'-p00405-projection1-'+k+'-v1' for k,n in zip(['prestyle','prepare','static','preflight','unit','post'],[37102,37104,37106,37108,37110,37112])},privateDirs=dict(prepare='pg37104-p00405-projection1-prepare-v1',unit='pg37110-p00405-projection1-unit-v1'))
policy.checked_inputs(c);p=b/'input/4598_p00405_projection1_profile.json';p.open('x').write(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeClasses=1,wholeTests=1,expected=1,productRun=0)))
