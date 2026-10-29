"""One aggregated WBS join for two independently reviewed static groups; all runtime truth retained."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from f03_jms_type_priority_seventeen_trace_v2 import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
PRIOR=('PG14005-jms-type-priority-seventeen-trace-v2','93800c9f3b853037be7a7563e1c5cba65ab998788d99bfcc075e67b17626aa0e')
REVIEWS=[
 ('PG14021-batch-transaction-type-priority-twenty-eight-contexts-v2','544d50d47ef9abee500841c698b05dd39cddc973bab634e187d5b0846105a1fd','PG14022-batch-transaction-type-priority-twenty-eight-post-v1','2be36f603ec5b27ca1120d4080ae0cdc5009c60126a047fcb666eb5d99fda471',28),
 ('PG14028-remaining-main-type-priority-twenty-two-contexts-v1','ac8f64cc8ae4758453c9e1e3a63b759246397c393b522728510110a18d75a391','PG14030-remaining-main-type-priority-twenty-two-post-v1','84a7ac1e6f3bcee3fdce0d04b1d96f1a7dd9a5aab1400b71f273f221fc7b8b85',22),
]
OUT=data.BASE/'PG14032-main-type-priority-fifty-trace-v1'
RECORD='evidence/01_PT/018_NK-OPS-001/2560_残Main型判定二十二rawと五十合流_静的点検結果.md'
NEW_IDS=set(json.loads("[\"PMD-02703\",\"PMD-02704\",\"PMD-02705\",\"PMD-02706\",\"PMD-02707\",\"PMD-02708\",\"PMD-02709\",\"PMD-02710\",\"PMD-02711\",\"PMD-02712\",\"PMD-02713\",\"PMD-02714\",\"PMD-02756\",\"PMD-02757\",\"PMD-02758\",\"PMD-02759\",\"PMD-02760\",\"PMD-02761\",\"PMD-02762\",\"PMD-02763\",\"PMD-02764\",\"PMD-02765\",\"PMD-02766\",\"PMD-02767\",\"PMD-02768\",\"PMD-02769\",\"PMD-02770\",\"PMD-02771\",\"PMD-00107\",\"PMD-00114\",\"PMD-00181\",\"PMD-00182\",\"PMD-00183\",\"PMD-00184\",\"PMD-00188\",\"PMD-00189\",\"PMD-00194\",\"PMD-00395\",\"PMD-02819\",\"PMD-03066\",\"PMD-03067\",\"PMD-03068\",\"PMD-03069\",\"PMD-03070\",\"PMD-03071\",\"PMD-03072\",\"PMD-03073\",\"PMD-07193\",\"PMD-07200\",\"PMD-07336\"]"))

def state_after():
    ids,refs,pending=previous_state()
    assert len(NEW_IDS)==50 and NEW_IDS<=ids-refs and (len(ids),len(refs),len(pending))==(6247,3441,2580)
    return ids,refs|NEW_IDS,pending|NEW_IDS

def inputs():
    assert len({PRIOR[0],OUT.name,*[r[0] for r in REVIEWS],*[r[2] for r in REVIEWS]})==6
    prior=data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1]);assert prior['source']==SOURCE
    rows=[]
    for name,pin,post_name,post_pin,count in REVIEWS:
        raw=data.read_checked(data.BASE/name/'manifest.json',pin)
        post=data.read_checked(data.BASE/post_name/'manifest.json',post_pin)
        selected=data.read_checked(data.BASE/name/'review.json',raw['reviewSha256'])['rows']
        assert raw['source']==post['source']==SOURCE and raw['actualExit']==post['actualExit']==post['productTestsExecuted']==0
        assert raw['sourceContexts']==post['sourceContexts']==raw['rawRetained']==count and post['reviewManifestSha256']==pin
        assert len(selected)==count and all(r['rawRetained'] is r['currentWholeJoinPending'] is True for r in selected)
        rows.extend(selected)
    assert {r['id'] for r in rows}==NEW_IDS and len(rows)==len(NEW_IDS)
    normal=data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert len(prior['sourceRows'])==995 and all(r['sha256']==normal['begin']['inputHashes'][r['path']] for r in prior['sourceRows'])
    base='d08abbd3edf8c29424ffffdfaaeb3bff3e1aeb21'
    raw,snap=[subprocess.check_output(['git','show',base+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw)=='bb90ab5305dbc342a0141db4ab0c1b412b9e542495ee3d7b28be2b21a8681690'
    assert data.sha(snap)=='9503c4084dd1158f004c13b43ed4186e2b39085b9952a2edc205d82646de1306'
    return prior,sorted(rows,key=lambda r:r['id']),raw,snap

def expected(prior,rows):
    ids,refs,pending=state_after();value=copy.deepcopy(prior)
    for name in ['invocation','wholeWbsAuditBefore','toolCorrection']:value.pop(name,None)
    value.update(source=SOURCE,record=RECORD,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
      currentMainTypePriorityFiftyReferences=dict(source=SOURCE,reviewGroups=[dict(review=name,reviewSha256=pin,post=post,postSha256=post_pin,rawRetained=count) for name,pin,post,post_pin,count in REVIEWS],rows=rows,newSourceReasonRows=50,uniqueOperandSpans=29,uniqueCatchClauses=13,newCurrentReferences=50,rawRetained=50,sourceChanged=False,productTestsExecuted=0,currentRuntimeQualification=False,allFiftyAddedToGlobalJoinPending=True),
      priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=SOURCE,oldRuntimeDomainsReassigned=False),
      all995RegistryRowsAndHistoricalRuntimeUnchanged=True,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    assert value['sourceRows']==prior['sourceRows'] and value['currentQualification']==prior['currentQualification']
    assert (len(refs),len(pending),len(ids-refs))==(3491,2630,2756)
    return value

def documents(value,raw,snap):
    current=json.loads(raw);result=raw
    overlay=dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,qualification=value['currentMainTypePriorityFiftyReferences'],joinedContextWarnings=3491,currentWholeJoinPending=2630,sourceDerivedRaw=6247,totalPriorCorrections=3194,all995OldRuntimePreserved=True,newSourceReasonRows=50,uniqueOperandSpans=29,uniqueCatchClauses=13,newAccepted=0,formalUpdated=False)
    for name in SECTIONS:
        section=copy.deepcopy(current[name]);assert 'mainTypePriorityFiftyPG14032Overlay' not in section
        section['mainTypePriorityFiftyPG14032Overlay']=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    result_snap,_,_=replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,result_snap,current,json.loads(snap))
    return result,result_snap
