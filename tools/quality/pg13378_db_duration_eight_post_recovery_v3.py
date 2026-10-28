"""Independent original8 XML/exec/same-source two-class four counters, no Product Test replay."""
import copy
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validation
import pg13374_db_duration_eight_pt as original
import pg9666_pagination_static as runner

RAW = '4b1ec5302ed94d27ecdcfe20aa48b158a6db645a70165a5db9c58a629b9075fc'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13374-db-duration-eight-pt-v1'
OUT = data.BASE/'PG13378-db-duration-eight-post-recovery-v3'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13378-db-duration-eight-post-recovery-v3'
PREFIX = 'dev/codex/schubert/nk/api/monitoring/'
NAMES = {PREFIX+'DbQueryDurationMetricCollector',PREFIX+'DbQueryDurationMetricCollector$Observation'}

def assess(raw):
    validation.common.SOURCE = original.SOURCE;validation.COUNTS = original.COUNTS;validation.EXPECTED_FIXTURE_HASHES = {}
    validation.assess(raw)

def receipt_classpath(stages,audit,libraries,jdk):
    command = stages[1]['command'];assert len(command) == 6 and command[:2] == [str(jdk/'java'),'-cp']
    parts = command[2].split(os.pathsep);assert parts[0] == str(audit) and len(parts) == len(libraries)+1 and len(set(parts)) == len(parts) and set(parts[1:]) == set(libraries)
    compiled = stages[0]['command'];assert compiled[:2] == [str(jdk/'javac'),'--release'] and compiled[compiled.index('-cp')+1].split(os.pathsep) == parts[1:]
    assert command[3:] == ['CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]
    return command[2]

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    raw = data.read_checked(data.BASE/'PG13374-db-duration-eight-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes()) == RAW;assess(raw)
    normal = data.read_checked(data.BASE/'PG13362-api-maintenance-literal-v1/manifest.json',original.COMPILE_SHA)
    static_post = data.read_checked(data.BASE/'PG13367-api-maintenance-literal-v1/manifest.json','f76bc7122d47b49ff7389c1937361e841beb3293e4c7ed20d0203a025b54de0d')
    prior = data.read_checked(data.BASE/'PG13368-api-maintenance-literal-v1/manifest.json','ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186')
    assert normal['source'] == static_post['source'] == prior['source'] == raw['source'] == original.SOURCE
    assert normal['actualExit'] == static_post['actualExit'] == normal['testsExecuted'] == 0
    snapshot = original.COMPILE/'snapshot';hashes = normal['begin']['inputHashes']
    assert hashes == raw['begin']['sourceHashes'] and all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == sha for p,sha in hashes.items())
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in raw['begin'][key].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256']
    cases = []
    for name,sha in raw['xmlHashes'].items():
        path = RUN/'xml'/name;assert data.sha(path.read_bytes()) == sha;root = ET.parse(path).getroot()
        assert raw['suites'][root.get('name')] == {k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for case in root.findall('testcase'):assert not list(case);cases.append((case.get('classname'),case.get('name')))
    assert len(cases) == len(set(cases)) == 8 and set(cases) == {(r['classname'],r['name']) for r in raw['cases']}
    agent = '-javaagent:'+str(validation.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites'] == original.COUNTS
    negatives = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('failed',lambda x:x['cases'][0].update(result='NOT_PASS')),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),
        ('scope',lambda x:x['begin'].update(selectedSuites={'UnknownTest':8})),('union',lambda x:x['begin'].update(priorCoverageTransferred=True)),('formal',lambda x:x.update(formalUpdated=True)),('timeout',lambda x:x['stages'][1].update(timedOut=True))]:
        bad = copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:negatives.append(label)
        else:raise AssertionError('invalid original PT qualification accepted')
    failed = data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1'
    previous = data.read_checked(failed/'begin.safe.json','9a8e28060aa30432309eb10b11ebce9dc500800d96c6b6f2d2c8a795d692e17b')
    assert previous['source'] == original.SOURCE and previous['originalManifestSha256'] == RAW and previous['originalExecSha256'] == raw['execSha256']
    receipt_pins = {'compile-audit':'13bd479faebce8caa6653c43e0ebff345672ce8f047c6d4021b06e70000f24ab','session-identity':'2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b'}
    stages = [data.read_checked(failed/(name+'-exit.safe.json'),pin) for name,pin in receipt_pins.items()]
    assert all(r['actualExit'] == 0 and not r['timedOut'] for r in stages)
    for name,row in zip(receipt_pins,stages,strict=True):
        assert data.sha((failed/(name+'.stdout')).read_bytes()) == row['stdoutSha256'] and data.sha((failed/(name+'.stderr')).read_bytes()) == row['stderrSha256']
    assert (failed/'session-identity.stdout').read_text() == 'OWNED_COVERAGE_SESSION_MATCH\t1\n'
    assert not (failed/'coverage-audit-begin.safe.json').exists() and not (data.BASE/'PG13376-db-duration-eight-post-v1').exists()
    physical = previous['physicalClasses'];assert set(physical) == NAMES
    component = failed/'component'
    for name,sha in physical.items():assert data.sha((component/(name+'.class')).read_bytes()) == data.sha((snapshot/'src/schubert-nk-api/target/classes'/(name+'.class')).read_bytes()) == sha
    compiled = {'ComponentCoverageAudit.class':'f1a340d176750cfa6539e4ba3fc348585c9f22f789ff275bb013c0cce65a97f4','CoverageSessionIdentity.class':'952347b8c627e21ab651819e2b7aef728a0a061187f3df38af2dd9408025ab38'}
    audit = failed/'audit';assert {p.name for p in audit.iterdir()} == set(compiled)
    assert all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items())
    tools = previous['toolAndDependencyHashes'];assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items())
    libraries = [p for p in tools if p.endswith('.jar')];assert len(libraries) == 4
    jdk = runner.TC/'jdk-25.0.4/bin';full_cp = receipt_classpath(stages,audit,libraries,jdk)
    cp_negatives = []
    for label,change in [('compile-order',lambda x:x[0]['command'].__setitem__(x[0]['command'].index('-cp')+1,os.pathsep.join(reversed(full_cp.split(os.pathsep)[1:])))),('duplicate',lambda x:x[1]['command'].__setitem__(2,full_cp+os.pathsep+libraries[0])),('missing',lambda x:x[1]['command'].__setitem__(2,os.pathsep.join(full_cp.split(os.pathsep)[:-1]))),('wrong-owned-exec',lambda x:x[1]['command'].__setitem__(4,'other.exec'))]:
        bad = copy.deepcopy(stages);change(bad)
        try:receipt_classpath(bad,audit,libraries,jdk)
        except AssertionError:cp_negatives.append(label)
        else:raise AssertionError('false ordered receipt accepted')
    SLOT.mkdir();runner.SLOT = SLOT
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,originalExecSha256=raw['execSha256'],priorFailedPostBeginSha256='9a8e28060aa30432309eb10b11ebce9dc500800d96c6b6f2d2c8a795d692e17b',reusedMetadataReceipts=receipt_pins,reusedCompiledClasses=compiled,physicalClasses=physical,toolAndDependencyHashes=tools,productTestsReexecuted=0))
    result = runner.step('coverage-audit',[str(jdk/'java'),'-cp',full_cp,'ComponentCoverageAudit',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)],SLOT,timeout=120)
    stages.append(result);data.write(SLOT/'coverage-audit-stage.safe.json',result);assert result['actualExit'] == 0 and not result['timedOut']
    rows = {}
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':rows[fields[1]] = dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    assert set(rows) == NAMES and all(set(r['counters']) == {'LINE','METHOD','CLASS','BRANCH'} and all(v['missed'] == 0 for v in r['counters'].values()) for r in rows.values())
    totals = {kind:dict(missed=sum(r['counters'][kind]['missed'] for r in rows.values()),covered=sum(r['counters'][kind]['covered'] for r in rows.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
    assert all(v['covered'] > 0 and v['missed'] == 0 for v in totals.values())
    path = 'src/schubert-nk-api/src/test/java/'+PREFIX+'DbQueryDurationMetricCollectorTest.java';owner, = [r for r in prior['sourceRows'] if r['path'] == path]
    assert owner['sha256'] == hashes[path] and owner['canonicalOwner'] == owner['canonicalCostOwner'] == 'WBS-P018-09'
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items()) and data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items());verify(invocation);OUT.mkdir()
    for name,sha in raw['xmlHashes'].items():
        with (OUT/name).open('xb') as stream:stream.write((RUN/'xml'/name).read_bytes())
        assert data.sha((OUT/name).read_bytes()) == sha
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,staticPostManifestSha256='f76bc7122d47b49ff7389c1937361e841beb3293e4c7ed20d0203a025b54de0d',
        tests=8,suites=1,failures=0,errors=0,skipped=0,flaky=0,reruns=0,newTestIds=0,xmlHashes=raw['xmlHashes'],cases=raw['cases'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,
        scope='TWO_CURRENT_COLLECTOR_PHYSICAL_CLASSES_NOT_WHOLE_ARTIFACT',generatedRecordContracts=dict(methods=['outcome','elapsedNanoseconds','equals','hashCode','toString'],witnessCasePrefix='dbConn005',officialJacocoFiltersUnmodified=True,addedCounterExclusions=[]),
        independentMetadataNegativeVectors=len(negatives),negativeLabels=negatives,stages=stages,toolAndDependencyHashes=tools,priorRegistryReference=dict(path='PG13368-api-maintenance-literal-v1',sha256='ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186'),sourceOwner=owner['canonicalOwner'],sourceCostOwner=owner['canonicalCostOwner'],registryChanged=False,reusedMetadataReceipts=receipt_pins,reusedCompiledClasses=compiled,orderedClasspathNegativeLabels=cp_negatives,priorRecoveryFailure=dict(session=95441,actualExit=1,entrySha256='354cdda450dc977ca40a94d49d9e740c7e07d106f20e0b8515cb368f98bf0b63',newCommandsExecuted=0),originalFailedPost=dict(session=43143,actualExit=1,entrySha256='50f639a41d91a4e4b02f8ce1221ff361e76d57402f96bdeaf2862a1c6b01cca1',failure='FileExistsError immutable progress write',productTestsReexecuted=0),
        productTestsReexecutedByPost=0,priorCoverageTransferred=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=8,suites=1,totals=totals,crcMismatch=0,singleSession=True)))

if __name__ == '__main__':main()
