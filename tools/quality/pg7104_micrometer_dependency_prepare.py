"""Exact missing public dependency from an existing recorded vendor distribution; no network or runtime."""
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7104-micrometer-dependency-prepare-v1'
OUT=host.BASE/'PG7104-micrometer-dependency-prepare-v1'
HDR=host.TC/'artemis/apache-artemis-2.56.0/lib/HdrHistogram-2.2.2.jar'
HDR_SHA='22d1d4316c4ec13a68b559e98c8256d69071593731da96136640f864fa14fad8'
CORE=host.TC/'m2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
CORE_SHA='9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'
REPOSITORY=host.TC/'m2/repository'
COORDINATE=REPOSITORY/'org/hdrhistogram/HdrHistogram'
TARGET=COORDINATE/'2.2.2'
RECORD=host.ROOT/'documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md'
POM_ENTRY='META-INF/maven/org.hdrhistogram/HdrHistogram/pom.xml'


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only tool installation, observe original result instead of repeating')
    require(host.sha(HDR)==HDR_SHA and host.sha(CORE)==CORE_SHA,'exact public installed vendor and recorded core bytes')
    record=RECORD.read_text()
    require(CORE_SHA in record and '441ad38aa1b0526e5709edf43542039f016669d24134056613e4cbafdf6b101e5351f79f7ee190b43fc8031f6ec596a5fd075490dcee4d3eb3a88d8ed2cfc01b' in record,
            'existing core pin and previously verified official distribution provenance recorded')
    require(not TARGET.exists() and TARGET.resolve().is_relative_to(REPOSITORY.resolve()),
            'only a missing exact coordinate, no existing object overwritten or redirected')
    before={str(p.relative_to(COORDINATE)):host.sha(p) for p in COORDINATE.rglob('*') if p.is_file()} if COORDINATE.exists() else {}
    with zipfile.ZipFile(HDR) as jar:
        props='META-INF/maven/org.hdrhistogram/HdrHistogram/pom.properties'
        require(jar.namelist().count(POM_ENTRY)==jar.namelist().count(props)==1,'unique embedded public Maven metadata')
        properties=dict(line.split('=',1) for line in jar.read(props).decode().splitlines() if line and not line.startswith('#'))
        require(properties==dict(artifactId='HdrHistogram',groupId='org.hdrhistogram',version='2.2.2'),
                'exact embedded public Maven coordinate')
        pom=jar.read(POM_ENTRY);tree=ET.fromstring(pom)
        require([tree.findtext('{*}'+key) for key in ('groupId','artifactId','version')]==['org.hdrhistogram','HdrHistogram','2.2.2'],
                'unaltered original POM coordinate, no synthesized dependency model')
        os.umask(0o077);SLOT.mkdir()
        extracted=Path(jar.extract(POM_ENTRY,SLOT))
    require(host.sha(extracted)==hashlib.sha256(pom).hexdigest(),'exact original public vendor POM extraction')
    command=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-N',
      '-Dmaven.repo.local='+str(REPOSITORY),'org.apache.maven.plugins:maven-install-plugin:3.1.2:install-file',
      '-Dfile='+str(HDR),'-DpomFile='+str(extracted),'-DgeneratePom=false']
    env=dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
      MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8')
    begin=dict(command=command,invocation=invocation,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      sourceHdrSha256=HDR_SHA,recordedCoreSha256=CORE_SHA,originalPomSha256=host.sha(extracted),
      coordinateBefore=before,wholeOriginalDistributionArchiveCurrentlyAvailable=False,
      provenance='RECORDED_PRIOR_OFFICIAL_ARCHIVE_CHECK_PLUS_CURRENT_INSTALLED_METADATA_AND_PIN',
      networkAllowed=False,existingCoordinateOverwritten=False,testsExecuted=0,actualVmActions=0,actualDatabaseActions=0)
    host.write(SLOT/'begin.safe.json',begin)
    with (SLOT/'maven.log').open('xb') as log:
        child=subprocess.Popen(command,cwd=host.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        host.write(SLOT/'process.safe.json',dict(pid=child.pid,command=command,cwd=str(host.ROOT)))
        code=child.wait();log.flush();os.fsync(log.fileno())
    terminal=dict(actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      beginSha256=host.sha(SLOT/'begin.safe.json'),logSha256=host.sha(SLOT/'maven.log'))
    host.write(SLOT/'exit.safe.json',terminal)
    installed={p.name:host.sha(p) for p in TARGET.glob('*') if p.is_file()}
    checks=dict(sourceJarUnchanged=host.sha(HDR)==HDR_SHA,coreUnchanged=host.sha(CORE)==CORE_SHA,
      installedJarExact=installed.get('HdrHistogram-2.2.2.jar')==HDR_SHA,
      installedOriginalPomExact=installed.get('HdrHistogram-2.2.2.pom')==host.sha(extracted),
      oldNonMetadataObjectsUnchanged=all(host.sha(COORDINATE/p)==h for p,h in before.items()
        if not p.startswith('maven-metadata-local.xml')))
    value=dict(actualExit=code,begin=begin,terminal=terminal,installedFiles=installed,checks=checks,
      toolRecordSha256=host.sha(RECORD),allChecksPassed=all(checks.values()),
      originalDistributionUrl='https://downloads.apache.org/artemis/artemis/2.56.0/apache-artemis-2.56.0-bin.tar.gz',
      testsExecuted=0,status='TOOLCHAIN_INSTALL_NOT_PT',productionPomChanged=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    host.write(SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=code,checks=checks,testsExecuted=0,manifestSha256=host.sha(OUT/'manifest.json'))))
    require(code==0 and all(checks.values()),'original install failure/partial state preserved, no blind retry')


if __name__=='__main__':main()
