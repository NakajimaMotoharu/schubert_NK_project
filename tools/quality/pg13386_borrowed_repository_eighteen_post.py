"""Independent two whole Test XML/exec/three Main physical counters; reused tools, never old results."""
import copy
import json
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validator
import pg13384_borrowed_repository_eighteen_pt as original
import pg9666_pagination_static as runner

RAW = 'b4b321b37f81358d9acbdcd66466db6e5b1f7aa121a5482f6854de0e9434e764'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13384-borrowed-repository-eighteen-pt-v1'
OUT = data.BASE/'PG13386-borrowed-repository-eighteen-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13386-borrowed-repository-eighteen-post-v1'
PREFIX = 'dev/codex/schubert/nk/api/monitoring/'
NAMES = {PREFIX+'persistence/AsyncJobCountRepository',PREFIX+'persistence/OutboxObservationRepository',PREFIX+'persistence/OutboxObservationRepository$Snapshot'}
TOTAL = sum(original.COUNTS.values())

def assess(raw):
    validator.common.SOURCE = original.SOURCE;validator.COUNTS = original.COUNTS;validator.EXPECTED_FIXTURE_HASHES = {};validator.assess(raw)

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw = data.read_checked(data.BASE/'PG13384-borrowed-repository-eighteen-pt-v1/manifest.json',RAW);assert data.sha((RUN/'manifest.safe.json').read_bytes()) == RAW;assess(raw)
    normal = data.read_checked(data.BASE/'PG13362-api-maintenance-literal-v1/manifest.json',original.COMPILE_SHA)
    static = data.read_checked(data.BASE/'PG13367-api-maintenance-literal-v1/manifest.json','f76bc7122d47b49ff7389c1937361e841beb3293e4c7ed20d0203a025b54de0d')
    prior = data.read_checked(data.BASE/'PG13368-api-maintenance-literal-v1/manifest.json','ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186')
    assert raw['source'] == normal['source'] == static['source'] == prior['source'] == original.SOURCE
    assert normal['actualExit'] == static['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];snapshot = original.COMPILE/'snapshot';assert hashes == raw['begin']['sourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == sha for p,sha in hashes.items())
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in raw['begin'][key].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256']
    actual_cases = []
    for filename,sha in raw['xmlHashes'].items():
        path = RUN/'xml'/filename;assert data.sha(path.read_bytes()) == sha;root = ET.parse(path).getroot()
        assert raw['suites'][root.get('name')] == {k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for case in root.findall('testcase'):assert not list(case);actual_cases.append((case.get('classname'),case.get('name')))
    assert len(actual_cases) == len(set(actual_cases)) == TOTAL and set(actual_cases) == {(r['classname'],r['name']) for r in raw['cases']}
    agent = '-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites'] == original.COUNTS
    negative_labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('failed',lambda x:x['cases'][0].update(result='NOT_PASS')),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),('scope',lambda x:x['begin'].update(selectedSuites={'UnknownTest':TOTAL})),
        ('union',lambda x:x['begin'].update(priorCoverageTransferred=True)),('formal',lambda x:x.update(formalUpdated=True)),('timeout',lambda x:x['stages'][1].update(timedOut=True))]:
        bad = copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:negative_labels.append(label)
        else:raise AssertionError('false current ordinary PT qualification accepted')
    runtime = data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot = data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit = tool_slot/'audit'
    tools = runtime['toolAndDependencyHashes'];compiled = runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items()) and {p.name for p in audit.iterdir()} == set(compiled)
    assert all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items())
    receipt = data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    full_cp = receipt['command'][2];entries = full_cp.split(os.pathsep);libraries = {p for p in tools if p.endswith('.jar')}
    assert entries[0] == str(audit) and set(entries[1:]) == libraries and len(entries) == len(libraries)+1 == 5
    owners = {}
    for name in original.COUNTS:
        path = 'src/schubert-nk-api/src/test/java/'+PREFIX+name+'.java';row, = [r for r in prior['sourceRows'] if r['path'] == path]
        assert row['sha256'] == hashes[path] and row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P018-09';owners[path] = dict(sha256=row['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'])
    SLOT.mkdir();runner.SLOT = SLOT;component = SLOT/'component';component.mkdir();physical = {}
    for name in sorted(NAMES):
        path = snapshot/'src/schubert-nk-api/target/classes'/(name+'.class');target = component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);physical[name] = data.sha(path.read_bytes());assert data.sha(target.read_bytes()) == physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=original.COMPILE_SHA,physicalClasses=physical,reusedToolRuntimeOnly=dict(manifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',compiled=compiled,dependencies=tools,orderedClasspath=full_cp,priorProductResultsReused=False),productTestsReexecuted=0))
    jdk = runner.TC/'jdk-25.0.4/bin';stages = []
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',full_cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',full_cp,'ComponentCoverageAudit',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])]:
        stage = runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit'] == 0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows = {}
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':rows[fields[1]] = dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    assert set(rows) == NAMES and all(set(r['counters']) == {'LINE','METHOD','CLASS','BRANCH'} and all(v['missed'] == 0 for v in r['counters'].values()) for r in rows.values())
    totals = {kind:dict(missed=sum(r['counters'][kind]['missed'] for r in rows.values()),covered=sum(r['counters'][kind]['covered'] for r in rows.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
    assert all(v['missed'] == 0 and v['covered'] > 0 for v in totals.values())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items()) and all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items());verify(invocation);OUT.mkdir()
    for filename,sha in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes()) == sha
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,staticPostManifestSha256='f76bc7122d47b49ff7389c1937361e841beb3293e4c7ed20d0203a025b54de0d',tests=TOTAL,suites=len(original.COUNTS),failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,
        cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,stages=stages,owners=owners,registryChanged=False,
        scope='TWO_REPOSITORY_JAVA_SOURCES_THREE_PHYSICAL_MAIN_CLASSES_NOT_WHOLE_ARTIFACT',generatedRecordContracts=dict(physicalClass=PREFIX+'persistence/OutboxObservationRepository$Snapshot',methods=['counts','ages','equals','hashCode','toString'],witnessCasePrefix='outboxDb010',officialFiltersUnchanged=True,addedCounterExclusions=[]),
        metadataNegativeVectors=len(negative_labels),negativeLabels=negative_labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=TOTAL,suites=len(original.COUNTS),totals=totals,crcMismatch=0,singleSession=True)))

if __name__ == '__main__':main()
