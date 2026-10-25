"""Five fixture support primaries by complete known direct-consumer responsibility, not Main CP."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_api_web42 as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9530-fixture-consumer5-source-metadata-v1/candidates.json'
CATALOG_SHA='c41e36744c0b7ba066ec19079511ae30b52c1dc13edb18a6e784f1101fb17b93'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable fixture5 consumer catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=5:raise ValueError('exact unique5 fixture responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_SINGLE_CONSUMER_OWNER_FIXTURE5_1932_9530_9532_NOT_MAIN_CP_OR_RUNTIME_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'],
          referenceArtifactWitnesses=row['reviewedConsumerWitnesses'],artifactWitnessScope=row['witnessScope'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact fixture5 consumer responsibility/witnesses required')
