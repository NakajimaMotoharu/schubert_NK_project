"""Fresh six-module compile/package only, no business/native/Root test invocation.

Source is the exact c285 pipeline source, not the later operator/document commit.
This is explicitly not a full PT/coverage/451 qualification. All skipped PT stay unrun.
"""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
from pg7000_monitoring_mode_host import MODULES

SOURCE = 'c285c38ac4fcc3f16bfd3d2051ec76c352227f74'
SLOT = host.W/'pg7030-monitoring-six-compile-v1'
OUT = host.BASE/'PG7030-monitoring-six-compile-v1'
ROLES = ('protocol','storage','bootstrap','api','web','batch')
PLUGINS = {'maven-compiler-plugin','maven-surefire-plugin','maven-jar-plugin',
           'jacoco-maven-plugin','spotbugs-maven-plugin','maven-enforcer-plugin',
           'spotless-maven-plugin'}


def preflight():
    subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','pom.xml','.mvn','mvnw'],
                   cwd=host.ROOT,stdout=subprocess.DEVNULL,check=True)
    paths = ['pom.xml',*['src/schubert-nk-'+r+'/pom.xml' for r in ROLES]]
    records=[]
    for path in paths:
        raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        root=ET.fromstring(raw)
        names={n.findtext('{*}artifactId') for n in root.findall('.//{*}build/{*}plugins/{*}plugin')}
        if not names <= PLUGINS:
            raise ValueError('unknown plugin must be reviewed before compile stage')
        records.append(dict(path=path,sha256=host.sha(host.ROOT/path),plugins=sorted(names)))
    return records


def main():
    os.umask(0o077)
    if SLOT.exists():
        raise ValueError('new-only source compile, observe original job instead of restarting')
    poms=preflight()
    SLOT.mkdir()
    archive=SLOT/'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git','archive','--format=tar',SOURCE,'pom.xml','.mvn','mvnw','src',
                        'program/characterization/pom.xml'],cwd=host.ROOT,stdout=f,check=True)
    snapshot=SLOT/'snapshot';snapshot.mkdir();host.safe_extract(archive,snapshot)
    inputs=host.inventory(snapshot)
    command=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o',
             '--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository'),
             '-pl',MODULES,'-am','-DskipTests=true','package']
    env=dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
             MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',
             MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')
    begin=dict(source=SOURCE,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
      startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,
      archiveSha256=host.sha(archive),inputHashes=inputs,pomPreflight=poms,
      testsExecuted=0,testStatus='UNRUN_NOT_PASS_COMPILE_ONLY',wholePtQualified=False,
      commonModuleSelected=False,actualVmActions=0,actualDatabaseActions=0,rootMainInvoked=False,
      toolSha256=host.sha(Path(__file__)))
    host.write(SLOT/'begin.safe.json',begin)
    with (SLOT/'maven.log').open('xb') as log:
        child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
        host.write(SLOT/'process.safe.json',dict(pid=child.pid,cwd=str(snapshot),source=SOURCE,
          command=command,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        code=child.wait();log.flush();os.fsync(log.fileno())
    terminal=dict(source=SOURCE,actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  beginSha256=host.sha(SLOT/'begin.safe.json'),logSha256=host.sha(SLOT/'maven.log'))
    host.write(SLOT/'exit.safe.json',terminal)
    xmls=[p for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml')]
    if xmls:
        raise ValueError('no suite may execute in the compile-only stage')
    if any(host.sha(snapshot/p)!=h for p,h in inputs.items()):
        raise ValueError('fixed entire source snapshot changed')
    jars={}
    for role in ROLES:
        path=snapshot/f'src/schubert-nk-{role}/target/schubert-nk-{role}-0.1.0-SNAPSHOT.jar'
        if path.is_file():jars[role]=dict(path=str(path),sha256=host.sha(path))
    value=dict(begin=begin,terminal=terminal,jars=jars,source=SOURCE,actualExit=code,
      testsExecuted=0,testStatus='UNRUN_NOT_PASS_COMPILE_ONLY',sourceInputsUnchanged=True,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    host.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=code,source=SOURCE,jars=len(jars),testsExecuted=0,
                         manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(code)


if __name__=='__main__':
    main()
