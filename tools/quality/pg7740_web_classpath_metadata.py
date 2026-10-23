"""BUG1671: offline metadata goal only on existing successful normal snapshot, no repeated compile or PT."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg6966_chr_adapter_host as host
import pg7730_media_stream_six_compile as compilation
from pg7000_monitoring_mode_host import MODULES
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7740-web-classpath-metadata-v1'
OUT=host.BASE/'PG7740-web-classpath-metadata-v1'
PLUGIN=host.TC/'m2/repository/org/apache/maven/plugins/maven-dependency-plugin/3.9.0/maven-dependency-plugin-3.9.0.jar'

def require(value,message):
    if not value:raise ValueError(message)

def class_outputs(snapshot):
    result={}
    for kind in ('classes','test-classes'):
        for path in snapshot.glob('src/*/target/'+kind+'/**/*.class'):
            result[str(path.relative_to(snapshot))]=dict(sha256=host.sha(path),mtimeNs=path.stat().st_mtime_ns)
    return result

def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only metadata receipt')
    file=compilation.SLOT/'manifest.safe.json';normal=json.loads(file.read_bytes());snapshot=compilation.SLOT/'snapshot'
    require(host.sha(file)=='163b819a053677f352969b505bad07a790f6ef2b902419e8cee9e9007d5cb977'
      and normal['source']==compilation.SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0
      and normal['testsExecuted']==0 and normal['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY','original genuine normal compile, not repeated or PT pass')
    inputs=normal['begin']['inputHashes'];require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all source/POM/input bytes fixed')
    require(not (snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt').exists(),'output genuinely absent before first metadata goal')
    before=class_outputs(snapshot);require(len(before)>1767,'all own already compiled Main/Test artifacts exist')
    jars={item['path']:item['sha256'] for item in normal['jars'].values()}
    require(all(host.sha(Path(p))==h for p,h in jars.items()),'all original six Jar hashes')
    require(PLUGIN.is_file(),'already installed reviewed metadata plugin only; no download')
    plugin_sha=host.sha(PLUGIN)
    with zipfile.ZipFile(PLUGIN) as archive:descriptor=ET.fromstring(archive.read('META-INF/maven/plugin.xml'))
    mojo=next(row for row in descriptor.findall('.//mojo') if row.findtext('goal')=='build-classpath')
    require(descriptor.findtext('version')=='3.9.0' and mojo.findtext('requiresDependencyResolution')=='test'
      and all(mojo.find(k) is None for k in ('executePhase','executeGoal','executeLifecycle')),'metadata resolution only, no forked compile/Test lifecycle')
    command=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
      '-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-pl',MODULES,'-am',
      'org.apache.maven.plugins:maven-dependency-plugin:3.9.0:build-classpath','-DincludeScope=test','-Dmdep.outputFile=target/pgpt-test-classpath.txt']
    require(not any(p in command for p in ('package','compile','test','verify','install','deploy','clean','-DskipTests=true')),
      'only one metadata goal, no compile/PT skip or replay')
    env=dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
      MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true')
    os.umask(0o077);SLOT.mkdir();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    host.write(SLOT/'begin.safe.json',dict(source=compilation.SOURCE,startUTC=started,command=command,
      originalCompileSha256=host.sha(file),pluginSha256=plugin_sha,classCountBefore=len(before),invocation=invocation))
    with (SLOT/'metadata.log').open('xb') as log:
        child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
        host.write(SLOT/'process.safe.json',dict(pid=child.pid,command=command,cwd=str(snapshot),source=compilation.SOURCE,startUTC=started))
        code=child.wait();log.flush();os.fsync(log.fileno())
    terminal=dict(actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),logSha256=host.sha(SLOT/'metadata.log'))
    host.write(SLOT/'exit.safe.json',terminal);require(code==0,'genuine metadata goal terminal zero')
    require(before==class_outputs(snapshot) and all(host.sha(snapshot/p)==h for p,h in inputs.items())
      and all(host.sha(Path(p))==h for p,h in jars.items()) and host.sha(PLUGIN)==plugin_sha,'all original class bytes/mtimes/source/Jars/plugin unchanged')
    log=(SLOT/'metadata.log').read_text();goals=[line for line in log.splitlines() if line.startswith('[INFO] --- ')]
    require(goals and all('dependency:3.9.0:build-classpath' in line for line in goals),'only original approved metadata mojo ran')
    cp=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt';require(cp.is_file(),'actual Maven-produced Web classpath')
    dependencies=[Path(p) for p in cp.read_text().strip().split(os.pathsep)]
    require(dependencies and all(p.is_file() for p in dependencies),'real resolved metadata dependencies')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,startUTC=started,terminal=terminal,command=command,
      originalCompileSha256=host.sha(file),pluginSha256=plugin_sha,classpath=dict(path=str(cp),sha256=host.sha(cp)),
      resolvedMetadataJarHashes={str(p):host.sha(p) for p in dependencies},originalClassCount=len(before),
      originalClassBytesAndMtimesUnchanged=True,originalJarHashes=jars,sourceInputsUnchanged=True,
      metadataOnly=True,compileRepeated=False,productionPtExecuted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,
      cachedInternalArtifactsNotQualifiedForExecution=True,relatedBug='BUG-1671',relatedExpansion='YKT-1422',
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,metadataGoals=len(goals),classesUnchanged=len(before),pt=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
