"""One ordinary offline current Protocol module verify, source-bound full106/23, no other projects."""
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg6966_chr_adapter_host as host
import pg9666_pagination_static as runner
from host_tool_invocation import capture,verify

SOURCE = 'a75a490666973b2d1fc9b4901290074aa1c32a0f'
NORMAL_PIN = '44e2344df9c30086f80a2fcecb59103373f79e4feed09e0915e1da0bb560f5ae'
OUT = data.BASE/'PG13392-protocol-module-verify-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13392-protocol-module-verify-v1'
SESSION = 'PG13392-PROTOCOL-CURRENT-WHOLE106'
MODULE = 'src/schubert-nk-protocol'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13362-api-maintenance-literal-v1/manifest.json',NORMAL_PIN)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT) == b''
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in normal['begin']['dependencyJarHashes'].items())
    poms = {name:data.sha((data.ROOT/name).read_bytes()) for name in ['pom.xml',MODULE+'/pom.xml']}
    pom = ET.parse(data.ROOT/MODULE/'pom.xml').getroot();dependencies = [x.findtext('{*}groupId')+':'+x.findtext('{*}artifactId') for x in pom.findall('./{*}dependencies/{*}dependency')]
    assert dependencies == ['org.jspecify:jspecify','org.junit.jupiter:junit-jupiter']
    limits = pom.findall('.//{*}limits/{*}limit');assert len(limits) == 4 and {x.findtext('{*}counter') for x in limits} == {'LINE','METHOD','CLASS','BRANCH'} and all(x.findtext('{*}minimum') == '1.0' for x in limits)
    assert not pom.findall('.//{*}excludes') and not pom.findall('.//{*}skipTests')
    SLOT.mkdir();archive = SLOT/'source.tar'
    with archive.open('xb') as stream:subprocess.run(['git','archive','--format=tar',SOURCE,'pom.xml','.mvn','mvnw','src','program/characterization/pom.xml'],cwd=data.ROOT,stdout=stream,check=True)
    snapshot = SLOT/'snapshot';snapshot.mkdir();host.safe_extract(archive,snapshot);assert host.inventory(snapshot) == hashes
    catalog = {};test_sources = {};root = snapshot/MODULE/'src/test/java'
    for path in sorted(root.rglob('*Test.java')):
        text = path.read_text();methods = re.findall(r'@Test\s+(?:public\s+)?void\s+(\w+)\s*\(',text);assert methods and len(methods) == len(set(methods)) == text.count('@Test')
        assert not any(v in text for v in ['@Disabled','@BeforeAll','@TempDir','@ParameterizedTest','ProcessBuilder','DriverManager','JMSContext','TemporaryInfrastructureException','java.nio.file.','java.net.','javax.crypto.'])
        name = str(path.relative_to(root).with_suffix('')).replace('/','.');catalog[name] = methods;test_sources[str(path.relative_to(snapshot))] = data.sha(path.read_bytes())
    assert len(catalog) == 23 and sum(map(len,catalog.values())) == 106
    maven = runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';jdk = runner.TC/'jdk-25.0.4'
    command = [str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-f',MODULE+'/pom.xml','-Djacoco.sessionId='+SESSION,'-Djacoco.append=false','verify']
    runner.SLOT = SLOT
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),invocation=invocation,normalManifestSha256=NORMAL_PIN,archiveSha256=data.sha(archive.read_bytes()),inputHashes=hashes,pomHashes=poms,command=command,environment=runner.ENV,expectedCatalog=catalog,testSourceHashes=test_sources,expectedTests=106,expectedSuites=23,dependencies=dependencies,toolHashes={str(p):data.sha(p.read_bytes()) for p in [maven,jdk/'bin/java',jdk/'bin/javac']},dependencyJarHashes=normal['begin']['dependencyJarHashes'],actualVmActions=0,actualDatabaseActions=0,actualJmsActions=0,rootMainInvoked=False,newTestIds=0,priorCoverageTransferred=False))
    stage = runner.step('protocol-verify',command,snapshot,timeout=600);target = snapshot/MODULE/'target';suites = {};cases = [];xmls = {}
    for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        doc = ET.parse(path).getroot();name = doc.get('name');assert name in catalog and name not in suites
        suites[name] = {key:int(doc.get(key,'0')) for key in ['tests','failures','errors','skipped']};xmls[path.name] = data.sha(path.read_bytes())
        for case in doc.findall('testcase'):
            invalid = [node.tag for node in case if node.tag not in ['system-out','system-err']]
            cases.append(dict(classname=case.get('classname'),rawName=case.get('name'),method=case.get('name').removesuffix('()'),result='NOT_PASS' if invalid else 'PASS',nonPass=invalid))
    counters = {};report = target/'site/jacoco/jacoco.xml'
    if report.is_file():counters = {x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in ET.parse(report).getroot().findall('counter') if x.get('type') in ['LINE','METHOD','CLASS','BRANCH']}
    expected = {(name,method) for name,methods in catalog.items() for method in methods};observed = {(r['classname'],r['method']) for r in cases}
    pt_complete = len(cases) == len(observed) == 106 and observed == expected and all(r['result'] == 'PASS' for r in cases) and len(suites) == 23 and all(r == dict(tests=len(catalog[name]),failures=0,errors=0,skipped=0) for name,r in suites.items())
    reports = {str(path.relative_to(target)):data.sha(path.read_bytes()) for path in [target/'jacoco.exec',report,target/'spotbugsXml.xml'] if path.is_file()}
    main_classes = {str(path.relative_to(target/'classes')):data.sha(path.read_bytes()) for path in sorted((target/'classes').rglob('*.class'))}
    with zipfile.ZipFile(normal['jars']['protocol']['path']) as jar:normal_classes = {name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')}
    physical_equal = main_classes == normal_classes and len(main_classes) == 176
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == sha for p,sha in hashes.items());verify(invocation);OUT.mkdir()
    for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        # Surefire properties contain only the clean own JVM environment; copies are reviewed by public scan.
        with (OUT/path.name).open('xb') as stream:stream.write(path.read_bytes())
    if report.is_file():
        with (OUT/'jacoco.xml').open('xb') as stream:stream.write(report.read_bytes())
    if (target/'spotbugsXml.xml').is_file():
        with (OUT/'spotbugs.xml').open('xb') as stream:stream.write((target/'spotbugsXml.xml').read_bytes())
    value = dict(actualExit=stage['actualExit'],source=SOURCE,invocation=invocation,stage=stage,beginSha256=data.sha((SLOT/'begin.safe.json').read_bytes()),normalManifestSha256=NORMAL_PIN,expectedCatalog=catalog,sourceInputHashes=hashes,testSourceHashes=test_sources,suites=suites,cases=cases,xmlHashes=xmls,ptComplete=pt_complete,productTestsExecuted=len(cases),expectedTests=106,expectedSuites=23,coverageCounters=counters,reports=reports,mainPhysical=len(main_classes),mainClassHashes=main_classes,normalMainClassHashes=normal_classes,allProtocolMainByteIdentical=physical_equal,coverageSessionExpected=SESSION,newTestIds=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None,qualification='RAW_ORIGINAL_MODULE_RESULT_INDEPENDENT_POST_PENDING',priorCoverageTransferred=False)
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=stage['actualExit'],tests=len(cases),suites=len(suites),ptComplete=pt_complete,counters=counters,mainPhysical=len(main_classes),normalMainByteEqual=physical_equal,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(stage['actualExit'])

if __name__ == '__main__':main()
