"""Current3716/545/all1643 and six same-source host/native reports; no raw session export."""
import base64
import hashlib
import json
import shlex
from lan_server import run
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require
from pg3280_wbs_current_source import redact_report


def main():
    full_path = W / 'pg3930-current-boundary-whole-qualified-v1/manifest.safe.json'
    native_path = W / 'pg3938-current-boundary-native-qualified-v1/manifest.safe.json'
    full = json.loads(full_path.read_bytes()); native = json.loads(native_path.read_bytes()); f, n = full['result'], native['result']
    require(full['actualExit'] == native['actualExit'] == f['actualExit'] == n['actualExit'] == 0 and f['productionSource'] == n['productionSource'] == SOURCE, 'genuine same-source successes')
    require((f['tests'], f['suites'], f['mainClasses'], f['FESFlakyNotRun'], f['staticSixModules']) == (3716, 545, 1643, 0, 0) and not f['changedClasses'], 'actual3716 and all physical Main identical')
    require(n['qualified3928Tests'] == 3716 and n['currentNativeStreams'] == 18 and n['validatedNativePoints'] == 20 and n['classByteMismatch'] == 0 and not n['oldNativeImported'] and not n['historicalSourceNativeImported'], 'same current original20/18 eligibility')
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3954-current-boundary-qualified-v1'; require(not public.exists(), 'new-only public capsule')
    projections = {}
    for module, expected in n['xmlHashes'].items():
        require(module in {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, 'closed module set')
        code = """import base64,hashlib
from pathlib import Path
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3938-native-v1')/(MODULE+'-union.xml');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;print(base64.b64encode(raw).decode())
"""
        status, output = run('python3 -c ' + shlex.quote('MODULE=' + repr(module) + '\nEXPECTED=' + repr(expected) + '\n' + code), timeout=30)
        require(status == 0, 'exact current coverage read')
        raw = base64.b64decode(output.strip(), validate=True); require(hashlib.sha256(raw).hexdigest() == expected, 'original raw report hash')
        projections[module] = redact_report(raw, n['moduleCounters'][module])
    require(len(projections) == 6, 'all six reports required')
    public.mkdir()
    modules = []
    for module, (raw, redaction) in projections.items():
        p = public / 'coverage' / module / 'site/jacoco/jacoco.xml'; p.parent.mkdir(parents=True); p.write_bytes(raw)
        modules.append({'module': module, 'coverageXmlSha256': hashlib.sha256(raw).hexdigest(), 'rawCoverageXmlSha256': n['xmlHashes'][module], 'pt': f['modules'][module], 'redaction': redaction})
    value = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3954-current-boundary-qualified-v1', 'tests': 3716, 'suites': 545, 'mainClasses': 1643,
             'sourceSnapshot': f['sourceSnapshot'], 'sourceArchiveSha256': f['sourceArchiveSha256'], 'FES': 0, 'staticIssues': 0,
             'staticIssuesScope': 'Compiler/NullAway/SpotBugs all six; F03 raw1840/technical304/unclassified1536 NOT_ACCEPTED',
             'F03Accepted': False, 'modules': modules, 'moduleCounters': n['moduleCounters'], 'coverageRoot': str(public.relative_to(ROOT) / 'coverage'),
             'remaining': {k: sum(v[k]['missed'] for v in n['moduleCounters'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
             'allOriginal3714CasesRetained': True, 'newCases': f['newCases'], 'all1643PhysicalMainUnchanged': True,
             'allPhysicalMainSha256': f['allPhysicalMainSha256'], 'nativeStreams': 18, 'nativePoints': 20, 'newVmOperations': 0, 'historicalSourceNativeImported': False,
             'wholeQualificationSha256': f['qualificationManifestSha256'], 'nativeServerManifestSha256': native['manifestSha256'],
             'wholeLocalReceiptSha256': hashlib.sha256(full_path.read_bytes()).hexdigest(), 'nativeLocalReceiptSha256': hashlib.sha256(native_path.read_bytes()).hexdigest(),
             'formalAccepted': False, 'acceptedLeafDelta': 0, 'effortPercent': None, 'rawSessionPublished': False}
    raw = (json.dumps(value, sort_keys=True) + '\n').encode(); (public / 'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit': 0, 'tests': 3716, 'suites': 545, 'mainClasses': 1643, 'remaining': value['remaining'], 'manifestSha256': hashlib.sha256(raw).hexdigest()}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
