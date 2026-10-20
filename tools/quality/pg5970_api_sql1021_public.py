"""Independent original1021 XML/Jar/Main/counter projection; never run PT or services."""
import datetime
import hashlib
import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import ROOT, W, BASE, MODULES, sha
from pg5966_api_sql_selected import inventory, source_test_names

SOURCE = '1f87a31c419582c999487b725e8c9231a881325b'


def four100(counters):
    return len(counters) == 16 and all(set(c) == {'LINE', 'METHOD', 'CLASS', 'BRANCH'} and all(type(c[k][f]) is int for k in c for f in ('missed', 'covered'))
                                      and all(c[k]['missed'] == 0 and c[k]['covered'] > 0 for k in c) for c in counters.values())


def main():
    path = W/'pg5966-api-sql-selected1021-v1/manifest.safe.json'; v = json.loads(path.read_bytes()); snapshot = path.parent/'source'
    sp = BASE/'PG5968-api-sql-static-v1/manifest.json'; s = json.loads(sp.read_bytes()); private = W/'pg5968-api-sql-static-v1/manifest.safe.json'
    if sha(sp) != 'f888e1a0817b7fc77521410df29c89c8fa95a7a3d5d4b3e17196d6be09e0d454' or sha(private) != s['privateManifestSha256'] or sha(path) != s['selectedManifestSha256']:
        raise ValueError('actual original1021 and all851/1666 raw static first')
    proof = json.loads(private.read_bytes()); cases, counts, targets = inventory()
    expected, actual, physical, counters, xmls, jars = {}, {}, {}, {}, {}, {}; output = []
    start = int(datetime.datetime.fromisoformat(v['startedUTC']).timestamp()*1e9); end = int(datetime.datetime.fromisoformat(v['completedUTC']).timestamp()*1e9)
    oldp = BASE/'PG5944-current3973-cases/cases.json'
    if sha(oldp) != '81a354697110977b2b859b14347cf62dad6b077d609d06997a3f891d7f4cc250':
        raise ValueError('unchanged Test semantic identities only, not historical PASS')
    old = {(r['class'], r['caseNameSha256']) for r in json.loads(oldp.read_bytes())}
    for module in MODULES:
        target = snapshot/('src/schubert-nk-'+module+'/target')
        for relative in cases[module]:
            name = 'dev.codex.schubert.nk.'+relative
            tp = snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.', '/')+'.java')
            expected[name] = source_test_names(tp)
            if len(expected[name]) != counts[name] or sha(tp) != sha(ROOT/tp.relative_to(snapshot)):
                raise ValueError('exact named Test source inventory, no oracle mutation')
        for p in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            tree = ET.parse(p).getroot(); name = tree.get('name'); actual[name] = set(); digest = sha(p)
            if name in xmls or not start <= p.stat().st_mtime_ns <= end or len(tree.findall('testcase')) != int(tree.get('tests')) or any(int(tree.get(k)) for k in ('failures', 'errors', 'skipped')):
                raise ValueError('one fresh original complete nonfailed suite')
            xmls[name] = dict(module=module, sha256=digest)
            if xmls[name] != v['xmlHashes'][name]:
                raise ValueError('original selected XML hashes fixed')
            for case in tree.findall('testcase'):
                raw = case.get('name'); method = raw.split('(', 1)[0]; identity = hashlib.sha256(raw.encode()).hexdigest()
                if method in actual[name] or any(n.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()) or (name, identity) not in old:
                    raise ValueError('each unchanged actual case once; no aliases/old result import')
                actual[name].add(method)
                output.append(dict(module=module, **{'class': name}, caseNameSha256=identity, xmlSha256=digest, result='PASS_ORIGINAL_SELECTED_XML', source=SOURCE))
        member_hashes = {p.relative_to(target/'classes').as_posix(): sha(p) for p in (target/'classes').rglob('*.class')}
        physical.update({module+':'+k: d for k, d in member_hashes.items()})
        jp = target/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        with zipfile.ZipFile(jp) as jar:
            jar_members = {n: hashlib.sha256(jar.read(n)).hexdigest() for n in jar.namelist() if n.endswith('.class')}
        if jar_members != member_hashes:
            raise ValueError('all actual Jar Main bytes equal compiled classes')
        jars[module] = sha(jp)
        if module in targets:
            nodes = {c.get('name'): c for c in ET.parse(target/'site/jacoco/jacoco.xml').getroot().findall('package/class')}
            for name in targets[module]:
                node = nodes['dev/codex/schubert/nk/'+name]
                counters[module+':'+name] = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in node.findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    sources = {p.relative_to(snapshot).as_posix(): sha(p) for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not (v['actualExit'] == v['mavenActualExit'] == 0 and v['source'] == proof['source'] == SOURCE and v['phaseExits'] == [0, 0] and v['sourceFixed']
            and v['selectedQualified'] and actual == expected and len(actual) == 175 and len(output) == 1021 and len(xmls) == len(v['xmlHashes'])
            and len(physical) == 1666 and physical == v['allPhysicalMainSha256'] == proof['auxClassHashes'] and len(sources) == 851 and sources == proof['allSourceHashes']
            and counters == v['targetCounters'] and four100(counters) and set(v['staticIssues']) == set(MODULES) and not any(v['staticIssues'].values())
            and s['rawDiagnosticsRemovedByPg'] == 21 and s['pmdRawFindings'] == 1430 and s['pmdProcessingErrors'] == s['checkstyleFindings'] == 0):
        raise ValueError('genuine1021/175, actual16 four100/8511666/Jar/source/static/raw21 conditions')
    out = BASE/'PG5970-api-sql1021-v1'; os.umask(0o077); out.mkdir()
    for i, case in enumerate(output, 1):
        case['testId'] = 'PT-PG5966-'+str(i).zfill(4)
    with (out/'cases.json').open('x') as f:
        json.dump(output, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, tests=1021, suites=175, apiTests=1010, guardTests=11, sourceFiles=851, physicalMain=1666,
                 originalManifestSha256=sha(path), staticManifestSha256=sha(sp), casesSha256=sha(out/'cases.json'), jarHashes=jars,
                 targetCounters=counters, targetFour100=True, changedPhysicalClasses=s['changedPhysicalClasses'], unchangedPhysicalClasses=s['unchangedPhysicalClasses'],
                 debugOnlyProof=s['debugOnlyProof'], xmlHashes=xmls, toolchain=dict(jdk='25.0.4', maven='3.9.12', jacoco='0.8.15', spotbugs='4.10.4.0'),
                 startedUTC=v['startedUTC'], completedUTC=v['completedUTC'], archiveSha256=v['archiveSha256'], rawDiagnosticsRemovedByPg=21, pmdRawFindings=1430,
                 formalAccepted=False, fullSourceFormalQualificationPending=True, oldWholeNativeImported=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, tests=1021, suites=175, target16Four100=True, physicalMain=1666, jars=6, rawFixed=21,
                         manifestSha256=sha(out/'manifest.json'), casesSha256=sha(out/'cases.json'))))


if __name__ == '__main__':
    main()
