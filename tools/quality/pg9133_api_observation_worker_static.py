"""Current finite RO attempt raw static, preserves all unclassified rows pending individual review."""
import datetime
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import pg9134_api_observation_worker_host as selected
import scoped_prometheus_post as steps
from host_tool_invocation import capture,verify

host=selected.run.host
SLOT=host.W/'pg9133-api-observation-worker-static-v1'
OUT=host.BASE/'PG9133-api-observation-worker-static-v1'
RAW=host.W/'pg9134-api-observation-worker-host-v1/manifest.safe.json'
RAW_SHA=host.sha(RAW)
MAIN={'api':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java'}

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    assert host.sha(RAW)==RAW_SHA
    raw=json.loads(RAW.read_text())
    assert raw['actualExit']==0 and raw['begin']['source']==selected.SOURCE
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_text())
    assert normal['actualExit']==0 and normal['source']==selected.SOURCE
    input_hashes=normal['begin']['inputHashes']
    sources={path:host.sha(host.ROOT/path) for path in MAIN.values()}
    assert all(input_hashes[path]==digest for path,digest in sources.items())
    dependencies=raw['begin']['dependencyHashes']
    assert all(host.sha(Path(path))==digest for path,digest in dependencies.items())
    SLOT.mkdir();steps.SLOT=SLOT
    component=SLOT/'component';component.mkdir()
    physical={}
    for role,row in normal['jars'].items():
        assert host.sha(Path(row['path']))==row['sha256']
        if role not in MAIN: continue
        name='dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker'
        with zipfile.ZipFile(row['path']) as archive:
            for suffix in ('.class',):
                member=name+suffix
                target=component/member;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.read(member))
                physical[member]=host.sha(target)
    assert len(physical)==1
    filelist=SLOT/'source-list.txt'
    filelist.write_text(''.join(str(host.ROOT/path)+'\n' for path in sorted(sources)))
    static=host.TC/'static-gates-20261015'
    rules=host.ROOT/'tools/quality/static'
    jdk=host.TC/'jdk-25.0.4/bin'
    pmd_cp=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    aux=os.pathsep.join([str(component),*dependencies])
    commands=[
      ('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(str(p) for p in pmd_cp),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',aux,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')]),
      ('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(filelist)])]
    project=ET.Element('project',xmlns='http://maven.apache.org/POM/4.0.0')
    for key,value in [('modelVersion','4.0.0'),('groupId','qualified.analysis'),('artifactId','management-static-only'),('version','1')]:
        ET.SubElement(project,key).text=value
    deps=ET.SubElement(project,'dependencies')
    for n,path in enumerate(dependencies):
        if path in (str(selected.run.AGENT),str(selected.run.LAUNCHER)): continue
        dep=ET.SubElement(deps,'dependency')
        for key,value in [('groupId','qualified.bytebinding'),('artifactId','binding-'+str(n)),('version','1'),('scope','system'),('systemPath',path)]:
            ET.SubElement(dep,key).text=value
    build=ET.SubElement(project,'build')
    ET.SubElement(build,'directory').text=str(SLOT/'static-target')
    ET.SubElement(build,'outputDirectory').text=str(component)
    plugin=ET.SubElement(ET.SubElement(build,'plugins'),'plugin')
    for key,value in [('groupId','com.github.spotbugs'),('artifactId','spotbugs-maven-plugin'),('version','4.10.4.0')]:
        ET.SubElement(plugin,key).text=value
    config=ET.SubElement(plugin,'configuration')
    for key,value in [('effort','Max'),('threshold','Low'),('xmlOutput','true'),('failOnError','true')]:
        ET.SubElement(config,key).text=value
    pom=SLOT/'pom.xml';ET.ElementTree(project).write(pom,encoding='utf-8',xml_declaration=True)
    commands.append(('spotbugs',[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-f',str(pom),'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']))
    tool_inputs=[*pmd_cp,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']
    tool_hashes={str(path):host.sha(path) for path in tool_inputs}
    rows={}
    for name,command in commands:
        receipt,_=steps.step(name,command)
        report=SLOT/(name+'.xml') if name!='spotbugs' else SLOT/'static-target/spotbugsXml.xml'
        assert report.is_file()
        doc=ET.parse(report).getroot()
        findings=doc.findall('.//{*}violation') if name=='pmd' else doc.findall('.//error') if name=='checkstyle' else doc.findall('.//BugInstance')
        errors=doc.findall('.//MissingClass') if name=='spotbugs' else doc.findall('.//{*}error') if name=='pmd' else []
        rows[name]=dict(receipt=receipt,reportSha256=host.sha(report),rawFindings=[dict(node.attrib,message=' '.join(''.join(node.itertext()).split())) for node in findings],findings=len(findings),processingErrors=len(errors))
    passed=all(not row['receipt']['timedOut'] and row['receipt']['actualExit']==0 and row['findings']==row['processingErrors']==0 for row in rows.values())
    assert all(host.sha(host.ROOT/path)==input_hashes[path] for path in MAIN.values())
    assert all(host.sha(Path(path))==digest for path,digest in tool_hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0 if passed else 1,source=selected.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,normalManifestSha256=selected.COMPILE_SHA,originalHostManifestSha256=RAW_SHA,sourceHashes=sources,physicalClasses=physical,dependencyHashes=dependencies,toolHashes=tool_hashes,static=rows,productTestsExecuted=0,ordinaryComponentPt='PG9134_CURRENT44_ONLY',actualCallerNativePt='UNRUN_HOLD',coverage=None,ptExecutionExempt=False,suppressionsAdded=False,unclassified=sum(row['findings'] for row in rows.values()),formalUpdated=False,newAccepted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=value['actualExit'],static={name:dict(findings=row['findings'],processingErrors=row['processingErrors'],exit=row['receipt']['actualExit']) for name,row in rows.items()},manifestSha256=host.sha(OUT/'manifest.json'))))
    return value['actualExit']

if __name__=='__main__':
    raise SystemExit(main())
