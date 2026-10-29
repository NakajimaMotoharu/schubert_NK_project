"""Original public config parse result and exact scope; XML counters are not Java coverage."""
import copy
import json
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import scoped_prometheus_post as validator
import pg13862_broker_config_whole_four_pt as original
import pg9666_pagination_static as runner

RAW = '5708f9388ae416c686392115ce962425ea435ee58c5dc0ec1b252ac337c3df22'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13862-broker-config-whole-four-pt-v1'
OUT = data.BASE/'PG13864-broker-config-whole-four-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13864-broker-config-whole-four-post-v1'

def assess(raw):
    validator.common.SOURCE = original.SOURCE
    validator.COUNTS = original.COUNTS
    validator.EXPECTED_FIXTURE_HASHES = {}
    validator.assess(raw)

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    raw = data.read_checked(data.BASE/'PG13862-broker-config-whole-four-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes()) == RAW;assess(raw)
    normal = data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json',original.COMPILE_SHA)
    assert normal['actualExit'] == normal['testsExecuted'] == 0 and normal['source'] == original.SOURCE
    hashes = normal['begin']['inputHashes'];snapshot = original.COMPILE/'snapshot'
    assert hashes == raw['begin']['sourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == sha for p,sha in hashes.items())
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in raw['begin'][key].items())
    assert hashes[original.CONFIG] == data.sha((snapshot/original.CONFIG).read_bytes()) == original.CONFIG_SHA
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256']
    agent = '-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command']
    server, = [p for p in raw['begin']['dependencyHashes'] if p.endswith('/artemis-server/2.56.0/artemis-server-2.56.0.jar')]
    assert raw['begin']['dependencyHashes'][server] == '4bc0bb2d74e340fbb54d84121f2c52708e00bdad0a84751b9bd4f4b21e03c358'
    cases = []
    for name,sha in raw['xmlHashes'].items():
        path = RUN/'xml'/name;assert data.sha(path.read_bytes()) == sha
        root = ET.parse(path).getroot()
        assert raw['suites'][root.get('name')] == {k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for case in root.findall('testcase'):
            assert not list(case);cases.append((case.get('classname'),case.get('name')))
    assert len(cases) == len(set(cases)) == 4 and set(cases) == {(r['classname'],r['name']) for r in raw['cases']}
    prior = data.read_checked(data.BASE/'PG13846-snapshot-program-trace-v1/manifest.json','f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107')
    test_path = str(original.TESTS['ArtemisBrokerConfigurationTest'].relative_to(data.ROOT))
    owner, = [r for r in prior['sourceRows'] if r['path'] == test_path]
    assert owner['sha256'] == hashes[test_path] == '8f3158a7b9ffe84312e4ac902e3d850ae9963b270302818fc737f1e6c1dfe1d9'
    assert owner['canonicalOwner'] == owner['canonicalCostOwner'] == 'WBS-C04'
    labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('failed',lambda x:x['cases'][0].update(result='NOT_PASS')),
        ('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),('scope',lambda x:x['begin'].update(selectedSuites={'UnknownTest':4})),
        ('union',lambda x:x['begin'].update(priorCoverageTransferred=True)),('formal',lambda x:x.update(formalUpdated=True)),
        ('timeout',lambda x:x['stages'][1].update(timedOut=True)),('fixture',lambda x:x['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad = copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('invalid original config qualification accepted')
    runtime = data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot = data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit = tool_slot/'audit'
    tools = runtime['toolAndDependencyHashes'];compiled = runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items())
    assert {p.name for p in audit.iterdir()} == set(compiled) and all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items())
    receipt = data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp = receipt['command'][2];entries = cp.split(os.pathsep)
    assert entries[0] == str(audit) and set(entries[1:]) == {p for p in tools if p.endswith('.jar')} and len(entries) == 5
    SLOT.mkdir();runner.SLOT = SLOT
    stage = runner.step('session-identity',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION],SLOT,timeout=120)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    verify(invocation);OUT.mkdir()
    for name,sha in raw['xmlHashes'].items():
        shutil.copyfile(RUN/'xml'/name,OUT/name);assert data.sha((OUT/name).read_bytes()) == sha
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,
        normalManifestSha256=original.COMPILE_SHA,tests=4,suites=1,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,
        originalXmlHashes=raw['xmlHashes'],cases=raw['cases'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,sessionStage=stage,
        publicConfigurationPath=original.CONFIG,publicConfigurationSha256=original.CONFIG_SHA,configurationOnly=True,productExecutableSourceClasses=0,
        coverage=None,coverageGateExit=None,coverageApplicability='NOT_APPLICABLE_TO_NON_EXECUTABLE_XML_NOT_EXCLUSION_OF_ANY_JAVA',addedCounterExclusions=[],
        canonicalOwner=owner['canonicalOwner'],canonicalCostOwner=owner['canonicalCostOwner'],registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,
        thirdPartyParserJarSha256=raw['begin']['dependencyHashes'][server],productTestsReexecutedByPost=0,priorProductResultsReused=False,oldCoverageTransferred=False,
        actualBrokerStarted=False,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,nativeQualification=False,
        whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
