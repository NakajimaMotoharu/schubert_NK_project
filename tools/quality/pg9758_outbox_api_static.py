"""Current API Main static analysis with exact current six-Jar dependencies, never product PT."""
import datetime as dt
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg9666_pagination_static as previous
from host_tool_invocation import capture, verify

ROOT = data.ROOT
WORK = ROOT.parent / 'pgpt-runs/PG379'
TC = ROOT.parent / 'toolchain'
SOURCE = 'e598a81bb4200b4e4930278b31479ff927aa025f'
NORMAL = WORK / 'pg9750-outbox-report-six-compile-v1/snapshot'
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT = WORK / 'pg9758-outbox-api-static-v1'
OUT = BASE / 'PG9758-outbox-api-static-v1'
MODULES = ('api',)


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p, h in normal['begin']['inputHashes'].items())
    current_jars = {}
    for module in normal['jars']:
        path = Path(normal['jars'][module]['path'])
        assert path.parent == NORMAL / ('src/schubert-nk-' + module) / 'target'
        assert data.sha(path.read_bytes()) == normal['jars'][module]['sha256']
        current_jars[str(path)] = normal['jars'][module]['sha256']
    os.umask(0o077)
    SLOT.mkdir()
    previous.SLOT = SLOT
    results = {}
    all_physical = {}
    for module in MODULES:
        role = SLOT / module
        role.mkdir()
        component = role / 'component'
        component.mkdir()
        jar = Path(normal['jars'][module]['path'])
        physical = {}
        with zipfile.ZipFile(jar) as archive:
            entries = [name for name in archive.namelist() if name.endswith('.class')]
            assert entries and len(entries) == len(set(entries))
            for entry in entries:
                assert entry.startswith('dev/codex/schubert/nk/') and '..' not in Path(entry).parts
                raw = archive.read(entry)
                target = component / entry
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(raw)
                physical[entry] = data.sha(raw)
                assert entry not in all_physical
                all_physical[entry] = dict(module=module, sha256=data.sha(raw))
        cp_file = NORMAL / ('src/schubert-nk-' + module) / 'target/pgpt-test-classpath.txt'
        dependencies = dict(current_jars)
        removed_internal = []
        for text in cp_file.read_text().strip().split(os.pathsep):
            path = Path(text)
            if '/dev/codex/schubert/' in text:
                removed_internal.append(text)
                continue
            if path.is_relative_to(NORMAL / 'src'):
                continue
            assert path.is_relative_to(TC / 'm2/repository') and path.is_file() and not path.is_symlink() and path.suffix == '.jar'
            dependencies[str(path)] = data.sha(path.read_bytes())
        assert len(dependencies) > 6
        project = ET.Element('project', xmlns='http://maven.apache.org/POM/4.0.0')
        for key, value in [('modelVersion', '4.0.0'), ('groupId', 'qualified.analysis'), ('artifactId', 'pagination-static-' + module), ('version', '1')]:
            ET.SubElement(project, key).text = value
        deps = ET.SubElement(project, 'dependencies')
        for number, path in enumerate(sorted(dependencies)):
            dep = ET.SubElement(deps, 'dependency')
            for key, value in [('groupId', 'qualified.bytebinding'), ('artifactId', 'binding-' + str(number)),
                               ('version', '1'), ('scope', 'system'), ('systemPath', path)]:
                ET.SubElement(dep, key).text = value
        build = ET.SubElement(project, 'build')
        ET.SubElement(build, 'directory').text = str(role / 'static-target')
        ET.SubElement(build, 'outputDirectory').text = str(component)
        plugin = ET.SubElement(ET.SubElement(build, 'plugins'), 'plugin')
        for key, value in [('groupId', 'com.github.spotbugs'), ('artifactId', 'spotbugs-maven-plugin'), ('version', '4.10.4.0')]:
            ET.SubElement(plugin, key).text = value
        config = ET.SubElement(plugin, 'configuration')
        for key, value in [('effort', 'Max'), ('threshold', 'Low'), ('xmlOutput', 'true'), ('failOnError', 'true')]:
            ET.SubElement(config, key).text = value
        pom = role / 'pom.xml'
        ET.ElementTree(project).write(pom, encoding='utf-8', xml_declaration=True)
        receipt = previous.step(module + '-spotbugs', [str(TC / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
            '-o', '--no-transfer-progress', '-Dmaven.repo.local=' + str(TC / 'm2/repository'), '-f', str(pom),
            'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'], role, timeout=300)
        report = role / 'static-target/spotbugsXml.xml'
        root = ET.parse(report).getroot()
        aux = [node.text for node in root.findall('Project/AuxClasspathEntry')]
        assert all(isinstance(path, str) and '/m2/repository/dev/codex/schubert/' not in path for path in aux)
        assert set(aux) == set(dependencies)
        assert [node.text for node in root.findall('Project/Jar')] == [str(component)]
        assert all(data.sha((component / name).read_bytes()) == h for name, h in physical.items())
        assert all(data.sha(Path(path).read_bytes()) == h for path, h in dependencies.items())
        results[module] = dict(receipt=receipt, findings=len(root.findall('.//BugInstance')),
            processingErrors=len(root.findall('.//MissingClass')) + len(root.findall('.//Error')),
            reportSha256=data.sha(report.read_bytes()), physicalClasses=physical, dependencyHashes=dependencies,
            sourceClasspathSha256=data.sha(cp_file.read_bytes()), removedOldInternalM2Entries=removed_internal,
            actualAuxExactlyExplicitInputs=True, pomSha256=data.sha(pom.read_bytes()))
        print(json.dumps(dict(module=module, actualExit=receipt['actualExit'], findings=results[module]['findings'],
            processingErrors=results[module]['processingErrors'])), flush=True)
    assert all_physical and all(p.startswith('dev/codex/schubert/nk/api/') for p in all_physical)
    passed = all(r['receipt']['actualExit'] == 0 and not r['receipt']['timedOut'] and r['findings'] == r['processingErrors'] == 0 for r in results.values())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p, h in normal['begin']['inputHashes'].items())
    assert not list(NORMAL.glob('src/*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    for module in MODULES:
        with (OUT / ('current-spotbugs-' + module + '.xml')).open('xb') as stream:
            stream.write((SLOT / module / 'static-target/spotbugsXml.xml').read_bytes())
    data.write(OUT / 'manifest.json', dict(actualExit=0 if passed else 1, source=SOURCE, invocation=invocation,
        timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), results=results, allInputMainClasses=len(all_physical),
        scope='CURRENT_API_MAIN_ALL_CLASSES_SPOTBUGS_ONLY',
        productTestsExecuted=0, suppressionsAdded=False, exclusionsAdded=False, oldM2ArtifactsModified=False,
        coverage=None, wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
