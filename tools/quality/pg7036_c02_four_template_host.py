"""Ordinary PT over four public text resources; no executable application dependency."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
from pg7000_monitoring_mode_host import MODULES

SLOT = host.W/'pg7036-c02-four-template-host-v1'
OUT = host.BASE/'PG7036-c02-four-template-host-v1'
POM = 'tools/quality/harnesses/deployment-unit-pom.xml'
SUITE = 'dev.codex.schubert.nk.batch.platform.SupplementaryUnitTemplateTest'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java'
FILES = ('schubert-nk-backup.service.template','schubert-nk-bootstrap-admin.service.template',
         'caddy.service.d/schubert-nk-startup-policy.conf','caddy.service.d/schubert-nk-stop-policy.conf')
METHODS = {'unitSup001BackupAllDeclaredContracts','unitSup002AdminDisabledAndDedicatedAllDeclaredContracts',
           'unitSup003CaddyStartupResetsAndFixedDaemonAbi','unitSup004CaddyStopOnlyDeclaredOverrides',
           'unitSup005IndependentOracleMutationCanaries'}


def main():
    os.umask(0o077)
    if SLOT.exists():
        raise ValueError('new-only actual fixture; observe existing job instead of replay')
    subprocess.run(['git','diff','--exit-code','HEAD','--','src','pom.xml','.mvn','mvnw',POM],
                   cwd=host.ROOT,stdout=subprocess.DEVNULL,check=True)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    SLOT.mkdir()
    archive=SLOT/'source.tar'
    with archive.open('xb') as stream:
        subprocess.run(['git','archive','--format=tar',source,'pom.xml','.mvn','mvnw','src',POM,
                        'program/characterization/pom.xml'],cwd=host.ROOT,stdout=stream,check=True)
    snapshot=SLOT/'snapshot';snapshot.mkdir();host.safe_extract(archive,snapshot)
    inputs=host.inventory(snapshot)
    maven=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o',
           '--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository')]
    commands=[('format-six',maven+['-pl',MODULES,'spotless:check']),
              ('template-test',maven+['-f',POM,'test'])]
    env=dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
      MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',MAVEN_OPTS='-Xmx1g')
    begin=dict(source=source,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch='dev-foundation',archiveSha256=host.sha(archive),inputHashes=inputs,commands=commands,
      selectedTest=TEST,selectedSuite=SUITE,resourceFiles=list(FILES),actualVmActions=0,actualDatabaseActions=0,
      productionExecutableDependencies=[],mainSourcesCompiled=0,toolSha256=host.sha(Path(__file__)))
    host.write(SLOT/'begin.safe.json',begin)
    stages=[]
    for name,command in commands:
        with (SLOT/(name+'.log')).open('xb') as log:
            child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
            host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,source=source,
              command=command,cwd=str(snapshot),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
            code=child.wait();log.flush();os.fsync(log.fileno())
        row=dict(command=command,actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 logSha256=host.sha(SLOT/(name+'.log')))
        host.write(SLOT/(name+'-exit.safe.json'),row);stages.append(row)
        if code:break
    target=snapshot/'tools/quality/harnesses/target-deployment-unit'
    suites={};cases=[];xmls={};resources={}
    for p in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        r=ET.parse(p).getroot()
        if r.get('name')!=SUITE or suites:
            raise ValueError('only declared text-source suite')
        suites[SUITE]={k:int(r.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        xmls[p.name]=host.sha(p)
        for c in r.findall('testcase'):
            bad=[n.tag for n in c if n.tag not in ('system-out','system-err')]
            cases.append(dict(name=c.get('name'),result='NOT_PASS' if bad else 'PASS',nonPass=bad))
    for name in FILES:
        path=target/'test-classes/systemd'/name
        if path.exists():
            if host.sha(path)!=host.sha(snapshot/'src/deployment/systemd'/name):
                raise ValueError('actual PT resource must match public source byte exactly')
            resources[name]=host.sha(path)
    if list((target/'classes').rglob('*.class')):
        raise ValueError('no Production executable class in this text-only harness')
    if any(host.sha(snapshot/p)!=h for p,h in inputs.items()):
        raise ValueError('fixed source snapshot must stay identical')
    value=dict(actualExit=stages[-1]['actualExit'],source=source,begin=begin,stages=stages,
      suites=suites,cases=cases,xmlHashes=xmls,actualResources=resources,sourceInputsUnchanged=True,
      coverage='NOT_APPLICABLE_CONFIGURATION_NOT_JAVA_NO_0_OVER_0_PASS',
      formalUpdated=False,newAccepted=0,wholeC02Accepted=False,effortPercent=None)
    host.write(SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=value['actualExit'],source=source,suites=suites,
                         resources=len(resources),manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(value['actualExit'])


if __name__=='__main__':
    main()
