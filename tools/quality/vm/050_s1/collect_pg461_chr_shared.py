"""Fixed shared-Current L01 helper tests: safe XML only, never native/production acceptance."""
import hashlib, json, pathlib, xml.etree.ElementTree as E
R = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
O = R / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG461-chr-shared-l01-unit-v1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
log = W / 'pg461-chr-shared-l01-unit-v1.log'
assert 'BUILD SUCCESS' in log.read_text() and 'BUILD FAILURE' not in log.read_text()
assert not O.exists()
O.mkdir(mode=0o750)
files = []
for name, count in [('SharedLogProjectionDriverTest', 2), ('TargetAdapterTest', 3), ('ArtifactComparatorTest', 5)]:
    p = R / ('program/characterization/target/surefire-reports/TEST-dev.codex.schubert.characterization.' + name + '.xml')
    q = E.parse(p).getroot()
    assert int(q.get('tests')) == count and len(q.findall('testcase')) == count
    assert all(int(q.get(k)) == 0 for k in ['failures', 'errors', 'skipped'])
    s = E.Element('testsuite', {k:q.get(k) for k in ['name','tests','failures','errors','skipped','time']})
    for c in q.findall('testcase'):
        assert all(child.tag in ('system-out','system-err') for child in c)
        E.SubElement(s,'testcase',{k:c.get(k) for k in ['name','classname','time']})
    E.indent(s)
    out = O / p.name
    E.ElementTree(s).write(out, encoding='utf-8', xml_declaration=True)
    files.append({'path':out.name,'sha256':sha(out)})
m = {'id':O.name,'branch':'dev-foundation','sourceCommitBeforeChanges':'00785cf0698aecf1ace1e60b87e8849639e85b97',
    'sourceDirtyAtExecution':True,'exitCode':0,'tests':10,'suites':3,'failures':0,'errors':0,'skipped':0,
    'finishedAt':'2026-10-05T05:00:04+09:00','startTime':'not persisted; not inferred',
    'environment':'Linux/JDK25.0.4/Maven3.9.12','command':'./mvnw -o -pl program/characterization spotless:apply test -Dtest=SharedLogProjectionDriverTest,TargetAdapterTest,ArtifactSinkTest,ArtifactComparatorTest (3 existing classes/10 actual cases)',
    'testIds':['CHR-L01-shared-operation-order','CHR-L01-query-failure'],'relatedSsc':['SSC-182','SSC-183'],
    'expected':'literal Current navigation order/search/ACTION/page1, DB snapshot read once before DOM counts, independent actions/types and 2 rows/details; empty and failed DB query cannot pass',
    'actual':'10 actual cases pass; nonexistent ArtifactSinkTest selector produced no cases and is not counted',
    'sourceFilesSha256':{str(p.relative_to(R)):sha(p) for p in [R/'program/characterization/tests/java/dev/codex/schubert/characterization/CurrentCharacterizationTest.java',R/'program/characterization/tests/java/dev/codex/schubert/characterization/SharedLogProjectionDriverTest.java']},
    'logSha256':sha(log),'files':files,'formal':False,'nativeL01Accepted':False,'productionPtAdded':0,'coverageQualified':False,
    'limitations':['No browser or VM fixture run; no Current baseline rewrite, action normalization, source/run substitution or outage replay acceptance.'],
    'redaction':'Only suite/case names and public flags; XML properties/stdout/stderr omitted; no credential or token.'}
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':m['id'],'tests':10,'suites':3,'manifestSha256':sha(O/'manifest.json')}))
