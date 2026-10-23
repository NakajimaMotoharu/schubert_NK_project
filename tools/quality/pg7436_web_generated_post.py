"""Independent actual27 XML/current normal class CRC, entire monitoring component/static domain."""
import datetime
import json
import os
import platform
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg7434_web_generated_host as original
import pg7032_monitoring_six_artifact_post as steps
import pg7106_micrometer_http_host as sdk
import pg7362_api_pool_observation_host as normal_sdk
from host_tool_invocation import capture, verify

SLOT=host.W/'pg7436-web-generated-post-v1'
OUT=host.BASE/'PG7436-web-generated-post-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
NAMES={PREFIX+'HttpMetricContract'+s for s in ('','$Metric','$Route','$Method','$Status','$Labels')}
NAMES|={PREFIX+n for n in ('HttpMetricRecorder','HttpMetricValve','HttpMetricValve$Completion')}
RAW_SHA=None
COMPILE_SHA=None


def require(value,message):
    if not value:raise ValueError(message)


def main():
    global RAW_SHA,COMPILE_SHA
    RAW_SHA=host.sha(original.SLOT/'manifest.safe.json');COMPILE_SHA=host.sha(original.COMPILE/'manifest.safe.json')
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only post, never repeat an unknown operation')
    require(host.sha(original.SLOT/'manifest.safe.json')==RAW_SHA
            and host.sha(original.COMPILE/'manifest.safe.json')==COMPILE_SHA,'exact original actual27 and compile witnesses')
    raw=json.loads((original.SLOT/'manifest.safe.json').read_bytes())
    compiled=json.loads((original.COMPILE/'manifest.safe.json').read_bytes())
    require(raw['actualExit']==compiled['actualExit']==0 and raw['source']==compiled['source'], 'same fixed source genuinely zero')
    require(len(raw['cases'])==27 and all(c['result']=='PASS' for c in raw['cases'])
            and len({(c['classname'],c['name']) for c in raw['cases']})==27,'genuine unique cases, no rerun/flaky/nonpass accepted')
    require(len(raw['suites'])==4 and all(v==dict(tests=original.COUNTS[k.rpartition('.')[2]],failures=0,errors=0,skipped=0)
            for k,v in raw['suites'].items()),'all exact suites/FES0')
    require(all(host.sha(original.SLOT/'xml'/p)==h for p,h in raw['xmlHashes'].items()),'genuine returned XML')
    snapshot=original.COMPILE/'snapshot';target=snapshot/'src/schubert-nk-web/target'
    inputs=compiled['begin']['inputHashes']
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all frozen source input bytes')
    sources={p:h for p,h in inputs.items() if p.startswith('src/schubert-nk-web/') and '/monitoring/' in p and p.endswith('.java')}
    require(len(sources)==8 and all(host.sha(host.ROOT/p)==h for p,h in sources.items()),'complete eight current Main/Test source files')
    require(host.sha(original.SLOT/'jacoco.exec')==raw['execSha256'],'original one-session execution data')
    dependencies=raw['begin']['dependencyHashes']
    require(all(host.sha(Path(p))==h for p,h in dependencies.items()),'all actual current normal dependencies including internal six Jars')
    require(all(dependencies.get(p)==h for p,h in sdk.SDK.items())
            and compiled['begin']['dependencyJarHashes']==normal_sdk.DEPENDENCIES,'actual JVM/static/compile same four pinned Micrometer dependencies')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT
    component=SLOT/'component';component.mkdir()
    physical={p.relative_to(target/'classes').as_posix():host.sha(p) for p in (target/'classes'/PREFIX).rglob('*.class')}
    require(set(physical)=={n+'.class' for n in NAMES}|{PREFIX+'package-info.class'},'every actual component class, no owned-class exclusions')
    for name,digest in physical.items():
        destination=component/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(target/'classes'/name,destination)
        require(host.sha(destination)==digest,'exact current normal byte, debug differences included')
    jdk=host.TC/'jdk-25.0.4/bin';static=host.TC/'static-gates-20261015'
    libraries=[host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
      *[host.TC/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    require(all(p.is_file() for p in libraries),'official existing coverage readers')
    audit=SLOT/'audit-classes';audit.mkdir();cp=os.pathsep.join(str(p) for p in libraries)
    helper=host.ROOT/'tools/quality/architecture/ComponentCoverageAudit.java'
    commands=[('audit-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(audit),str(helper)]),
      ('audit-run',[str(jdk/'java'),'-cp',str(audit)+os.pathsep+cp,'ComponentCoverageAudit',str(original.SLOT/'jacoco.exec'),str(component),*sorted(NAMES)])]
    stages=[];output=''
    for name,command in commands:
        row,output=steps.step(name,command);stages.append(row)
        require(row['actualExit']==0,'independent exact CRC/session/all-four counters must succeed')
    executable={}
    for line in output.splitlines():
        parts=line.split('\t')
        if parts[0]=='CLASS':
            counts={}
            for item in parts[3:]:
                kind,missed,covered=item.split(':');counts[kind]=dict(missed=int(missed),covered=int(covered))
            executable[parts[1]]=dict(crc64=parts[2],counters=counts)
    require(set(executable)==NAMES,'all nine current executable classes accounted')
    totals={kind:dict(missed=sum(v['counters'][kind]['missed'] for v in executable.values()),
      covered=sum(v['counters'][kind]['covered'] for v in executable.values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    require(all(v['missed']==0 and v['covered']>0 for v in totals.values()),'nonvacuous actual four100')
    filelist=SLOT/'main.txt';main=[snapshot/p for p in sources if '/src/main/java/' in p]
    with filelist.open('x') as stream:stream.write(''.join(str(p)+'\n' for p in sorted(main)))
    rules=host.ROOT/'tools/quality/static'
    pmdcp=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    aux=os.pathsep.join([str(target/'classes'),*dependencies])
    checks=[('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(str(p) for p in pmdcp),'net.sourceforge.pmd.cli.PmdCli','check',
      '--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5',
      '--aux-classpath',aux,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')]),
      ('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),
      '-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(filelist)])]
    # Analysis-only POM: each system binding is an alias for the exact original JVM classpath,
    # never a production dependency substitute. Only precompiled new component classes are analyzed.
    project=ET.Element('project',xmlns='http://maven.apache.org/POM/4.0.0')
    for key,value in [('modelVersion','4.0.0'),('groupId','qualified.analysis'),('artifactId','http-terminal-static'),('version','1')]:
        ET.SubElement(project,key).text=value
    deps=ET.SubElement(project,'dependencies')
    for i,path in enumerate(dependencies):
        if str(path).endswith('runtime.jar') or path==str(original.LAUNCHER):continue
        dep=ET.SubElement(deps,'dependency')
        for key,value in [('groupId','qualified.bytebinding'),('artifactId','binding-'+str(i)),('version','1'),('scope','system'),('systemPath',path)]:
            ET.SubElement(dep,key).text=value
    build=ET.SubElement(project,'build');ET.SubElement(build,'directory').text=str(SLOT/'static-target')
    ET.SubElement(build,'outputDirectory').text=str(component)
    plugin=ET.SubElement(ET.SubElement(build,'plugins'),'plugin')
    for key,value in [('groupId','com.github.spotbugs'),('artifactId','spotbugs-maven-plugin'),('version','4.10.4.0')]:ET.SubElement(plugin,key).text=value
    config=ET.SubElement(plugin,'configuration')
    for key,value in [('effort','Max'),('threshold','Low'),('failOnError','true'),('xmlOutput','true')]:ET.SubElement(config,key).text=value
    pom=SLOT/'static-pom.xml'
    with pom.open('xb') as stream:stream.write(ET.tostring(project,encoding='utf-8',xml_declaration=True))
    checks.append(('spotbugs',[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
      '-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-f',str(pom),'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']))
    old_env={key:os.environ.get(key) for key in ('JAVA_HOME','PATH','MAVEN_USER_HOME','MAVEN_SKIP_RC')}
    os.environ.update(JAVA_HOME=str(jdk.parent),PATH=str(jdk)+':/usr/bin:/bin',MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true')
    static_raw={}
    try:
        for name,command in checks:
            row,_=steps.step(name,command)
            report=SLOT/(name+'.xml') if name!='spotbugs' else SLOT/'static-target/spotbugsXml.xml'
            root=ET.parse(report).getroot()
            nodes=root.findall('.//{*}violation') if name=='pmd' else root.findall('.//error') if name=='checkstyle' else root.findall('.//BugInstance')
            static_raw[name]=dict(row,reportSha256=host.sha(report),findings=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in nodes],
              processingErrors=len(root.findall('.//{*}error')) if name=='pmd' else len(root.findall('.//MissingClass')) if name=='spotbugs' else 0)
    finally:
        for key,value in old_env.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()) and all(host.sha(Path(p))==h for p,h in dependencies.items()),'original source/dependencies unchanged after independent analysis')
    value=dict(actualExit=0,source=raw['source'],sourceRun='PG'+original.SLOT.name.removeprefix('pg'),tests=27,suites=4,
      originalManifestSha256=RAW_SHA,originalCompileSha256=COMPILE_SHA,invocation=invocation,
      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.platform(),sourceFiles=sources,
      actualCrcMismatch=0,actualSessions=1,physicalClasses=physical,executableClasses=executable,counters=totals,
      additionalSdkAuxiliaryJarHashes=sdk.SDK,
      staticRaw=static_raw,staticAnalysisPomSha256=host.sha(pom),staticAuxiliaryAliasSemantics='ACTUAL_RUNTIME_BYTE_BINDINGS_NOT_PRODUCTION_COORDINATES',
      coverageScope='ALL_NINE_CURRENT_MONITORING_EXECUTABLES_NOT_ALL_WEB_OR_WHOLE451',
      originalXmlHashes=raw['xmlHashes'],coverageExecSha256=raw['execSha256'],auditStages=stages,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    verify(invocation);host.write(SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=27,counters=totals,static={k:dict(actualExit=v['actualExit'],findings=len(v['findings']),processingErrors=v['processingErrors']) for k,v in static_raw.items()},manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
