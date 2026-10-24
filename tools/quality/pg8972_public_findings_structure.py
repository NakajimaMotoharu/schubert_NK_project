"""Structural triage only, no scan rerun and no secret/context serialization or false-positive waiver."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import re
from host_tool_invocation import capture, verify
from public_blob_scan import sha

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW = BASE / 'PG8968-public-blob-scan-v1'
POST = BASE / 'PG8970-public-blob-scan-post-v1/manifest.json'
OUT = BASE / 'PG8972-public-findings-structural-triage-v1'
SNAPSHOT = ROOT.parent / 'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    manifest = json.loads((RAW / 'manifest.json').read_bytes())
    post = json.loads(POST.read_bytes())
    assert post['actualExit'] == 0 and post['scanManifestSha256'] == sha((RAW / 'manifest.json').read_bytes())
    findings = json.loads((RAW / 'findings.json').read_bytes())
    inventory = json.loads((RAW / 'inventory.json').read_bytes())['rows']
    known_public_hashes = {row['sha256'] for row in inventory}
    paths = Counter(); keys = Counter(); shapes = Counter(); per_rule = Counter()
    classified = []
    current = None; lines = []
    for finding in sorted(findings, key=lambda row: (row['path'], row['startLine'], row['ruleId'])):
        name = finding['path']
        if current != name:
            data = (SNAPSHOT / name).read_bytes()
            assert sha(data) == finding['inputSha256']
            lines = data.decode('utf-8', errors='replace').split('\n'); current = name
        text = '\n'.join(lines[finding['startLine'] - 1:finding['endLine']])
        # Report shape and validated safe key names only, never the line, match, candidate or its hash.
        match = re.match(r'^\s*"([A-Za-z][A-Za-z0-9_]{0,79})"\s*:', text)
        key = match.group(1) if match else 'KEY_NOT_PUBLIC_IDENTIFIER'
        literals = re.findall(r'["\x27]([0-9a-f]{64})["\x27]', text)
        if any(value in known_public_hashes for value in literals):
            shape = 'LINE_CONTAINS_KNOWN_PUBLIC_BLOB_SHA256_NOT_MATCH_ATTRIBUTED'
        elif literals:
            shape = 'LINE_CONTAINS_SHA256_SHAPE_NOT_PROVEN'
        else:
            shape = 'OTHER_REQUIRES_INDIVIDUAL_REVIEW'
        paths[name.split('/')[0]] += 1; keys[key] += 1; shapes[shape] += 1; per_rule[finding['ruleId']] += 1
        classified.append(dict(**finding, safeKey=key, structuralCategory=shape,
                               disposition='UNCLASSIFIED_NOT_FALSE_POSITIVE_OR_PASS'))
    verify(invocation); OUT.mkdir()
    with (OUT / 'triage.json').open('x', encoding='utf-8') as stream:
        json.dump(classified, stream, ensure_ascii=False, sort_keys=True, indent=2); stream.write('\n')
    value = dict(actualExit=0, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), invocation=invocation,
          source=manifest['source'], contentCommit=manifest['contentCommit'],
          scanManifestSha256=sha((RAW / 'manifest.json').read_bytes()), independentPostSha256=sha(POST.read_bytes()),
          triageSha256=sha((OUT / 'triage.json').read_bytes()), findings=len(classified),
          perRoot=dict(paths), perRule=dict(per_rule), safeKeyCounts=dict(keys), structuralCategoryCounts=dict(shapes),
          falsePositiveWaivers=0, confirmedLiveSecrets=None, unclassified=len(classified),
          scanRerun=False, rawValuesOrStandaloneSecretHashPersisted=False,
          whole451SecretGateAccepted=False, productTestsExecuted=0, productCoverage=None, formalUpdated=False)
    with (OUT / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({key: value[key] for key in ('actualExit', 'findings', 'perRoot', 'perRule', 'safeKeyCounts', 'structuralCategoryCounts', 'unclassified')}))


if __name__ == '__main__':
    main()
