"""One new-only offline pure monitoring PT; no VM/service/DB/native/Root execution."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host

SLOT = host.W/'pg7000-monitoring-mode-host-v1'
SUITE = 'dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicyTest'
MODULES = ','.join('src/schubert-nk-'+m for m in ('protocol','storage','bootstrap','api','web','batch'))


def main():
    os.umask(0o077)
    if SLOT.exists():
        raise ValueError('new-only job; never restart an existing begin or terminal')
    subprocess.run(['git','diff','--exit-code','HEAD','--','src','pom.xml','.mvn','mvnw'],
                   cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    SLOT.mkdir()
    archive = SLOT/'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git','archive','--format=tar',source,'pom.xml','.mvn','mvnw','src',
                        'program/characterization/pom.xml'],cwd=host.ROOT,stdout=f,check=True)
    snapshot = SLOT/'snapshot';snapshot.mkdir();host.safe_extract(archive,snapshot)
    inputs = host.inventory(snapshot)
    maven = [str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o',
             '--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository')]
    commands = {
      'format-six':maven+['-pl',MODULES,'spotless:check'],
      'selected-package':maven+['-pl','src/schubert-nk-batch','-am','-Dtest='+SUITE,
                              '-Dsurefire.failIfNoSpecifiedTests=false','package'],
      'report-batch':maven+['-pl','src/schubert-nk-batch','jacoco:report'],
      'spotbugs-component':maven+['-pl','src/schubert-nk-batch',
        '-Dspotbugs.onlyAnalyze=dev.codex.schubert.nk.batch.monitoring.*',
        'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']}
    env = dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
               MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',
               MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')
    begin = dict(source=source,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch='dev-foundation',archiveSha256=host.sha(archive),inputHashes=inputs,commands=commands,
      toolSha256=host.sha(Path(__file__)),selectedSuites=[SUITE],actualVmActions=0,
      actualDatabaseActions=0,nativeTestsSelected=0,original4222Replayed=False,
      original44Replayed=False,scope='PURE_MONITORING_COMPONENT_NOT_WHOLE_QUALIFICATION')
    host.write(SLOT/'begin.safe.json',begin)
    stages = []
    for name, command in commands.items():
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (SLOT/(name+'.log')).open('xb') as log:
            child = subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
            host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,cwd=str(snapshot),
                       source=source,command=command,startUTC=started))
            code = child.wait();log.flush();os.fsync(log.fileno())
        row = dict(name=name,command=command,actualExit=code,startUTC=started,
                   endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   logSha256=host.sha(SLOT/(name+'.log')))
        host.write(SLOT/(name+'-exit.safe.json'),row);stages.append(row)
        if code:
            break
    code = stages[-1]['actualExit']
    after = {p:host.sha(snapshot/p) for p in inputs}
    if after != inputs:
        raise ValueError('fixed full source snapshot changed')
    target = snapshot/'src/schubert-nk-batch/target'
    suites, cases, xmls = {}, [], {}
    for module in ('protocol','storage','bootstrap','api','web','batch'):
        reports = snapshot/('src/schubert-nk-'+module)/'target/surefire-reports'
        for path in sorted(reports.glob('TEST-*.xml')):
            root = ET.parse(path).getroot();name = root.get('name')
            if name != SUITE or name in suites:
                raise ValueError('no undeclared suite or repeated result')
            suites[name] = {k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')}
            xmls[path.relative_to(snapshot).as_posix()] = host.sha(path)
            for case in root.findall('testcase'):
                children = [c.tag for c in case if c.tag not in ('system-out','system-err')]
                cases.append(dict(classname=case.get('classname'),name=case.get('name'),
                                  result='PASS' if not children else 'NOT_PASS',nonPass=children))
    counters = {}
    report = target/'site/jacoco/jacoco.xml'
    if report.exists():
        for package in ET.parse(report).getroot().findall('package'):
            if package.get('name') != 'dev/codex/schubert/nk/batch/monitoring':
                continue
            for node in package.findall('class'):
                counters[node.get('name')] = {c.get('type'):dict(missed=int(c.get('missed')),
                  covered=int(c.get('covered'))) for c in node.findall('counter')
                  if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    value = dict(source=source,actualExit=code,begin=begin,stages=stages,
      inputHashesUnchanged=after==inputs,suites=suites,cases=cases,xmlHashes=xmls,
      measuredComponentCounters=counters,formalUpdated=False,newAccepted=0,
      effortPercent=None,qualification='RAW_TERMINAL_ONLY_INDEPENDENT_POST_PENDING')
    host.write(SLOT/'manifest.safe.json',value)
    out = host.BASE/'PG7000-monitoring-mode-host-v1';out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(source=source,actualExit=code,suites=suites,counters=counters,
                         manifestSha256=host.sha(out/'manifest.json'))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
