"""New-only byte auth includes the approved canonical SHA256SUMS, no extra exemption."""
import ast
import hashlib
from pathlib import Path
from pg1002_cold_readonly import capture
from pg1026_cold_observation_contract import canonical_sum_bytes
from pg1030_cold_handoff_preflight_v3 import payload as previous


def payload():
    import json
    root = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg932-release-v1')
    manifest = (root / 'RELEASE-MANIFEST.json').read_bytes()
    expected = canonical_sum_bytes(json.loads(manifest)['artifacts'], hashlib.sha256(manifest).hexdigest())
    if (root / 'SHA256SUMS').read_bytes() != expected:
        raise ValueError('qualified host canonical checksum refused')
    raw = previous().replace('pg1030-cold-handoff-preflight-v3', 'pg1031-cold-handoff-preflight-v4')
    raw = raw.replace('PG1030_REFUSED', 'PG1031_REFUSED')
    marker = " records=json.loads(manifest)['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':MANIFEST_SIZE,'sha256':BOM}]"
    if raw.count(marker) != 1:
        raise ValueError('closed inventory shape refused')
    replacement = marker + "\n canonical=contract.canonical_sum_bytes(json.loads(manifest)['artifacts'],BOM)\n require(hashlib.sha256(canonical).hexdigest()==CHECKSUM_HASH)\n records.append({'path':'SHA256SUMS','size':len(canonical),'sha256':CHECKSUM_HASH})"
    raw = 'CHECKSUM_HASH=' + repr(hashlib.sha256(expected).hexdigest()) + '\n' + raw.replace(marker, replacement)
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    capture('pg1031-cold-handoff-preflight-v4', payload())
