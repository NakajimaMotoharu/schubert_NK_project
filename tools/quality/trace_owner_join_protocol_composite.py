"""Literal ten protocol primaries plus related scopes; not majority-vote scope assignment."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_composite_reference as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9398-protocol-composite-metadata-v1/candidates.json'
CATALOG_SHA='616faaac9af59f9e9e8556898b752050dc4ae6fba70d0b10a94c43eb5b8e49a1'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable reviewed protocol10 catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=10:raise ValueError('exact unique ten protocol source responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_TEN_LITERAL_PROTOCOL_PRIMARY_RELATED_RESPONSIBILITIES_1910_9398_9400_NOT_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('literal primary and related source responsibilities required')
