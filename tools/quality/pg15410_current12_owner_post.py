"""Independent exact11 owner candidate delta; original all PT/counters/costs remain historical and unchanged."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG15410-current1800-exact12-owner-post-v3'
REG=('PG15408-current1800-exact12-owner-registry-v3','75c239f0250f38bb7ed4f6d9cf812eaaf8dd6766f38e93d917f81be0ae287640')
PREV=('PG15396-current1800-auth-wire-policy-registry-v1','84e8cb25872c6b063a596e66ef45c631b6befc20769de36fbe06343ff40223c5')
PPOST=('PG15398-current1800-auth-wire-policy-registry-post-v1','0688cb78770d148a8472f8b4820fc0d556edfd01ecf4cbbb995545f39a9e4e47')
EXPECTED={"ApiStartupInputsTest":("WBS-P018-05","ApiStartupInputs",4),"OutboxPolicyTest":("WBS-P006-02","OutboxRetrySchedule",4),"OutboxModelTest":("WBS-P006-02","OutboxEntry",4),"OutboxDlqMetadataTest":("WBS-P006-02","OutboxDlqMetadata",2),"OutboxDispatchReportBoundaryTest":("WBS-P006-02","OutboxDispatchReport",3),"QuestionCommandTimeBoundaryTest":("WBS-P011-03","QuestionCommandMetadata",3),"LoginUsernameTest":("WBS-P018-09","LoginUsername",3),"PasswordPolicyTest":("WBS-P007-01","PasswordPolicy",3),"LoginAttemptStateTest":("WBS-P007-01","LoginAttemptState",5),"LoginAttemptSequenceTest":("WBS-P007-01","LoginAttemptState",4),"AuthenticationResponseMapperTest":("WBS-P007-04","AuthenticationResponseMapper",3),"AuthorizationServiceTest":("WBS-P007-03","AuthorizationService",2)}
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,current,post=read(PREV),read(REG),read(PPOST)
    proof=data.read_checked(data.BASE/REG[0]/'owner-proof.json',current['ownershipProofSha256'])
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(current['actualExit']==post['actualExit']==proof['actualExit']==old['actualExit']==0 and current['source']==post['source']==old['source']==proof['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c','exact genuine source')
    rows={r['path']:r for r in proof['rows']}
    require(len(rows)==len(proof['rows'])==12 and {p.rsplit('/',1)[-1][:-5] for p in rows}==set(EXPECTED),'exact independent11 names')
    expected=copy.deepcopy(old['owners']);cases=set()
    for path,row in rows.items():
        name=path.rsplit('/',1)[-1][:-5];owner,anchor,count=EXPECTED[name]
        require(row['anchor'].endswith('/'+anchor+'.java') and row['anchor'] in logical and logical[row['anchor']]['owner']==logical[row['anchor']]['costOwner']==owner,'independent explicit subject/owner/cost')
        require(row['before']==old['owners'][path] and row['before']['ownershipStatus']=='UNKNOWN' and path not in logical,'no baseline reassignment')
        expected[path]={**old['owners'][path],**dict(canonicalOwner=owner,canonicalCostOwner=owner,ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='PGD937_EXACT_CURRENT12_REVIEWED_SUBJECT_CONTRACT_NOT_CHANGE_OWNER; ORIGINAL_SCOPE_COST_RUN_AND_ACCEPTANCE_UNCHANGED')}
        require(row['after']==expected[path] and row['sha256']==old['owners'][path]['sha256'] and len(row['originalCases'])==count,'actual before/after/hash/case references')
        p=read(row['originalPost']);require(p['actualExit']==0 and p['source']==current['source'],'original same source successful post, not replay')
        for c in row['originalCases']:
            require(c in p['cases'] and c['result']=='PASS' and not c['nonPass'],'actual prior TestID')
            cases.add((c['classname'],c['name']))
    require(len(cases)==40 and len({c for c,n in cases})==12 and proof['originalMethodsReferenced']==40 and proof['originalSuitesReferenced']==12,'references only, no new success')
    for path,pin in proof['sourceHashes'].items():require(data.sha((data.ROOT/path).read_bytes())==pin,'exact current source inputs')
    unchanged=[k for k in old if k not in {'invocation','owners','ownerStatusCounts','unknownOwnerPaths','ownershipRuleRevision','ownershipOverlayPreviousRegistry','ownershipOverlayPreviousPost','ownershipProofSha256','ownershipRuleSha256','ownershipContractVectors'}]
    def contract(v):
        require(all(wire(v[k])==wire(old[k]) for k in unchanged),'every case/counter/CRC/run/old proof/resource/cost semantics unchanged')
        require(wire(v['owners'])==wire(expected),'exact eleven candidate rows and all others unchanged')
        require(wire(v['ownerStatusCounts'])==wire(dict(BASELINE_LOGICAL_REFERENCE=295,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=103)) and type(v['unknownOwnerPaths']) is int and v['unknownOwnerPaths']==103,'exact candidate-only count')
        require(v['ownershipOverlayPreviousRegistry']==list(PREV) and v['ownershipOverlayPreviousPost']==list(PPOST) and v['ownershipRuleRevision']=='PG-D937_EXACT12_V3_CANDIDATE_ONLY' and v['ownershipContractVectors']==63,'both prior proofs/58 baseline-rejection contracts')
        require(all(type(v[k]) is int and v[k]==0 for k in ['newProductExecutionsForOwnership','newTestIdsForOwnership','newAcceptedForOwnership']) and v['historicalCostsReallocated'] is False,'no extra executions/new acceptance/reallocation')
    contract(current);labels=[]
    for key,value in [('source','OLD'),('cases',[]),('tests',1761),('fullSourceUnits',{}),('metadataClasses',{}),('originalPostReferences',[]),('totalMethodExecutions',1869),('four100SourcePrograms',198),('incompleteSourcePrograms',0),('unknownOwnerPaths',0),('unknownOwnerPaths',False),('newProductExecutionsForOwnership',1),('newTestIdsForOwnership',1),('newAcceptedForOwnership',1),('newAcceptedForOwnership',False),('historicalCostsReallocated',True),('ownershipContractVectors',55),('ownershipOverlayPreviousPost',[])]:
        bad=copy.deepcopy(current);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key+'-'+str(value))
        else:raise ValueError('false semantic accepted')
    for path in [*rows,next(p for p in old['owners'] if not p.startswith('src/'))]:
        for key,value in [('canonicalOwner','WBS-G01'),('canonicalCostOwner','WBS-G03'),('ownershipStatus','BASELINE_LOGICAL_REFERENCE')]:
            bad=copy.deepcopy(current);bad['owners'][path][key]=value
            try:contract(bad)
            except ValueError:labels.append(path+':'+key)
            else:raise ValueError('false owner accepted')
    summary=copy.deepcopy(post['summary']);summary['ownerStatusCounts']=current['ownerStatusCounts'];summary['unknownOwnerPaths']=103
    require(all(wire(v)==wire(current[k]) for k,v in summary.items()),'all typed summary values match actual registry')
    for v in [old,current,post]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=current['source'],invocation=invocation,registryManifestSha256=REG[1],previousRegistrySha256=PREV[1],previousPostSha256=PPOST[1],ownershipProofSha256=current['ownershipProofSha256'],summary=summary,ownershipReclassifiedCandidates=12,allOtherOwnerRowsUnchanged=True,originalMethodsReferenced=40,originalSuitesReferenced=12,resolverContractVectors=63,metadataNegativeVectors=len(labels),negativeLabels=labels,historicalCostsReallocated=False,productTestsExecuted=0,newTestIds=0,newSourcePrograms=0,newCoverage=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
