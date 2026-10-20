"""Read immutable review deltas without copying or suppressing complete diagnostic inventories."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT
from pg5758_static_rebind import rationale_text

BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
IDENTITY=('findingId','sourcePath','sourceSha256','rule','beginline','endline','begincolumn','endcolumn')
DECIDED={'CONTEXT_NOT_APPLICABLE','REQUIRED_CONTRACT','FALSE_POSITIVE'}
LEGACY={
 '2ccfa8c7271d621f074d917861b06670d964677186a42e70eae0b27dbac0a0ad':('findings.json','2b758e909aff50e50962d97a0dbe0bce1224c4ac6670008b9129a1d8163a3c93'),
 '9ba9f2af5c8d4c578bf3c645288759ef64bc3e6f818ac88117703c0c81f65484':('decisions.json','d34e3f2ac12769a2351795e738524bc00797fed227786ccd5f1ae25065298ae5'),
 'b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487':('decisions.json','ae131abf937b0c0ccb8cf9f900ee1efa667d1229b1c582cc0f8b79b8956d4e87')}


def apply_decisions(rows,decisions):
    index={r['findingId']:i for i,r in enumerate(rows)}
    if len(index)!=len(rows):raise ValueError('raw diagnostic IDs must be unique')
    result=copy.deepcopy(rows);seen=set()
    for decision in decisions:
        ident=decision['findingId']
        if ident in seen or ident not in index:raise ValueError('one existing diagnostic per overlay')
        seen.add(ident);prior=result[index[ident]]
        if any(prior[k]!=decision[k]for k in IDENTITY):raise ValueError('immutable entire source/diagnostic identity')
        pending=decision['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
        if prior['status']!='NOT_REVIEWED_CURRENT_SOURCE'or decision['status']not in DECIDED and not pending:raise ValueError('no silent reclassification or unresolved-to-success conversion')
        if pending and(not decision.get('currentWholeJoinPending')or decision.get('currentWholeCaseRefs')!=[]or decision.get('priorDisposition')not in DECIDED):raise ValueError('pending is never whole success; no current PT references')
        if not decision.get('reason')or not decision.get('rawWarningRetained'):raise ValueError('individual rationale and raw warning retention required')
        result[index[ident]]=copy.deepcopy(decision)
    if [r['findingId']for r in rows]!=[r['findingId']for r in result]:raise ValueError('no removed/reordered raw diagnostic')
    return result


def read_exact(path,digest):
    path=Path(path)
    if path.is_symlink()or not path.is_file()or not path.resolve().is_relative_to(BASE.resolve()):raise ValueError('regular public evidence only')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('immutable evidence hash')
    return json.loads(raw)


def validate_rationales(rows):
    for row in rows:
        if row['status'] in DECIDED|{'SOURCE_REBOUND_CURRENT_WHOLE_PENDING'} and rationale_text(row) is None:
            raise ValueError('classified diagnostic requires nonblank individual rationale;historical missing text is not approval')


def load(path,digest,source,seen=()):
    if digest in seen or len(seen)>63:raise ValueError('acyclic bounded review chain')
    value=read_exact(path,digest)
    if value['source']!=source or value['actualExit']!=0:raise ValueError('one declared source, real review result')
    legacy=LEGACY.get(digest)
    if legacy:filename,child_digest=legacy
    elif value.get('inventoryFile')=='findings.json':filename,child_digest='findings.json',value['inventorySha256']
    else:filename,child_digest='decisions.json',value['decisionsSha256']
    child=read_exact(Path(path).with_name(filename),child_digest)
    if filename=='findings.json':rows=child
    else:
        parent=ROOT/value['baseManifestPath'];rows=load(parent,value['baseManifestSha256'],source,seen+(digest,))
        rows=apply_decisions(rows,child)
    if Counter(r['status']for r in rows)!=Counter(value['statusCounts']):raise ValueError('all dispositions/counts correspond to immutable raw inventory')
    count=value.get('rawFindings',value.get('currentRawFindings'))
    if len(rows)!=count:raise ValueError('complete raw finding count')
    validate_rationales(rows)
    return rows
