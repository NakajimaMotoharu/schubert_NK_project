"""Current systemd source-scope matrix only; never query or operate a manager/Unit."""
import hashlib
import json
import os
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates

DESIGN = 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
PREFIX = 'src/deployment/systemd/'
TESTS = {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootServiceUnitTest.java': ('schubert-nk-api.service.template', 'schubert-nk-web.service.template'),
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceUnitTest.java': ('schubert-nk-morning-controller.service.template', 'schubert-nk-morning.target.template'),
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/CleanupServiceUnitTest.java': ('schubert-nk-cleanup.service.template', 'schubert-nk-expiry-cleanup.service.template'),
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ArtemisServiceUnitTest.java': ('artemis.service',),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDeploymentTest.java': ('schubert-nk-inbox-inspector.service', 'optional/inbox-inspector-context-previous.conf', 'optional/inbox-inspector-response-previous.conf')}
PROFILES = {
 'artemis.service': 'schubert-artemis', 'schubert-nk-api.service.template': 'schubert-api',
 'schubert-nk-web.service.template': 'schubert-web', 'schubert-nk-backup.service.template': 'schubert-backup',
 'schubert-nk-bootstrap-admin.service.template': 'schubert-api', 'schubert-nk-cleanup.service.template': 'root',
 'schubert-nk-expiry-cleanup.service.template': 'root', 'schubert-nk-morning-controller.service.template': 'root',
 'schubert-nk-inbox-inspector.service': 'schubert-inbox-inspector'}


def directives(text):
    section, result = None, []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('[') and line.endswith(']') and len(line) > 2:
            section = line[1:-1]
            continue
        key, separator, value = line.partition('=')
        if section is None or not separator or not key.strip():
            raise ValueError('explicit section/key/value; do not normalize malformed configuration')
        result.append((section, key.strip(), value.strip()))
    if not result:
        raise ValueError('nonempty declared source')
    return result


def values(rows, section, key):
    return [v for s, k, v in rows if (s, k) == (section, key)]


def common_profile(name, rows):
    # Source sanity subset only; no inference about inherited/effective properties or kernel identity.
    user = PROFILES[name]
    for key, expected in (('User', [user]), ('Group', [user]), ('ProtectSystem', ['strict']), ('SendSIGKILL', ['no'])):
        if values(rows, 'Service', key) != expected:
            raise ValueError('fixed declared dedicated identity/strict/no auto-kill profile')
    if values(rows, 'Service', 'NoNewPrivileges') not in (['true'], ['yes']):
        raise ValueError('declared NNP required, never effective/NSS proof')
    starts = values(rows, 'Service', 'ExecStart')
    if len(starts) != 1 or not starts[0] or starts[0].startswith('+'):
        raise ValueError('one real nonempty declared entry, no all-hardening bypass')
    if any(k.startswith('Condition') for s, k, _ in rows if s == 'Unit'):
        raise ValueError('do not substitute a skipped condition for actual child completion')


def main():
    qp, q, cases = read_whole()
    if sha(qp) != '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731':
        raise ValueError('fixed current original4222')
    source = q['productionSource']
    pmo = ROOT / 'documents/400_PGPT/470_PMO'
    inventory = json.loads((pmo / '485_WBS網羅性・受入対応.json').read_bytes())
    owned_rows = [a for a in inventory['currentPhysicalCandidate']['artifacts'] if a['owner'] == 'WBS-C02']
    owned = {a['path']: a['sha256'] for a in owned_rows}
    disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / PREFIX).rglob('*') if p.is_file()}
    if len(owned_rows) != 14 or len(owned) != 14 or disk != set(owned):
        raise ValueError('all14 actual owned sources only, no missing/duplicate/extra/alias artifact')
    design = subprocess.check_output(['git', 'show', 'origin/main:' + DESIGN], cwd=ROOT)
    if design != (ROOT / DESIGN).read_bytes():
        raise ValueError('canonical design/current document match')
    run = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    if begin['source'] != source or sha(run / 'source.tar') != begin['archiveSha256']:
        raise ValueError('exact original archive')
    hashes = {}
    with tarfile.open(run / 'source.tar') as tar:
        for path in (*sorted(owned), *sorted(TESTS)):
            item = tar.getmember(path)
            raw = (ROOT / path).read_bytes()
            if (ROOT / path).is_symlink() or not item.isfile() or tar.extractfile(item).read() != raw or subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT) != raw:
                raise ValueError('regular original/current/git source bytes fixed')
            hashes[path] = hashlib.sha256(raw).hexdigest()
    if {p: hashes[p] for p in owned} != owned:
        raise ValueError('each current inventory source hash exact')
    units = {}
    for path in sorted(owned):
        rows = directives((ROOT / path).read_text())
        name = path.removeprefix(PREFIX)
        if name in PROFILES:
            common_profile(name, rows)
        units[name] = dict(path=path, sha256=hashes[path], orderedDirectives=rows,
          sourceSanitySubsetChecked=name in PROFILES, effectiveOrRuntimeVerified=False)
    joined = []
    for path, artifacts in TESTS.items():
        text = (ROOT / path).read_text()
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        rows = []
        for method in ordinary_names(text):
            digest = hashlib.sha256(source_case_candidates(text, method)[0].encode()).hexdigest()
            found = [c for c in cases if c['class'] == cls and c['caseNameSha256'] == digest]
            if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML' or found[0]['source'] != source:
                raise ValueError('one current original case per existing independent method')
            rows.append(dict(method=method, originalCase=found[0]))
        joined.append(dict(testPath=path, testSourceSha256=hashes[path], relatedOwnedArtifacts=[PREFIX + a for a in artifacts], cases=rows))
    if sum(len(t['cases']) for t in joined) != 22:
        raise ValueError('actual22 independent original methods, no vector counting')
    mapped = {p for t in joined for p in t['relatedOwnedArtifacts']}
    if not mapped <= set(owned) or len(mapped) != 10:
        raise ValueError('ten explicitly related source files; remaining mapping is not silently covered')
    caddy = [r for n, u in units.items() if n.startswith('caddy.service.d/') for r in u['orderedDirectives']]
    dependency_declarations = {k: values(caddy, 'Unit', k) for k in ('After', 'Requires')}
    result = dict(actualExit=0, source=source, originalQualificationSha256=sha(qp), originalArchiveSha256=begin['archiveSha256'],
      designMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
      designSha256=hashlib.sha256(design).hexdigest(), ownedArtifactCount=14, sourceSanityProfiles=9,
      units=units, referencedOriginalTests=joined, originalCasesReferenced=22, explicitlyRelatedArtifacts=10,
      notMappedByThisBoundedCaseSet=sorted(set(owned) - mapped),
      caddyDropinDeclaredDependencies=dependency_declarations,
      unresolved=['Caddy base/package composition and SS342 section4.1 After/Requires Web need separate proof; do not infer missing/present effective dependency from dropins alone',
        'four files have no explicit relation in this bounded five-class case matrix; other evidence not exhaustively classified',
        'full literal contract/profile, systemd native syntax/combined effective/NSS/permission/runtime qualification not complete'],
      localEvidenceChecks=['WBS-C02:scope'], contractComplete=False, qualityComplete=False,
      systemdCommandsIssued=0, actualServiceActions=0, vmActions=0, credentialMaterialRead=False,
      originalTestsReplayed=False, testsExecutedByReader=0, javaPassCountAdded=0, acceptedLeafDelta=0,
      formalAccepted=False, effortPercent=None, ptAlternativeCompleted=0,
      toolSha256=sha(ROOT / 'tools/quality/pg6950_c02_scope_matrix.py'))
    out = BASE / 'PG6950-c02-current-scope-v1'
    os.umask(0o077)
    out.mkdir()
    with (out / 'manifest.json').open('x') as f:
        json.dump(result, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(out / 'manifest.json'), artifacts=14,
      originalCasesReferenced=22, relatedFiles=10, localEvidenceChecks=1, contractComplete=False, qualityComplete=False)))


if __name__ == '__main__':
    main()
