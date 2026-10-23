"""BUG1646: normal verify of actual pure source/Test, not a dependency test bypass."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
from pg7000_monitoring_mode_host import MODULES, SUITE

SLOT = host.W/'pg7006-monitoring-pure-host-v1'
POM = 'tools/quality/harnesses/monitoring-pom.xml'


def main(slot=SLOT, selected=(SUITE,)):
    os.umask(0o077)
    if slot.exists():
        raise ValueError('new-only original run; never replay an existing begin')
    subprocess.run(['git','diff','--exit-code','HEAD','--','src','pom.xml','.mvn','mvnw',POM],
                   cwd=host.ROOT,stdout=subprocess.DEVNULL,check=True)
    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    slot.mkdir()
    archive = slot/'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git','archive','--format=tar',source,'pom.xml','.mvn','mvnw','src',
                        'program/characterization/pom.xml',POM],cwd=host.ROOT,stdout=f,check=True)
    snapshot = slot/'snapshot';snapshot.mkdir();host.safe_extract(archive,snapshot)
    inputs = host.inventory(snapshot)
    maven = [str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o',
             '--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository')]
    commands = [('format-six',maven+['-pl',MODULES,'spotless:check']),
                ('component-verify',maven+['-f',POM,'verify'])]
    env = dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
               MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',
               MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')
    begin = dict(source=source,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch='dev-foundation',archiveSha256=host.sha(archive),inputHashes=inputs,commands=commands,
      toolSha256=host.sha(Path(__file__)),selectedSuites=list(selected),actualVmActions=0,
      actualDatabaseActions=0,nativeTestsSelected=0,original4222Replayed=False,
      original44Replayed=False,scope='PURE_COMPONENT_NOT_WHOLE_QUALIFICATION')
    host.write(slot/'begin.safe.json',begin)
    stages = []
    for name, command in commands:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (slot/(name+'.log')).open('xb') as log:
            child = subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
            host.write(slot/(name+'-process.safe.json'),dict(pid=child.pid,cwd=str(snapshot),
                       source=source,command=command,startUTC=started))
            code = child.wait();log.flush();os.fsync(log.fileno())
        row = dict(name=name,command=command,actualExit=code,startUTC=started,
                   endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   logSha256=host.sha(slot/(name+'.log')))
        host.write(slot/(name+'-exit.safe.json'),row);stages.append(row)
        if code:
            break
    code = stages[-1]['actualExit']
    if {p:host.sha(snapshot/p) for p in inputs} != inputs:
        raise ValueError('fixed original source changed')
    target = snapshot/'tools/quality/harnesses/target'
    cases, xmls, suites = [], {}, {}
    for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        root = ET.parse(path).getroot()
        name = root.get('name')
        if name not in selected or name in suites:
            raise ValueError('exact declared original suites, no unknown or repeated XML')
        suites[name] = {k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        xmls[path.name] = host.sha(path)
        for case in root.findall('testcase'):
            invalid = [c.tag for c in case if c.tag not in ('system-out','system-err')]
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),
                              result='PASS' if not invalid else 'NOT_PASS',nonPass=invalid))
    counters = {}
    report = target/'site/jacoco/jacoco.xml'
    if report.exists():
        for p in ET.parse(report).getroot().findall('package'):
            for c in p.findall('class'):
                counters[c.get('name')] = {n.get('type'):dict(missed=int(n.get('missed')),
                  covered=int(n.get('covered'))) for n in c.findall('counter')
                  if n.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    value = dict(source=source,actualExit=code,begin=begin,stages=stages,sourceInputsUnchanged=True,
      suites=suites,cases=cases,xmlHashes=xmls,counters=counters,newAccepted=0,
      formalUpdated=False,effortPercent=None,qualification='RAW_TERMINAL_ONLY_POST_PENDING')
    host.write(slot/'manifest.safe.json',value)
    out = host.BASE/('PG'+slot.name.removeprefix('pg'));out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(source=source,actualExit=code,suites=suites,counters=counters,
                         manifestSha256=host.sha(out/'manifest.json'))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
