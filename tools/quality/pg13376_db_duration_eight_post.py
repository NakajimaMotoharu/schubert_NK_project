"""Independent original8 XML/exec/same-source two-class four counters, no Product Test replay."""
import copy
import json
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validation
import pg13374_db_duration_eight_pt as original
import pg9666_pagination_static as runner

RAW = '4b1ec5302ed94d27ecdcfe20aa48b158a6db645a70165a5db9c58a629b9075fc'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13374-db-duration-eight-pt-v1'
OUT = data.BASE/'PG13376-db-duration-eight-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1'
PREFIX = 'dev/codex/schubert/nk/api/monitoring/'
NAMES = {PREFIX+'DbQueryDurationMetricCollector',PREFIX+'DbQueryDurationMetricCollector$Observation'}

def assess(raw):
    validation.common.SOURCE = original.SOURCE;validation.COUNTS = original.COUNTS;validation.EXPECTED_FIXTURE_HASHES = {}
    validation.assess(raw)

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
    SLOT.mkdir();runner.SLOT = SLOT;component = SLOT/'component';component.mkdir();physical = {}
    for name in sorted(NAMES):
        path = snapshot/'src/schubert-nk-api/target/classes'/(name+'.class');destination = component/(name+'.class');destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination);physical[name] = data.sha(path.read_bytes());assert data.sha(destination.read_bytes()) == physical[name]
    libraries = [runner.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[runner.TC/('m2/repository/org/ow2/asm/'+name+'/9.10.1/'+name+'-9.10.1.jar') for name in ['asm','asm-tree','asm-commons']]]
    helpers = [data.ROOT/'tools/quality/architecture/ComponentCoverageAudit.java',data.ROOT/'tools/quality/architecture/CoverageSessionIdentity.java'];jdk = runner.TC/'jdk-25.0.4/bin';tools = {str(p):data.sha(p.read_bytes()) for p in [*libraries,*helpers,jdk/'java',jdk/'javac']}
    audit = SLOT/'audit';audit.mkdir();cp = os.pathsep.join(map(str,libraries));full_cp = str(audit)+os.pathsep+cp
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,originalExecSha256=raw['execSha256'],normalManifestSha256=original.COMPILE_SHA,physicalClasses=physical,toolAndDependencyHashes=tools,productTestsReexecuted=0))
    stages = []
    for name,command in [('compile-audit',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(audit),*map(str,helpers)]),
        ('session-identity',[str(jdk/'java'),'-cp',full_cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),
        ('coverage-audit',[str(jdk/'java'),'-cp',full_cp,'ComponentCoverageAudit',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])]:
        result = runner.step(name,command,SLOT,timeout=120);stages.append(result)
        data.write(SLOT/'stages.safe.json',stages);assert result['actualExit'] == 0 and not result['timedOut']
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
    for name,sha in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/name,OUT/name);assert data.sha((OUT/name).read_bytes()) == sha
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,staticPostManifestSha256='f76bc7122d47b49ff7389c1937361e841beb3293e4c7ed20d0203a025b54de0d',
        tests=8,suites=1,failures=0,errors=0,skipped=0,flaky=0,reruns=0,newTestIds=0,xmlHashes=raw['xmlHashes'],cases=raw['cases'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,
        scope='TWO_CURRENT_COLLECTOR_PHYSICAL_CLASSES_NOT_WHOLE_ARTIFACT',generatedRecordContracts=dict(methods=['outcome','elapsedNanoseconds','equals','hashCode','toString'],witnessCasePrefix='dbConn005',officialJacocoFiltersUnmodified=True,addedCounterExclusions=[]),
        independentMetadataNegativeVectors=len(negatives),negativeLabels=negatives,stages=stages,toolAndDependencyHashes=tools,priorRegistryReference=dict(path='PG13368-api-maintenance-literal-v1',sha256='ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186'),sourceOwner=owner['canonicalOwner'],sourceCostOwner=owner['canonicalCostOwner'],registryChanged=False,
        productTestsReexecutedByPost=0,priorCoverageTransferred=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=8,suites=1,totals=totals,crcMismatch=0,singleSession=True)))

if __name__ == '__main__':main()
