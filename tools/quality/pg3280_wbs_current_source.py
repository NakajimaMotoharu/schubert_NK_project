"""Stage current-a9 WBS measurement after actual3701/native28; acceptance credit0.

Only seven fixed read-only files from approved aru. Raw XML stays private;
public session IDs are hashed, all semantic counter content must be unchanged.
"""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import lan_server
from pg1446_current_cold_stage import W
from pg3274_header_group_full_six import ROOT, SOURCE
from wbs_progress_audit import unique_object, verify

MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
COUNTERS = ('LINE', 'METHOD', 'CLASS', 'BRANCH')
REMOTE = '/home/mini/schubert-nk-pgpt/runs/PG3278-native-join-v1'
PUBLIC = Path('evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3278-current-WBS-source-v1')
OUT = W / 'pg3280-wbs-current-source-v1'
PMO = ROOT / 'documents/400_PGPT/470_PMO'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def authorities(full, native):
    require(type(full['actualExit']) is int and full['actualExit'] == 0
            and type(native['actualExit']) is int and native['actualExit'] == 0, 'actual authorities0 required')
    f, n = full['result'], native['result']
    require(f['productionSource'] == n['productionSource'] == SOURCE, 'same actual production source required')
    for key, expected in {'actualExit': 0, 'tests': 3701, 'suites': 542, 'mainClasses': 1643,
                          'FESFlakyNotRun': 0, 'staticSixModules': 0}.items():
        require(type(f[key]) is int and f[key] == expected, 'exact full field required: ' + key)
    for key, expected in {'actualExit': 0, 'qualifiedFullTests': 3701, 'qualifiedNativeStreams': 28,
                          'distinctSessions': 28, 'mainClassesIdentical': 1643,
                          'allResourceMetaMembersIdentical': 79, 'VMOperations': 0}.items():
        require(type(n[key]) is int and n[key] == expected, 'exact native field required: ' + key)
    require(n['oldSourceNativeImported'] in (False, 0), 'no foreign-source import required')
    require(set(f['modules']) == set(n['xmlHashes']) == set(n['moduleCounters']) == set(MODULES), 'all six complete modules required')
    require(sum(m['tests'] for m in f['modules'].values()) == 3701
            and f['modules']['protocol']['tests'] == 84 and f['modules']['batch']['tests'] == 1299, 'exact real new Test set required')
    return f, n


def report_counters(root):
    return {n.get('type'): {'missed': int(n.get('missed')), 'covered': int(n.get('covered'))}
            for n in root.findall('counter')}


def semantic_report(root):
    clean = copy.deepcopy(root)
    for session in clean.findall('sessioninfo'):
        session.set('id', '')
    return ET.tostring(clean, encoding='utf-8')


def redact_report(raw, expected):
    root = ET.fromstring(raw)
    require(root.tag == 'report' and report_counters(root) == expected, 'exact original native report counters required')
    before = semantic_report(root); ids = []
    for session in root.findall('sessioninfo'):
        value = session.get('id')
        require(isinstance(value, str) and value, 'technical session ID required')
        ids.append(value)
        session.set('id', 'SHA256:' + sha(value.encode()))
    public = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    require(semantic_report(ET.fromstring(public)) == before, 'counter/class/method/line or timestamp drift forbidden')
    require(all(s.get('id').startswith('SHA256:') for s in ET.fromstring(public).findall('sessioninfo')), 'all public technical sessions redacted')
    return public, {'rawSha256': sha(raw), 'publicSha256': sha(public), 'semanticSha256': sha(before),
                    'redactedSessionRecords': len(ids), 'counterContentUnchanged': True}


def fetch_fixed(name, target):
    allowed = {'manifest.safe.json', *(m + '-union.xml' for m in MODULES)}
    require(name in allowed and '/' not in name, 'fixed seven remote evidence leaves only')
    require(target.parent.resolve().is_relative_to(W.resolve()) and not target.exists() and not target.is_symlink(), 'new-only private receive path required')
    key = lan_server.pinned_key()  # Credentials are read only after current pin authentication.
    with tempfile.TemporaryDirectory(prefix='pg3280-pinned-') as directory:
        known = Path(directory) / 'known_hosts'; known.write_text(key + '\n'); known.chmod(0o600)
        remote_shell = shlex.join(['ssh', *lan_server.ssh_options(known)])
        code, output = lan_server.authenticated(['rsync', '-a', '--partial', '--stats', '--secluded-args',
                                                '-e', remote_shell, f'mini@{lan_server.HOST}:{REMOTE}/{name}', str(target)], known, 120)
    with target.with_suffix(target.suffix + '.transfer.private.log').open('x') as stream:
        stream.write(output)
    require(code == 0 and target.is_file() and not target.is_symlink(), 'actual complete immutable evidence transfer required')
    target.chmod(0o600)


def runtime_stage_proofs():
    # Historical executions on THIS source, not current live capabilities. Do
    # not replay them to fill a management binding, or transfer old-source A01.
    definitions = {
        'parent': ('pg3130-browser-resume-terminal-v1', ['genuineParentDone', 'genuinePid1StartDone', 'genuineRootDone', 'newActivationSameRunCutoff', 'normalUnit0or10']),
        'full': ('pg3134-browser-resume-full-seal-v1', ['currentFourOwnedLive', 'sqlOracleQualified']),
        'browser': ('pg3184-browser-business-actual-v3', ['sameFourOrdinaryOwnersBeforeAfter', 'all24IndependentPost']),
        'stop': ('pg3156-browser-business-owned-post-v1', ['all24UnchangedTwice', 'allActorGone', 'allClientAdvisoryFlock0', 'allTenUnitsKernelEmpty', 'whole187SignedArtifactBytesVerified', 'normalCurrentOwnedStopScopesSealed']),
        'retired': ('pg3198-browser-runtime-retirement-post-v1', ['all24UnchangedTwice', 'allActorGone', 'allClientAdvisoryFlock0', 'allTenUnitsKernelEmpty', 'whole187SignedArtifactBytesVerified', 'normalCurrentRetirementScopesSealed', 'exactRuntimeEntryRetired'])}
    records = {}
    for label, (slot, flags) in definitions.items():
        path = W / slot / 'manifest.safe.json'; data = read(path)
        require(type(data['actualExit']) is int and data['actualExit'] == 0 and data['productionSource'] == SOURCE,
                'actual same-source runtime stage authority required')
        require(all(data[k] is True for k in flags), 'complete exact runtime stage flags required')
        record = {'source': SOURCE, 'run': slot, 'receiptSha256': sha(path.read_bytes()),
                  'actualExit': 0, 'verifiedFlags': flags, 'currentLiveAuthority': False}
        if label == 'parent':
            require(data['completionCode'] == 10 and data['completionOutcome'] == 'WARNING'
                    and 0 < data['elapsedSeconds'] < 1800, 'actual genuine parent10 inside original budget required')
            record.update(completionCode=10, completionOutcome='WARNING', elapsedSeconds=data['elapsedSeconds'],
                          managerExitCodeObserved=data['managerExitCodeObserved'])
        elif label == 'full':
            require(data['signedArtifacts'] == 187, 'actual all187 signed artifacts required')
            record['signedArtifacts'] = 187
        elif label == 'browser':
            tls = data['independentNormalTlsBeforeAfter']
            require(data['plannedCases'] == data['passedCases'] == 12
                    and tls['normalChainAndIpSanValidated'] is True and tls['sameOwnedCaddyListener'] is True,
                    'actual finite12 and independent owned TLS required')
            record.update(finiteBrowserCases=12, independentOwnedTls=True, fullChrA01=False)
        records[label] = record
    return records


def prepare():
    os.umask(0o077)
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean source required')
    full = read(W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json')
    native = read(W / 'pg3278-header-group-native-qualified-v1/manifest.safe.json')
    f, n = authorities(full, native)
    runtime = runtime_stage_proofs()
    before = verify()  # Strict old-source binding must still be valid; no bypass.
    inventory = read(PMO / '485_WBS網羅性・受入対応.json')
    paths = [a['path'] for a in inventory['artifacts']]
    require(len(paths) == 941 and not subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', *paths], cwd=ROOT), 'all941 artifacts byte-identical to production source required')
    require(not (ROOT / PUBLIC).exists(), 'new-only public measurement evidence required')
    OUT.mkdir(mode=0o700); rawdir = OUT / 'raw'; rawdir.mkdir(mode=0o700)
    old_hashes = {}
    for name in ['485_WBS網羅性・受入対応.json', '486_WBS現行実績.json']:
        data = (PMO / name).read_bytes(); old_hashes[name] = sha(data)
        (OUT / ('before-' + name)).write_bytes(data)
    fetch_fixed('manifest.safe.json', rawdir / 'manifest.safe.json')
    require(sha((rawdir / 'manifest.safe.json').read_bytes()) == native['manifestSha256']
            and read(rawdir / 'manifest.safe.json') == n, 'exact original native authority hash/result required')
    projections = {}
    for module in MODULES:
        target = rawdir / (module + '-union.xml'); fetch_fixed(target.name, target)
        data = target.read_bytes(); require(sha(data) == n['xmlHashes'][module], 'exact raw XML hash required')
        projections[module] = redact_report(data, n['moduleCounters'][module])
    public_root = ROOT / PUBLIC; public_root.mkdir(parents=True, mode=0o700)
    modules = []
    for module, (data, redaction) in projections.items():
        path = public_root / 'coverage' / module / 'site/jacoco/jacoco.xml'; path.parent.mkdir(parents=True, mode=0o700)
        with path.open('xb') as stream:
            stream.write(data)
        modules.append({'module': module, 'coverageXmlSha256': sha(data), 'rawCoverageXmlSha256': n['xmlHashes'][module],
                        'pt': f['modules'][module], 'redaction': redaction})
    value = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3278-current-WBS-source-v1',
             'kind': 'SAME_BYTE_HOST_NATIVE_WBS_MEASUREMENT_NOT_ACCEPTANCE', 'FES': 0, 'staticIssues': 0,
             'sourceSnapshot': f['sourceSnapshot'], 'tests': 3701, 'suites': 542, 'mainClasses': 1643,
             'coverageRoot': str(PUBLIC / 'coverage'), 'modules': modules,
             'fullPrivateReceiptSha256': sha((W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json').read_bytes()),
             'nativePrivateReceiptSha256': sha((W / 'pg3278-header-group-native-qualified-v1/manifest.safe.json').read_bytes()),
             'originalNativeManifestSha256': native['manifestSha256'], 'nativeStreams': 28,
             'beforeFileHashes': old_hashes, 'beforeSource': inventory['source'], 'beforeBinding': inventory['measurementBindings'],
             'all941ArtifactChanges': 0, 'semanticCoverageContentChanged': False,
             'runtimeStageProofs': runtime,
             'runtimeVerifiedRows': ['WBS-N05', 'WBS-N06', 'WBS-N07', 'WBS-N08', 'WBS-N09', 'WBS-N10', 'WBS-N12', 'WBS-N14'],
             'unmappedHistoricalRuntimeRequiresRecheck': ['WBS-N13', 'WBS-CHR-A01'],
             'scopeChanged': False, 'acceptedLeafDelta': 0, 'formalAccepted': False,
             'effortPercent': None, 'secretsSaved': False, 'vmActions': 0, 'mavenReissued': False,
             'stagedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    public_manifest = public_root / 'manifest.json'
    with public_manifest.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    with (OUT / 'manifest.safe.json').open('x') as stream:
        json.dump({'actualExit': 0, 'publicManifest': str(PUBLIC / 'manifest.json'),
                   'publicManifestSha256': sha(public_manifest.read_bytes()), 'beforeFileHashes': old_hashes,
                   'oldAuditAccepted': before['acceptedTasks'], 'applied': False}, stream, sort_keys=True)
    print(json.dumps({'actualExit': 0, 'stagedModules': len(modules), 'source': SOURCE,
                      'sourceBindingApplied': False, 'acceptedLeafDelta': 0, 'publicManifestSha256': sha(public_manifest.read_bytes())}))
    return 0


if __name__ == '__main__':
    raise SystemExit(prepare())
