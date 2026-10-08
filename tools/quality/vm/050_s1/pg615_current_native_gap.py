"""Private gap coordinates on the verified eight-current-stream diagnostic cohort."""
import hashlib
import json
import os
import pathlib
import subprocess
import xml.etree.ElementTree as ET

W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J = pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    cohort = W / 'pg614-current-eight-native-v1'
    assert sha(cohort / 'manifest.safe.json') == '4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1'
    record = json.loads((cohort / 'manifest.safe.json').read_bytes())
    assert record['actualExit'] == 0 and record['productionSource'] == '23b14a44b10504172e030bbd6625926bf049fb5c'
    target = W / 'pg615-current-native-gap-v1'
    assert not os.path.lexists(target)
    target.mkdir(mode=0o700)
    assert sha(W/'pg562-current-native-gap-v1/classes/NativeCoverageXml471.class')=='022716de432254edbc4a085a1d7c0a8e7e3a8cef31cdfbc7639479d308cc998b'
    cp = [str(W / 'pg562-current-native-gap-v1/classes')]
    repo = pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar', 'org/jacoco/org.jacoco.report/0.8.15/*.jar',
                    'org/ow2/asm/asm/9.10.1/*.jar', 'org/ow2/asm/asm-tree/9.10.1/*.jar', 'org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths = list(repo.glob(pattern));assert len(paths) == 1;cp.append(str(paths[0]))
    modules = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
    host = W / 'pg599-candidate-bootstrap-six-host-v1'
    assert sha(host/'manifest.safe.json')==record['frozenHostManifestSha256']
    host_record=json.loads((host/'manifest.safe.json').read_bytes())
    data = [host / m / 'jacoco.exec' for m in modules]
    assert all(sha(p) == record['hostExecHashes'][m] for m, p in zip(modules, data))
    for i, expected in enumerate(record['selected']):
        p = cohort / (str(i) + '.exec');assert sha(p) == expected['sha256'];data.append(p)
    assert len(data) == 14
    gaps = {};xml_hashes = {}
    for module in ('bootstrap', 'api', 'batch'):
        jar = host / module / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        assert sha(jar)==host_record['moduleResults'][module]['jarSha256']
        xml = target / (module + '.xml')
        result = subprocess.run([str(J / 'java'), '-cp', ':'.join(cp), 'NativeCoverageXml471', str(jar), str(xml),
                                 *[str(p) for p in data]], capture_output=True, timeout=45)
        assert result.returncode == 0 and not result.stderr
        root = ET.parse(xml).getroot()
        counts = {c.attrib['type']: int(c.attrib['missed']) for c in root.findall('counter')}
        assert all(counts[k] == record['moduleCounters'][module][k]['missed'] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH'))
        entries = []
        for package in root.findall('package'):
            for cls in package.findall('class'):
                missed = {c.attrib['type']: int(c.attrib['missed']) for c in cls.findall('counter')}
                if any(missed.get(k, 0) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')):
                    methods = [{**m.attrib, 'missed': {c.attrib['type']: int(c.attrib['missed']) for c in m.findall('counter')}}
                               for m in cls.findall('method') if any(int(c.attrib['missed']) for c in m.findall('counter')
                                                                    if c.attrib['type'] in ('LINE', 'METHOD', 'BRANCH'))]
                    entries.append({'class': cls.attrib['name'], 'source': cls.attrib.get('sourcefilename'), 'missed': missed, 'methods': methods})
        gaps[module] = entries;xml_hashes[module] = sha(xml)
    record = {'productionSource':record['productionSource'],'parentManifestSha256':sha(cohort/'manifest.safe.json'),
              'xmlHashes':xml_hashes,'gaps':gaps,'formalAccepted':False,'sourceOrClassExclusions':False}
    with (target / 'gap.safe.json').open('x') as f:
        json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'gapFamilies':{k:len(v) for k,v in gaps.items()},'gapSha256':sha(target/'gap.safe.json'),
                      'formalAccepted':False}))


if __name__ == '__main__':
    main()
