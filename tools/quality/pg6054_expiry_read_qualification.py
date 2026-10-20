"""Read original148 XML/Jars; run only PMD/Checkstyle against the exact archived Main,not a rebuild."""
import hashlib
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6052_expiry_combined_selected import MAIN, inventory
from pg5732_enum48_selected import MODULES, PACKAGE
from pg5966_api_sql_selected import source_test_names
from pg5910_storage_static_rebind import ordered_pairs
from pmd_diagnostic_identity import diagnostic_row

SOURCE = 'c4d0242abe53fa7916451ac22caffcdfc13d82b6'
RUN = W/'pg6052-expiry-combined-green-v1'
OLD = BASE/'PG6044-remaining33-static-v2/manifest.json'


def actual_original(manifest, begin, expected, source=SOURCE, expected_counts=(148, 16)):
    if not (manifest['source'] == begin['source'] == source and manifest['actualExit'] == manifest['mavenActualExit'] == 0
            and manifest['phaseExits'] == [0, 0] and manifest['exactInventory'] and manifest['sourceFixed']
            and manifest['selectedQualified'] and not manifest['failedOrSkipped']
            and (manifest['tests'], manifest['suites'], begin['expectedTests']) == (expected_counts[0], expected_counts[1], expected_counts[0])
            and set(manifest['staticIssues']) == set(MODULES) and not any(manifest['staticIssues'].values())
            and {k: sorted(v) for k, v in expected.items()} == begin['expected']):
        raise ValueError('genuine same-source148/16 XML and all six actual static,never missing terminal or other-source PASS')


def qualify(source, run, case_definitions, expected_counts, source_paths, old_public_path,
            old_public_sha, old_path, prior_raw_path, slot, public_name):
    manifest_path = run/'manifest.safe.json'; begin_path = run/'begin.safe.json'
    m, b = [json.loads(p.read_bytes()) for p in (manifest_path, begin_path)]
    snapshot = run/'source'
    expected = {PACKAGE+n: source_test_names(snapshot/('src/schubert-nk-'+mod+'/src/test/java')/((PACKAGE+n).replace('.', '/')+'.java'))
        for mod in MODULES for n in case_definitions[mod]}
    if (sum(map(len, expected.values())), len(expected)) != tuple(expected_counts):
        raise ValueError('complete explicit module/case/suite inventory')
    actual_original(m, b, expected, source, expected_counts)
    if sha(run/'source.tar') != b['archiveSha256'] or m['archiveSha256'] != b['archiveSha256']:
        raise ValueError('original source archive identity')
    archived = {}
    with tarfile.open(run/'source.tar') as archive:
        for member in archive.getmembers():
            if member.isfile():
                if member.name in archived:
                    raise ValueError('unique original archive input')
                archived[member.name] = hashlib.sha256(archive.extractfile(member).read()).hexdigest()
    if any(sha(snapshot/p) != h for p, h in archived.items()):
        raise ValueError('every original Main/Test/rule input unchanged')
    current = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current) != 851 or any(archived.get(p) != h for p, h in current.items()):
        raise ValueError('all851 actual current Main bytes equal archived source')
    if sha(old_public_path) != old_public_sha:
        raise ValueError('immutable old8c static')
    old_public = json.loads(old_public_path.read_bytes())
    if sha(old_path) != old_public['privateManifestSha256']:
        raise ValueError('original old1667 physical/851source map')
    old = json.loads(old_path.read_bytes())
    if set(current) != set(old['allSourceHashes']) or {p for p in current if current[p] != old['allSourceHashes'][p]} != set(source_paths):
        raise ValueError('exact declared localized Production source differences')
    physical, jars, xmls, cases, counters = {}, {}, {}, [], {}
    for module in MODULES:
        target = snapshot/('src/schubert-nk-'+module+'/target')
        choices = list(target.glob('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'))
        if len(choices) != 1:
            raise ValueError('one original generated Main Jar per module')
        jar = choices[0]; jars[module] = jar
        with zipfile.ZipFile(jar) as z:
            names = [n for n in z.namelist() if n.endswith('.class')]
            if len(names) != len(set(names)):
                raise ValueError('unique actual class entries')
            jarbytes = {module+':'+n: hashlib.sha256(z.read(n)).hexdigest() for n in names}
        built = {module+':'+p.relative_to(target/'classes').as_posix(): sha(p) for p in (target/'classes').rglob('*.class')}
        if built != jarbytes:
            raise ValueError('all actual Jar bytes equal compiled Main,not rebuilt inputs')
        physical.update(built)
        for p in (target/'surefire-reports').glob('TEST-*.xml'):
            tree = ET.parse(p).getroot(); name = tree.get('name'); methods = set()
            if name not in expected or name in xmls:
                raise ValueError('one expected original suite')
            xmls[name] = sha(p)
            for case in tree.findall('testcase'):
                method = case.get('name', '').split('(', 1)[0]
                if method in methods or any(x.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for x in case.iter()):
                    raise ValueError('no duplicate/failed/skipped/flaky cases')
                methods.add(method); cases.append(dict(source=source, module=module, className=name, method=method, xmlSha256=sha(p), result='PASS_ORIGINAL_XML'))
            if methods != expected[name] or m['xmlHashes'][name]['sha256'] != sha(p):
                raise ValueError('all actual named methods exactly match independent source declarations')
        report = target/'site/jacoco/jacoco.xml'
        if sha(report) != m['coverage'][module]['sha256']:
            raise ValueError('actual original JaCoCo report hash')
        for cls in ET.parse(report).getroot().findall('package/class'):
            counters[module+':'+cls.get('name')+'.class'] = {k.get('type'): dict(covered=int(k.get('covered')), missed=int(k.get('missed'))) for k in cls.findall('counter')}
    owners = {p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5] for p in source_paths}
    old_physical = old.get('auxClassHashes', old.get('allPhysicalMainSha256'))
    changed = sorted(k for k in physical if physical[k] != old_physical.get(k))
    if (len(physical) != 1667 or physical != m['allPhysicalMainSha256'] or set(physical) != set(old_physical)
            or not {o+'.class' for o in owners} <= set(changed)
            or any(not any(k == o+'.class' or k.startswith(o+'$') for o in owners) for k in changed)
            or set(xmls) != set(expected) or len(cases) != expected_counts[0]):
        raise ValueError('all1667/148 original bytes and exact localized owner/nested physical differences')
    os.umask(0o077); out = W/slot; out.mkdir(mode=0o700)
    files = out/'all-main.txt'; files.write_text(''.join(str(snapshot/p)+'\n' for p in sorted(current)))
    tail = old_path.with_name('aux-classpath.txt').read_text().splitlines()[6:]
    aux = out/'aux-classpath.txt'; aux.write_text('\n'.join([*(str(jars[x]) for x in MODULES), *tail])+'\n')
    analyzers = TC/'static-gates-20261015'
    if (sha(analyzers/'record-fix-v1/pmd-record-1298.jar') != '4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'
            or sha(analyzers/'checkstyle-14.3.0-all.jar') != '754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2'):
        raise ValueError('unchanged pinned analyzers')
    pmd, cs = [x.copy() for x in old['commands']]
    for flag, val in (('--file-list', str(files)), ('--aux-classpath', 'file:'+str(aux)), ('--report-file', str(out/'pmd.xml')), ('--rulesets', str(snapshot/'tools/quality/static/pmd.xml'))):
        pmd[pmd.index(flag)+1] = val
    cs[cs.index('-c')+1] = str(snapshot/'tools/quality/static/checkstyle.xml'); cs[cs.index('-o')+1] = str(out/'checkstyle.xml'); cs[-1] = '@'+str(files)
    exits = []
    for name, command in (('pmd', pmd), ('checkstyle', cs)):
        with (out/(name+'.private.log')).open('xb') as log:
            exits.append(subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=240).returncode)
    tree = ET.parse(out/'pmd.xml').getroot(); rows = []
    for file in tree.findall('{*}file'):
        name = os.path.relpath(file.get('name'), snapshot)
        if name not in current:
            raise ValueError('actual Main-only diagnostic')
        for warning in file.findall('{*}violation'):
            rows.append(diagnostic_row(name, current[name], warning, len(rows)+1))
    processing = len(tree.findall('.//{*}error')); cs_count = len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'))
    prior = json.loads(prior_raw_path.read_bytes()); pairs = ordered_pairs(prior, rows)
    if (exits[0] not in (0, 4) or exits[1] != 0 or processing or cs_count
            or any(r['sourcePath'] not in source_paths and r['findingId'] not in pairs for r in rows)
            or Counter(r['sourcePath'] for r in prior if r['sourcePath'] not in source_paths) != Counter(r['sourcePath'] for r in rows if r['sourcePath'] not in source_paths)):
        raise ValueError('unfiltered actual reports/no processing errors/all unaffected diagnostics unchanged')
    result = dict(source=source, actualExit=0, tests=expected_counts[0], suites=expected_counts[1], sourceFiles=851, physicalMain=1667,
        originalManifestSha256=sha(manifest_path), originalArchiveSha256=b['archiveSha256'], allSourceHashes=current,
        allPhysicalMainSha256=physical, changedPhysical=changed, unchangedPhysical=1667-len(changed),
        xmlHashes=xmls, allActualCounters=counters, pmdRawFindings=len(rows), ruleCounts=dict(Counter(r['rule'] for r in rows)),
        originalSixSpotBugs=0, pmdExit=exits[0], checkstyleExit=exits[1], pmdProcessingErrors=processing, checkstyleFindings=cs_count,
        targetCounters={k: v for k, v in counters.items() if any(k == o+'.class' or k.startswith(o+'$') for o in owners)},
        commands=[pmd, cs], additionalBuildsIssued=0, testsExecutedByReader=0, currentWholePending=True,
        formalAccepted=False, nativeQualified=False, ptAlternativeCompleted=0)
    for name, value in (('manifest.safe.json', result), ('cases.safe.json', cases), ('findings.safe.json', rows)):
        with (out/name).open('x') as f:
            json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    public = BASE/public_name; public.mkdir()
    summary = {k: v for k, v in result.items() if k not in ('allSourceHashes', 'allPhysicalMainSha256', 'allActualCounters', 'commands')}
    summary.update(privateManifestSha256=sha(out/'manifest.safe.json'), casesSha256=sha(out/'cases.safe.json'), findingsSha256=sha(out/'findings.safe.json'))
    with (public/'manifest.json').open('x') as f:
        json.dump(summary, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, tests=expected_counts[0], suites=expected_counts[1], raw=len(rows), changedPhysical=changed, targetCounters=result['targetCounters'], manifestSha256=sha(public/'manifest.json'))))


def main():
    definitions, _ = inventory('green')
    return qualify(SOURCE, RUN, definitions, (148, 16), {MAIN}, OLD,
        '9221ffadcdc28435bee4e2cb7a289f97dc813b24132c2e2fcc43bb53a0d1ea23',
        W/'pg6044-remaining33-static-v2/manifest.safe.json', OLD.with_name('findings.json'),
        'pg6054-expiry-read-qualification-v1', 'PG6054-expiry-read-qualification-v1')


if __name__ == '__main__':
    main()
