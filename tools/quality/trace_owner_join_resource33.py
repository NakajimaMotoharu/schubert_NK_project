"""Exact resource-backed33 source responsibilities; never infer owners from absence of Main refs."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_reflective25 as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9422-resource33-source-metadata-v1/candidates.json'
CATALOG_SHA='cd7eee9a232333d120e0cd8a2262a300ae25b16a7bd12da11ae498a1c1ccb3ae'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable resource33 source catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=33:raise ValueError('exact unique33 resource source responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_LITERAL33_RESOURCE_ARTIFACT_BACKED_SOURCE_PRIMARY_1914_9422_9424_NOT_RUNTIME_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'],
          referenceArtifactWitnesses=row['reviewedArtifactWitnesses'],artifactWitnessScope=row['witnessScope'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact literal resource-backed primary responsibility required')
