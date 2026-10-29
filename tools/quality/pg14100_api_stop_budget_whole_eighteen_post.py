"""Independent original whole18 fixed-clock source closure/session/CRC/counters."""
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
import pg14098_api_stop_budget_whole_eighteen_pt as original
import snapshot_program_qualified_v2 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='6e4a7b629ec9236a89c2fcd3379e4deb4eceb2c7c8c31fc7101fb477f7b87626'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14098-api-stop-budget-whole-eighteen-pt-v1'
OUT=data.BASE/'PG14100-api-stop-budget-whole-eighteen-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14100-api-stop-budget-whole-eighteen-post-v1'
NAME='dev/codex/schubert/nk/api/bootstrap/ApiStopBudget'
MAIN='src/schubert-nk-api/src/main/java/'+NAME+'.java'
TOTAL=18

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG14098-api-stop-budget-whole-eighteen-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='7625ceb8d6f774482934ab5133973ef3adfbb1cf9af21483a12339b396f58c51'
    static=data.read_checked(cfg.out(cfg,13838)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0
    assert hashes==raw['begin']['sourceHashes'] and hashes[MAIN]=='6ae561e25cfcdcce0b6b61641b3b2afd7867cf0eaa646059c8b3606dd915e28b'
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
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
        else:raise AssertionError('false current ordinary qualification')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        closure={p[:-6] for p in jar.namelist() if p==NAME+'.class' or p.startswith(NAME+'$') and p.endswith('.class')}
        assert closure=={NAME}
        path=snapshot/'src/schubert-nk-api/target/classes'/(NAME+'.class')
        assert jar.read(NAME+'.class')==path.read_bytes()
    import classfile_code_metadata as code
    decoded=code.decode(path.read_bytes(),NAME+'.class')
    assert {m['name'] for m in decoded['methods'] if m['hasCode']}=={'<init>','begin','remainingNanos','time','<clinit>'}
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in [MAIN,*[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]]}
    assert owners[MAIN]['canonicalOwner']==owners[MAIN]['canonicalCostOwner']=='WBS-P018-05'
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir()
    target=component/(NAME+'.class');target.parent.mkdir(parents=True);shutil.copyfile(path,target)
    physical={NAME:data.sha(path.read_bytes())};assert data.sha(target.read_bytes())==physical[NAME]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java'
    diagnostic_pin='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),NAME])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={}
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    assert set(rows)=={NAME} and set(rows[NAME]['counters'])=={'LINE','METHOD','CLASS','BRANCH'}
    totals=rows[NAME]['counters'];four100=all(v['missed']==0 and v['covered']>0 for v in totals.values())
    applicable=all(v['missed']==0 for v in totals.values())
    natural_branch=totals['BRANCH']==dict(missed=0,covered=0)
    assert four100 and applicable and not natural_branch
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=1,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=1,completeSourceUnitClosure=sorted(closure),sourcePhysicalInventory={NAME:dict(sha256=physical[NAME],methods=decoded['methods'])},completeSourceCoverageMeasured=True,naturalZeroBranch=natural_branch,branchPercent=None if natural_branch else 100*totals['BRANCH']['covered']/(totals['BRANCH']['covered']+totals['BRANCH']['missed']),branchReason='NATURAL_ZERO_NOT_SYNTHETIC_100' if natural_branch else 'ALL_MEASURED_BRANCHES_COVERED',targetUnitFour100=four100,allMeasuredApplicableCountersCovered=applicable,strictFour100GateExit=0 if four100 else 1,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,onlySuppliedClockAndOwnThreads=True,rootMainInvoked=False))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=18,suites=1,totals=totals,crcMismatch=0,singleSession=True,naturalBranchNA=natural_branch)))
if __name__=='__main__':main()
