"""Independent original965 XML/Jar/source/counter verification; no test rerun."""
import datetime
import hashlib
import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import ROOT, W, BASE, MODULES, sha
from pg6026_error_boundary_selected import inventory
from pg5966_api_sql_selected import source_test_names
from pg6028_error_boundary_static import SOURCE, NEW_INTERFACE

NEW_TEST = 'dev.codex.schubert.nk.batch.mq.ArtemisManagementEncoderBoundaryTest'
NEW_METHODS = {'encoderForwardsExactInputsAndRejectsMissingPort', 'encoderPreservesUnknownAndRedactsDeclaredFailures',
               'parentGuardIsCheckedBeforeBorrowedStartAndRemovedAfterFailure'}


def four100(counters):
    return len(counters) == 2 and all(set(c) == {'LINE', 'METHOD', 'CLASS', 'BRANCH'} and
        all(type(c[k][f]) is int for k in c for f in ('missed', 'covered')) and
        all(c[k]['missed'] == 0 and c[k]['covered'] > 0 for k in c) for c in counters.values())


def original_identity(name, raw, old):
    ident = hashlib.sha256(raw.encode()).hexdigest()
    if name == NEW_TEST:
        if raw not in NEW_METHODS or (name, ident) in old:
            raise ValueError('only three separately declared new ordinary Tests;no alias')
    elif (name, ident) not in old:
        raise ValueError('unchanged source Test must retain its actual original case identity')
    return ident


def main():
    op = W/'pg6026-error-boundary-selected965-v1/manifest.safe.json'
    v = json.loads(op.read_bytes()); snapshot = op.parent/'source'
    sp = BASE/'PG6028-error-boundary-static-v2/manifest.json'
    s = json.loads(sp.read_bytes()); private = W/'pg6028-error-boundary-static-v2/manifest.safe.json'
    if sha(private) != s['privateManifestSha256'] or sha(op) != s['selectedManifestSha256']:
        raise ValueError('original selected receipt linked to independent static proof')
    proof = json.loads(private.read_bytes()); cases, counts, targets = inventory()
    oldp = BASE/'PG6014-current3973-cases/cases.json'
    if sha(oldp) != 'f0173678ea06129e2224c5333b86c7dc7924a0f062032e5105679d4196f82219':
        raise ValueError('immutable preceding semantic identities,not old PASS import')
    old = {(r['class'], r['caseNameSha256']) for r in json.loads(oldp.read_bytes())}
    start = int(datetime.datetime.fromisoformat(v['startedUTC']).timestamp()*1e9)
    end = int(datetime.datetime.fromisoformat(v['completedUTC']).timestamp()*1e9)
    expected, actual, xmls, physical, jars, counters, output = {}, {}, {}, {}, {}, {}, []
    metadata_only_interface = None
    for module in MODULES:
        target = snapshot/('src/schubert-nk-'+module+'/target')
        for relative in cases[module]:
            name = 'dev.codex.schubert.nk.'+relative
            tp = snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.', '/')+'.java')
            expected[name] = source_test_names(tp)
            if len(expected[name]) != counts[name] or sha(tp) != sha(ROOT/tp.relative_to(snapshot)):
                raise ValueError('actual named Test source/hash remains fixed')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            tree = ET.parse(path).getroot(); name = tree.get('name'); digest = sha(path)
            if name in actual or not start <= path.stat().st_mtime_ns <= end or len(tree.findall('testcase')) != int(tree.get('tests')) or any(int(tree.get(k)) for k in ('failures', 'errors', 'skipped')):
                raise ValueError('one complete fresh original unskipped suite')
            actual[name] = set(); xmls[name] = dict(module=module, sha256=digest)
            if xmls[name] != v['xmlHashes'][name]:
                raise ValueError('original XML bytes fixed')
            for case in tree.findall('testcase'):
                raw = case.get('name'); method = raw.split('(', 1)[0]
                if method in actual[name] or any(n.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
                    raise ValueError('unique actual case,never failed/flaky/skipped counted PASS')
                identity = original_identity(name, raw, old); actual[name].add(method)
                output.append(dict(module=module, **{'class': name}, caseNameSha256=identity, xmlSha256=digest,
                                   result='PASS_ORIGINAL_SELECTED_XML', source=SOURCE, newCase=name == NEW_TEST))
        members = {p.relative_to(target/'classes').as_posix(): sha(p) for p in (target/'classes').rglob('*.class')}
        physical.update({module+':'+k: d for k, d in members.items()})
        jarpath = target/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        with zipfile.ZipFile(jarpath) as jar:
            jar_members = {n: hashlib.sha256(jar.read(n)).hexdigest() for n in jar.namelist() if n.endswith('.class')}
        if jar_members != members:
            raise ValueError('every physical class equals its actual Jar member')
        jars[module] = sha(jarpath)
        if module in targets:
            nodes = {c.get('name'): c for c in ET.parse(target/'site/jacoco/jacoco.xml').getroot().findall('package/class')}
            for name in targets[module]:
                node = nodes['dev/codex/schubert/nk/'+name]
                counters[module+':'+name] = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in node.findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
            if module == 'batch':
                interface_name = NEW_INTERFACE.split(':', 1)[1][:-6]
                node = nodes.get(interface_name)
                metadata_only_interface = dict(physicalClass=NEW_INTERFACE, xmlPresent=node is not None,
                    xmlCounters={} if node is None else {c.get('type'): dict(c.attrib) for c in node.findall('counter')},
                    noExecutedCodeClaimed=True, coverageExclusionAdded=False)
                if metadata_only_interface['xmlCounters']:
                    raise ValueError('inspect any unexpected executable counters on abstract interface')
    sources = {p.relative_to(snapshot).as_posix(): sha(p) for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not (v['source'] == proof['source'] == SOURCE and sha(op) == '9ecd53b6a1aa5380db0c8420f38323e9d2282871d68f146e636a9d03e088ab6f'
            and v['actualExit'] == v['mavenActualExit'] == 1 and v['phaseExits'] == [0, 1] and v['sourceFixed'] and not v['selectedQualified'] and v['exactInventory']
            and actual == expected and len(actual) == 162 and len(output) == 965 and sum(r['newCase'] for r in output) == 3 and len(xmls) == len(v['xmlHashes'])
            and len(physical) == 1667 and physical == v['allPhysicalMainSha256'] == proof['auxClassHashes']
            and len(sources) == 851 and sources == proof['allSourceHashes'] and counters == v['targetCounters'] and four100(counters)
            and v['staticIssues'] == dict(protocol=0, storage=0, bootstrap=0, api=0, web=0, batch=3)
            and s['originalSelectedOverallExit'] == 1 and not s['originalSelectedOverallAccepted'] and s['originalSpotBugsIssues'] == v['staticIssues']
            and s['rawDiagnosticsRemovedByPg'] == 21 and s['pmdRawFindings'] == 1327 and s['pmdProcessingErrors'] == s['checkstyleFindings'] == 0):
        raise ValueError('genuine965/162/three new,851/1667/Jars/actual two four100/unsuppressed static delta')
    out = BASE/'PG6030-error-boundary965-v1'; os.umask(0o077); out.mkdir()
    for index, case in enumerate(output, 1):
        case['testId'] = 'PT-PG6026-'+str(index).zfill(4)
    with (out/'cases.json').open('x') as f:
        json.dump(output, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, tests=965, suites=162, declaredNewCases=3,
        sourceFiles=851, physicalMain=1667, originalManifestSha256=sha(op), staticManifestSha256=sha(sp),
        casesSha256=sha(out/'cases.json'), jarHashes=jars, xmlHashes=xmls, targetCounters=counters, targetFour100=True,
        newAbstractInterface=metadata_only_interface, changedPhysicalClasses=s['changedPhysicalClasses'],
        unchangedPhysicalClasses=s['unchangedPhysicalClasses'], startedUTC=v['startedUTC'], completedUTC=v['completedUTC'],
        archiveSha256=v['archiveSha256'], toolchain=dict(jdk='25.0.4', maven='3.9.12', jacoco='0.8.15', spotbugs='4.10.4.0'),
        pmdRawFindings=1327, rawDiagnosticsRemovedByPg=21, fullSourceFormalQualificationPending=True,
        formalAccepted=False, originalSelectedOverallExit=1, originalSelectedOverallAccepted=False,
        unresolvedBug='BUG1526', originalSpotBugsIssues=v['staticIssues'], oldWholeNativeImported=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, tests=965, suites=162, newCases=3, twoFour100=True,
                         manifestSha256=sha(out/'manifest.json'), casesSha256=sha(out/'cases.json'))))


if __name__ == '__main__':
    main()
