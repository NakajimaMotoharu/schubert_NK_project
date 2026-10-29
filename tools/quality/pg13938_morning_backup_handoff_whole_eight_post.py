"""Independent original whole8 literal backup handoff/completion; no actual backup or DB."""
import copy
import json
import os
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validator
import pg13936_morning_backup_handoff_whole_eight_pt as original
import snapshot_program_qualified_v2 as cfg
import pg9666_pagination_static as runner

RAW = 'f954b3d94e705c742822ed8bb83c685f5599386b0bafba3f527654b54ca1cd14'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13936-morning-backup-handoff-whole-eight-pt-v1'
OUT = data.BASE/'PG13938-morning-backup-handoff-whole-eight-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13938-morning-backup-handoff-whole-eight-post-v1'
PREFIX = 'dev/codex/schubert/nk/batch/file/'
NAMES = {PREFIX+name for name in ['MorningBackupPreparation','MorningBackupCompletion']}
METADATA = {PREFIX+'MorningBackupPreparation$'+name for name in ['Publisher','Continuation']}
CLASS_MODULES = {name:'batch' for name in NAMES|METADATA}
TOTAL = sum(original.COUNTS.values())

def assess(raw):
    validator.common.SOURCE = original.SOURCE;validator.COUNTS = original.COUNTS;validator.EXPECTED_FIXTURE_HASHES = {};validator.assess(raw)

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw = data.read_checked(data.BASE/'PG13936-morning-backup-handoff-whole-eight-pt-v1/manifest.json',RAW);assert data.sha((RUN/'manifest.safe.json').read_bytes()) == RAW;assess(raw)
    normal,normal_pin = cfg.normal()
    static_pin = '7625ceb8d6f774482934ab5133973ef3adfbb1cf9af21483a12339b396f58c51'
    static = data.read_checked(cfg.out(cfg,13838)/'manifest.json',static_pin)
    prior = data.read_checked(data.BASE/'PG13846-snapshot-program-trace-v1/manifest.json','f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107')
    assert raw['source'] == normal['source'] == static['source'] == original.SOURCE
    assert prior['source'] == original.SOURCE
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
        ('union',lambda x:x['begin'].update(priorCoverageTransferred=True)),('formal',lambda x:x.update(formalUpdated=True)),('timeout',lambda x:x['stages'][1].update(timedOut=True)),('fixture',lambda x:x['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
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
        path = str(original.TESTS[name].relative_to(data.ROOT));row, = [r for r in prior['sourceRows'] if r['path'] == path]
        expected_owner = 'WBS-P017-06'
        assert row['sha256'] == original.PINS[name] and row['canonicalOwner'] == row['canonicalCostOwner'] == expected_owner;owners[path] = dict(sha256=hashes[path],priorRegistrySha256=row['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'])
    closure = set()
    for name in NAMES:
        with zipfile.ZipFile(normal['jars'][CLASS_MODULES[name]]['path']) as jar:
            closure.update(entry[:-6] for entry in jar.namelist() if entry.endswith('.class') and (entry == name+'.class' or entry.startswith(name+'$')))
    assert closure == NAMES|METADATA and len(NAMES) == 2 and len(closure) == 4
    SLOT.mkdir();runner.SLOT = SLOT;component = SLOT/'component';component.mkdir();physical = {}
    for name in sorted(NAMES|METADATA):
        path = snapshot/('src/schubert-nk-'+CLASS_MODULES[name]+'/target/classes')/(name+'.class');target = component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);physical[name] = data.sha(path.read_bytes());assert data.sha(target.read_bytes()) == physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,reusedToolRuntimeOnly=dict(manifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',compiled=compiled,dependencies=tools,orderedClasspath=full_cp,priorProductResultsReused=False),productTestsReexecuted=0))
    jdk = runner.TC/'jdk-25.0.4/bin';stages = []
    diagnostic = data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java'
    diagnostic_pin = 'fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    diagnostic_classes = data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    diagnostic_class_pin = '3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    assert data.sha(diagnostic.read_bytes()) == diagnostic_pin and data.sha((diagnostic_classes/'ComponentCoverageDiagnostic.class').read_bytes()) == diagnostic_class_pin
    diagnostic_cp = str(diagnostic_classes)+os.pathsep+full_cp
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',full_cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',diagnostic_cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES),*['--metadata='+name for name in sorted(METADATA)]])]:
        stage = runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit'] == 0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows = {}
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':rows[fields[1]] = dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    natural_metadata = [line.split('\t')[1] for line in (SLOT/'coverage-audit.stdout').read_text().splitlines() if line.startswith('METADATA\t')]
    assert len(natural_metadata) == 2 and set(natural_metadata) == METADATA
    assert set(rows) == NAMES and all(set(r['counters']) == {'LINE','METHOD','CLASS','BRANCH'} for r in rows.values())
    totals = {kind:dict(missed=sum(r['counters'][kind]['missed'] for r in rows.values()),covered=sum(r['counters'][kind]['covered'] for r in rows.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
    four100 = all(v['missed'] == 0 and v['covered'] > 0 for v in totals.values())
    assert data.sha(diagnostic.read_bytes()) == diagnostic_pin
    missed_lines = [line.split('\t')[1:] for line in (SLOT/'coverage-audit.stdout').read_text().splitlines() if line.startswith('MISSED_LINE\t')]
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items()) and all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items());verify(invocation);OUT.mkdir()
    for filename,sha in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes()) == sha
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=len(original.COUNTS),failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,
        naturalZeroInterfaceMetadata=sorted(METADATA),executablePhysical=2,targetSourceUnits=2,targetUnitFour100=four100,coverageGateExit=0 if four100 else 1,missedLines=missed_lines,diagnosticToolSha256=diagnostic_pin,diagnosticClassSha256=data.sha((diagnostic_classes/'ComponentCoverageDiagnostic.class').read_bytes()),cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,stages=stages,owners=owners,registryChanged=False,
        scope='COMPLETE_TWO_SOURCE_UNITS_MEMORY_BACKUP_HANDOFF_COMPLETION_NOT_ACTUAL_DATABASE_OR_BACKUP',officialGeneratedFiltersUnchanged=True,addedCounterExclusions=[],completeSourceUnitClosure=sorted(closure),realBackupDatabaseAndNativeNotQualified=True,ffmFactorySymbolBindingExpected=False,nativeAccessFlagsAdded=False,nativeQualification=False,
        metadataNegativeVectors=len(negative_labels),negativeLabels=negative_labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=TOTAL,suites=len(original.COUNTS),totals=totals,crcMismatch=0,singleSession=True)))

if __name__ == '__main__':main()
