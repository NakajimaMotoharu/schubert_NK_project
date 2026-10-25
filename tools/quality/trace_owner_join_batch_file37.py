"""Exact37 Batch file source responsibility labels, not runtime success or method trace."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_batch_platform22 as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9494-batch-file37-source-metadata-v1/candidates.json'
CATALOG_SHA='eabd9be7062d8aea08111dd731465846e9c3afc184c5ce11fc820497167e988a'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable batch file37 catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=37:raise ValueError('exact unique37 source responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_LITERAL_BATCH_FILE37_PRIMARY_RELATED_1926_9494_9496_NOT_RUNTIME_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact batch file37 primary/related/runtime scopes required')
