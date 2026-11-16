"""Admit complete self-contained first3/80 ordinary tests, no method selection or backend."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from trace_owner_join import canonical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain'
core='84d9d3eda489c89c522ff4a4785a12c4c5a51f20'
compile_path=b/'evidence/PG36872-ssc450-four-main-compile-v1/manifest.json'
compiled=json.loads(compile_path.read_text());assert compiled['actualExit']==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
names={'AssetStagingTables':32,'MigrationMasterColumnVerifier':26,'MigrationMasterConstraintVerifier':22}
prefix='dev/codex/schubert/nk/migration/'
main=['src/schubert-nk-bootstrap/src/main/java/'+prefix+n+'.java' for n in names]
tests=[dict(path='src/schubert-nk-bootstrap/src/test/java/'+prefix+n+'Test.java',tests=count) for n,count in names.items()]
logical={x['path']:x for x in json.loads((r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text())['artifacts']}
owners={p:canonical(p,logical)['canonicalOwner'] for p in main};assert set(owners.values())=={'WBS-P019-03'}
pins={p:sha(r/p) for p in main+[x['path'] for x in tests]}
for path,h in pins.items():
    assert hashlib.sha256(subprocess.check_output(['git','show',core+':'+path])).hexdigest()==h
    source=(r/path).read_text()
    assert not any(word in source for word in ['DriverManager','DataSource','Class.forName','java.lang.foreign','java.net.Socket','ProcessBuilder','@BeforeAll','@TestFactory','@ParameterizedTest','Files.','getenv('])
for item in tests:
    source=(r/item['path']).read_text();methods=re.findall(r'@Test\s+void (\w+)\s*\(',source)
    assert len(methods)==item['tests']
physical=sorted(n for n in compiled['physicalClassHashes']['bootstrap'] if
    any(n==prefix+name+'.class' or n.startswith(prefix+name+'$') for name in names))
assert len(physical)==8
out=b/'evidence/PG36874-ssc450-sql80-source-admission-v1';assert not out.exists();out.mkdir()
proof=dict(actualExit=0,sourceCore=core,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    scope='Three entire Main sources/eight physical including four true NoCode private interfaces, three entire original Test classes/80 declarations',
    inputHashes=pins,ownerByMain=owners,physicalClasses=physical,
    independentOracle='Original unchanged literal SQL/column/constraint/row/timeout/order/null/exception/close assertions in the three whole Test sources; source equivalence only supplemental',
    runtimeBoundary='Only JDBC-interface Proxy fixtures and owned bounded executor tasks; no backend driver/JAR/app/files/native/Root/key/held classes',
    sourceEffectsReviewed=True,remainingOther3Tests=80,wholeSixNotYetAccepted=True,
    productTestsExecuted=0,heldClassfileActions=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
c=json.loads((b/'input/4459_ssc448_pure8_profile_v3.json').read_text())
c.update(id='PG36884-SSC450-SQL80',productionCoreMain=core,mainSources=main,testSources=tests,
    expectedTests=80,newTestDefinitions=0,pomInputs=['pom.xml','src/schubert-nk-bootstrap/pom.xml'],
    productOwnerByMainPath=owners,physicalClasses=physical,targetClasses=[n[:-6] for n in physical],
    oracleSpecs=[ref(b/'4453_SSC450閉SQL六Main単体仕様.md')],
    closureProofs=[ref(out/'manifest.json'),ref(b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json')],
    sdkJars=['com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'],
    slots=dict(zip(['prestyle','prepare','static','preflight','unit','post'],[
       'evidence/01_PT/018_NK-OPS-001/evidence/'+name for name in [
       'PG36876-ssc450-sql80-prestyle-v1','PG36878-ssc450-sql80-prepare-v1',
       'PG36880-ssc450-sql80-static-v1','PG36882-ssc450-sql80-preflight-v1',
       'PG36884-ssc450-sql80-unit-v1','PG36886-ssc450-sql80-post-v1']])),
    privateDirs=dict(prepare='pg36878-ssc450-sql80-prepare-v1',unit='pg36884-ssc450-sql80-unit-v1'))
c['preparedDependencyHashes']={str(p):sha(p) for p in [tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',
    tc/'junit-platform-console-standalone-1.13.4.jar',tc/'m2/repository'/c['sdkJars'][0]]}
for path in c['slots'].values():assert not (r/path).exists()
p=b/'input/4507_ssc450_sql80_profile.json';assert not p.exists();p.open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,main=3,physical=8,wholeTests=80,remainingOther80=True,profile=str(p.relative_to(r)))))
