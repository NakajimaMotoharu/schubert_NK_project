"""Aggregate four already verified Source-monitor groups once; never qualify runtime."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_last_main_type_two_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR=('PG14044-last-main-type-two-trace-v1','28092d60e031be855606ea95218097fa5f748c54f978f33b6e4f30478f3ed761')
PAIRS=[
 ('PG14052-sampling-budget-admission-monitor-contexts-v1','4d35f74a33d5cf228fa06d4435201c9fd9f5969bcf419fa3262fcb99d98e30c0','PG14054-sampling-budget-admission-monitor-post-v1','d1781651fd07c1aab04093eeb710f89dcf0df32679041b802c74be86aae4bdf0',22),
 ('PG14066-api-dispatch-observation-monitor-v1','7180480aee83bb1e074355f380d6f55e5dd738a1ee38b4d8d9cf6b6fd0f149e7','PG14068-api-dispatch-observation-monitor-post-v1','991059acda73b03d74d4d740a830671dcb5c85e94ac8532864a8bf09a1cdb7bc',12),
 ('PG14077-web-state-local-recording-monitor-v3','17fb76724e4105220c0c68c25baec3856d7d63f4d673000af9e02d9ab9560806','PG14078-web-state-local-recording-monitor-post-v1','a0828fbe888747cdca9365ead01bba3fe2a523402b86a25f9d7bceaca7f8adf5',10),
 ('PG14082-batch-retained-scope-monitor-v1','3ecf31a8456d8c44326f38dcbceefd7db115bc30444a79273777a1872b2dc515','PG14084-batch-retained-scope-monitor-post-v1','08228ad53eddd1119bd55b1f60b29fea9a47c58029240120f14bf9887fac3ec0',37)]
OUT=data.BASE/'PG14086-main-monitor-eighty-one-trace-v1'
RECORD='evidence/01_PT/018_NK-OPS-001/2572_Batch保持scope同期三十七・全八十一trace_結果.md'
BASE='189a0a632e623f4da61138787d78979b7a4fb246'
ORIGINAL=('PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')

def new_ids():
    catalog=data.read_checked(data.BASE/ORIGINAL[0],ORIGINAL[1])
    result={r['id'] for r in catalog if '/src/main/java/' in r['path'] and r['rule']=='AvoidSynchronizedStatement'}
    assert len(result)==81
    return result

def state_after():
    ids,refs,pending=previous_state();extra=new_ids()
    assert extra<=ids-refs and (len(ids),len(refs),len(pending))==(6247,3493,2632)
    return ids,refs|extra,pending|extra

def inputs():
    prior=data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1]);rows=[]
    for reviewname,reviewpin,postname,postpin,count in PAIRS:
        review=data.read_checked(data.BASE/reviewname/'manifest.json',reviewpin)
        post=data.read_checked(data.BASE/postname/'manifest.json',postpin)
        selected=data.read_checked(data.BASE/reviewname/'review.json',review['reviewSha256'])['rows']
        assert review['source']==post['source']==SOURCE
        assert type(review['actualExit']) is int and review['actualExit']==post['actualExit']==post['productTestsExecuted']==0
        assert review['sourceContexts']==post['sourceContexts']==len(selected)==count and post['reviewManifestSha256']==reviewpin
        rows.extend(selected)
    assert len(rows)==len({r['id'] for r in rows})==81 and {r['id'] for r in rows}==new_ids()
    assert all(r['rawRetained'] is r['currentWholeJoinPending'] is True and r['sourceChanged'] is False and type(r['productTestsExecuted']) is int and r['productTestsExecuted']==0 for r in rows)
    normal=data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows'])==995 and all(r['sha256']==normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw)=='bf450f04a036d9ea265929e7f65243803a8673cfa500c634ab2eb3dc7818794d'
    assert data.sha(snap)=='966d84869770015c274c949e0cf6b6c400d23b7417fe527360778fc180d81de1'
    return prior,sorted(rows,key=lambda r:r['id']),raw,snap

def expected(prior,rows):
    ids,refs,pending=state_after();value=copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:value.pop(key,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
      currentMainMonitorEightyOneReferences=dict(groups=[dict(review=p[0],reviewSha256=p[1],post=p[2],postSha256=p[3],contexts=p[4]) for p in PAIRS],source=SOURCE,rows=rows,newSourceReasonRows=81,newCurrentReferences=81,sourceFiles=len({r['path'] for r in rows}),rawRetained=81,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allAddedToGlobalJoinPending=True),
      priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
      all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows']==prior['sourceRows'] and value['currentQualification']==prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs))==(3574,2713,2673)
    return value

def documents(value,raw,snap):
    original=json.loads(raw);result=raw
    overlay=dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,qualification=value['currentMainMonitorEightyOneReferences'],joinedContextWarnings=3574,currentWholeJoinPending=2713,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=81,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section=copy.deepcopy(original[name]);assert 'mainMonitorEightyOnePG14086Overlay' not in section
        section['mainMonitorEightyOnePG14086Overlay']=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    result_snap,_,_=replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,original,json.loads(snap))
    return result,result_snap
