"""One source-bound static finding disposition with original actual independent cipher witness."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
CODEC = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodecTest.java'


def main():
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    diagnostic = json.loads((public / 'PG3422-candidate-static/manifest.json').read_bytes())
    canary = json.loads((public / 'PG3424-crypto-rule-canary/manifest.json').read_bytes())
    assert diagnostic['actualExit'] == canary['actualExit'] == 0
    assert canary['dynamicValidationLabelFalsePositiveReproduced'] and canary['trueUnsafeCounterexampleStillDetected']
    assert hashlib.sha256((ROOT / CODEC).read_bytes()).hexdigest() == diagnostic['sourceSha256'][CODEC]
    old = '497fdb37f99529c7f233f5ef86030ab8590a902d'
    assert (ROOT / CODEC).read_bytes() == subprocess.check_output(['git', 'show', old + ':' + CODEC], cwd=ROOT)
    assert (ROOT / TEST).read_bytes() == subprocess.check_output(['git', 'show', old + ':' + TEST], cwd=ROOT)
    code = (ROOT / CODEC).read_text()
    assert 'this.currentKey = validateKey(currentKey, "currentKey");' in code
    assert 'return key.clone();' in code and 'Objects.requireNonNull(key, name);' in code
    command = """python3 - <<'PROOF'
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
b=Path('/home/mini/schubert-nk-pgpt');d=b/'runs/PG3422-candidate-static-v1/pmd.xml';r=E.parse(d).getroot();rows=[]
for f in r.findall('{*}file'):
 for v in f.findall('{*}violation'):
  if v.get('rule')=='HardCodedCryptoKey':rows.append({'file':str(Path(f.get('name')).relative_to(b/'source-PG3408-related-v1')),'rule':v.get('rule'),'beginline':int(v.get('beginline')),'begincolumn':int(v.get('begincolumn')),'message':(v.text or '').strip()})
assert len(rows)==1
whole=b/'runs/PG3398-six-v1';m=json.loads((whole/'manifest.safe.json').read_bytes());assert m['mavenExit']==m['actualExit']==0
x=whole/'api/surefire-reports/TEST-dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodecTest.xml';h=hashlib.sha256(x.read_bytes()).hexdigest();assert h==m['modules']['api']['xmlHashes'][x.name]
t=E.parse(x).getroot();method='fixedNonceCiphertextMatchesIndependentCompressionAndAadVector';cases=[c for c in t.findall('testcase')if c.get('name')==method];assert len(cases)==1 and not any(n.tag in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']for n in cases[0])
print(json.dumps({'finding':rows[0],'reportSha256':hashlib.sha256(d.read_bytes()).hexdigest(),'existingActualWitness':{'run':'PG3398-six-v1','method':method,'found':1,'FESFlaky':0,'xmlSha256':h,'sourceSnapshot':m['sourceSnapshotHead']}}))
PROOF"""
    rc, raw = run(command, timeout=30); assert rc == 0
    actual = json.loads(raw.strip()); assert actual['finding']['file'] == CODEC
    assert actual['reportSha256'] == diagnostic['results']['pmd']['reportSha256']
    line = actual['finding']['beginline']; assert '"currentKey"' in code.splitlines()[line - 1]
    result = {'dispositionId': 'STATIC-FP-001', 'candidateSource': diagnostic['candidateSource'],
              'finding': actual['finding'], 'sourceSha256': diagnostic['sourceSha256'][CODEC],
              'reportSha256': actual['reportSha256'], 'classification': 'FALSE_POSITIVE_VALIDATION_LABEL_NOT_KEY',
              'basis': 'Caller-provided byte array is length-checked and cloned; the currentKey literal names the argument for validation errors, never supplies cryptographic material. Exact unchanged source/component with original independent JCE/compression/AAD vector witness; same-rule dynamic-label canary and genuine unsafe array sensitivity both confirmed.',
              'sameRuleCanaryManifestSha256': hashlib.sha256((public / 'PG3424-crypto-rule-canary/manifest.json').read_bytes()).hexdigest(),
              'existingActualWitness': actual['existingActualWitness'], 'testSourceSha256': hashlib.sha256((ROOT / TEST).read_bytes()).hexdigest(),
              'sourceComponentUnchangedSinceOriginalTest': True, 'testReplayed': False,
              'officialRuleSource': 'https://raw.githubusercontent.com/pmd/pmd/pmd_releases/7.28.0/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/security/AbstractHardCodedConstructorArgsVisitor.java',
              'rawPmdFindings': 2217, 'classifiedNonDefect': 1, 'unclassifiedPmdFindings': 2216,
              'applicableDefectsRemaining': None, 'rawCheckstyleFindings': 645,
              'findingRemovedOrSuppressed': False, 'rulesChanged': False, 'F03Accepted': False,
              'newProductionPtCredit': 0, 'formalUpdated': False}
    os.umask(0o077); out = public / 'PG3426-crypto-finding-disposition'; out.mkdir()
    path = out / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'classified': 1, 'unclassifiedPmd': 2216, 'rawPmd': 2217,
                      'F03Accepted': False, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
