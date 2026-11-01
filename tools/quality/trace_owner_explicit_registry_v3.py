"""Pure immutable candidates from one hash-pinned historical registry; never a runtime grant."""
from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
import trace_owner_explicit_query_v2 as prior

REGISTRY_SHA='ddca86f481cba3be23f37c2b2c4f580caf04ad0090670c8848ff755cada66855'
@dataclass(frozen=True,slots=True)
class VerifiedRules:
    entries: object
    registry_sha256: str

def require(ok,message):
    if not ok:raise ValueError(message)

def from_original_bytes(blob,paths):
    require(type(blob) is bytes and hashlib.sha256(blob).hexdigest()==REGISTRY_SHA,'exact original explicit registry bytes')
    require(type(paths) is tuple and 1<=len(paths)<=24 and all(type(p) is str for p in paths) and len(set(paths))==len(paths),'bounded unique explicit paths')
    require(all(p.startswith('src/schubert-nk-') and p.endswith('.java') and '..' not in p.split('/') and not any(v in p for v in ['RootFailed','/private/','.private.','SnapshotKeyCloseWitness','pg9892_']) for p in paths),'held names excluded before row lookup')
    m=json.loads(blob);require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']=='70165b0768a1fabd13371cc25a55978fcf3452ba' and m['canonicalOwnerAndCostPreserved'] is True,'original candidate semantics')
    rows={r['path']:r for r in m['sourceRows']};require(len(rows)==len(m['sourceRows'])==971,'exact original path registry')
    result={}
    for path in paths:
        require(path in rows,'explicit original path, not class-name guess')
        r=rows[path];owner=r['canonicalOwner']
        require(r['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' and owner==r['canonicalCostOwner'] and type(owner) is str and owner.startswith('WBS-'),'explicit candidate owner/cost only')
        require(r['currentSourcePtQualificationInferred'] is r['historicalCostsReallocated'] is r['historicalRunReassigned'] is False and r['additionalSharedCostPp']==0 and r['actualAllocatedPp'] is None,'no historical execution/cost transfer')
        require(type(r['sha256']) is str and len(r['sha256'])==64 and type(r['basis']) is str and r['basis'],'exact hash and declared basis')
        result[path]=(r['sha256'],owner,r['basis'])
    return VerifiedRules(MappingProxyType(result),REGISTRY_SHA)

def canonical(path,logical,current_sha256,rules):
    require(type(rules) is VerifiedRules and rules.registry_sha256==REGISTRY_SHA,'verified exact metadata rules required')
    resolved=prior.canonical(path,logical,current_sha256)
    if resolved['ownershipStatus']!='UNKNOWN':return resolved
    row=rules.entries.get(path)
    if row is None or current_sha256!=row[0]:return resolved
    return dict(canonicalOwner=row[1],canonicalCostOwner=row[1],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXPLICIT_9982_SAME_BYTE_ONLY:'+row[2])
