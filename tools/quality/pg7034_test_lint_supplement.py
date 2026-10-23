"""BUG1647: synthetic Test-compile warning rejection, no original PT repetition."""
import datetime
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg7030_monitoring_six_compile as whole

SLOT = host.W/'pg7034-test-lint-supplement-v1'
OUT = host.BASE/'PG7034-test-lint-supplement-v1'
NS = 'http://maven.apache.org/POM/4.0.0'
POM = host.ROOT/'tools/quality/harnesses/monitoring-pom.xml'
CANARY = host.ROOT/'tools/quality/canaries/test-lint/TestLintCanary.java'


def tag(name):
    return '{'+NS+'}'+name


def require(value, message):
    if not value:
        raise ValueError(message)


def config(tree):
    for plugin in tree.findall('.//{*}build/{*}plugins/{*}plugin'):
        if plugin.findtext('{*}artifactId')=='maven-compiler-plugin':
            return plugin.find('{*}configuration')
    raise ValueError('explicit compiler plugin required')


def main():
    os.umask(0o077)
    require(not SLOT.exists() and not OUT.exists(),'new-only lint fixture; no duplicate compilation')
    prior=host.W/'pg7026-monitoring-pipeline-host-v1'
    old_pom=prior/'snapshot/tools/quality/harnesses/monitoring-pom.xml'
    parent=prior/'snapshot/pom.xml'
    old=ET.fromstring(old_pom.read_bytes());new=ET.fromstring(POM.read_bytes())
    old_args=[n.text for n in config(old).findall('{*}compilerArgs/{*}arg')]
    new_args=[n.text for n in config(new).findall('{*}compilerArgs/{*}arg')]
    require(old_args==[] and new_args==['-Xlint:all','-Werror'],'specific old/new Test global gate change')
    compile_manifest=json.loads((whole.SLOT/'manifest.safe.json').read_bytes())
    require(compile_manifest['source']==whole.SOURCE and compile_manifest['actualExit']==0
            and compile_manifest['testsExecuted']==0,'genuine existing full compile-only terminal')
    full=whole.SLOT/'snapshot/src/schubert-nk-batch'
    full_tree=ET.parse(full/'pom.xml').getroot()
    require([n.text for n in config(full_tree).findall('{*}compilerArgs/{*}arg')]==['-Xlint:all','-Werror'],
            'actual full Production module already enforces Test lint')
    first=prior/'snapshot/tools/quality/harnesses/target/test-classes'
    second=full/'target/test-classes'
    prefix='dev/codex/schubert/nk/batch/monitoring'
    original_classes={p.relative_to(first).as_posix():host.sha(p) for p in (first/prefix).rglob('*.class')}
    full_classes={p.relative_to(second).as_posix():host.sha(p) for p in (second/prefix).rglob('*.class')}
    require(original_classes==full_classes and len(full_classes)>=6,
            'every actual old48 Test class byte matches strict full compile, no successful PT replay')
    SLOT.mkdir()
    ET.register_namespace('',NS)
    results=[]
    for label, root, expected in (('old',old,0),('new',new,1)):
        variant=SLOT/label;variant.mkdir()
        sources=variant/'test-source';sources.mkdir();shutil.copyfile(CANARY,sources/'TestLintCanary.java')
        root.find('{*}parent/{*}relativePath').text=str(parent)
        root.find('{*}artifactId').text='test-lint-'+label+'-fixture'
        build=root.find('{*}build')
        build.find('{*}sourceDirectory').text=str(variant/'empty-main')
        build.find('{*}testSourceDirectory').text=str(sources)
        resources=build.find('{*}testResources')
        if resources is not None:build.remove(resources)
        compiler=config(root)
        for name in ('includes','testIncludes'):
            value=compiler.find(tag(name))
            if value is not None:compiler.remove(value)
        fixture=variant/'pom.xml'
        with fixture.open('xb') as f:ET.ElementTree(root).write(f,encoding='utf-8',xml_declaration=True)
        command=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o',
          '--no-transfer-progress','-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-f',str(fixture),'test-compile']
        env=dict(PATH=str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(host.TC/'jdk-25.0.4'),
          MAVEN_USER_HOME=str(host.TC/'m2'),MAVEN_SKIP_RC='true',LANG='C.UTF-8',MAVEN_OPTS='-Xmx1g')
        begin=dict(command=command,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          expectedExit=expected,fixturePomSha256=host.sha(fixture),canarySha256=host.sha(CANARY),
          parentPomSha256=host.sha(parent),businessTestsExecuted=0)
        host.write(variant/'begin.safe.json',begin)
        with (variant/'maven.log').open('xb') as log:
            child=subprocess.Popen(command,cwd=variant,env=env,stdout=log,stderr=subprocess.STDOUT)
            host.write(variant/'process.safe.json',dict(pid=child.pid,command=command,cwd=str(variant)))
            code=child.wait();log.flush();os.fsync(log.fileno())
        terminal=dict(actualExit=code,expectedExit=expected,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          logSha256=host.sha(variant/'maven.log'),beginSha256=host.sha(variant/'begin.safe.json'))
        host.write(variant/'exit.safe.json',terminal)
        text=(variant/'maven.log').read_text()
        require(code==expected and (label=='old' or 'warnings found and -Werror specified' in text),
                'the intentional raw-type Test compiles only without the required warning gate')
        require(not list(variant.glob('target/surefire-reports/TEST-*.xml')),'no Test/Main execution in compiler canary')
        results.append(dict(label=label,begin=begin,terminal=terminal,
                            meaning='OLD_GATE_MISSED_WARNING' if label=='old' else 'EXPECTED_WARNING_REJECTION_NOT_PT_FAILURE'))
    value=dict(actualExit=0,source=whole.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      command='python3 -B tools/quality/pg7034_test_lint_supplement.py',toolSha256=host.sha(Path(__file__)),
      oldHarnessSha256=host.sha(old_pom),newHarnessSha256=host.sha(POM),canarySha256=host.sha(CANARY),
      originalFullCompileManifestSha256=host.sha(whole.SLOT/'manifest.safe.json'),
      allOriginalTestClassHashes=original_classes,testClassCount=len(original_classes),
      allOriginalTestClassBytesEqualStrictProductionCompile=True,compilerCanaryResults=results,
      businessTestsExecuted=0,original48Replayed=False,original4222Replayed=False,original44Replayed=False,
      formalUpdated=False,newAccepted=0,bug='BUG-1647',rollout='YKT-1400')
    host.write(SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,oldCanaryExit=0,newCanaryExit=1,testClassesEqual=len(original_classes),
                         businessTestsExecuted=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
