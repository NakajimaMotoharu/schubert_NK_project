"""Read synthetic controller class files with ArchUnit. The fixture code is never run."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
TOOL = Path('tools/quality/architecture/ModuleDependencyAudit.java')
TC = Path('/home/mini/codex/project1/work/toolchain')
JAVA = TC / 'jdk-25.0.4/bin/java'
ARCH = TC / 'architecture/archunit-1.4.2/archunit-1.4.2.jar'
SLF = TC / 'm2/repository/org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar'
PINS = {
    ARCH: '6d8adf69a3f109ebe1b395764feb07f919e9e0e2ab5e2ea141d2e6251ba7d17f',
    SLF: '44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55',
}
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
P = 'dev.codex.schubert.nk.'
WEB = P + 'web.canary.'
RULES = frozenset({'MODULE_EDGES', 'FRAMEWORK_FENCES', 'CONTROLLER_BOUNDARY',
                   'REPOSITORY_DIRECTION', 'INTERNAL_OWNER'})
STUBS = {
    'org.springframework.jms.core.JmsTemplate': 'public final class JmsTemplate {}',
    'jakarta.jms.Message': 'public interface Message {}',
    'javax.jms.Message': 'public interface Message {}',
    'org.springframework.web.bind.annotation.RestController':
        '@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface RestController {}',
    'org.springframework.stereotype.Controller':
        '@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface Controller {}',
    WEB + 'SafeFacade': 'public final class SafeFacade { private jakarta.jms.Message message; public void send() {} }',
}
# Test ID, own type name, Java body, independently specified direct violations, original detections.
CASES = [
    ('001', 'FacadeController',
     'public void handle(SafeFacade facade) { facade.send(); }', (), ()),
    ('002', 'HttpController',
     'public void stream(java.io.OutputStream output) throws java.io.IOException { output.write(7); }', (), ()),
    ('003', 'JdbcController', 'public java.sql.Connection connection;',
     ('java.sql.Connection',), ('java.sql.Connection',)),
    ('004', 'StorageController', f'public {P}storage.KnownValue value;',
     (P + 'storage.KnownValue',), (P + 'storage.KnownValue',)),
    ('005', 'SpringJmsController', 'public org.springframework.jms.core.JmsTemplate template;',
     ('org.springframework.jms.core.JmsTemplate',), ()),
    ('006', 'JakartaController', 'public jakarta.jms.Message value;',
     ('jakarta.jms.Message',), ()),
    ('007', 'JavaxController', 'public javax.jms.Message value;',
     ('javax.jms.Message',), ()),
    ('008', 'NioFilesController',
     'public boolean exists(java.nio.file.Path input) { return java.nio.file.Files.exists(input); }',
     ('java.nio.file.Files',), ()),
    ('009', 'FileChannelController',
     'public long length(java.nio.channels.FileChannel file) throws java.io.IOException { return file.size(); }',
     ('java.nio.channels.FileChannel',), ()),
    ('010', 'LegacyFileController', 'public java.io.File fixture() { return new java.io.File("synthetic"); }',
     ('java.io.File',), ()),
    ('011', 'AnnotatedEndpoint', '@org.springframework.web.bind.annotation.RestController '
     '# public java.nio.file.Path fixture() { return java.nio.file.Path.of("synthetic"); }',
     ('java.nio.file.Path',), ()),
    ('012', 'NamedHandler', '@org.springframework.stereotype.Controller # public javax.jms.Message value;',
     ('javax.jms.Message',), ()),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def dump(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', *args], timeout=35)


def fixture_sources(base):
    rows = {P + m + '.KnownValue': 'public final class KnownValue {}' for m in MODULES}
    rows[P + 'protocol.KnownValue'] = (
        'public final class KnownValue { static { System.setProperty("nk.archunit.canary.initialized","true"); } }'
    )
    rows.update(STUBS)
    for _, clazz, body, _, _ in CASES:
        header, _, member = body.partition('#') if '#' in body else ('', '', body)
        rows[WEB + clazz] = f'{header} public final class {clazz} {{ {member} }}'
    result = {}
    for name, body in sorted(rows.items()):
        path = base / (name.replace('.', '/') + '.java')
        path.parent.mkdir(exist_ok=True, parents=True)
        text = 'package ' + name.rsplit('.', 1)[0] + ';\n' + body + '\n'
        path.write_text(text)
        result[name] = path
    return result


def execute(out, name, command, cwd):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'},
                            check=False, timeout=100)
    (out / (name + '.stdout.txt')).write_bytes(result.stdout)
    (out / (name + '.stderr.txt')).write_bytes(result.stderr)
    status = dict(actualExit=result.returncode, stdout=pin(out / (name + '.stdout.txt')),
                  stderr=pin(out / (name + '.stderr.txt')), command=[str(item) for item in command])
    dump(out / (name + '-exit.json'), status)
    return status, result.stdout.decode()


def archive(path, names, classes):
    with zipfile.ZipFile(path, 'x') as jar:
        for name in sorted(names):
            entry = name.replace('.', '/') + '.class'
            jar.write(classes / entry, entry)


def check_result(output, status, mode, expected_counts):
    lines = [line.split('\t') for line in output.splitlines()]
    count = sum(expected_counts.values())
    assert [row for row in lines if row[0] == 'ARCHUNIT'] == [['ARCHUNIT', '1.4.2', str(count), str(count)]]
    assert {r[1]: int(r[2]) for r in lines if r[0] == 'MODULE'} == expected_counts
    inspected, = (r for r in lines if r[0] == 'INSPECTED')
    assert int(inspected[1]) > 0 and int(inspected[2]) > 0
    found = {tuple(r[1:]) for r in lines if r[0] == 'FINDING'}
    observed = {r[1]: int(r[2]) for r in lines if r[0] == 'RULE'}
    expected = {
        ('CONTROLLER_BOUNDARY', WEB + clazz, target)
        for _, clazz, _, new, old in CASES for target in (old if mode == 'before' else new)
    }
    assert len(observed) == len(RULES) and set(observed) == RULES
    assert sum(observed.values()) == len(found) and found == expected, (found, expected)
    assert status == 1 and observed['CONTROLLER_BOUNDARY'] == len(expected)
    assert all(row[0] in {'ARCHUNIT', 'MODULE', 'RULE', 'FINDING', 'INSPECTED'} for row in lines)
    return [
        dict(testId='PT-F02-ARCH-' + id_, origin=WEB + clazz, expected=list(new),
             actual=sorted(row[2] for row in found if row[1] == WEB + clazz),
             correct=tuple(sorted(row[2] for row in found if row[1] == WEB + clazz)) == tuple(sorted(new)))
        for id_, clazz, _, new, _ in CASES
    ]


def main(mode):
    assert mode in ('before', 'after')
    start = json.loads(next(PLAN.glob('576_F02*.json')).read_text())
    source = start['values']['source'] if mode == 'before' else git('rev-parse', 'HEAD').decode().strip()
    content = git('show', f'{source}:{TOOL}')
    if mode == 'before':
        assert sha(content) == start['values']['oracleReferences'][0]['sha256']
    assert all(pin(path)['sha256'] == checksum for path, checksum in PINS.items())
    out = OPS / ('PG40064-f02-controller-fences-archunit-v1' if mode == 'before'
                 else 'PG40066-f02-controller-fences-archunit-v2')
    ram = Path('/dev/shm')
    limits = os.statvfs(ram)
    assert limits.f_bavail * limits.f_frsize >= 128 * 1024 * 1024
    out.mkdir()
    with tempfile.TemporaryDirectory(prefix='pgpt-controller-archunit-', dir=ram) as temporary:
        slot = Path(temporary)
        original = slot / TOOL.name
        original.write_bytes(content)
        classes, tool_classes = slot / 'fixtures', slot / 'tool'
        java_sources = fixture_sources(slot / 'source')
        base_cp = os.pathsep.join(map(str, (ARCH, SLF)))
        receipts = {}
        opt = ['--release', '25', '-Xlint:all', '-Werror', '-proc:none']
        commands = {
            'tool-compile': [JAVA.with_name('javac'), *opt, '-cp', base_cp, '-d', tool_classes, original],
            'fixture-compile': [JAVA.with_name('javac'), *opt, '-d', classes, *java_sources.values()],
        }
        for name, command in commands.items():
            receipts[name], _ = execute(out, name, command, slot)
            assert receipts[name]['actualExit'] == 0, name
        jars = []
        counts = {}
        for module in MODULES:
            names = [P + module + '.KnownValue']
            if module == 'web':
                names.extend(STUBS)
                names.extend(WEB + label[1] for label in CASES)
            counts[module] = len(names)
            jar = slot / (module + '.jar')
            archive(jar, names, classes)
            jars.append(dict(module=module, classes=names, sha256=pin(jar)['sha256']))
        cp = os.pathsep.join((str(tool_classes), base_cp))
        command = [JAVA, '-cp', cp, 'ModuleDependencyAudit',
                   *(module + '=' + str(slot / (module + '.jar')) for module in MODULES)]
        receipts['audit'], output = execute(out, 'audit', command, slot)
        cases = check_result(output, receipts['audit']['actualExit'], mode, counts)
        passed = sum(row['correct'] for row in cases)
        assert passed == (4 if mode == 'before' else 12)
        manifest = dict(actualExit=0, childArchUnitExit=receipts['audit']['actualExit'],
                        source=source, productionCoreMain=start['values']['productionCoreMain'],
                        toolInput=dict(path=str(TOOL), sha256=sha(content)), receipts=receipts,
                        syntheticArtifacts=jars, tested=len(cases), correct=passed, incorrect=len(cases) - passed,
                        cases=cases, measurement='STATIC_ARCHITECTURE_CANARY_ONLY', productTests=0,
                        productClassesLoaded=0, productJarsScanned=0, wholeF02Accepted=False,
                        canonicalDesign=git('rev-parse', 'origin/main').decode().strip(),
                        terminalAtUTC=timestamp(), verifier=pin(Path(__file__)),
                        externalOperations=0)
    dump(out / 'manifest.json', manifest)
    print(passed, len(cases), pin(out / 'manifest.json'))


if __name__ == '__main__':
    main(sys.argv[1])
