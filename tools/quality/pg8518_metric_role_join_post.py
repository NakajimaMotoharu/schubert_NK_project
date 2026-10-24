"""Independent six new SS/role-schema contracts; never a new Main coverage qualification."""
import copy
import datetime
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import scoped_prometheus_post as post
import pg8516_metric_role_join_host as original
from host_tool_invocation import capture, verify

host = post.host
RUN = host.W / 'pg8516-metric-role-join-host-v1'
OUT = host.BASE / 'PG8518-metric-role-join-post-v1'
RAW_SHA = '1c9ea4814ae4f69e2c65a05ba1cf3993a1b3aad784adef0151d4aead15065e47'
SS = 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
SS_SHA = '9da7c4e4f24740e031f37f984ec562d56e14ff098b1433af3ec55fe15bd195e6'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert not OUT.exists() and host.sha(RUN / 'manifest.safe.json') == RAW_SHA
    raw = json.loads((RUN / 'manifest.safe.json').read_text())
    post.common.SOURCE = original.SOURCE
    post.COUNTS = original.COUNTS
    post.assess(raw)
    assert host.sha(original.COMPILE / 'manifest.safe.json') == original.COMPILE_SHA
    normal = json.loads((original.COMPILE / 'manifest.safe.json').read_text())
    assert normal['source'] == original.SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    for path, digest in normal['begin']['inputHashes'].items():
        assert host.sha(host.ROOT / path) == host.sha(original.COMPILE / 'snapshot' / path) == digest
    for key in ('dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes'):
        assert all(host.sha(Path(p)) == h for p,h in raw['begin'][key].items())
    assert host.sha(host.ROOT / SS) == SS_SHA
    canonical = subprocess.check_output(['git','show','origin/main:' + SS],cwd=host.ROOT)
    import hashlib
    assert hashlib.sha256(canonical).hexdigest() == SS_SHA
    assert host.sha(RUN / 'jacoco.exec') == raw['execSha256']
    cases = []
    for path in sorted((RUN / 'xml').glob('TEST-*.xml')):
        assert host.sha(path) == raw['xmlHashes'][path.name]
        suite = ET.parse(path).getroot()
        assert {k:int(suite.get(k,'0')) for k in ('tests','failures','errors','skipped')} == dict(tests=6,failures=0,errors=0,skipped=0)
        for case in suite.findall('testcase'):
            assert not list(case)
            cases.append((case.get('classname'),case.get('name')))
    assert len(cases) == len(set(cases)) == 6 and {name[:13] for _,name in cases} == {'metricjoin001','metricjoin002','metricjoin003','metricjoin004','metricjoin005','metricjoin006'}
    assert set(cases) == {(r['classname'],r['name']) for r in raw['cases']}
    assert len(raw['stages']) == 2
    for stage,name in zip(raw['stages'],('fresh-test-compile.log','selected-junit.log')):
        assert stage['actualExit'] == 0 and not stage['timedOut'] and host.sha(RUN / name) == stage['logSha256']
    rejected = []
    for name,mutate in (
        ('source-tail',lambda r:r.update(source=post.different_source_tail(r['source']))),
        ('failed-case',lambda r:r['cases'][0].update(result='NOT_PASS')),
        ('duplicate-case',lambda r:r['cases'].__setitem__(1,copy.deepcopy(r['cases'][0]))),
        ('fixture-change',lambda r:r['begin'].update(fixtureHashes={'unknown':'0'*64})),
        ('coverage-union',lambda r:r['begin'].update(priorCoverageTransferred=True)),
        ('formal-inflation',lambda r:r.update(formalUpdated=True)),
        ('timeout-pass',lambda r:r['stages'][1].update(timedOut=True))):
        candidate = copy.deepcopy(raw)
        mutate(candidate)
        try:
            post.assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('every metadata guard rejects')
    assert len(rejected) == 7
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0,source=original.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,originalManifestSha256=RAW_SHA,normalManifestSha256=original.COMPILE_SHA,normalCompileReplayed=False,tests=6,suites=1,failed=0,errors=0,skipped=0,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],independentSs=dict(path=SS,sha256=SS_SHA,originMainByteIdentical=True),technicalSchemaMeasurement=dict(roleRows=29,uniqueNames=26,api=16,web=7,batch=6,sharedNames=['nk_outbox_rows','nk_outbox_oldest_seconds','nk_db_pool_connections']),newNegativeGuards=rejected,productionSourceChanged=False,newProductionClasses=0,coverageQualified=False,staticQualificationAdded=False,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,providerOrEndpointAccepted=False,productTestsExecutedByPost=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT / 'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=6,uniqueSchemaNames=26,roleRows=29,newMain=0,coverageQualified=False,manifestSha256=host.sha(OUT / 'manifest.json'))))

