"""Only the fixed 280 individually enumerated, dual-parser source candidates; baseline wins."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_storage_residual as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9346-direct-companion-jdk-post-v1/confirmed-candidates.json'
CATALOG_SHA='a3217e70b48808e16ccc13270d59ed7b2b3051f732acb9119dab3c93b078bc9d'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable reviewed direct-companion catalog required')
_rows=json.loads(raw)
DECISIONS={row['path']:row for row in _rows}
if len(DECISIONS)!=len(_rows) or len(_rows)!=280 or any(row['owner']!=row['costOwner'] for row in _rows):
    raise ValueError('unique single-primary catalog required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        owner=DECISIONS[path]['owner']
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_ENUMERATED_COMPANION_SOURCE_DUAL_PARSER_9344_9346_NOT_PT_OR_SYMBOL_RESOLUTION')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('exact dual-parser source responsibility catalog required')
