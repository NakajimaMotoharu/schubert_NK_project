"""Original HTTP metric28 and complete three Source/nine physical from exact Web module Jar; no Product rerun."""
from contextlib import ExitStack
import copy
import json
import os
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validator
import pg14450_http_metric_whole_twenty_eight_pt as original
import typed_marker_guard_qualified_v1 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='bb9dffe858c471cb258a75278b7119b3e47f0b5f5f5507f0b845a8b70b992beb'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14450-http-metric-whole-twenty-eight-pt-v1'
OUT=data.BASE/'PG14452-http-metric-whole-twenty-eight-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14452-http-metric-whole-twenty-eight-post-v1'
SOURCE_PATHS={'dev/codex/schubert/nk/web/monitoring/HttpMetricContract': 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricContract.java', 'dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder': 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder.java', 'dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry': 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry.java'}
MODULES={'dev/codex/schubert/nk/web/monitoring/HttpMetricContract': 'web', 'dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder': 'web', 'dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry': 'web'}
SOURCES={'dev/codex/schubert/nk/web/monitoring/HttpMetricContract': '019f126d38fdfbfd60baf8f38c254201db2427e7a0c2087e052712812a889c03', 'dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder': '9ca3687779ab82d12966d3300d35d7acd8320e6020ad2d8acd0e829b55990483', 'dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry': '29df7d74914a7a854c8d9ea345056ede3ca4d60cc0100f7c51b23efb2851a5a5'}
CLOSURES={n:set(v) for n,v in {'dev/codex/schubert/nk/web/monitoring/HttpMetricContract': ['dev/codex/schubert/nk/web/monitoring/HttpMetricContract', 'dev/codex/schubert/nk/web/monitoring/HttpMetricContract$Method', 'dev/codex/schubert/nk/web/monitoring/HttpMetricContract$Route', 'dev/codex/schubert/nk/web/monitoring/HttpMetricContract$Status', 'dev/codex/schubert/nk/web/monitoring/HttpMetricContract$Labels', 'dev/codex/schubert/nk/web/monitoring/HttpMetricContract$Metric'], 'dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder': ['dev/codex/schubert/nk/web/monitoring/HttpMetricRecorder'], 'dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry': ['dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry', 'dev/codex/schubert/nk/web/monitoring/OverflowSafeHttpMeterRegistry$OverflowSafeTimer']}.items()}
CLASS_MODULES={c:MODULES[n] for n,closure in CLOSURES.items() for c in closure}
NAMES=set().union(*CLOSURES.values())
METADATA=set()
EXECUTABLE=NAMES-METADATA
TOTAL=28

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/p):h for p,h in original.FIXTURES.items()};validator.EXPECTED_FIXTURE_HASHES.update({str(RUN/'fresh-test-classes'/p.split('/src/test/resources/',1)[1]):h for p,h in original.FIXTURES.items()});validator.assess(raw)

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG14450-http-metric-whole-twenty-eight-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    prefix=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            if any(line.startswith(k+'=') for k in ('runtime.version','os.name','os.arch','os.version')):
                prefix.append(line.strip().split('=',1))
    assert len(prefix)==4 and len(dict(prefix))==4 and dict(prefix)==raw['stages'][1]['reportedEnvironment']
    assert raw['stages'][1]['environmentBasis']=='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e'
    static=data.read_checked(cfg.out(cfg,14224)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0 and hashes==raw['begin']['sourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    for name,h in SOURCES.items():assert hashes[SOURCE_PATHS[name]]==h
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        assert all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][key].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256']
    actual=[]
    for filename,h in raw['xmlHashes'].items():
        path=RUN/'xml'/filename;assert data.sha(path.read_bytes())==h;root=ET.parse(path).getroot()
        assert raw['suites'][root.get('name')]=={k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for case in root.findall('testcase'):
            assert not list(case);actual.append((case.get('classname'),case.get('name')))
    assert len(actual)==len(set(actual))==TOTAL and set(actual)=={(r['classname'],r['name']) for r in raw['cases']}
    agent='-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites']==original.COUNTS
    labels=[]
    for label,change in [('source',lambda v:v.update(source='0'*40)),('failed',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('scope',lambda v:v['begin'].update(selectedSuites={'UnknownTest':TOTAL})),('union',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('fixture',lambda v:v['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false original32 qualification')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5
    inventory={};closures={}
    with ExitStack() as stack:
        jars={m:stack.enter_context(zipfile.ZipFile(normal['jars'][m]['path'])) for m in set(MODULES.values())}
        for name in SOURCES:
            jar=jars[MODULES[name]]
            closure={p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}
            assert closure==CLOSURES[name];closures[name]=sorted(closure)
        assert set().union(*[set(v) for v in closures.values()])==NAMES
        for name in sorted(NAMES):
            jar=jars[CLASS_MODULES[name]]
            path=snapshot/('src/schubert-nk-'+CLASS_MODULES[name]+'/target/classes')/(name+'.class')
            assert jar.read(name+'.class')==path.read_bytes()
            parsed=code.decode(path.read_bytes(),name+'.class')
            assert any(m['hasCode'] for m in parsed['methods'])
            if name in METADATA:raise ValueError('unexpected zero-counter metadata in four complete original source closures')
            inventory[name]=dict(sha256=data.sha(path.read_bytes()),flags=parsed['flags'],sourceFile=parsed['sourceFile'],methods=parsed['methods'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=list(SOURCE_PATHS.values())+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    expected_owners={name:'WBS-P018-09' for name in SOURCES}
    for name,expected_owner in expected_owners.items():
        path=SOURCE_PATHS[name]
        assert owners[path]['canonicalOwner']==owners[path]['canonicalCostOwner']==expected_owner
    assert all(owners[str(p.relative_to(data.ROOT))]['canonicalOwner']==owners[str(p.relative_to(data.ROOT))]['canonicalCostOwner']=='WBS-P018-09' and owners[str(p.relative_to(data.ROOT))]['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for p in original.TESTS.values())
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir();physical={}
    for name in sorted(NAMES):
        path=snapshot/('src/schubert-nk-'+CLASS_MODULES[name]+'/target/classes')/(name+'.class');target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        physical[name]=data.sha(path.read_bytes());assert data.sha(target.read_bytes())==physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java';diagnostic_pin='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),*sorted(EXECUTABLE),*['--metadata='+n for n in sorted(METADATA)]])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={};missed_lines=[];metadata=[]
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
        if fields[0]=='MISSED_LINE':missed_lines.append(fields[1:])
        if fields[0]=='METADATA':metadata.append(fields[1])
    assert set(rows)==EXECUTABLE and set(metadata)==METADATA and len(metadata)==0 and all(set(r['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for r in rows.values())
    kinds=['LINE','METHOD','CLASS','BRANCH']
    def totals(names):return {k:dict(missed=sum(rows[n]['counters'][k]['missed'] for n in names if n in rows),covered=sum(rows[n]['counters'][k]['covered'] for n in names if n in rows)) for k in kinds}
    units={}
    for name,closure in closures.items():
        counters=totals(closure)
        units[name]=dict(physical=closure,totals=counters,four100=all(v['missed']==0 and v['covered']>0 for v in counters.values()),metadataOnly=set(closure)<=METADATA,branchNaturallyZero=counters['BRANCH']==dict(missed=0,covered=0) and not set(closure)<=METADATA,threeCounter100=all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']))
    overall=totals(NAMES);four100=all(v['four100'] for v in units.values())
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=3,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=3,completeSourceUnitClosure=closures,sourcePhysicalInventory=inventory,completeSourceCoverageMeasured=True,fullSourceUnits=units,targetUnitFour100=four100,strictFour100GateExit=0 if four100 else 1,missedLines=missed_lines,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=overall,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,onlySuppliedObservationsAndOwnThreads=True,rootMainInvoked=False,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,metadataClasses=sorted(METADATA),metadataKind='NONE',naturalZeroBranchSourceUnits=[n for n,v in units.items() if v['branchNaturallyZero']],metadataSourceUnits=[n for n,v in units.items() if v['metadataOnly']],reportedEnvironment=raw['stages'][1]['reportedEnvironment'],branch='dev-foundation'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=TOTAL,suites=3,sourcePrograms=len(SOURCES),executablePhysical=len(EXECUTABLE),metadataPhysical=len(METADATA),totals=overall,perSourceFour100={n:v['four100'] for n,v in units.items()},crcMismatch=0,singleSession=True)))
if __name__=='__main__':main()
