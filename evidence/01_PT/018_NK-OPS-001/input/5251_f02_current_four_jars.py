"""Package four already qualified Main outputs and verify their exact archive contents."""
from pathlib import Path
import hashlib
import runpy
import shutil
from zipfile import ZipFile

HERE = Path(__file__)
helpers = runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
git, read, ref, save, step, utc = (helpers[k] for k in ('git', 'read', 'ref', 'save', 'step', 'utc'))
start = next(helpers['D'].glob('544_*'))
out = helpers['E'] / 'PG39980-f02-current-four-production-jars-v1'
work = Path.cwd().parent / 'pgpt-runs/PG379' / out.name.lower()
modules = ('protocol', 'storage', 'bootstrap', 'batch')
version = '0.1.0-SNAPSHOT'


def inventory(path):
    return {p.relative_to(path).as_posix(): ref(p)['sha256'] for p in path.rglob('*') if p.is_file()}


def verify_jar(path, artifact, classes, pom):
    with ZipFile(path) as jar:
        names = [entry.filename for entry in jar.infolist() if not entry.is_dir()]
        assert jar.testzip() is None and len(names) == len(set(names))
        meta = f'META-INF/maven/dev.codex.schubert/{artifact}/'
        expected = set(classes) | {'META-INF/MANIFEST.MF', meta + 'pom.xml', meta + 'pom.properties'}
        assert set(names) == expected and jar.read(meta + 'pom.xml') == pom
        properties = dict(line.split('=', 1) for line in jar.read(meta + 'pom.properties').decode().splitlines()
                          if line and not line.startswith('#'))
        assert properties == dict(artifactId=artifact, groupId='dev.codex.schubert', version=version)
        for name, expected_hash in classes.items():
            binary = jar.read(name)
            assert binary.startswith(b'\xca\xfe\xba\xbe') and int.from_bytes(binary[6:8], 'big') == 69
            assert hashlib.sha256(binary).hexdigest() == expected_hash
    return dict(artifact=ref(path), coordinates=properties, classes=len(classes),
                nonClassEntries=len(names)-len(classes), crcOK=True, classMajor=69, allClassHashesMatch=True)


def main():
    recorded = read(start)['values']
    assert git('rev-parse', 'HEAD').decode().strip() == recorded['source']
    pins = recorded['oracleReferences']
    assert all(ref(Path(pin['path'])) == pin for pin in pins)
    prior = read(pins[0]['path'])
    core = recorded['productionCoreMain']
    assert prior['sourceCore'] == core and prior['actualExit'] == 0
    core_to_head = git('diff', '--name-only', core, 'HEAD', '--', 'src', 'pom.xml').decode().splitlines()
    assert core_to_head == [
        'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/'
        'ServiceDatabaseSourcePortTest.java'
    ]
    assert not git('diff', '--name-only', 'HEAD', '--', 'src', 'pom.xml')
    assert shutil.disk_usage(Path.cwd()).free >= 128 * 1024**2
    assert not work.exists() and not out.exists()
    poms = {k: git('show', f'{core}:{k}') for k in prior['sourceInputs'] if k.endswith('pom.xml')}
    assert len(poms) == 8
    assert all(Path(k).read_bytes() == raw and hashlib.sha256(raw).hexdigest() == prior['sourceInputs'][k]
               for k, raw in poms.items())
    tc = helpers['TC']
    plugin = tc/'m2/repository/org/apache/maven/plugins/maven-jar-plugin/3.4.1/maven-jar-plugin-3.4.1.jar'
    assert ref(helpers['JDK']/'java')['sha256'] == prior['tools']['javaSha256']
    assert ref(helpers['MAVEN'])['sha256'] == prior['tools']['mavenLauncherSha256']
    folders = {module: Path(f'src/schubert-nk-{module}') for module in modules}
    inputs = prior['physicalClassHashes']
    for module, folder in folders.items():
        assert inventory(Path(prior['cwd'])/folder/'target/classes') == inputs[module]
        assert not git('ls-tree', '-r', '--name-only', core, '--', str(folder/'src/main/resources'))
    assert sum(map(len, inputs.values())) == 1102

    work.mkdir(mode=0o700)
    out.mkdir()
    for name, raw in poms.items():
        dest = work/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    for module, folder in folders.items():
        path = work/folder/'target/classes'
        shutil.copytree(Path(prior['cwd'])/folder/'target/classes', path)
        assert inventory(path) == inputs[module]

    command = prior['command'][:-2] + ['org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar']
    assert prior['command'][-2:] == ['-am', 'compile']
    save(out/'begin.json', dict(sourceCore=core, gitHead=recorded['source'], priorCompile=pins[0],
         plugin=ref(plugin), poms={name: ref(work/name)['sha256'] for name in poms},
         selectedModules=list(modules), command=command, classes=1102, coreToHeadTestOnly=core_to_head,
         applicationExecuted=False, testsExecuted=0))
    execution = step('maven-jar', command, work, out, 120)
    maven_log = Path(execution['log']['path']).read_text()
    packaged = {}
    if execution['actualExit'] == 0:
        assert maven_log.count('Building jar:') == 4 and 'BUILD SUCCESS' in maven_log
        assert not any(marker in maven_log for marker in (':compile (', ':testCompile (', ':test ('))
        for module, folder in folders.items():
            output = work/folder/'target'
            name = folder.name
            assert inventory(output/'classes') == inputs[module]
            jars = list(output.glob('*.jar'))
            assert len(jars) == 1 and jars[0].name == f'{name}-{version}.jar'
            packaged[module] = verify_jar(jars[0], name, inputs[module], poms[str(folder/'pom.xml')])
    save(out/'manifest.json', dict(sourceCore=core, gitHead=recorded['source'], checkId='PG39980',
         wbs='WBS-F02-a', execution=execution, actualExit=execution['actualExit'], terminalAtUTC=utc(),
         sourceMain=prior['mainCounts'], inputClassCount=1102, jars=packaged,
         mavenPlugin=ref(plugin), reusableEvidence=pins, verifier=ref(HERE), testsExecuted=0,
         preparationAttempts=[dict(actualExit=1, reason='Initial source guard also included the separate unit test',
                                   mavenStarted=False)],
         untestedModules=['api','web'], wholeF02Accepted=False, whole451Accepted=False))
    print(execution['actualExit'], {k:v['classes'] for k,v in packaged.items()})
    return execution['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
