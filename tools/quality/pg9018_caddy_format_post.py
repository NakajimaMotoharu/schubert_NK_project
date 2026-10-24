"""Same-source ordinary3/XML/CRC/session and honest whole-class partial coverage; no exclusions."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from host_tool_invocation import capture,verify
from public_blob_scan import sha

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
WORK=ROOT.parent/'pgpt-runs/PG379'
TC=ROOT.parent/'toolchain'
NORMAL=BASE/'PG9014-caddy-format-six-compile-v1/manifest.json'
RUN=BASE/'PG9016-caddy-format-host-v1/manifest.json'
HOST_SLOT=WORK/'pg9016-caddy-format-host-v1'
SLOT=WORK/'pg9018-caddy-format-post-v1'
OUT=BASE/'PG9018-caddy-format-post-v1'
SOURCE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'


def step(name,command):
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    result=subprocess.run(command,cwd=SLOT,env={'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'},
                          capture_output=True,timeout=60,check=False)
    with (SLOT/(name+'.log')).open('xb') as stream:stream.write(result.stdout+result.stderr)
    value=dict(command=command,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExit=result.returncode,
               logSha256=sha((SLOT/(name+'.log')).read_bytes()))
    assert result.returncode==0 and not result.stderr
    return result.stdout.decode(),value


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    assert sha(NORMAL.read_bytes())=='01bad7736bbef335cb0b8dee60947e5767d57180bb59c631ae4ea9374058c18c'
    assert sha(RUN.read_bytes())=='e5a51ce6969ab8800c6111ef5ce5c0e422947d0a2d01002aeff7810b2eac43f7'
    normal=json.loads(NORMAL.read_bytes());run=json.loads(RUN.read_bytes())
    assert normal['source']==run['source']==SOURCE and normal['actualExit']==run['actualExit']==0
    assert run['begin']['compileManifestSha256']==sha(NORMAL.read_bytes())
    assert run['begin']['workingDirectory']==str(WORK/'pg9014-caddy-format-six-compile-v1/snapshot/src/schubert-nk-batch')
    assert all(sha(Path(name).read_bytes())==digest for name,digest in run['begin']['dependencyHashes'].items())
    assert all(sha(Path(name).read_bytes())==digest for name,digest in run['begin']['testSourceHashes'].items())
    assert all(sha((ROOT/name).read_bytes())==digest for name,digest in run['begin']['sourceHashes'].items())
    assert run['begin']['selectedSuites']=={'CaddyPublicConfigurationTest':3}
    assert len(run['cases'])==3 and all(row['result']=='PASS' for row in run['cases'])
    assert {row['name'] for row in run['cases']}=={'caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly','caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed','caddy455008DeploymentTemplateMatchesIndependentDirectiveSet'}
    xml=next((HOST_SLOT/'xml').glob('TEST-*.xml'))
    root=ET.parse(xml).getroot()
    assert {key:int(root.get(key)) for key in ('tests','failures','errors','skipped')}==dict(tests=3,failures=0,errors=0,skipped=0)
    assert sha(xml.read_bytes())==run['xmlHashes'][xml.name]
    assert sha((HOST_SLOT/'jacoco.exec').read_bytes())==run['execSha256']
    command=run['stages'][-1]['command']
    assert '-javaagent:'+str(TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar')+'=destfile='+str(HOST_SLOT/'jacoco.exec')+',append=false,sessionid=PG9016-CADDY-FORMAT' in command
    SLOT.mkdir(mode=0o700);classes=SLOT/'report-classes';classes.mkdir()
    class_name='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration.class'
    found=[]
    for item in normal['jars'].values():
        path=Path(item['path']);assert sha(path.read_bytes())==item['sha256']
        with zipfile.ZipFile(path) as archive:
            if class_name in archive.namelist():found.append(archive.read(class_name))
    assert len(found)==1
    target=SLOT/'CaddyPublicConfiguration.class'
    with target.open('xb') as stream:stream.write(found[0])
    libraries=[TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
               *[TC/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ('asm','asm-tree','asm-commons')]]
    assert all(path.is_file() for path in libraries)
    cp=os.pathsep.join(str(path) for path in libraries)
    helper=ROOT/'tools/quality/architecture/CaddyConfigurationCoverageMeasure.java'
    _,compile_stage=step('compile-report',[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(helper)])
    text,report_stage=step('measure-report',[str(TC/'jdk-25.0.4/bin/java'),'-cp',str(classes)+os.pathsep+cp,
          'CaddyConfigurationCoverageMeasure',str(HOST_SLOT/'jacoco.exec'),str(target)])
    counters={};crc=None
    for line in text.splitlines():
        fields=line.split('\t')
        if fields[0]=='COUNTER':counters[fields[1]]=dict(missed=int(fields[2]),covered=int(fields[3]))
        elif fields[0]=='CLASS':crc=fields[2]
    assert set(counters)=={'LINE','METHOD','CLASS','BRANCH'} and crc
    all100=all(row['missed']==0 and row['covered']>0 for row in counters.values())
    assert not all100  # Expected unresolved Root/TLS/native scope, not a reduced coverage acceptance.
    verify(invocation);OUT.mkdir()
    for name,path in [('coverage-measurement.txt',SLOT/'measure-report.log'),(xml.name,xml)]:
        with (OUT/name).open('xb') as stream:stream.write(path.read_bytes())
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,source=SOURCE,
       normalManifestSha256=sha(NORMAL.read_bytes()),hostManifestSha256=sha(RUN.read_bytes()),
       actualTests=3,suites=1,failures=0,errors=0,skipped=0,allDeclaredCasesRun=True,xmlSha256=sha(xml.read_bytes()),
       execSha256=run['execSha256'],sessionId='PG9016-CADDY-FORMAT',physicalClassSha256=sha(found[0]),classCrc=crc,
       wholeClassCounters=counters,requiredWholeClassFour100=all100,coverageUnion=False,exclusionsAdded=False,
       coverageRequirementRelaxed=False,heldScope='ROOT_NATIVE_READ_TLS_UNRUN_HOLD_NOT_A_PT_EXEMPTION',
       reportStages=[compile_stage,report_stage],reportHelperSha256=sha(helper.read_bytes()),
       reportLibraryHashes={str(path):sha(path.read_bytes()) for path in libraries},
       coverageMeasurementSha256=sha((OUT/'coverage-measurement.txt').read_bytes()),
       newJavaTestIds=0,wholeC01Or451Accepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,actualTests=3,wholeClassCounters=counters,requiredWholeClassFour100=all100,wholeC01Or451Accepted=False)))


if __name__=='__main__':main()
