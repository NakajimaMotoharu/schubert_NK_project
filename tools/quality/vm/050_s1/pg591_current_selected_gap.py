"""Current private gap coordinates; frozen successful host + current native + selected PG590."""
import hashlib
import json
import os
import pathlib
import subprocess
import xml.etree.ElementTree as ET

W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
REPO = pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
JAVA = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    selected = W / 'pg590-cleanup-expiry-db-v1'
    assert sha(selected / 'manifest.safe.json') == '79abf4caf1be1284f78d9f0e660d1eaf6c9de03b75bd49e8c8c66c0a3b1d1f50'
    admitted = json.loads((selected / 'manifest.safe.json').read_bytes())
    assert admitted['actualExit'] == 0 and admitted['mainClassBytesEqualInstalledCurrentPG585'] == 1600
    host = W / 'pg585-access-reactor-v3'
    assert sha(host / 'manifest.safe.json') == '96b0f247b5770bed3b9777d336f3f2bdc0d916281811d7a880ab6ae604d41f6a'
    full = json.loads((host / 'manifest.safe.json').read_bytes())
    cp = [str(W / 'pg562-current-native-gap-v1/classes')]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar', 'org/jacoco/org.jacoco.report/0.8.15/*.jar',
                    'org/ow2/asm/asm/9.10.1/*.jar', 'org/ow2/asm/asm-tree/9.10.1/*.jar', 'org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths = list(REPO.glob(pattern))
        assert len(paths) == 1
        cp.append(str(paths[0]))
    modules = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
    data = [host / module / 'jacoco.exec' for module in modules]
    for module, path in zip(modules, data):
        assert sha(path) == full['moduleResults'][module]['execSha256']
    for dirname, field, count in (('pg561-current-native-v2', 'currentNativeFiles', 9),
                                  ('pg581-current-eighteen-native-v3', 'newFiles', 8)):
        base = W / dirname
        manifest = json.loads((base / 'manifest.safe.json').read_bytes())
        assert len(manifest[field]) == count
        for index, item in enumerate(manifest[field]):
            path = base / (str(index) + '.exec')
            assert sha(path) == item['sha256']
            data.append(path)
    boot = W / 'pg571-current-ten-native-v2/bootstrap.exec'
    assert sha(boot) == '0f8869c6ef5e43f9ce858bf08a7da0cc161dc51b329b2209ef62a5092ed1ad9e'
    data.extend([boot, selected / 'selected-batch.exec'])
    assert len(data) == 25 and sha(data[-1]) == admitted['selectedExecSha256']
    target = W / 'pg591-current-selected-gap-v1'
    assert not os.path.lexists(target)
    target.mkdir(mode=0o700)
    result = {'source': admitted['productionSource'], 'selectedSource': admitted['operatorSource'],
              'formalAccepted': False, 'counters': {}, 'gaps': {}, 'xmlHashes': {}}
    for module in modules:
        xml = target / (module + '.xml')
        process = subprocess.run([JAVA, '-cp', ':'.join(cp), 'NativeCoverageXml471',
                                  str(host / module / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')),
                                  str(xml), *map(str, data)], capture_output=True, timeout=45)
        assert process.returncode == 0 and not process.stderr
        root = ET.parse(xml).getroot()
        result['counters'][module] = {c.attrib['type']: int(c.attrib['missed']) for c in root.findall('counter')}
        result['xmlHashes'][module] = sha(xml)
        entries = []
        for cls in root.findall('./package/class'):
            missed = {c.attrib['type']: int(c.attrib['missed']) for c in cls.findall('counter')}
            if any(missed.get(k, 0) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')):
                methods = [{**m.attrib, 'missed': {c.attrib['type']: int(c.attrib['missed']) for c in m.findall('counter')}}
                           for m in cls.findall('method') if any(int(c.attrib['missed']) for c in m.findall('counter')
                                                               if c.attrib['type'] in ('LINE', 'METHOD', 'BRANCH'))]
                entries.append({'class': cls.attrib['name'], 'missed': missed, 'methods': methods})
        result['gaps'][module] = entries
    assert all(result['counters']['batch'][k] == admitted['batchByteAlignedDiagnosticCounters'][k]['missed']
               for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH'))
    with (target / 'gap.safe.json').open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    print(json.dumps({'actualExit': 0, 'remaining': {k: sum(v[k] for v in result['counters'].values())
                                                  for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')},
                      'gapSha256': sha(target / 'gap.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__':
    main()
