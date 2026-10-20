"""Read/fetch only original PG6040 generated artifacts; never start PT, services or a VM."""
import base64
import hashlib
import inspect
import json
import os
import shlex
import subprocess
import tarfile
from pathlib import PurePosixPath
from pyflakes.api import check
from lan_server import run, copy
from pg6040_remaining33_whole import SOURCE, ROOT, W, BASE, SLOT as ORIGINAL, plan
from pg6030_error_boundary_public import NEW_TEST, NEW_METHODS

SLOT = 'pg6042-original3976-artifacts-v2'
REMOTE = '/home/mini/schubert-nk-pgpt/transfer/PG6042-original3976-v2'
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def expected_case_keys(rows):
    result = {(r['module'], r['class'], r['caseNameSha256']) for r in rows}
    if len(result) != len(rows):
        raise ValueError('unique expected source Test identities,not invocation aliases')
    return result


def production_source_inputs(inputs):
    prefixes = tuple('src/schubert-nk-'+module+'/src/main/java/' for module in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'))
    return {k: v for k, v in inputs.items() if k.startswith(prefixes) and k.endswith('.java')}


def physical_difference(before, after, owners, expected_counts=(1666, 1667), expected_added=None):
    added = set(after)-set(before); removed = set(before)-set(after)
    interface = 'batch:dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$OperationEncoder.class'
    changed = {k for k in before.keys() & after.keys() if before[k] != after[k]}
    wanted = {interface} if expected_added is None else set(expected_added)
    if (len(before), len(after)) != tuple(expected_counts) or added != wanted or removed or not owners or not owners <= changed:
        raise ValueError('all old1666/current1667;declared interface1 and all23 changed owners')
    if any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changed | added):
        raise ValueError('no undeclared physical change outside23 source owners')
    return sorted(changed), sorted(added), len(after)-len(changed)-len(added)


def global_four100(modules):
    if set(modules) != {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}:
        raise ValueError('all six actual module reports required')
    for module in modules.values():
        counters = module['coverage']
        if any(k not in counters or type(counters[k]['missed']) is not int or type(counters[k]['covered']) is not int or counters[k]['missed'] < 0 or counters[k]['covered'] <= 0 for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')):
            raise ValueError('explicit actual four counters,no absent/0-as-100 inference')
    return all(module['coverage'][k]['missed'] == 0 for module in modules.values() for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH'))


def inspect_original(data):
    import base64
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import xml.etree.ElementTree as ET
    import zipfile
    base = Path('/home/mini/schubert-nk-pgpt')
    campaign = data.get('campaign', 'PG6040')
    expected_counts = tuple(data.get('expectedCounts', (3976, 593, 1667)))
    if (campaign, expected_counts, len(data['changedOwnerKeys'])) not in (('PG6040', (3976, 593, 1667), 23), ('PG6060', (3979, 594, 1667), 1), ('PG6088', (3985, 595, 1667), 5)):
        raise ValueError('explicit reviewed whole campaign/counts/owner inventory')
    source = base/('source-full-'+campaign); out = base/('runs/'+campaign+'-six-v1')
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    original = json.loads((out/'manifest.safe.json').read_bytes())
    returned = data['returnedOriginalResult']
    terminal_fields = ('run', 'actualExit', 'mavenExit', 'sourceInputsUnchanged', 'sourceSnapshotHead', 'productionSource', 'tests', 'expectedTests', 'startUTC', 'endUTC', 'elapsedSeconds', 'logSha256')
    if any(original[k] != returned[k] for k in terminal_fields) or original['run'] != campaign+'-six-v1' or original['productionSource'] != data['source'] or original['sourceSnapshotHead'] != data['source']:
        raise ValueError('exact original returned terminal/run/source,not a begin or another job')
    if not (original['actualExit'] == original['mavenExit'] == 0 and original['tests'] == expected_counts[0] and not original['issues'] and original['sourceInputsUnchanged']):
        raise ValueError('genuine original3976 terminal0 required')
    if digest(base/('transfer/'+campaign+'-source.tar')) != data['archiveSha256']:
        raise ValueError('original source archive identity')
    for name, expected in data['allSourceInputs'].items():
        path = source/name
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('each archived Main/Test/oracle/build input stays fixed')
    timing = json.loads((out/'format-before-pt.safe.json').read_bytes())
    format_proof = json.loads((out/'format-preflight.safe.json').read_bytes())
    begin = json.loads((out/'begin.safe.json').read_bytes())
    if not (format_proof['actualExit'] == 0 and format_proof['sameInputs'] is True and format_proof['testsIssued'] is False
            and format_proof['command'][-1:] == ['spotless:check']
            and format_proof['command'][format_proof['command'].index('-pl')+1] == ','.join('src/schubert-nk-'+m for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'))
            and timing['allSixFormatBeforeAnyPt'] is True and timing['sourceInputsUnchanged'] is True
            and timing['formatProofSha256'] == digest(out/'format-preflight.safe.json')
            and timing['formatCompletedMtimeNs'] <= timing['ptStartEpochNs']
            and begin['sourceSnapshotHead'] == begin['productionSource'] == data['source']
            and begin['sourceArchiveSha256'] == data['archiveSha256'] and begin['inputs'] == data['allSourceInputs']):
        raise ValueError('durable allsix format-before-PT/source/archive/complete input proof')
    start = timing['ptStartEpochNs']; end = int(datetime.datetime.fromisoformat(original['endUTC']).timestamp()*1e9)
    actual, physical, all_counts, modules, artifacts, coverage_artifacts = [], {}, {}, {}, {}, {}
    for module in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'):
        target = source/('src/schubert-nk-'+module+'/target'); xmls = {}; seen_suites = set()
        def check_time(path):
            if not start <= path.stat().st_mtime_ns <= end:
                raise ValueError('all original artifacts in this PT time window')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            check_time(path); tree = ET.parse(path).getroot(); klass = tree.get('name'); xhash = digest(path)
            if klass in seen_suites or len(tree.findall('testcase')) != int(tree.get('tests')) or any(int(tree.get(k)) for k in ('failures', 'errors', 'skipped')):
                raise ValueError('unique complete unskipped original suite')
            seen_suites.add(klass); xmls[path.name] = xhash; seen_cases = set()
            for ordinal, case in enumerate(tree.findall('testcase'), 1):
                name_hash = hashlib.sha256(case.get('name').encode()).hexdigest()
                if case.get('classname') != klass or name_hash in seen_cases or any(n.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
                    raise ValueError('no duplicate/failed/flaky/rerun/skipped case acceptance')
                seen_cases.add(name_hash)
                key = (module, klass, name_hash)
                actual.append(dict(testId='PT-WHOLE-'+hashlib.sha256(json.dumps(key).encode()).hexdigest(), module=module,
                    **{'class': klass}, caseNameSha256=name_hash, caseOrdinalInXml=ordinal,
                    sourceXml=path.name, xmlSha256=xhash, result='PASS_ORIGINAL_XML', source=data['source']))
        coverage = target/'site/jacoco/jacoco.xml'; spotbugs = target/'spotbugsXml.xml'
        for p in (coverage, spotbugs):
            check_time(p)
        if ET.parse(spotbugs).getroot().findall('BugInstance'):
            raise ValueError('all six original SpotBugs reports zero')
        croot = ET.parse(coverage).getroot()
        for node in croot.findall('package/class'):
            key = module+':'+node.get('name')+'.class'
            if key in all_counts:
                raise ValueError('unique physical coverage class')
            all_counts[key] = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in node.findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
        members = {p.relative_to(target/'classes').as_posix(): digest(p) for p in (target/'classes').rglob('*.class')}
        jarpath = target/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'); check_time(jarpath)
        with zipfile.ZipFile(jarpath) as jar:
            names = [n for n in jar.namelist() if n.endswith('.class')]
            if len(names) != len(set(names)) or {n: hashlib.sha256(jar.read(n)).hexdigest() for n in names} != members:
                raise ValueError('every actual Jar class equals original compiled Main')
        physical.update({module+':'+k: v for k, v in members.items()})
        modules[module] = dict(tests=sum(r['module'] == module for r in actual), suites=len(seen_suites), mainClasses=len(members),
            xmlHashes=xmls, coverageXmlSha256=digest(coverage), staticSha256=digest(spotbugs), jarSha256=digest(jarpath),
            coverage={c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in croot.findall('counter')})
        prior = original['modules'][module]
        if not (prior['xmlHashes'] == xmls and prior['mainClassHashes'] == members and prior['coverage'] == modules[module]['coverage']
                and prior['tests'] == modules[module]['tests'] and prior['suites'] == len(seen_suites)
                and prior['mainClasses'] == len(members) and prior['staticIssues'] == 0
                and all(prior[k] == 0 for k in ('failures', 'errors', 'skipped', 'flaky'))):
            raise ValueError('every original module XML/Main/counter/zero failure receipt exact')
        # Only generated Main jars, never raw test logs/DB/key/runtime files.
        artifacts[module] = base64.b64encode(jarpath.read_bytes()).decode('ascii')
        if data.get('includeCoverageXml') is True:
            if campaign != 'PG6088':
                raise ValueError('only explicitly reviewed current3985 original coverage export')
            coverage_artifacts[module] = base64.b64encode(coverage.read_bytes()).decode('ascii')
    if expected_case_keys(actual) != expected_case_keys(data['expectedCases']) or (len(actual), sum(m['suites'] for m in modules.values()), len(physical)) != expected_counts or not set(all_counts) <= set(physical):
        raise ValueError('exact3976 semantic Test set/593 suites/all1667,not old PASS arithmetic')
    changed, added, unchanged = physical_difference(data['priorFullMain'], physical, set(data['changedOwnerKeys']), data.get('physicalExpectedCounts', (1666, 1667)), data.get('physicalExpectedAdded'))
    if data.get('expectedCurrentMain') is not None and physical != data['expectedCurrentMain']:
        raise ValueError('current selected and whole compiled Main byte maps exactly equal;PT successes not imported')
    targets = {key: all_counts[key] for key in data['changedOwnerKeys']}
    if len(targets) != len(data['changedOwnerKeys']) or any(set(v) != {'LINE', 'METHOD', 'CLASS', 'BRANCH'} for v in targets.values()):
        raise ValueError('all23 actual outer counter sets explicit,no missing-as-zero')
    main_inputs = production_source_inputs(data['allSourceInputs'])
    if len(main_inputs) != 851 or main_inputs != data['expectedMainSourceInputs']:
        raise ValueError('all851 actual Main source inputs explicit')
    value = dict(actualExit=0, productionSource=data['source'], sourceSnapshot=data['source'], tests=expected_counts[0], suites=expected_counts[1], mainClasses=expected_counts[2],
        serverManifestSha256=digest(out/'manifest.safe.json'), sourceArchiveSha256=data['archiveSha256'], returnedOriginalTerminalExact=True,
        FESFlakyNotRun=0, staticSixModules=0, modules=modules, allPhysicalMainSha256=physical, allActualClassCounters=all_counts,
        coveragePhysicalClassKeysNotInXml=sorted(set(physical)-set(all_counts)), changedOuterCounters=targets,
        changedPhysicalClasses=changed, addedPhysicalClasses=added, unchangedPhysicalClasses=unchanged,
        global100=global_four100(modules), allSixFormatBeforeAnyPt=True, formatBeforePtProofSha256=digest(out/'format-before-pt.safe.json'),
        command=begin['command'], os=dict(system=os.uname().sysname, release=os.uname().release, machine=os.uname().machine),
        logSha256=original['logSha256'],
        startUTC=original['startUTC'], endUTC=original['endUTC'], elapsedSeconds=original['elapsedSeconds'],
        currentOriginalXmlQualified=True, currentStaticPhysicalQualificationPending=True, formalAccepted=False, F03Accepted=False,
        sourceFiles=851, allSourceHashes=main_inputs,
        oldNativeImported=False, candidateNativePending=True, vmActions=0, refusedPtRetried=False, cases=actual, artifactJarBase64=artifacts)
    if coverage_artifacts:
        value['artifactCoverageXmlBase64'] = coverage_artifacts
    return value


def emitted(data_hash, remote=REMOTE):
    raw = 'import hashlib,json\nfrom pathlib import Path\np=Path('+repr(remote+'/input.safe.json')+')\n'
    raw += 'if hashlib.sha256(p.read_bytes()).hexdigest()!='+repr(data_hash)+':raise ValueError("fixed input bytes")\n'
    raw += inspect.getsource(expected_case_keys)+'\n'+inspect.getsource(production_source_inputs)+'\n'+inspect.getsource(physical_difference)+'\n'+inspect.getsource(global_four100)+'\n'+inspect.getsource(inspect_original)
    raw += '\nprint(json.dumps(inspect_original(json.loads(p.read_bytes()))))\n'
    if check(raw, '<complete original3976 artifact reader>'):
        raise ValueError('complete independent read-only reader namespace')
    compile(raw, '<read original6040 only>', 'exec')
    return raw


def main():
    original_path = W/ORIGINAL/'manifest.safe.json'; original = json.loads(original_path.read_bytes())
    if not (original['source'] == SOURCE and original['actualExit'] == 0 and original['result']['run'] == 'PG6040-six-v1'):
        raise ValueError('genuine original terminal required;never restart for collection')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('fixed original source/Test/gates')
    changes = subprocess.check_output(['git', 'diff', '--name-status', 'bc0cac2f6a7055b938f581e8cd163db398f8a656', SOURCE, '--', ':(glob)src/*/src/test/**'], cwd=ROOT, text=True).splitlines()
    if changes != ['A\tsrc/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisManagementEncoderBoundaryTest.java']:
        raise ValueError('all prior3973 Test/oracle bodies unchanged;only declared new3 source added')
    begin = json.loads((W/ORIGINAL/'begin.safe.json').read_bytes()); archive = W/ORIGINAL/'source.tar'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != begin['archiveSha256']:
        raise ValueError('original local source archive fixed')
    inputs = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():
                continue
            name = PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts or member.name in inputs:
                raise ValueError('unique regular archived source inputs only')
            inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldpath = BASE/'PG6014-current3973-cases/qualification.json'; oldcases = oldpath.with_name('cases.json')
    if hashlib.sha256(oldpath.read_bytes()).hexdigest() != '50285cd7e326b7709269caeca141abb287978e6e69fc3892863a1e1cc4a7e120' or hashlib.sha256(oldcases.read_bytes()).hexdigest() != 'f0173678ea06129e2224c5333b86c7dc7924a0f062032e5105679d4196f82219':
        raise ValueError('original prior physical/semantic identities only,not current PASS')
    expected = [{k: r[k] for k in ('module', 'class', 'caseNameSha256')} for r in json.loads(oldcases.read_bytes())]
    expected += [dict(module='batch', **{'class': NEW_TEST}, caseNameSha256=hashlib.sha256(name.encode()).hexdigest()) for name in sorted(NEW_METHODS)]
    owners = {r['path'].split('/')[1].removeprefix('schubert-nk-')+':'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}
    owners.add('web:dev/codex/schubert/nk/web/messaging/WebBrokerContexts.class')
    main_inputs = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(main_inputs) != 851 or main_inputs != production_source_inputs(inputs):
        raise ValueError('actual all851 Production/archive identity;CHR remains in full input check')
    data = dict(source=SOURCE, returnedOriginalResult=original['result'], archiveSha256=begin['archiveSha256'], allSourceInputs=inputs, expectedMainSourceInputs=main_inputs,
                expectedCases=expected, priorFullMain=json.loads(oldpath.read_bytes())['allPhysicalMainSha256'], changedOwnerKeys=sorted(owners))
    return collect(data, original_path, SLOT, REMOTE, 'PG6040-current3976-cases', 2, 'BUG1532/pg6042-original3976-artifacts-v1')


def collect(data, original_path, slot, remote, public_name, attempt=1, prior_failure=None):
    os.umask(0o077); out = W/slot; out.mkdir(mode=0o700); dp = out/'input.safe.json'
    with dp.open('x') as f:
        json.dump(data, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    raw = emitted(hashlib.sha256(dp.read_bytes()).hexdigest(), remote); payload = out/'read-original.private.py'
    with payload.open('x') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    code, _ = run('mkdir -m700 '+shlex.quote(remote), timeout=30)
    if code:
        raise ValueError('new reader namespace unavailable;inspect saved result,do not reissue')
    for local in (dp, payload):
        code, _ = copy(local, remote+'/', timeout=90)
        if code:
            raise ValueError('fixed reader/input transfer failed')
    code, text = run('sha256sum '+shlex.quote(remote+'/input.safe.json')+' '+shlex.quote(remote+'/read-original.private.py'), timeout=30)
    if code or any(hashlib.sha256(p.read_bytes()).hexdigest() not in text for p in (dp, payload)):
        raise ValueError('independent input/reader bytes confirmed before read')
    code, text = run('python3 -B '+shlex.quote(remote+'/read-original.private.py'), timeout=240)
    if code:
        with (out/'failure.private.log').open('x') as f:
            f.write(text)
        raise ValueError('original artifact reader failed;no PT replay or alternate route')
    value = json.loads(next(line for line in reversed(text.splitlines()) if line.startswith('{')))
    artifact_values = value.pop('artifactJarBase64'); jars = out/'jars'; jars.mkdir()
    if set(artifact_values) != set(MODULES):
        raise ValueError('only six generated original Main jars transferred')
    for module in MODULES:
        body = base64.b64decode(artifact_values[module], validate=True)
        if hashlib.sha256(body).hexdigest() != value['modules'][module]['jarSha256']:
            raise ValueError('original jar transport bytes must match verified receipt')
        with (jars/('schubert-nk-'+module+'.jar')).open('xb') as f:
            f.write(body); f.flush(); os.fsync(f.fileno())
    coverage_values = value.pop('artifactCoverageXmlBase64', None)
    cases = value.pop('cases'); public = BASE/public_name; public.mkdir()
    if coverage_values is not None:
        if data.get('campaign') != 'PG6088' or data.get('includeCoverageXml') is not True or set(coverage_values) != set(MODULES):
            raise ValueError('only six explicitly requested original current coverage reports')
        for module in MODULES:
            body = base64.b64decode(coverage_values[module], validate=True)
            if hashlib.sha256(body).hexdigest() != value['modules'][module]['coverageXmlSha256']:
                raise ValueError('original coverage transport hash equals independently verified report')
            ET.fromstring(body)
            folder = public/'coverage'/module/'site/jacoco'; folder.mkdir(parents=True)
            with (folder/'jacoco.xml').open('xb') as f:
                f.write(body); f.flush(); os.fsync(f.fileno())
        value['coverageRoot'] = (public/'coverage').relative_to(ROOT).as_posix()
    for filename, body in (('cases.json', cases), ('qualification.json', value)):
        with (public/filename).open('x') as f:
            json.dump(body, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    receipt = dict(actualExit=0, source=data['source'], originalManifestSha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
        payloadSha256=hashlib.sha256(payload.read_bytes()).hexdigest(), inputSha256=hashlib.sha256(dp.read_bytes()).hexdigest(),
        publicQualificationSha256=hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),
        publicCasesSha256=hashlib.sha256((public/'cases.json').read_bytes()).hexdigest(), originalArtifactJarsFetched=6,
        wholeReplayed=False, formalAccepted=False, currentStaticPhysicalQualificationPending=True, vmActions=0,
        readerAttempt=attempt, priorReaderFailurePreserved=prior_failure,
        originalCoverageXmlFetched=6 if coverage_values is not None else 0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(receipt, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(receipt)); print(json.dumps(dict(tests=value['tests'], suites=value['suites'], mainClasses=value['mainClasses'], global100=value['global100'])))
    return receipt


if __name__ == '__main__':
    main()
