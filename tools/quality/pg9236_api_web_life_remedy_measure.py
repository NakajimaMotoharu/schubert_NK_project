"""All two-lifetime source-unit counters from this actual14 only; never a coverage acceptance."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import pg9234_api_web_life_remedy_host as selected
import scoped_prometheus_post as steps
from host_tool_invocation import capture, verify

host=selected.run.host
SOURCE=selected.SOURCE
RUN=host.W/'pg9234-api-web-life-remedy-host-v1'
HOST_SHA='43eecddc6ec582273c2bd34ee9e8ae4f385a6290319b29ea31ad822dfad0f217'
SLOT=host.W/'pg9236-api-web-life-remedy-measure-v1'
OUT=host.BASE/'PG9236-api-web-life-remedy-measure-v1'
API='dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime'
WEB='dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime'
NAMES={API,API+'$1',WEB}

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    normal_path=selected.COMPILE/'manifest.safe.json'
    assert host.sha(normal_path)==selected.COMPILE_SHA and host.sha(RUN/'manifest.safe.json')==HOST_SHA
    normal=json.loads(normal_path.read_bytes()); run=json.loads((RUN/'manifest.safe.json').read_bytes())
    assert normal['source']==run['source']==SOURCE and normal['actualExit']==run['actualExit']==0
    assert run['begin']['selectedSuites']==selected.COUNTS and run['begin']['compileManifestSha256']==selected.COMPILE_SHA
    expected={'lifeBudget'+str(i).zfill(3) for i in range(1,11)}|{'apiObsBoot009','wlClose001','wlClose002','wlClose003'}
    assert len(run['cases'])==14 and {row['name'] for row in run['cases']}==expected
    assert all(row['result']=='PASS' and not row['nonPass'] for row in run['cases'])
    assert all(row['actualExit']==0 and row['timedOut'] is False for row in run['stages'])
    assert all(host.sha(Path(path))==digest for path,digest in run['begin']['dependencyHashes'].items())
    assert all(host.sha(Path(path))==digest for path,digest in run['begin']['testSourceHashes'].items())
    assert all(host.sha(host.ROOT/path)==digest for path,digest in run['begin']['sourceHashes'].items())
    for file in (RUN/'xml').glob('TEST-*.xml'):
        root=ET.parse(file).getroot()
        assert {key:int(root.get(key)) for key in ('tests','failures','errors','skipped')}==dict(
          tests=selected.COUNTS[root.get('name').rpartition('.')[2]],failures=0,errors=0,skipped=0)
        assert host.sha(file)==run['xmlHashes'][file.name]
    assert len(run['xmlHashes'])==3 and host.sha(RUN/'jacoco.exec')==run['execSha256']
    session='PG9234-API-WEB-LIFE-REMEDY'
    assert '-javaagent:'+str(selected.run.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+session in run['stages'][-1]['command']
    helper=host.ROOT/'tools/quality/architecture/ApiWebLifetimeCoverageMeasure.java'
    assert re.findall(r'getId\(\)\.equals\("([^"]+)"\)',helper.read_text())==[session]
    SLOT.mkdir(); steps.SLOT=SLOT; physical={}; paths=[]
    for role,prefix in (('api',API),('web',WEB)):
        jar=normal['jars'][role]; assert host.sha(Path(jar['path']))==jar['sha256']
        with zipfile.ZipFile(jar['path']) as archive:
            members={name for name in archive.namelist() if name.startswith(prefix) and name.endswith('.class')}
            assert members=={name+'.class' for name in NAMES if name.startswith(prefix)}
            for member in sorted(members):
                target=SLOT/Path(member).name
                with target.open('xb') as stream: stream.write(archive.read(member))
                physical[member]=host.sha(target); paths.append(target)
    libraries=[host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
      *[host.TC/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ('asm','asm-tree','asm-commons')]]
    cp=os.pathsep.join(str(path) for path in libraries); classes=SLOT/'reader'; classes.mkdir()
    jdk=host.TC/'jdk-25.0.4/bin'
    compiled,_=steps.step('compile-report',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(helper)])
    assert compiled['actualExit']==0 and compiled['timedOut'] is False
    measured,output=steps.step('measure-report',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),*[str(path) for path in paths]])
    assert measured['actualExit']==0 and measured['timedOut'] is False
    records={}; counters={}
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
    assert all(v>=0 for row in counters.values() for count in row.values() for v in count.values())
    assert all(records[name]['recordStatus']=='CURRENT_RECORD' for name in (API,WEB))
    assert records[API+'$1']['recordStatus']=='UNEXECUTED_NO_RECORD_NOT_QUALIFIED'
    totals={kind:dict(missed=sum(row[kind]['missed'] for row in counters.values()),covered=sum(row[kind]['covered'] for row in counters.values())) for kind in kinds}
    assert any(row['missed']>0 for row in totals.values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,normalManifestSha256=selected.COMPILE_SHA,hostManifestSha256=HOST_SHA,
      actualTests=14,suites=3,newTestIds=3,necessaryRegression=11,failures=0,errors=0,skipped=0,
      exactSelectedCaseIds=sorted(expected),sessionId=session,execSha256=run['execSha256'],xmlHashes=run['xmlHashes'],
      physicalClasses=physical,executableClasses={name:dict(**records[name],counters=counters[name]) for name in sorted(NAMES)},
      wholeSourceUnitCounters=totals,requiredWholeClassFour100=False,coverageUnion=False,exclusionsAdded=False,
      coverageRequirementRelaxed=False,historicalHookOrTermCasesSelected=False,programPtComplete=False,
      reportHelperSha256=host.sha(helper),reportLibraryHashes={str(path):host.sha(path) for path in libraries},
      reportStages=[compiled,measured],productTestsExecutedByMeasurement=0,
      actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=14,counters=totals,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
