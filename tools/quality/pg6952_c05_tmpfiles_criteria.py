"""Fixed boot-only tmpfiles declaration and original evidence; never execute tmpfiles/locks."""
import hashlib
import json
import os
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg6092_current3985_static_join import source_case_candidates

ARTIFACT = 'src/deployment/tmpfiles/schubert-nk-maintenance.conf'
DESIGN = 'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
# Independent SS namespace / pre-existing fixedProvisioningContract golden, not a production parser.
EXPECTED = (
 'd! /run/schubert-nk 0755 root root -',
 'd! /run/schubert-nk/maintenance 0700 root root -',
 'd! /run/schubert-nk/startup 0700 root root -',
 'd! /run/schubert-nk/backup-request 0700 root root -',
 'd! /run/schubert-nk/cleanup-request 0700 root root -',
 'd! /run/schubert-nk/expiry-request 0700 root root -',
 'f! /run/schubert-nk/maintenance.lock 0600 root root -',
 'f! /run/schubert-nk/startup-admission.lock 0600 root root -')
TESTS = {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MaintenanceFileLockTest.java':
   ('fixedProvisioningContract', 'PT-OPS-LOCK-008'),
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerificationTest.java':
   ('fullBom010OnlyFixedSignedBootProvisioningFileIsPermittedAndTamperRefuses', 'fullBom010')}


def verify_declaration(text):
    if '\r' in text or '\0' in text:
        raise ValueError('fixed LF public declaration')
    rows = tuple(' '.join(s.split()) for s in text.splitlines() if s.strip() and not s.lstrip().startswith('#'))
    if rows != EXPECTED:
        raise ValueError('exact boot-only6 directories/2 nontruncating locks/root modes/no aging/glob/cleanup')
    return rows


def main():
    qp, q, cases = read_whole()
    if sha(qp) != '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731':
        raise ValueError('frozen original4222')
    source = q['productionSource']
    design = subprocess.check_output(['git', 'show', 'origin/main:' + DESIGN], cwd=ROOT)
    if design != (ROOT / DESIGN).read_bytes():
        raise ValueError('canonical design/current document agree')
    run = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    if begin['source'] != source or sha(run / 'source.tar') != begin['archiveSha256']:
        raise ValueError('same original archive')
    inputs = {}
    with tarfile.open(run / 'source.tar') as tar:
        for path in (ARTIFACT, *TESTS):
            item = tar.getmember(path)
            raw = (ROOT / path).read_bytes()
            if (ROOT / path).is_symlink() or not item.isfile() or tar.extractfile(item).read() != raw or subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT) != raw:
                raise ValueError('all original/source/current input bytes fixed')
            inputs[path] = hashlib.sha256(raw).hexdigest()
    inv = json.loads((ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owned = [a for a in inv['currentPhysicalCandidate']['artifacts'] if a['owner'] == 'WBS-C05']
    if len(owned) != 1 or owned[0]['path'] != ARTIFACT or owned[0]['sha256'] != inputs[ARTIFACT]:
        raise ValueError('exact full C05 assigned artifact; no undisclosed extra source')
    rows = verify_declaration((ROOT / ARTIFACT).read_text())
    joined = []
    for path, (method, tid) in TESTS.items():
        text = (ROOT / path).read_text()
        digest = hashlib.sha256(source_case_candidates(text, method)[0].encode()).hexdigest()
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        found = [c for c in cases if c['class'] == cls and c['caseNameSha256'] == digest]
        if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML' or found[0]['source'] != source:
            raise ValueError('one actual original same-source case per policy/signature method')
        joined.append(dict(testId=tid, method=method, testPath=path, testSourceSha256=inputs[path], originalCase=found[0]))
    value = dict(actualExit=0, source=source, artifact=ARTIFACT, inputHashes=inputs, originalQualificationSha256=sha(qp),
      designMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
      designSha256=hashlib.sha256(design).hexdigest(), declaredRules=rows, directoryRules=6, fileRules=2,
      originalCases=joined, localEvidenceChecks=['WBS-C05:scope'],
      declaredBootProfileEvidenceReady=True, contractComplete=False, qualityComplete=False,
      unresolved=['C05 title covers other persistent directories/owner/mode/capacity; one assigned tmpfiles artifact alone does not prove these',
        'real boot provisioning, root UID/GID/ACL/nlink/FS/metadata/no-owner condition not reauthenticated',
        'actual lock/current/old run namespace never read or repaired; no distribution/restore claim'],
      tmpfilesCommandsIssued=0, actualRuntimePathsAccessed=0, permissionChanges=0, vmActions=0,
      originalTestsReplayed=False, testsExecutedByReader=0, javaPassCountAdded=0, acceptedLeafDelta=0,
      formalAccepted=False, effortPercent=None, ptAlternativeCompleted=0,
      toolSha256=sha(ROOT / 'tools/quality/pg6952_c05_tmpfiles_criteria.py'))
    out = BASE / 'PG6952-c05-tmpfiles-current-v1'
    os.umask(0o077)
    out.mkdir()
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(out / 'manifest.json'), rules=8,
      originalCases=2, localEvidenceChecks=1, contractComplete=False, qualityComplete=False)))


if __name__ == '__main__':
    main()
