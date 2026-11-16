"""One-source one-exec161 for six changed SQL programs; retain all helper counters."""
from pathlib import Path
import datetime
import hashlib
import json
import re

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001'
a=json.loads((b/'input/4509_ssc450_sql80_profile_v2.json').read_text())
z=json.loads((b/'input/4511_ssc450_data80_profile.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
new='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/AssetStagingSelfSuppressionTest.java'
text=(r/new).read_text();assert len(re.findall(r'@Test\s+void (\w+)\s*\(',text))==1
assert not any(x in text for x in ['DriverManager','DataSource','Class.forName','java.lang.foreign','Files.','getenv(','ProcessBuilder'])
original=json.loads((b/'evidence/PG36868-ssc450-sql-source-manufacture-v1/manifest.json').read_text())
assert all(sha(r/p)==h for p,h in original['originalTestSourceHashes'].items())
main=sorted(set(a['mainSources'])|set(z['mainSources']));physical=sorted(set(a['physicalClasses'])|set(z['physicalClasses']))
targets=sorted(set(a['targetClasses'])|set(z['targetClasses']))
tests=a['testSources']+[dict(path=new,tests=1)]+z['testSources']
assert len(main)==26 and len(physical)==46 and len(targets)==16
assert len(tests)==7 and sum(x['tests'] for x in tests)==161
out=b/'evidence/PG36916-ssc450-all161-source-admission-v1';assert not out.exists();out.mkdir()
proof=dict(actualExit=0,sourceCore=a['productionCoreMain'],atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    scope='Six entire changed SQL Main targets16 physical including true NoCode9, plus all required entire helpers; total26Main/46physical; seven entire Test sources/161',
    original160TestSourceHashes=original['originalTestSourceHashes'],original160Unchanged=True,
    newTest=dict(path=new,sha256=sha(r/new),testId='PT-MIG-ASSETSELF-001',tests=1,conditions=6),
    sourceInputs={p:sha(r/p) for p in main+[x['path'] for x in tests]},
    independentOracle='Unchanged independent160 literal SQL/row/metadata/hash/bind/close assertions plus same-object identity/zero suppression/resource counters from4454',
    runtimeBoundary='JDBC-interface Proxy, synthetic memory datasets and bounded owned executors only; no backend/driver/app/files/native/Root/keys/held classes',
    sameExecRequired=True,old80HasBranch2Miss=True,old80NotAddedOrCombined=True,
    oldData80PlannedNotStarted=True,allHelperUncoveredCountersRetained=True,
    productTestsExecuted=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').open('x').write(json.dumps(proof,indent=2)+'\n')
a.update(id='PG36926-SSC450-ALL161',mainSources=main,testSources=tests,physicalClasses=physical,
    targetClasses=targets,productOwnerByMainPath=dict(a['productOwnerByMainPath'],**z['productOwnerByMainPath']),
    expectedTests=161,newTestDefinitions=1,
    oracleSpecs=[ref(b/'4453_SSC450閉SQL六Main単体仕様.md'),ref(b/'4454_SSC450自己同一cleanup追加試験仕様.md')],
    closureProofs=[ref(out/'manifest.json'),ref(b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json')],
    slots=dict(zip(['prestyle','prepare','static','preflight','unit','post'],[
      'evidence/01_PT/018_NK-OPS-001/evidence/'+name for name in [
       'PG36918-ssc450-all161-prestyle-v1','PG36920-ssc450-all161-prepare-v1',
       'PG36922-ssc450-all161-static-v1','PG36924-ssc450-all161-preflight-v1',
       'PG36926-ssc450-all161-unit-v1','PG36928-ssc450-all161-post-v1']])) ,
    privateDirs=dict(prepare='pg36920-ssc450-all161-prepare-v1',unit='pg36926-ssc450-all161-unit-v1'))
for path in a['slots'].values():assert not (r/path).exists()
p=b/'input/4517_ssc450_all161_profile.json';assert not p.exists();p.open('x').write(json.dumps(a,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,Main26=True,physical46=True,wholeTests=161,newDefinitions=1,old160Changed=0)))
