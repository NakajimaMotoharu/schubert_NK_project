"""Actual whole-Life outer/anonymous counters including misses, not a coverage acceptance."""
import datetime as dt
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import pg9284_api_pure_readiness_host as selected
import scoped_prometheus_post as steps
from host_tool_invocation import capture, verify

host=selected.run.host
SOURCE=selected.SOURCE
NORMAL=selected.COMPILE/'manifest.safe.json'
NORMAL_SHA=selected.COMPILE_SHA
RUN=host.W/'pg9284-api-pure-readiness-host-v1'
HOST_SHA='08188fea15ae032bf77ec0e34e571b6a63eb273e4222ad9f5b8eb4f722d8f95f'
SLOT=host.W/'pg9286-api-pure-readiness-measure-v1'
OUT=host.BASE/'PG9286-api-pure-readiness-measure-v1'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessMain'
NAMES={PREFIX,PREFIX+'$Startup',PREFIX+'$ConfigurationLoad'}
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiReadinessPredicateTest.java'

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    assert host.sha(NORMAL)==NORMAL_SHA and host.sha(RUN/'manifest.safe.json')==HOST_SHA
    normal=json.loads(NORMAL.read_bytes()); run=json.loads((RUN/'manifest.safe.json').read_bytes())
    assert normal['source']==run['source']==SOURCE and normal['actualExit']==run['actualExit']==0
    assert run['begin']['compileManifestSha256']==NORMAL_SHA
    assert run['begin']['selectedSuites']=={'ApiReadinessPredicateTest':3}
    assert len(run['cases'])==3 and all(row['result']=='PASS' and not row['nonPass'] for row in run['cases'])
    assert {row['name'] for row in run['cases']}==selected.METHODS
    assert all(row['actualExit']==0 and row['timedOut'] is False for row in run['stages'])
    assert all(host.sha(Path(path))==digest for path,digest in run['begin']['dependencyHashes'].items())
    assert all(host.sha(host.ROOT/path)==digest for path,digest in run['begin']['sourceHashes'].items())
    assert host.sha(host.ROOT/MAIN)==normal['begin']['inputHashes'][MAIN]
    assert host.sha(host.ROOT/UNIT)==normal['begin']['inputHashes'][UNIT]
    xml=RUN/'xml/TEST-dev.codex.schubert.nk.api.bootstrap.ApiReadinessPredicateTest.xml'
    tree=ET.parse(xml).getroot()
    assert {key:int(tree.get(key)) for key in ('tests','failures','errors','skipped')}==dict(tests=3,failures=0,errors=0,skipped=0)
    assert host.sha(xml)==run['xmlHashes'][xml.name] and host.sha(RUN/'jacoco.exec')==run['execSha256']
    session='PG9284-API-PURE-READINESS'
    expected='-javaagent:'+str(selected.run.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+session
    assert expected in run['stages'][-1]['command']
    api=normal['jars']['api']; assert host.sha(Path(api['path']))==api['sha256']
    SLOT.mkdir(mode=0o700); steps.SLOT=SLOT; physical={}; paths=[]
    with zipfile.ZipFile(api['path']) as archive:
        actual={name for name in archive.namelist() if name.startswith(PREFIX) and name.endswith('.class')}
        assert actual=={name+'.class' for name in NAMES}
        for name in sorted(actual):
            target=SLOT/Path(name).name
            with target.open('xb') as stream: stream.write(archive.read(name))
            physical[name]=host.sha(target); paths.append(target)
    libraries=[host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
      *[host.TC/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ('asm','asm-tree','asm-commons')]]
    cp=os.pathsep.join(str(path) for path in libraries)
    helper=host.ROOT/'tools/quality/architecture/ApiPureReadinessCoverageMeasure.java'
    assert '"'+session+'"' in helper.read_text() and 'PG9198-' not in helper.read_text()
    classes=SLOT/'reader'; classes.mkdir(); jdk=host.TC/'jdk-25.0.4/bin'
    compiled,_=steps.step('compile-report',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(helper)])
    assert compiled['actualExit']==0 and compiled['timedOut'] is False
    measured,output=steps.step('measure-report',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,
      'ApiPureReadinessCoverageMeasure',str(RUN/'jacoco.exec'),*[str(path) for path in paths]])
    assert measured['actualExit']==0 and measured['timedOut'] is False
    counters={}; records={}
    for line in output.splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':
            assert len(fields)==4 and fields[1] in NAMES and fields[1] not in records
            records[fields[1]]=dict(crc64=fields[2],recordStatus=fields[3])
        elif fields[0]=='COUNTER':
            assert len(fields)==5 and fields[1] in NAMES
            counters.setdefault(fields[1],{})[fields[2]]=dict(missed=int(fields[3]),covered=int(fields[4]))
    assert set(counters)==set(records)==NAMES
    kinds={'LINE','METHOD','CLASS','BRANCH'}
    assert all(set(row)==kinds for row in counters.values())
    assert all(value>=0 for row in counters.values() for count in row.values() for value in count.values())
    assert records[PREFIX]['recordStatus']=='CURRENT_RECORD'
    assert all(records[name]['recordStatus']=='DECLARED_INTERFACE_NO_EXECUTABLE_CODE' and all(value==0 for row in counters[name].values() for value in row.values()) for name in NAMES-{PREFIX})
    assert all(row['recordStatus'] in ('CURRENT_RECORD','DECLARED_INTERFACE_NO_EXECUTABLE_CODE') for row in records.values())
    totals={kind:dict(missed=sum(row[kind]['missed'] for row in counters.values()),covered=sum(row[kind]['covered'] for row in counters.values())) for kind in kinds}
    all100=all(row['missed']==0 and row['covered']>0 for row in totals.values())
    assert not all100
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),source=SOURCE,invocation=invocation,
      normalManifestSha256=NORMAL_SHA,hostManifestSha256=HOST_SHA,actualTests=3,suites=1,newTestIds=0,necessaryRegression=3,failures=0,errors=0,skipped=0,
      exactSelectedCaseIds=[row['name'] for row in run['cases']],historicalHookOrTermCasesSelected=False,allDeclaredCasesRun=True,
      physicalClasses=physical,executableClasses={name:dict(**records[name],counters=counters[name]) for name in sorted(NAMES)},
      wholeSourceUnitCounters=totals,requiredWholeClassFour100=all100,coverageUnion=False,exclusionsAdded=False,coverageRequirementRelaxed=False,
      heldScope='ACTUAL_MAIN_STARTUP_ADMISSION_AND_NATIVE_UNRUN_HOLD_NOT_A_PT_EXEMPTION',programPtComplete=False,
      execSha256=run['execSha256'],xmlSha256=host.sha(xml),sessionId=session,reportHelperSha256=host.sha(helper),
      reportLibraryHashes={str(path):host.sha(path) for path in libraries},reportStages=[compiled,measured],
      productTestsExecutedByMeasurement=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=3,counters=totals,requiredWholeClassFour100=all100,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
