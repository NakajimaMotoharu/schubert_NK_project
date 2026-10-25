"""Seven fixture resource/common-contract primaries, with original artifact and runtime scopes."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_fixture_consumer5 as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9542-shared-fixture7-source-metadata-v1/candidates.json'
CATALOG_SHA='554b712174726e9bea65c9cdd387703ab0167995428e9190d741951e18ee6163'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable shared fixture7 catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=7:raise ValueError('exact unique7 fixture responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_SHARED_FIXTURE7_DDL_OR_COMMON_MAIN_1934_9542_9544_NOT_RUNTIME_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'],
          referenceArtifactWitnesses=row['reviewedArtifactWitnesses'],artifactWitnessScope=row['witnessScope'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact shared fixture7 responsibility/resource scopes required')
