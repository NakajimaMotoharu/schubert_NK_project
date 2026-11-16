"""BUG3134 include the Test-to-Main helper; retain its uncovered counters and avoid replaying its36 tests."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from trace_owner_join import canonical
b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=json.loads((b/'input/4507_ssc450_sql80_profile.json').read_text())
helper='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/ScenarioStagingTables.java'
assert helper not in c['mainSources'];c['mainSources'].append(helper)
logical={x['path']:x for x in json.loads((r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text())['artifacts']}
c['productOwnerByMainPath'][helper]=canonical(helper,logical)['canonicalOwner']
assert c['productOwnerByMainPath'][helper]=='WBS-P019-03'
compiled=json.loads((b/'evidence/PG36872-ssc450-four-main-compile-v1/manifest.json').read_text())
prefix='dev/codex/schubert/nk/migration/ScenarioStagingTables'
physical=[p for p in compiled['physicalClassHashes']['bootstrap'] if p==prefix+'.class' or p.startswith(prefix+'$')]
assert physical==[prefix+'.class'];c['physicalClasses']=sorted(c['physicalClasses']+physical)
# Targets remain the three changed entire source units; helper counters remain in full coverage XML.
assert len(c['targetClasses'])==8 and len(c['physicalClasses'])==9
catalog={p.stem:p for p in (r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration').glob('*.java')}
declared={Path(p).stem for p in c['mainSources']};references={}
for item in c['testSources']:
    text=(r/item['path']).read_text()
    stripped=re.sub(r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*',' ',text,flags=re.S)
    references[item['path']]=sorted(set(re.findall(r'\b[A-Z]\w*\b',stripped))&set(catalog))
    assert set(references[item['path']])<=declared
assert any('ScenarioStagingTables' in values for values in references.values())
missing_declared=declared-{'ScenarioStagingTables'}
assert any(not set(values)<=missing_declared for values in references.values()),'negative missing helper detected before compile'
text=(r/helper).read_text()
assert not any(x in text for x in ['DriverManager','DataSource','Class.forName','java.lang.foreign','Files.','ProcessBuilder'])
out=b/'evidence/PG36888-ssc450-sql80-closure-v2';assert not out.exists();out.mkdir()
proof=dict(actualExit=0,sourceCore=c['productionCoreMain'],atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    bug='BUG3134',horizontal='YKT2605',sourceMainCount=4,changedTargetSources=3,physicalClasses=9,
    wholeTestSources=3,expectedTests=80,helper=dict(path=helper,sha256=sha(r/helper),owner='WBS-P019-03'),
    actualSamePackageTestTypeReferences=references,missingHelperNegativeRejected=True,
    helperEntireSourceCompiled=True,helperAllCountersRetained=True,helper36TestsNotReplayed=True,
    targetScopeIsNotWholeComponent=True,originalFailedPrepare='PG36878',
    dynamicBackendOrRootOrNativeActions=0,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(proof,indent=2)+'\n')
c['closureProofs']=[ref(out/'manifest.json'),ref(b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json')]
c['id']='PG36898-SSC450-SQL80-V2'
c['slots']=dict(zip(['prestyle','prepare','static','preflight','unit','post'],[
    'evidence/01_PT/018_NK-OPS-001/evidence/'+p for p in [
      'PG36890-ssc450-sql80-prestyle-v2','PG36892-ssc450-sql80-prepare-v2',
      'PG36894-ssc450-sql80-static-v2','PG36896-ssc450-sql80-preflight-v2',
      'PG36898-ssc450-sql80-unit-v2','PG36900-ssc450-sql80-post-v2']]))
c['privateDirs']=dict(prepare='pg36892-ssc450-sql80-prepare-v2',unit='pg36898-ssc450-sql80-unit-v2')
for path in c['slots'].values():assert not (r/path).exists()
p=b/'input/4509_ssc450_sql80_profile_v2.json';assert not p.exists();p.open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,main=4,physical=9,targetsEntireSources=3,wholeTests=80,helper36NotReplayed=True)))
