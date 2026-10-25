"""Fixed 55 compiler-bound code-reference candidates, never a general suffix ownership rule."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_direct_companion as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9362-static-companion-asm-v1/confirmed-candidates.json'
CATALOG_SHA='7f330ff0019011d31582fa98506ebdaa84c78afb891e156200110ef60fa03b03'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable compiler-bound catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=55 or any(row['owner']!=row['costOwner'] for row in _rows):
    raise ValueError('exact unique single-primary55 catalog required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        owner=DECISIONS[path]['owner']
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_ENUMERATED_STATIC_COMPILE_CODE_REFERENCE_ASM_JAVAP_9358_9360_9362_NOT_PT')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact compiled source responsibility required')
