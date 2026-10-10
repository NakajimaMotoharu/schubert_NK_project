"""Export allowlisted safe runtime evidence, never raw originals or native data."""
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1041_cold_policy_diagnostic import W

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG1177-1184-canonical-runtime'
TAGS = ['pg1177-canonical-runtime-owner-proof-v1', 'pg1178-canonical-runtime-owner-handoff-v1',
        'pg1180-runtime-verify-frozen-v1', 'pg1181-stage-v1', 'pg1181-recover-v1',
        'pg1182-canonical-runtime-post-v1', 'pg1183-stage-v1', 'pg1184-canonical-resume-once-v1']
FIELDS = ['run','action','mode','actualExit','operatorSource','productionSource','source',
          'startedUTC','completedUTC','scriptSha256','logSha256','privateLogSha256',
          'privateSnapshotSha256','privateAfterSha256','signals','finiteRecoveryAccepted',
          'genuineSourceProofVerified','sameActiveRunCutoffActivation','configurationWritesReloadStarts0']


def main():
    if OUT.exists():raise ValueError('existing public evidence retained')
    records = []
    for tag in TAGS:
        p = W/(tag+'.safe.json');raw = p.read_bytes();value = json.loads(raw)
        if value['actualExit'] != 0:raise ValueError('qualified actual scope required')
        records.append({'reference': p.name, 'safeRecordSha256': hashlib.sha256(raw).hexdigest(),
                        **{k: value[k] for k in FIELDS if k in value}})
    manifest = {'asOfUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'productionSource': 'd5b00104280028d9ea81b44c1d1c805f3c2861ed',
                'bomSha256': '0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',
                'evidenceSource': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
                'records': records, 'trace': ['NK-OPS-001','SS343','SS353','SSC259','SSC260','PT-DEP-1178001','PT-DEP-1179001..002','PT-DEP-1182001','PT-DEP-1183001','PT-DEP-1184001'],
                'technicalStagesClosed': ['canonicalOwnerHandoffFullPost', 'canonicalFreshNormalScopesIndependentPost'],
                'wholeWbsAcceptedDelta': 0, 'productionTestsAdded': 0, 'formalAccepted': False,
                'coverage': 'PRODUCTION_COUNTERS_UNCHANGED',
                'pending': ['sameRoot API/Web/Caddy/DONE','owned stop','same-source native','CHR','451 formal quality'],
                'rawCredentialsSessionsDbNativeIncluded': False,
                'old1176Exit143UnknownPreserved': True, 'canonicalRuntimeWriteReloadReplayed': False}
    OUT.mkdir(parents=True)
    with (OUT/'manifest.json').open('x') as f:
        json.dump(manifest, f, indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'manifest': str(OUT/'manifest.json'), 'sha256': hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(), 'wholeAcceptedDelta': 0}))


if __name__ == '__main__':main()
