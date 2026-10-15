"""Recover original3408 Maven0/60 without rerun; exact generated LNT+4, never CRC equality."""
import hashlib
import inspect
import json
import os

from lan_server import run
from pg1540_debug_line_delta import positions
from pg3348_related_boundary_group import classify, require
from pg3408_outbox_cause_related import CLASSES, DEPLOYED, W, ROOT


def verify_switch_debug(old, new):
    if type(old) is not bytes or type(new) is not bytes or len(old) != len(new):
        raise ValueError('fixed switch class bytes required')
    before, after = positions(old), positions(new)
    if before != after or len(before) != 1:
        raise ValueError('exact one generated switch line entry required')
    normalized = bytearray(new)
    for offset in before:
        if int.from_bytes(old[offset:offset + 2], 'big') != 154 or int.from_bytes(new[offset:offset + 2], 'big') != 158:
            raise ValueError('exact original154 to candidate158 source mapping required')
        normalized[offset:offset + 2] = old[offset:offset + 2]
    if bytes(normalized) != old:
        raise ValueError('non-line class byte changed')
    return {'lineEntries': 1, 'oldLine': 154, 'newLine': 158, 'lineOffset': 4,
            'allNonLineBytesIdentical': True, 'crcEqualityClaim': False}


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import tarfile
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077)
    b = Path('/home/mini/schubert-nk-pgpt'); original = b / 'runs/PG3408-related-v1'
    source = b / 'source-PG3408-related-v1'; output = b / 'runs/PG3409-related-qualified-v1'; output.mkdir()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    begin = json.loads((original / 'begin.safe.json').read_bytes())
    exit_path = original / 'maven-exit.safe.json'; actual = json.loads(exit_path.read_bytes())
    require(actual == {'mavenExit': 0, 'head': begin['sourceSnapshot']}, 'original Maven0, not wrapper1')
    require(begin['candidateSource'] == data['candidateSource'] and begin['archiveSha256'] == data['archiveSha256'], 'exact original candidate')
    archive = b / 'transfer/PG3408-related-v1/source.tar'
    require(sha(archive) == begin['archiveSha256'], 'original transferred source archive')
    with tarfile.open(archive) as t:
        for member in t:
            if member.isfile():
                p = source / member.name
                require(p.resolve().is_relative_to(source) and not p.is_symlink(), 'actual regular source')
                with t.extractfile(member) as f:
                    require(hashlib.sha256(f.read()).hexdigest() == sha(p), 'every frozen source unchanged')
    modules = {}; all_cases = set(); count = 0; debug = None
    changed = ['dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender$1.class',
               'dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class']
    for module, expected in data['classes'].items():
        target = source / ('src/schubert-nk-' + module + '/target')
        paths = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
        cases = classify([E.parse(p).getroot() for p in paths], expected); all_cases.update(cases)
        start = datetime.datetime.fromisoformat(begin['startUTC']).timestamp()
        require(all(p.stat().st_mtime >= start for p in paths), 'fresh original run XML')
        static = target / 'spotbugsXml.xml'; require(not E.parse(static).findall('.//BugInstance'), 'actual static0')
        jar = target / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        old = b / 'runs/PG3398-six-v1' / module / jar.name
        require(sha(old) == data['priorJarHashes'][module], 'original3707 jar authority')
        images = []; bytes_images = []
        for p in [old, jar]:
            with zipfile.ZipFile(p) as z:
                require(len(z.namelist()) == len(set(z.namelist())), 'unique complete members')
                material = {n: z.read(n) for n in z.namelist()}
                bytes_images.append(material)
                images.append({n: hashlib.sha256(v).hexdigest() for n, v in material.items()})
        require(images[0].keys() == images[1].keys(), 'same complete inventory')
        delta = sorted(n for n in images[0] if images[0][n] != images[1][n])
        require(delta == (changed if module == 'api' else []), 'one semantic plus one generated debug class only')
        if module == 'api':
            debug = verify_switch_debug(bytes_images[0][changed[0]], bytes_images[1][changed[0]])
        physical = sum(n.endswith('.class') for n in images[1]); count += physical
        coverage = target / 'site/jacoco/jacoco.xml'; cov = E.parse(coverage).getroot()
        value = {'tests': len(cases), 'suites': len(paths), 'mainClasses': physical,
                 'jarSha256': sha(jar), 'changedMembers': delta,
                 'xmlHashes': {p.name: sha(p) for p in paths}, 'coverageXmlSha256': sha(coverage), 'staticSha256': sha(static)}
        if module == 'api':
            cls = next(c for pkg in cov.findall('package') for c in pkg.findall('class') if c.get('name') + '.class' == changed[1])
            method = next(m for m in cls.findall('method') if m.get('name') == 'isDuplicateConfirmation')
            value['changedMethodCounters'] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in method.findall('counter')}
            require(all(value['changedMethodCounters'][k]['missed'] == 0 for k in ['LINE', 'METHOD', 'BRANCH']), 'whole changed graph method covered')
        modules[module] = value
    require(len(all_cases) == 60 and sum(m['suites'] for m in modules.values()) == 11 and count == 1643, 'original actual60/11/1643')
    result = {'actualExit': 0, 'mavenExit': 0, 'originalObserverExit': 1,
              'run': 'PG3409-related-qualified-v1', 'originalRun': 'PG3408-related-v1',
              'candidateSource': data['candidateSource'], 'sourceSnapshot': begin['sourceSnapshot'],
              'deployedProductionSource': data['deployedSource'], 'archiveSha256': sha(archive),
              'tests': 60, 'suites': 11, 'mainClasses': count, 'modules': modules,
              'FESFlakyNotRun': 0, 'existingStaticSixModules': 0, 'mavenReplayed': False,
              'semanticChangedClasses': 1, 'debugOnlyChangedClasses': 1, 'allOtherMainSameBytes': 1641,
              'generatedSwitchDebug': debug, 'oldNativeImported': False,
              'logSha256': sha(original / 'maven.private.log'), 'exitSha256': sha(exit_path),
              'startUTC': begin['startUTC'], 'qualifiedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'fullRegressionPending': True, 'nativePending': True, 'formalUpdated': False, 'vmActions': 0}
    (output / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    result['serverManifestSha256'] = sha(output / 'manifest.safe.json')
    print(json.dumps(result))


def main():
    before = json.loads((W / 'pg3408-outbox-cause-related-v1/manifest.safe.json').read_bytes())
    require(before['actualExit'] == 1, 'preserve original post-guard refusal')
    data = {'candidateSource': '4856b3fcaeb4cae983d77757a38dc0bf56a693e2', 'deployedSource': DEPLOYED,
            'archiveSha256': 'aaeb31cd0a433edc554f435a3d50e55e5193920b8efa4c3569074f43536260e0', 'classes': CLASSES,
            'priorJarHashes': json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']['jarHashes']}
    raw = '\n'.join(inspect.getsource(f) for f in [positions, verify_switch_debug, require, classify, server]) + '\nserver(' + repr(data) + ')\n'
    os.umask(0o077); out = W / 'pg3409-related-qualified-v1'; out.mkdir()
    (out / 'qualify.private.py').write_text(raw)
    rc, text = run("python3 - <<'QUALIFY'\n" + raw + '\nQUALIFY', timeout=60)
    (out / 'observer.private.log').write_text(text)
    receipt = {'actualExit': rc, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalUpdated': False}
    if rc == 0:
        receipt['result'] = json.loads(text.strip())
    (out / 'manifest.safe.json').write_text(json.dumps(receipt, sort_keys=True))
    require(rc == 0, 'genuine original related qualification required')
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3409-outbox-cause-related'
    public.mkdir(); path = public / 'manifest.json'; path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': rc, 'tests': 60, 'suites': 11, 'mavenReplayed': False,
                      'changedMethodCounters': receipt['result']['modules']['api']['changedMethodCounters'],
                      'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
