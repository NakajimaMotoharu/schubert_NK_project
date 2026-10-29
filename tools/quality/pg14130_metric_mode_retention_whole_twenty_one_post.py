"""Independent original whole21 metric/mode Source and exact approved TSV binding."""
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
import pg14128_metric_mode_retention_whole_twenty_one_pt as original
import snapshot_program_qualified_v2 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='3dca4c5e3301c7828a9adc7c72573284515d6f7eacd8742184b78ae64094398e'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14128-metric-mode-retention-whole-twenty-one-pt-v1'
OUT=data.BASE/'PG14130-metric-mode-retention-whole-twenty-one-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14130-metric-mode-retention-whole-twenty-one-post-v1'
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
SOURCES={PREFIX+n:h for n,h in [('MetricContract','056bb329bb251189434c73b8914141be9974b50686f7df227b8ef935e4bc93f8'),('MonitoringModePolicy','9eb653ff3b80236306ed03e7621b3d6dc6d4d86764760ba625aa7f203118da73')]}
CLOSURES={PREFIX+'MetricContract':{PREFIX+'MetricContract'+suffix for suffix in ['','$Kind']},PREFIX+'MonitoringModePolicy':{PREFIX+'MonitoringModePolicy'+suffix for suffix in ['','$DetailService','$RetentionConfiguration']}}
NAMES=set().union(*CLOSURES.values())
TOTAL=21

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/original.FIXTURE):original.FIXTURE_SHA,str(RUN/'fresh-test-classes/monitoring/metric-catalog.tsv'):original.FIXTURE_SHA};validator.assess(raw)

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG14128-metric-mode-retention-whole-twenty-one-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='7625ceb8d6f774482934ab5133973ef3adfbb1cf9af21483a12339b396f58c51'
    static=data.read_checked(cfg.out(cfg,13838)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0 and hashes==raw['begin']['sourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    for name,h in SOURCES.items():assert hashes['src/schubert-nk-batch/src/main/java/'+name+'.java']==h
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
        else:raise AssertionError('false original21 qualification')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5
    inventory={};closures={}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for name in SOURCES:
            closure={p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}
            assert closure==CLOSURES[name];closures[name]=sorted(closure)
        assert set().union(*[set(v) for v in closures.values()])==NAMES
        for name in sorted(NAMES):
            path=snapshot/'src/schubert-nk-batch/target/classes'/(name+'.class')
            assert jar.read(name+'.class')==path.read_bytes()
            parsed=code.decode(path.read_bytes(),name+'.class')
            assert any(m['hasCode'] for m in parsed['methods'])
            inventory[name]=dict(sha256=data.sha(path.read_bytes()),methods=parsed['methods'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-batch/src/main/java/'+name+'.java' for name in SOURCES]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    assert all(v['canonicalOwner']==v['canonicalCostOwner']=='WBS-P018-09' and v['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for v in owners.values())
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir();physical={}
    for name in sorted(NAMES):
        path=snapshot/'src/schubert-nk-batch/target/classes'/(name+'.class');target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        physical[name]=data.sha(path.read_bytes());assert data.sha(target.read_bytes())==physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java';diagnostic_pin='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={};missed_lines=[]
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
        if fields[0]=='MISSED_LINE':missed_lines.append(fields[1:])
    assert set(rows)==NAMES and all(set(r['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for r in rows.values())
    kinds=['LINE','METHOD','CLASS','BRANCH']
    def totals(names):return {k:dict(missed=sum(rows[n]['counters'][k]['missed'] for n in names),covered=sum(rows[n]['counters'][k]['covered'] for n in names)) for k in kinds}
    units={}
    for name,closure in closures.items():
        counters=totals(closure)
        units[name]=dict(physical=closure,totals=counters,four100=all(v['missed']==0 and v['covered']>0 for v in counters.values()))
    overall=totals(NAMES);four100=all(v['four100'] for v in units.values())
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=3,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=2,completeSourceUnitClosure=closures,sourcePhysicalInventory=inventory,completeSourceCoverageMeasured=True,fullSourceUnits=units,targetUnitFour100=four100,strictFour100GateExit=0 if four100 else 1,missedLines=missed_lines,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=overall,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,onlyConfigurationValuesAndOwnThreads=True,rootMainInvoked=False,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=21,suites=3,sourcePrograms=2,executablePhysical=5,totals=overall,perSourceFour100={n:v['four100'] for n,v in units.items()},crcMismatch=0,singleSession=True)))
if __name__=='__main__':main()
