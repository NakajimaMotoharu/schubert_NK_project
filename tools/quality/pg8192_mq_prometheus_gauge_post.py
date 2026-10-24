"""Independent fixed 14/2 result, all2 Main coverage and new exact-scope static checks; no product rerun."""
import copy
import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pg6966_chr_adapter_host as host
import scoped_prometheus_host as common
from host_tool_invocation import capture, verify

RUN=host.W/'pg8190-mq-prometheus-gauge-host-v1'
RAW_SHA='6ee4413b3f87f7e87c21bb381dbc6f9c46e30d1c74ee5c1fc7697827f9095f0c'
SLOT=host.W/'pg8192-mq-prometheus-gauge-post-v1'
OUT=host.BASE/'PG8192-mq-prometheus-gauge-post-v1'
NAMES={'dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorder',
       'dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorder$Snapshot'}
PREFIX='dev/codex/schubert/nk/api/monitoring/'
COUNTS={'MqPressureMetricRecorderTest':8,'MqPrometheusGaugeContractTest':6}
ENV=dict(common.ENV,JAVA_HOME=str(host.TC/'jdk-25.0.4'),
         MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true')
SOURCE_PATH='src/schubert-nk-api/src/main/java/'+PREFIX+'MqPressureMetricRecorder.java'


def require(value,message):
    if not value:
        raise ValueError(message)


def step(name,command):
    require(not (SLOT/(name+'-begin.safe.json')).exists(),'never restart unknown own step')
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    host.write(SLOT/(name+'-begin.safe.json'),dict(command=command,startUTC=start,environment=ENV))
    with (SLOT/(name+'.stdout.log')).open('xb') as out,(SLOT/(name+'.stderr.log')).open('xb') as err:
        child=subprocess.Popen(command,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,
                               stdout=out,stderr=err,close_fds=True)
        host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=command,cwd=str(SLOT),startUTC=start))
        timeout=False
        try:
            code=child.wait(timeout=180)
        except subprocess.TimeoutExpired:
            timeout=True
            child.kill()
            code=child.wait(timeout=15)
        for stream in (out,err):
            stream.flush()
            os.fsync(stream.fileno())
    value=dict(command=command,actualExit=code,timedOut=timeout,startUTC=start,
               endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               stdoutSha256=host.sha(SLOT/(name+'.stdout.log')),stderrSha256=host.sha(SLOT/(name+'.stderr.log')))
    host.write(SLOT/(name+'-exit.safe.json'),value)
    return value,(SLOT/(name+'.stdout.log')).read_text()


def assess(raw):
    require(raw['source']==common.SOURCE and raw['actualExit']==0,'exact source terminal')
    require(raw['begin']['selectedSuites']==COUNTS and raw['begin']['expectedTests']==14,'closed14/2 selection')
    require(len(raw['cases'])==14 and len({(r['classname'],r['name']) for r in raw['cases']})==14
            and all(r['result']=='PASS' and not r['nonPass'] for r in raw['cases']),'unique actual cases only')
    require(len(raw['suites'])==2 and all(row==dict(tests=COUNTS[n.rpartition('.')[2]],failures=0,errors=0,skipped=0)
            for n,row in raw['suites'].items()),'exact suites FES0')
    require(len(raw['stages'])==2 and all(r['actualExit']==0 and r['timedOut'] is False for r in raw['stages']),'actual compile and original JVM terminal')
    require(raw['begin']['fixtureHashes']=={} and raw['begin']['priorCoverageTransferred'] is False,'in-memory tests no undeclared fixture/old counter')
    require(raw['formalUpdated'] is False and raw['whole451Accepted'] is False and raw['effortPercent'] is None,'limited truth only')


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only independent post')
    require(host.sha(RUN/'manifest.safe.json')==RAW_SHA,'full immutable original JVM receipt')
    raw=json.loads((RUN/'manifest.safe.json').read_bytes())
    assess(raw)
    require(host.sha(common.COMPILE/'manifest.safe.json')==common.COMPILE_SHA,'original normal compile bound')
    snapshot=common.COMPILE/'snapshot'
    for p,h in raw['begin']['sourceHashes'].items():
        require(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h,'all original/current production bytes')
    for key in ('dependencyHashes','testSourceHashes','emptyConfigHashes'):
        require(all(host.sha(Path(p))==h for p,h in raw['begin'][key].items()),'all actual '+key+' byte pins')
    require(host.sha(RUN/'jacoco.exec')==raw['execSha256'],'original exec, not a union')
    actual_cases=[]
    for path in sorted((RUN/'xml').glob('TEST-*.xml')):
        require(raw['xmlHashes'].get(path.name)==host.sha(path),'original returned XML')
        doc=ET.parse(path).getroot()
        require(raw['suites'][doc.get('name')]=={k:int(doc.get(k,'0')) for k in ('tests','failures','errors','skipped')},'independent XML summary')
        for case in doc.findall('testcase'):
            require(not list(case),'no nonpass actual XML leaf')
            actual_cases.append((case.get('classname'),case.get('name')))
    require(set(actual_cases)=={(r['classname'],r['name']) for r in raw['cases']} and len(actual_cases)==14,'all exact XML test identities')
    command=raw['stages'][1]['command']
    require('-Dprometheus.config='+str(RUN/'empty-prometheus.properties') in command
            and raw['begin']['environment']==common.ENV,'own empty config/clean SDK initialization')
    require('-javaagent:'+str(common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid=PG8190-MQ-PROMETHEUS-GAUGE' in command,'one new actual exec identity')
    rejected=[]
    for name,change in (
        ('source-tail',lambda x:x.update(source=x['source'][:-1]+'0')),
        ('failed-case',lambda x:x['cases'][0].update(result='NOT_PASS')),
        ('duplicate-case',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),
        ('fixture-scope-change',lambda x:x['begin'].update(fixtureHashes={'unknown':'0'*64})),
        ('prior-counter-union',lambda x:x['begin'].update(priorCoverageTransferred=True)),
        ('formal-inflation',lambda x:x.update(formalUpdated=True)),
        ('timeout-normalized',lambda x:x['stages'][1].update(timedOut=True))):
        changed=copy.deepcopy(raw)
        change(changed)
        try:
            assess(changed)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('metadata negative must reject')
    os.umask(0o077)
    SLOT.mkdir()
    component=SLOT/'component'
    component.mkdir()
    target=snapshot/'src/schubert-nk-api/target/classes'
    physical={}
    for name in sorted(NAMES|{PREFIX+'package-info'}):
        destination=component/(name+'.class')
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(target/(name+'.class'),destination)
        physical[name+'.class']=host.sha(destination)
        require(host.sha(target/(name+'.class'))==physical[name+'.class'],'all actual normal class bytes')
    jdk=host.TC/'jdk-25.0.4/bin'
    libraries=[host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[host.TC/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    audit=SLOT/'audit'
    audit.mkdir()
    helper=host.ROOT/'tools/quality/architecture/ComponentCoverageAudit.java'
    cp=os.pathsep.join(str(p) for p in libraries)
    audit_stages=[]
    for name,cmd in (
        ('audit-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(audit),str(helper)]),
        ('audit-run',[str(jdk/'java'),'-cp',str(audit)+os.pathsep+cp,'ComponentCoverageAudit',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])):
        row,output=step(name,cmd)
        audit_stages.append(row)
        require(row['actualExit']==0 and row['timedOut'] is False,'actual two-Main four100 CRC/session must qualify')
    executable={}
    for line in output.splitlines():
        p=line.split('\t')
        if p[0]=='CLASS':
            executable[p[1]]=dict(crc64=p[2],counters={c.split(':')[0]:dict(missed=int(c.split(':')[1]),covered=int(c.split(':')[2])) for c in p[3:]})
    require(set(executable)==NAMES,'exact two-class executable scope')
    totals={k:dict(missed=sum(v['counters'][k]['missed'] for v in executable.values()),
                  covered=sum(v['counters'][k]['covered'] for v in executable.values())) for k in ('LINE','METHOD','CLASS','BRANCH')}
    require(all(v['missed']==0 and v['covered']>0 for v in totals.values()),'nonvacuous four100')
    source=host.ROOT/SOURCE_PATH
    require(host.sha(source)==raw['begin']['sourceHashes'][SOURCE_PATH],'exact current source')
    filelist=SLOT/'source-list.txt'
    with filelist.open('x') as stream:
        stream.write(str(source)+'\n')
    static=host.TC/'static-gates-20261015'
    rules=host.ROOT/'tools/quality/static'
    pmd_cp=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    aux=os.pathsep.join([str(component),*raw['begin']['dependencyHashes']])
    commands=[
        ('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(str(p) for p in pmd_cp),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',aux,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')]),
        ('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(filelist)])]
    project=ET.Element('project',xmlns='http://maven.apache.org/POM/4.0.0')
    for key,value in [('modelVersion','4.0.0'),('groupId','qualified.analysis'),('artifactId','mq-pressure-static'),('version','1')]:
        ET.SubElement(project,key).text=value
    dependencies=ET.SubElement(project,'dependencies')
    for n,path in enumerate(raw['begin']['dependencyHashes']):
        if path==str(common.AGENT) or path==str(common.LAUNCHER):
            continue
        dep=ET.SubElement(dependencies,'dependency')
        for key,value in [('groupId','qualified.bytebinding'),('artifactId','binding-'+str(n)),('version','1'),('scope','system'),('systemPath',path)]:
            ET.SubElement(dep,key).text=value
    build=ET.SubElement(project,'build')
    ET.SubElement(build,'directory').text=str(SLOT/'static-target')
    ET.SubElement(build,'outputDirectory').text=str(component)
    plugin=ET.SubElement(ET.SubElement(build,'plugins'),'plugin')
    for key,value in [('groupId','com.github.spotbugs'),('artifactId','spotbugs-maven-plugin'),('version','4.10.4.0')]:
        ET.SubElement(plugin,key).text=value
    config=ET.SubElement(plugin,'configuration')
    for key,value in [('effort','Max'),('threshold','Low'),('failOnError','true'),('xmlOutput','true')]:
        ET.SubElement(config,key).text=value
    pom=SLOT/'static-pom.xml'
    with pom.open('xb') as stream:
        stream.write(ET.tostring(project,encoding='utf-8',xml_declaration=True))
    commands.append(('spotbugs',[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-f',str(pom),'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']))
    static_rows={}
    for name,cmd in commands:
        row,_=step(name,cmd)
        report=SLOT/(name+'.xml') if name!='spotbugs' else SLOT/'static-target/spotbugsXml.xml'
        doc=ET.parse(report).getroot()
        findings=doc.findall('.//{*}violation') if name=='pmd' else doc.findall('.//error') if name=='checkstyle' else doc.findall('.//BugInstance')
        missing=doc.findall('.//MissingClass') if name=='spotbugs' else doc.findall('.//{*}error') if name=='pmd' else []
        static_rows[name]=dict(row,reportSha256=host.sha(report),findings=len(findings),processingErrors=len(missing))
        require(row['actualExit']==0 and not findings and not missing,'all exact-scope actual static checks zero')
    snapshot_class=target/(PREFIX+'MqPressureMetricRecorder$Snapshot.class')
    metadata,body=step('generated-metadata',[str(jdk/'javap'),'-p','-c','-s','-v',str(snapshot_class)])
    methods=['messages','queueBytes','addressMemoryBytes','addressPagedBytes','pagingActive','pageFiles','equals','hashCode','toString']
    require(metadata['actualExit']==0 and all(m+'(' in body for m in methods)
            and 'java/lang/runtime/ObjectMethods.bootstrap' in body,'record six fields/three generated contracts')
    require(any(c['name'].startswith('mqPress008') for c in raw['cases']),'current independent typed record contracts genuinely executed')
    require(all(host.sha(Path(p))==h for p,h in raw['begin']['dependencyHashes'].items())
            and all(host.sha(host.ROOT/p)==h for p,h in raw['begin']['sourceHashes'].items()),'all original bytes unchanged after analysis')
    verify(invocation)
    value=dict(actualExit=0,source=common.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        os=platform.platform(),originalManifestSha256=RAW_SHA,originalCompileSha256=common.COMPILE_SHA,
        tests=14,suites=2,sourceFiles={SOURCE_PATH:host.sha(source)},physicalClasses=physical,
        executableClasses=executable,counters=totals,actualCrcMismatch=0,actualSessions=1,
        coverageUnion=False,customExclusionsAdded=False,staticRaw=static_rows,
        staticSemantics='NEW_EXACT_TWO_EXECUTABLE_SCOPE_AND_CURRENT_SOURCE_ACTUAL_RUNTIME_AUX_BINDINGS_NOT_FULL_API',
        generatedTypes=[dict(className=PREFIX+'MqPressureMetricRecorder$Snapshot',sha256=host.sha(snapshot_class),
            metadata=metadata,methods=methods,ordinaryWitness='PG8190 MQPRESS008 fixed independent hash/text/typed equality')],
        negativeReceiptGuards=rejected,auditStages=audit_stages,auditHelperSha256=host.sha(helper),
        readerLibraryHashes={str(p):host.sha(p) for p in libraries},staticPomSha256=host.sha(pom),
        xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],actualVmActions=0,actualDatabaseActions=0,
        actualNetworkActions=0,actualServiceActions=0,productTestsExecutedByPost=0,newAccepted=0,
        formalUpdated=False,whole451Accepted=False,effortPercent=None)
    host.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=14,counters=totals,static={k:v['findings'] for k,v in static_rows.items()},
        negativeGuards=len(rejected),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
