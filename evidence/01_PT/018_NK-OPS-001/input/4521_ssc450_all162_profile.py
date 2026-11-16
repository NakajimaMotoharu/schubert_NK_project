"""One coherent162 source/run; preserve original160 and first independent self test."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=json.loads((b/'input/4517_ssc450_all161_profile.json').read_text())
new='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/AssetStagingSelfSuppressionTest.java'
text=(r/new).read_text();assert len(re.findall(r'@Test\s+void (\w+)\s*\(',text))==2
original=json.loads((b/'evidence/PG36868-ssc450-sql-source-manufacture-v1/manifest.json').read_text())
assert all(sha(r/p)==h for p,h in original['originalTestSourceHashes'].items())
previous=subprocess.check_output(['git','show','f808b38b68dd84ac0f943e7f483309f32f6df3f9:'+new],text=True)
def body(source):
    start=source.index('  void assetSelf001SameBodyAndCloseObjectNeverSelfSuppressesInEitherOwnedScope()')
    first=source.index('{',start);depth=1;i=first+1
    while depth:
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[start:i]
assert body(text)==body(previous),'existing ASSETSELF001 body unchanged'
for item in c['testSources']:
    if item['path']==new:assert item['tests']==1;item['tests']=2
assert sum(x['tests'] for x in c['testSources'])==162
out=b/'evidence/PG36932-ssc450-all162-source-admission-v1';assert not out.exists();out.mkdir()
proof=dict(actualExit=0,sourceCore=c['productionCoreMain'],atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    sourceInputs={p:sha(r/p) for p in c['mainSources']+[x['path'] for x in c['testSources']]},
    original160TestSourcesUnchanged=True,assetSelf001BodyUnchanged=True,
    wholeTestSources=7,expectedTests=162,newDefinitions=2,
    independentOracle='Existing160 plus same-object identity/suppressed0/ownedclose-count literals in ASSETSELF001 and REFSELF002',
    runtimeBoundary='Only memory JDBC-interface Proxy, public empty DTO and bounded executors; no driver/backend/files/native/Root/key/held operation',
    old80And161NotQualityQualified=True,oldExecCombined=False,allHelperCountersRetained=True,
    productTestsExecuted=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').open('x').write(json.dumps(proof,indent=2)+'\n')
c.update(id='PG36942-SSC450-ALL162',expectedTests=162,newTestDefinitions=2,
    oracleSpecs=c['oracleSpecs']+[ref(b/'4455_SSC450Reference自己同一cleanup追補仕様.md')],
    closureProofs=[ref(out/'manifest.json'),ref(b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json')],
    slots=dict(zip(['prestyle','prepare','static','preflight','unit','post'],[
      'evidence/01_PT/018_NK-OPS-001/evidence/'+name for name in [
        'PG36934-ssc450-all162-prestyle-v1','PG36936-ssc450-all162-prepare-v1',
        'PG36938-ssc450-all162-static-v1','PG36940-ssc450-all162-preflight-v1',
        'PG36942-ssc450-all162-unit-v1','PG36944-ssc450-all162-post-v1']])) ,
    privateDirs=dict(prepare='pg36936-ssc450-all162-prepare-v1',unit='pg36942-ssc450-all162-unit-v1'))
for p in c['slots'].values():assert not (r/p).exists()
p=b/'input/4522_ssc450_all162_profile.json';assert not p.exists();p.open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,expectedTests=162,original160Changed=0,assetSelf001Changed=0,newDefinitions=2)))
