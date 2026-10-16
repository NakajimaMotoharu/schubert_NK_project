"""Public new-Main whole/signature/static facts only; no old-native or formal promotion."""
import hashlib
import json
import shlex
from lan_server import run
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, require


def main():
    qp = W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json'; qualified = json.loads(qp.read_bytes()); q = qualified['result']
    sp = W / 'pg3976-candidate-build-v1.safe.json'; signed = json.loads(sp.read_bytes())
    dp = W / 'pg3970-current-main-static-v1/manifest.safe.json'; diagnostic = json.loads(dp.read_bytes()); d = diagnostic['result']
    require(qualified['actualExit'] == signed['actualExit'] == diagnostic['actualExit'] == 0 and q['productionSource'] == signed['candidateSource'] == d['mainGitSource'] == SOURCE, 'genuine same-source whole signature and fixed diagnostic')
    require((q['tests'], q['suites'], q['mainClasses'], q['FESFlakyNotRun'], q['staticSixModules']) == (3717, 545, 1643, 0, 0), 'exact new whole, not sum of selected/history')
    require(signed['hostGateSha256'] == hashlib.sha256(qp.read_bytes()).hexdigest() and signed['signatureVerified'] and signed['candidateNotDeployed'] and not q['oldNativeImported'], 'exact independent host gate and unused signature')
    code = """from pathlib import Path
import hashlib,json
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3966-six-v1/manifest.safe.json');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
v=json.loads(raw);print(json.dumps({k:v[k]for k in ['run','actualExit','mavenExit','startUTC','endUTC','elapsedSeconds','sourceSnapshotHead','productionSource','sourceInputsUnchanged','logSha256']}))
"""
    status, output = run('python3 -c ' + shlex.quote('EXPECTED=' + repr(q['serverManifestSha256']) + '\n' + code), timeout=30)
    require(status == 0, 'original unchanged genuine whole receipt')
    original = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    require(original['actualExit'] == original['mavenExit'] == 0 and original['sourceInputsUnchanged'], 'actual completed original, never interrupted source result')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3974-literal-invariant-whole-signed-v1'; out.mkdir()
    objects = {'all-six-results.json': q['modules'], 'all-1643-main-sha256.json': q['allPhysicalMainSha256'], 'all-physical-changes.json': q['changedClasses'],
               'host-only-counters.json': q['coverage'], 'host-signature-receipt.json': signed}
    for name, value in objects.items(): (out / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    result = {'actualExit': 0, 'productionSource': SOURCE, 'sourceSnapshot': q['sourceSnapshot'], 'sourceArchiveSha256': q['sourceArchiveSha256'],
              'run': 'PG3974-literal-invariant-whole-signed-v1', 'testIds': ['PT-OPS-WHOLE-3966', 'PT-OPS-QUAL-3968', 'PT-OPS-SIGN-3976', 'PT-F03-STATIC-3970'],
              'branch': 'dev-foundation', 'os': 'Linux aru dedicated host', 'jdk': '25.0.4', 'maven': '3.9.12 offline worker1',
              'command': 'pg3966_literal_invariant_full_six.py (original only); pg3968_literal_invariant_whole_qualification.py; pg3976_literal_invariant_signed_candidate.py',
              'originalWhole': original, 'tests': 3717, 'suites': 545, 'mainClasses': 1643, 'allOriginal3716CasesRetained': True, 'newCases': q['newCases'],
              'changedMainSourceFiles': len({r['sourcePath'] for r in q['changedClasses']}), 'changedPhysicalMainClasses': len(q['changedClasses']),
              'jacocoAnalyzedClasses': sum(m['jacocoReportClasses'] for m in q['modules'].values()),
              'unreportedPhysicalClasses': sum(len(m['originalSameJaCoCoUnreportedPhysicalClasses']) for m in q['modules'].values()), 'newExclusions': 0,
              'hostOnlyMissed': {k: sum(v[k]['missed'] for v in q['coverage'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
              'nullAwayCompilerSpotBugsModules': 6, 'nullAwayCompilerSpotBugsIssues': 0, 'F03': {'rawFindings': d['pmd']['rawFindings'], 'pmdActualExit': d['pmd']['actualExit'], 'processingErrors': d['pmd']['processingErrors'], 'checkstyleFindings': d['checkstyle']['findings'], 'technicalDispositionsCurrentSource': None, 'applicableViolations': None, 'accepted': False},
              'candidateRelease': signed['release'], 'candidateBomSha256': signed['manifestSha256'], 'candidateSignatureSha256': signed['signatureSha256'],
              'artifacts': 187, 'schema': '028', 'migrations': 28, 'history': 29, 'signatureVerified': True, 'candidateDeployed': False, 'candidateNativePending': True,
              'oldNativeImported': False, 'formalAccepted': False, 'formalTests': 1964, 'formalScopes': 53, 'effortPercent': None, 'qa051Final': 'HELD',
              'global100': False, 'pgptAllComplete': False, 'vmActions': 0, 'relatedBug': ['BUG1330', 'YKT1096'],
              'independentQualificationSha256': q['qualificationManifestSha256'], 'signatureLocalReceiptSha256': hashlib.sha256(sp.read_bytes()).hexdigest(),
              'files': {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in objects}}
    (out / 'manifest.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['actualExit', 'tests', 'suites', 'mainClasses', 'changedMainSourceFiles', 'changedPhysicalMainClasses', 'candidateBomSha256', 'hostOnlyMissed']}))
    print(json.dumps({'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest()})); return 0


if __name__ == '__main__': raise SystemExit(main())
