"""Exact25 reviewed static source labels; retain every runtime uncertainty and no exemptions."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_protocol_composite as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9410-reflective25-source-metadata-v2/candidates.json'
CATALOG_SHA='dd3c143636705aa89f1a03e584de5a57fec355a03b4e49f3b1d93e8f11de1cf5'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable full-path source catalog25 required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=25:raise ValueError('exact unique25 source responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        row=DECISIONS[path]
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_LITERAL25_STATIC_SOURCE_RESPONSIBILITY_1912_9410_9412_RUNTIME_UNCERTAINTY_RETAINED_NOT_PT',
          referenceRelatedOwners=row['relatedOwners'],runtimeUncertainty=row['unresolvedRuntimeReasons'])
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact static primary and runtime hold required')
