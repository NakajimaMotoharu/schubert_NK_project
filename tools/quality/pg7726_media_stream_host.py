"""Ordinary selected JUnit on normal six-reactor compiled source; no HTTP, DB or Root fixture."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg7730_media_stream_six_compile as compilation
from host_tool_invocation import capture, verify

COMPILE=compilation.SLOT
SLOT=host.W/'pg7726-media-stream-host-v1'
OUT=host.BASE/'PG7726-media-stream-host-v1'
LAUNCHER=host.TC/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
LAUNCHER_SHA='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
AGENT=host.TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
HELPER=host.ROOT/'tools/quality/architecture/WebMediaMetricJunitLauncher.java'
SESSION_ID='PG7726-WEB-MEDIA-STREAM'
COUNTS={'HttpMetricContractTest':6,'HttpMetricRecorderTest':9,'HttpMetricValveTest':8,'GeneratedWebValueContractTest':4,'MediaStreamsMetricRecorderTest':8}


def require(value,message):
    if not value:raise ValueError(message)


def step(name,command):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    require(not (SLOT/(name+'-begin.safe.json')).exists(),'new-only step, never repeat an unknown run')
    host.write(SLOT/(name+'-begin.safe.json'),dict(command=command,startUTC=started))
    with (SLOT/(name+'.log')).open('xb') as log:
        child=subprocess.Popen(command,cwd=COMPILE/'snapshot',stdout=log,stderr=subprocess.STDOUT)
        host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,command=command,cwd=str(COMPILE/'snapshot'),startUTC=started))
        code=child.wait();log.flush();os.fsync(log.fileno())
    value=dict(command=command,actualExit=code,startUTC=started,
       endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),logSha256=host.sha(SLOT/(name+'.log')))
    host.write(SLOT/(name+'-exit.safe.json'),value)
    return value


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only original JVM run')
    raw=json.loads((COMPILE/'manifest.safe.json').read_bytes());snapshot=COMPILE/'snapshot'
    require(raw['actualExit']==0 and raw['terminal']['actualExit']==0 and raw['testsExecuted']==0,
            'genuine normal compile-only terminal, not a successful PT')
    require(all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'fixed source archive unchanged')
    require(host.sha(LAUNCHER)==LAUNCHER_SHA and AGENT.is_file(),'known official JUnit launcher/JaCoCo')
    cpfile=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt'
    dependencies=[Path(p) for p in cpfile.read_text().strip().split(os.pathsep)]
    require(dependencies and all(p.is_file() for p in dependencies),'actual Maven-resolved normal test classpath')
    # Every internal Main comes from this exact reactor, never an old locally installed snapshot.
    external=[p for p in dependencies if '/dev/codex/schubert/' not in str(p)
              and not str(p).startswith(str(snapshot)+'/src/')]
    require(all(str(p).startswith(str(host.TC/'m2/repository')+'/') for p in external),'only existing local normal external jars')
    jars=[]
    for item in raw['jars'].values():
        p=Path(item['path']);require(host.sha(p)==item['sha256'],'all current normal six Jar bytes');jars.append(p)
    target=snapshot/'src/schubert-nk-web/target'
    classes=SLOT/'launcher-classes'
    inputs=[target/'test-classes',target/'classes',*jars,*external,LAUNCHER]
    classpath=os.pathsep.join(str(p) for p in dict.fromkeys(inputs))
    os.umask(0o077);SLOT.mkdir();classes.mkdir()
    begin=dict(source=raw['source'],compileManifestSha256=host.sha(COMPILE/'manifest.safe.json'),
      archiveSha256=raw['begin']['archiveSha256'],classpathFileSha256=host.sha(cpfile),
      dependencyHashes={str(p):host.sha(p) for p in [*jars,*external,LAUNCHER,AGENT]},
      selectedSuites=COUNTS,expectedTests=35,helperSha256=host.sha(HELPER),invocation=invocation,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,rootMainInvoked=False,
      startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    host.write(SLOT/'begin.safe.json',begin)
    jdk=host.TC/'jdk-25.0.4/bin'
    compiled=step('launcher-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
                                    '-cp',classpath,'-d',str(classes),str(HELPER)])
    stages=[compiled]
    if compiled['actualExit']==0:
        stages.append(step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
          '-javaagent:'+str(AGENT)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION_ID,
          '-cp',str(classes)+os.pathsep+classpath,'WebMediaMetricJunitLauncher',str(SLOT/'xml')]))
    suites={};cases=[];xml_hashes={}
    for path in sorted((SLOT/'xml').glob('TEST-*.xml')):
        root=ET.parse(path).getroot();name=root.get('name');simple=name.rpartition('.')[2]
        require(simple in COUNTS and name not in suites,'exact five suites only')
        suites[name]={k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        xml_hashes[path.name]=host.sha(path)
        for case in root.findall('testcase'):
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),
                              result='PASS' if not list(case) else 'NOT_PASS',nonPass=[c.tag for c in case]))
    code=stages[-1]['actualExit']
    if code==0:
        require(len(suites)==5 and len(cases)==35 and len({(c['classname'],c['name']) for c in cases})==35
          and all(row==dict(tests=COUNTS[name.rpartition('.')[2]],failures=0,errors=0,skipped=0)
                  for name,row in suites.items()) and all(c['result']=='PASS' for c in cases),'all35 actual cases, never not-run PASS')
    require(all(host.sha(Path(p))==h for p,h in begin['dependencyHashes'].items()),'exact runtime dependencies unchanged')
    require(host.sha(HELPER)==begin['helperSha256'] and all(host.sha(snapshot/p)==h for p,h in raw['begin']['inputHashes'].items()),'frozen source/helper unchanged')
    value=dict(source=raw['source'],actualExit=code,begin=begin,stages=stages,suites=suites,cases=cases,xmlHashes=xml_hashes,
      execSha256=host.sha(SLOT/'jacoco.exec') if (SLOT/'jacoco.exec').exists() else None,
      qualification='RAW_TERMINAL_ONLY_POST_PENDING',whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    verify(invocation);host.write(SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(source=raw['source'],actualExit=code,suites=suites,manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(code)


if __name__=='__main__':main()
