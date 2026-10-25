"""Exact independently reviewed47 graph candidates, never a general unique-owner heuristic."""
import hashlib
import json
from pathlib import Path
import trace_owner_join_inherited_companion as previous

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9386-composite-reference-graph-v3/candidates.json'
CATALOG_SHA='b292d002d3fddf7a33e95538e1555a7234896d9db99c0df3de9a5303060ab9b2'
raw=CATALOG.read_bytes()
if hashlib.sha256(raw).hexdigest()!=CATALOG_SHA:raise ValueError('immutable composite47 catalog required')
_rows=json.loads(raw);DECISIONS={row['path']:row for row in _rows}
if len(_rows)!=len(DECISIONS) or len(_rows)!=47:raise ValueError('exact47 responsibilities required')

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        owner=DECISIONS[path]['owner']
        if owner!=DECISIONS[path]['costOwner']:raise ValueError('single literal primary responsibility required')
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_ENUMERATED47_SAME_SOURCE_CP_HELPER_GRAPH_JAVAP_LITERAL_TABLE_9386_9388_NOT_PT')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):raise ValueError('exact reviewed composite47 responsibility required')
