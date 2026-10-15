"""Same frozen PMD/Checkstyle rules on closed related candidate inputs; no whole/VM replay."""
import hashlib
import inspect
import json
import os
from pathlib import Path

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077); b = Path('/home/mini/schubert-nk-pgpt')
    old = b / 'runs/PG3382-static-gate-v1/result'
    source = b / 'source-PG3408-related-v1'; out = b / 'runs/PG3422-candidate-static-v1'; out.mkdir()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    fixed = json.loads((old / 'manifest.safe.json').read_bytes())
    authority = b / 'runs/PG3409-related-qualified-v1/manifest.safe.json'
    assert sha(authority) == data['relatedManifestSha256']
    related = json.loads(authority.read_bytes()); assert related['actualExit'] == related['mavenExit'] == 0
    assert related['candidateSource'] == data['candidateSource']
    files = sorted(source.glob('src/*/src/main/java/**/*.java'))
    actual = {str(p.relative_to(source)): sha(p) for p in files}
    assert len(actual) == fixed['sourceFiles'] == 849
    old_sources = fixed['sourceSha256']
    assert actual.keys() == old_sources.keys()
    assert [p for p in actual if actual[p] != old_sources[p]] == [data['changedMainSource']]
    old_rule_root = old / 'source/tools/quality/static'
    assert data['ruleSha256'] == fixed['ruleSha256']
    assert all(sha(old_rule_root / p) == h for p, h in data['ruleSha256'].items())
    jars = []
    for module, item in related['modules'].items():
        jar = source / ('src/schubert-nk-' + module + '/target/schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        assert sha(jar) == item['jarSha256']; jars.append(jar)
    count = 0
    for jar in jars:
        with zipfile.ZipFile(jar) as z: count += sum(n.endswith('.class') for n in z.namelist())
    assert count == 1643
    for p, h in fixed['auxJarSha256'].items():
        path = Path(p)
        if path.is_relative_to(b / 'm2/repository'):
            assert sha(path) == h
            if path not in jars: jars.append(path)
    aux_hashes = {str(p): sha(p) for p in jars}
    overlay = b / 'runs/PG3386-pmd-record-after-v1/pmd-record-1298.jar'
    assert sha(overlay) == '4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'
    assert sha(b / 'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar') == fixed['pinnedToolSha256']['checkstyle-14.3.0-all.jar']
    assert sha(b / 'runs/PG3382-static-gate-v1/pmd-dist-7.28.0-bin.zip') == fixed['pinnedToolSha256']['pmd-dist-7.28.0-bin.zip']
    listing = out / 'all-java.txt'; listing.write_text(''.join(str(p) + '\n' for p in files))
    aux = out / 'aux-classpath.txt'; aux.write_text('\n'.join(map(str, jars)) + '\n')
    pmd = list(fixed['pmd']['argv']); pmd[2] = str(overlay) + ':' + pmd[2]
    pmd[pmd.index('--file-list') + 1] = str(listing)
    pmd[pmd.index('--aux-classpath') + 1] = 'file:' + str(aux)
    pmd[pmd.index('--report-file') + 1] = str(out / 'pmd.xml')
    checkstyle = list(fixed['checkstyle']['argv']); checkstyle[checkstyle.index('-o') + 1] = str(out / 'checkstyle.xml')
    checkstyle[-1] = '@' + str(listing)
    env = {k: v for k, v in os.environ.items() if k not in ['JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS']}
    results = {}; start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name, argv in [('pmd', pmd), ('checkstyle', checkstyle)]:
        with (out / (name + '.private.log')).open('xb') as log:
            result = subprocess.run(argv, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        root = E.parse(out / (name + '.xml')).getroot()
        findings = root.findall('.//{*}violation') if name == 'pmd' else root.findall('.//error')
        errors = root.findall('.//{*}error') if name == 'pmd' else []
        assert not errors, 'tool processing errors are not findings or pass'
        expected_exit = (4 if findings else 0) if name == 'pmd' else len(findings) % 256
        assert result.returncode == expected_exit
        results[name] = {'exit': result.returncode, 'violations': len(findings), 'processingErrors': len(errors),
                         'ruleCounts': dict(Counter(f.get('rule') if name == 'pmd' else f.get('source') for f in findings)),
                         'reportSha256': sha(out / (name + '.xml')), 'logSha256': sha(out / (name + '.private.log'))}
    assert all(sha(source / p) == h for p, h in actual.items()) and all(sha(Path(p)) == h for p, h in aux_hashes.items())
    result = {'actualExit': 0, 'run': 'PG3422-candidate-static-v1', 'candidateSource': data['candidateSource'],
              'sourceSnapshot': related['sourceSnapshot'], 'sourceFiles': 849, 'auxMainClasses': 1643,
              'sourceSha256': actual, 'auxJarSha256': aux_hashes, 'ruleSha256': data['ruleSha256'],
              'pinnedToolSha256': fixed['pinnedToolSha256'], 'recordOverlaySha256': sha(overlay),
              'sameRulesNoSuppressionAdded': True, 'relatedManifestSha256': sha(authority),
              'results': results, 'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'allInputsUnchangedAfter': True, 'F03Accepted': False, 'staticGatePass': False,
              'newProductionPtCredit': 0, 'formalUpdated': False, 'vmActions': 0, 'wholeReplay': False}
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps(result))


def main():
    related = json.loads((W / 'pg3409-related-qualified-v1/manifest.safe.json').read_bytes())['result']
    config = ROOT / 'tools/quality/static'
    data = {'candidateSource': related['candidateSource'], 'relatedManifestSha256': related['serverManifestSha256'],
            'changedMainSource': 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.java',
            'ruleSha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in config.glob('*.xml')}}
    payload = inspect.getsource(server) + '\nserver(' + repr(data) + ')\n'
    os.umask(0o077); out = W / 'pg3422-candidate-static-v1'; out.mkdir()
    (out / 'static.private.py').write_text(payload)
    rc, text = run("python3 - <<'STATIC'\n" + payload + '\nSTATIC', timeout=390)
    (out / 'observer.private.log').write_text(text)
    assert rc == 0, 'candidate diagnostic failed; preserve slot, no rerun'
    result = json.loads(text.strip())
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3422-candidate-static'
    public.mkdir(); path = public / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'sourceFiles': 849, 'auxMainClasses': 1643,
                      'results': result['results'], 'F03Accepted': False, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
