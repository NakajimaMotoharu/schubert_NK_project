"""Public template byte/ENV/current-case audit; no real credential or distribution access."""
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg6092_current3985_static_join import source_case_candidates

PREFIX = 'src/deployment/config/'
OWNED = {'api.env.template', 'api.yml.template', 'batch.yml.template', 'common.yml.template',
 'inbox-inspector.env.template', 'web.env.template', 'web.yml.template'}
DESIGNS = (
 'documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md',
 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md')
ENV = b'SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk\n'
INSPECTOR = (b'NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:@PG_PORT@/@PG_DATABASE@\n'
 b'NK_INSPECTOR_FINGERPRINT_VERSIONS=@FINGERPRINT_VERSION_NAMES@\n')
TESTS = {
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java':
   ('opsApiCfg006ShippedTemplatesMatchApprovedDefaults', 'PT-OPS-API-CFG-006'),
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfigTest.java':
   ('opsWebCfg006ShippedTemplatesMatchApprovedDefaults', 'PT-OPS-WEB-CFG-006'),
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorStaticEnvironmentTest.java':
   ('canonicalFixtures', 'PT-OPS-CFG-001')}


def flat_scalar_keys(text):
    # Inventory of this fixed JSON-scalar subset only, never claim a general YAML/security parser.
    if '\r' in text or '\0' in text:
        raise ValueError('fixed LF public scalar template')
    result = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'"(nk\.[a-z0-9_.-]+)"\s*:\s*(.+)', line)
        if match is None or match[1] in result:
            raise ValueError('unique explicit nk scalar key, no ignored directive')
        value = json.loads(match[2])
        if type(value) not in (str, int) or value == '':
            raise ValueError('only the existing string/integer subset, no tag/object/array/null')
        result[match[1]] = type(value).__name__
    if not result:
        raise ValueError('nonempty public key inventory')
    return result


def fixed_environment(raw, inspector=False):
    if raw != (INSPECTOR if inspector else ENV):
        raise ValueError('exact approved nonsecret source template, no alias/extra JVM/secret/environment expansion')


def main():
    qp, q, cases = read_whole()
    if sha(qp) != '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731':
        raise ValueError('fixed original4222')
    source = q['productionSource']
    inv = json.loads((ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    declared = [a for a in inv['currentPhysicalCandidate']['artifacts'] if a['owner'] == 'WBS-C06']
    expected = {PREFIX + p for p in OWNED}
    if len(declared) != 7 or {a['path'] for a in declared} != expected:
        raise ValueError('all seven assigned public artifacts only')
    design = {}
    for path in DESIGNS:
        raw = subprocess.check_output(['git', 'show', 'origin/main:' + path], cwd=ROOT)
        if raw != (ROOT / path).read_bytes():
            raise ValueError('canonical design/current document agree')
        design[path] = hashlib.sha256(raw).hexdigest()
    run = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    if begin['source'] != source or sha(run / 'source.tar') != begin['archiveSha256']:
        raise ValueError('exact original archive')
    inputs = {}
    with tarfile.open(run / 'source.tar') as tar:
        for path in (*sorted(expected), *TESTS):
            item = tar.getmember(path)
            raw = (ROOT / path).read_bytes()
            if (ROOT / path).is_symlink() or not item.isfile() or tar.extractfile(item).read() != raw or subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT) != raw:
                raise ValueError('all template and original Test bytes fixed')
            inputs[path] = hashlib.sha256(raw).hexdigest()
    if any(inputs[a['path']] != a['sha256'] for a in declared):
        raise ValueError('current inventory exact hashes')
    for name in ('api.env.template', 'web.env.template'):
        fixed_environment((ROOT / (PREFIX + name)).read_bytes())
    fixed_environment((ROOT / (PREFIX + 'inbox-inspector.env.template')).read_bytes(), inspector=True)
    keys = {name: flat_scalar_keys((ROOT / (PREFIX + name)).read_text()) for name in sorted(OWNED) if name.endswith('.yml.template')}
    joined = []
    for path, (method, tid) in TESTS.items():
        text = (ROOT / path).read_text()
        digest = hashlib.sha256(source_case_candidates(text, method)[0].encode()).hexdigest()
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        found = [c for c in cases if c['class'] == cls and c['caseNameSha256'] == digest]
        if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML' or found[0]['source'] != source:
            raise ValueError('one original same-source deployment method per explicit TestID')
        joined.append(dict(testId=tid, method=method, testPath=path, sourceSha256=inputs[path], originalCase=found[0]))
    value = dict(actualExit=0, source=source, originalQualificationSha256=sha(qp), inputHashes=inputs,
      designMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(), designHashes=design,
      ownedArtifacts=7, fixedEnvironmentTemplates=3, yamlScalarKeyInventory=keys, originalCases=joined,
      localEvidenceChecks=['WBS-C06:scope'], contractComplete=False, qualityComplete=False,
      unresolved=['all declared setting values/role runtime use/key versions/rotation/distribution require full criteria mapping',
        'batch.yml has no direct shipped-template method in this bounded three-case set; other evidence not exhausted',
        'real root/service0600/private runtime/LoadCredential/ACL/nlink/mode/material and key separation not reauthenticated'],
      realCredentialMaterialRead=False, keyOperations=0, environmentChanged=False, distributionChanges=0,
      vmActions=0, actualServiceActions=0, originalTestsReplayed=False, testsExecutedByReader=0,
      javaPassCountAdded=0, measuredCoverageAdded=False, universalSecretScanClaimed=False,
      acceptedLeafDelta=0, formalAccepted=False, effortPercent=None, ptAlternativeCompleted=0,
      toolSha256=sha(ROOT / 'tools/quality/pg6954_c06_public_config_scope.py'))
    out = BASE / 'PG6954-c06-public-config-current-v1'
    os.umask(0o077)
    out.mkdir()
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(out / 'manifest.json'), artifacts=7,
      fixedEnvTemplates=3, originalCases=3, localEvidenceChecks=1, contractComplete=False, qualityComplete=False)))


if __name__ == '__main__':
    main()
