"""Fresh source-only compilation/null/SpotBugs for declared private locks; no PT execution."""
import datetime
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pg5938_private_lock93_plan import ROOT, TC, BASE, W, sha

PLAN = BASE/'PG5938-private-lock93-plan-v1/manifest.json'
PLAN_SHA = '0f0100343ccfb402be11dfb829ae33120a8a5eea055b6798ad4d8d5c943fccc2'
OLD = '682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b'
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
SLOT = 'pg5940-private-lock-compile-v1'


def plan():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('immutable declaration before PG')
    return json.loads(PLAN.read_bytes())


def validate_source(source, root):
    declaration = plan(); paths = {r['path'] for r in declaration['sourcePlans']}
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changed) != paths or len(paths) != 33 or subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('only declared33 Main; Test/oracle/config/gate unchanged')
    before = json.loads((W/'pg5914-api-expression-static-v1/manifest.safe.json').read_bytes())
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
    expected = dict(before['allSourceHashes'])
    for row in declaration['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('original declared Main hash')
        expected[row['path']] = row['predictedAfterSha256']
    if actual != expected or len(actual) != 851:
        raise ValueError('exact all851 source and33 predetermined after hashes')
    return actual


def physical_changes(old, new):
    declaration = plan(); required = set(declaration['requiredClassKeys'])
    owners = {r['module']+':'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in declaration['sourcePlans']}
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    if len(old) != 1666 or set(new) != set(old) or not required <= changed or any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changed):
        raise ValueError('all1666/required34 actual targets/only declared source-owner nested/debug changes')
    return sorted(changed)


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('committed clean source/operator before compilation')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    source_hashes = validate_source(source, ROOT)
    os.umask(0o077); out = W/SLOT; out.mkdir(mode=0o700)
    archive = out/'source.tar'
    with archive.open('xb') as f:
        subprocess.run(['git', 'archive', source, 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization', 'tools/quality/static'], cwd=ROOT, stdout=f, check=True)
        f.flush(); os.fsync(f.fileno())
    snapshot = out/'source'; snapshot.mkdir(mode=0o700)
    with tarfile.open(archive) as f:
        f.extractall(snapshot, filter='data')
    validate_source(source, snapshot)
    # No exec/antrun/Failsafe plugin, shell/service or test runner is bound by these POMs.
    for p in [snapshot/'pom.xml', *snapshot.glob('src/*/pom.xml')]:
        tree = ET.parse(p).getroot(); ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        plugins = {x.text for x in tree.findall('.//m:plugin/m:artifactId', ns)}
        if not plugins <= {'maven-enforcer-plugin', 'spotless-maven-plugin', 'maven-compiler-plugin', 'maven-surefire-plugin', 'jacoco-maven-plugin', 'spotbugs-maven-plugin', 'maven-jar-plugin'}:
            raise ValueError('POM plugin side-effects require explicit review')
    base = [str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'), '-B', '-o', '-ntp', '-Dmaven.repo.local='+str(TC/'m2/repository'), '-pl', ','.join('src/schubert-nk-'+m for m in MODULES), '-am']
    commands = [base+['spotless:check'], base+['-DskipTests', 'package', 'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    env = {k: v for k, v in os.environ.items() if k not in ('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS', 'CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'), PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'], MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out), TZ='Asia/Tokyo')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(); codes = []
    for i, command in enumerate(commands):
        with (out/('phase-'+str(i)+'.private.log')).open('xb') as log:
            codes.append(subprocess.run(command, cwd=snapshot, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900).returncode)
            log.flush(); os.fsync(log.fileno())
        if codes[-1]:
            break
    if codes != [0, 0]:
        raise ValueError('compile-only failure retained in original phase logs; no PT success')
    if any(snapshot.glob('src/*/target/surefire-reports/TEST-*.xml')):
        raise ValueError('compile-only must not execute PT')
    physical = {m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix(): sha(p) for m in MODULES for p in (snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    old = json.loads((W/'pg5914-api-expression-static-v1/manifest.safe.json').read_bytes())
    changed = physical_changes(old['auxClassHashes'], physical)
    static = {m: len(ET.parse(snapshot/('src/schubert-nk-'+m+'/target/spotbugsXml.xml')).getroot().findall('BugInstance')) for m in MODULES}
    if any(static.values()) or validate_source(source, snapshot) != source_hashes or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() != source:
        raise ValueError('allsource/compiled null/type/static fixed0')
    value = dict(actualExit=0, source=source, priorProductionSource=OLD, startedUTC=started, completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 commands=commands, phaseExits=codes, archiveSha256=sha(archive), allSourceHashes=source_hashes, allPhysicalMainSha256=physical,
                 changedPhysicalClasses=changed, physicalMain=1666, requiredTargetClasses=plan()['requiredClassKeys'], staticSixModules=static,
                 testsExecuted=0, skippedTestsAreNotPass=True, ptAlternativeCompleted=0, formalAccepted=False, vmActions=0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, sourceFiles=851, physicalMain=1666, changedPhysicalClasses=changed, staticSixModules=static, testsExecuted=0, manifestSha256=sha(out/'manifest.safe.json'))))


if __name__ == '__main__':
    main()
