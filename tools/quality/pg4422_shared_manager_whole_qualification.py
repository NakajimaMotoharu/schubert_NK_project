"""Independent original XML, exact moved-case and complete physical Main inventory qualification."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run
from pg4420_shared_manager_full import SOURCE, ROOT, W

ALIASES = {
    'dev.codex.schubert.nk.batch.platform.LinuxSystemdQueryTest': 'dev.codex.schubert.nk.bootstrap.SystemManagerObservationTest',
    'dev.codex.schubert.nk.batch.platform.LinuxSystemdSessionTest': 'dev.codex.schubert.nk.bootstrap.LinuxSystemdSessionTest'}
NEW_CASES = [
    ('dev.codex.schubert.nk.bootstrap.SystemManagerObservationTest', 'everyFixedTargetKeepsFreshOwnerAndAllSevenFields'),
    ('dev.codex.schubert.nk.bootstrap.SystemManagerObservationTest', 'childFixedObserversKeepFreshReadsAndNeverSelectAnArbitraryUnit'),
    ('dev.codex.schubert.nk.bootstrap.ChildMaintenanceParentTest', 'eitherStablePropertyOrderKeepsAllParentValuesAndBothFreshReads'),
    ('dev.codex.schubert.nk.bootstrap.ChildMaintenanceParentTest', 'orderingDriftBetweenTheTwoLiveReadsStillFailsClosed')]


def qualify(data):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    import zipfile

    base = Path('/home/mini/schubert-nk-pgpt'); out = base / 'runs/PG4420-six-v1'; source = base / 'source-full-PG4420'
    old = base / 'runs/PG3966-six-v1'
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def need(v, why):
        if not v: raise ValueError(why)
    original = json.loads((out / 'manifest.safe.json').read_bytes()); begin = json.loads((out / 'begin.safe.json').read_bytes())
    need(original['actualExit'] == original['mavenExit'] == 0 and original['sourceInputsUnchanged'] is True
         and original['sourceSnapshotHead'] == original['productionSource'] == begin['sourceSnapshotHead'] == data['source'], 'original same-source genuine full0')
    need(sha(old / 'manifest.safe.json') == data['priorManifestSha256'], 'actual qualified old3717 baseline manifest')
    need(begin['sourceArchiveSha256'] == data['archiveSha256'] == sha(base / 'transfer/PG4420-source.tar'), 'all immutable archive bytes')
    need(all(sha(source / n) == h for n, h in begin['inputs'].items()), 'all original source/test/resource/settings unchanged')
    need({n: sha(source / n) for n in data['allMainSourceSha256']} == data['allMainSourceSha256'], 'all849 Main source bytes')
    oldcases = set(); cases = set(); oldphysical = {}; physical = {}; modules = {}; jars = {}; coverage = {}
    start = datetime.datetime.fromisoformat(begin['startUTC']).timestamp()
    def identities(directory, expected_hashes, fresh=False):
        found = set(); suites = 0
        for path in sorted(directory.glob('TEST-*.xml')):
            suites += 1; need(sha(path) == expected_hashes[path.name], 'genuine original/saved XML hash')
            root = E.parse(path).getroot(); entries = root.findall('testcase')
            need(all(root.get(k) == '0' for k in ['failures', 'errors', 'skipped']) and int(root.get('tests')) == len(entries), 'all XML complete success')
            if fresh: need(path.stat().st_mtime >= start, 'fresh current XML')
            for case in entries:
                need(not any(case.find(k) is not None for k in ['failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError']), 'FES/flaky/rerun not accepted')
                key = (case.get('classname'), case.get('name')); need(all(type(v) is str and v for v in key) and key not in found, 'unique actual class/method')
                found.add(key)
        return found, suites
    baseline = json.loads((old / 'manifest.safe.json').read_bytes())
    for module in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']:
        target = source / ('src/schubert-nk-' + module + '/target')
        oldrows, _ = identities(old / module / 'surefire-reports', baseline['modules'][module]['xmlHashes'])
        oldcases.update((data['aliases'].get(c, c), m) for c, m in oldrows)
        xml_hashes = original['modules'][module]['xmlHashes']
        rows, suites = identities(target / 'surefire-reports', xml_hashes, True); cases.update(rows)
        need({p.name: sha(p) for p in (out / module / 'surefire-reports').glob('TEST-*.xml')} == xml_hashes, 'saved complete current XML set')
        need(rows and not E.parse(target / 'spotbugsXml.xml').getroot().findall('.//BugInstance'), 'actual nonempty module and static0')
        jar = target / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'); oldjar = old / module / jar.name
        need(sha(oldjar) == data['priorJarHashes'][module], 'qualified old module Jar')
        jars[module] = sha(jar)
        for path, image in [(oldjar, oldphysical), (jar, physical)]:
            with zipfile.ZipFile(path) as archive:
                need(len(archive.namelist()) == len(set(archive.namelist())), 'whole unique physical inventory')
                values = {n: hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist() if n.endswith('.class')}
                image.update({module + ':' + n: h for n, h in values.items()})
                if image is physical:
                    need(all(sha(target / 'classes' / n) == h for n, h in values.items()), 'Jar Main equals actual reported classes')
        cov = target / 'site/jacoco/jacoco.xml'; tree = E.parse(cov).getroot()
        coverage[module] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in tree.findall('counter')}
        need(all(k in coverage[module] for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']), 'all required counters measured')
        modules[module] = {'tests': len(rows), 'suites': suites, 'mainClasses': sum(k.startswith(module + ':') for k in physical),
                           'xmlHashes': xml_hashes, 'staticSha256': sha(target / 'spotbugsXml.xml'), 'coverageXmlSha256': sha(cov)}
    additions = {tuple(v) for v in data['newCases']}
    need(len(oldcases) == 3717 and len(additions) == 4 and not oldcases & additions and cases == oldcases | additions
         and len(cases) == 3721 and sum(v['suites'] for v in modules.values()) == 545, 'all3717 exact aliases retained plus four independent methods')
    moves = {
        'batch:dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery': 'bootstrap:dev/codex/schubert/nk/bootstrap/SystemManagerObservation',
        'batch:dev/codex/schubert/nk/batch/platform/LinuxSystemdSession': 'bootstrap:dev/codex/schubert/nk/bootstrap/LinuxSystemdSession'}
    def family(name, stem): return name == stem + '.class' or name.startswith(stem + '$')
    def relocated(name):
        hits = [(a, b) for a, b in moves.items() if family(name, a)]
        need(len(hits) <= 1, 'one exact family alias')
        return hits[0][1] + name[len(hits[0][0]):] if hits else name
    added_enum = 'bootstrap:dev/codex/schubert/nk/bootstrap/SystemManagerObservation$Service.class'
    need(len(oldphysical) == 1643 and len(physical) == 1644 and set(physical) == {relocated(n) for n in oldphysical} | {added_enum}, 'all1644 exact relocation inventory and one fixed Service enum')
    modifications = []; immutable = 0
    mutable = ['bootstrap:dev/codex/schubert/nk/bootstrap/ChildStartupContext', 'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext']
    for name, digest in oldphysical.items():
        newname = relocated(name); newdigest = physical[newname]
        if name != newname or digest != newdigest:
            need(name != newname or any(family(name, prefix) for prefix in mutable), 'only four registered logical Main families differ')
            modifications.append({'oldClass': name, 'class': newname, 'oldSha256': digest, 'newSha256': newdigest, 'action': 'RELOCATED' if name != newname else 'MODIFIED'})
        else: immutable += 1
    modifications.append({'oldClass': None, 'class': added_enum, 'oldSha256': None, 'newSha256': physical[added_enum], 'action': 'ADDED_FIXED_ENUM'})
    need(all(sha(source / n) == h for n, h in begin['inputs'].items()), 'all original inputs remain immutable after independent qualification')
    return {'actualExit': 0, 'productionSource': data['source'], 'sourceSnapshot': begin['sourceSnapshotHead'],
            'sourceArchiveSha256': begin['sourceArchiveSha256'], 'tests': 3721, 'suites': 545, 'mainClasses': 1644,
            'FESFlakyNotRun': 0, 'staticSixModules': 0, 'allSixMainBuildsPassed': True,
            'allOriginalCaseIdentitiesRetained': True, 'testClassAliases': data['aliases'], 'newCases': data['newCases'],
            'modules': modules, 'coverage': coverage, 'jarHashes': jars, 'allPhysicalMainSha256': physical,
            'changedClasses': modifications, 'unchangedPhysicalClasses': immutable,
            'oldNativeImported': False, 'candidateNativePending': True, 'F03Accepted': False, 'formalAccepted': False,
            'global100': False, 'serverManifestSha256': sha(out / 'manifest.safe.json')}


def main():
    original = json.loads((W / 'pg4420-shared-manager-six-v1/manifest.safe.json').read_bytes())
    if original['actualExit'] != 0: raise ValueError('original whole genuine0 required; do not rerun it')
    prior = json.loads((W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    before = json.loads((W / 'pg4420-shared-manager-six-v1/begin.safe.json').read_bytes())
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=ROOT):
        raise ValueError('same actual fixed Main/Tests before qualification')
    data = {'source': SOURCE, 'priorManifestSha256': prior['serverManifestSha256'], 'priorJarHashes': prior['jarHashes'],
            'archiveSha256': before['archiveSha256'], 'aliases': ALIASES, 'newCases': NEW_CASES,
            'allMainSourceSha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw = inspect.getsource(qualify) + '\nprint(json.dumps(qualify(' + repr(data) + ')))\n'
    from pyflakes.api import check
    # imports used inside the saved standalone entry, not the module factory namespace
    raw = 'import json\n' + raw
    if check(raw, '<whole original independent>'): raise ValueError('whole standalone static0')
    out = W / 'pg4422-shared-manager-whole-qualified-v1'; os.umask(0o077); out.mkdir(mode=0o700)
    (out / 'qualify.private.py').write_text(raw)
    status, output = run("python3 -B - <<'PG4422'\n" + raw + '\nPG4422', timeout=180)
    (out / 'observer.private.log').write_text(output)
    result = {'actualExit': status, 'source': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if status == 0: result['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); print(json.dumps(result)); return status


if __name__ == '__main__':
    raise SystemExit(main())
