"""Independent exact11 owner candidate delta; original all PT/counters/costs remain historical and unchanged."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG15332-current1760-exact11-owner-post-v2'
REG=('PG15331-current1760-exact11-owner-registry-v3','cfb7c63e1b0761397371bf5fef625b7014aff588b992c35619c99b633374bd9f')
PREV=('PG15312-current1760-api-port-required-registry-v1','4b526f197b393c25f9d77293ad2dad1e7ab91a1724c835aa6bb552385397d080')
PPOST=('PG15314-current1760-api-port-required-registry-post-v1','5029262deaaafab2fe1b1ff4a6f7472a547941126eef469078262b554fea2c86')
EXPECTED={'ApiNonSecretConfigTest':('WBS-P018-01','ApiNonSecretConfig',7),'WebNonSecretConfigTest':('WBS-P018-01','WebNonSecretConfig',7),'ApiStopBudget':('WBS-P018-05','ApiProcessLifetime',0),'ApiStopBudgetTest':('WBS-P018-05','ApiProcessLifetime',18),'FixedServiceExecArgumentsTest':('WBS-P018-04','FixedServiceExecArguments',5),'FixedNativeCoverageProfileTest':('WBS-P018-08','FixedNativeCoverageProfile',5),'TerminalNativeCoverageProfileTest':('WBS-P018-08','FixedNativeCoverageProfile',4),'FixedNativeCoverageTerminalTest':('WBS-P018-08','FixedNativeCoverageTerminal',5),'ApiAdmittedConfigurationTest':('WBS-P018-05','ApiProcessMain',8),'ApiReadinessPredicateTest':('WBS-P018-05','ApiProcessMain',3),'RequiredColumnTest':('WBS-P004-05','RequiredColumn',1)}
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
    require(len(rows)==len(proof['rows'])==11 and {p.rsplit('/',1)[-1][:-5] for p in rows}==set(EXPECTED),'exact independent11 names')
    expected=copy.deepcopy(old['owners']);cases=set()
    for path,row in rows.items():
        name=path.rsplit('/',1)[-1][:-5];owner,anchor,count=EXPECTED[name]
        require(row['anchor'].endswith('/'+anchor+'.java') and row['anchor'] in logical and logical[row['anchor']]['owner']==logical[row['anchor']]['costOwner']==owner,'independent explicit subject/owner/cost')
        require(row['before']==old['owners'][path] and row['before']['ownershipStatus']=='UNKNOWN' and path not in logical,'no baseline reassignment')
        expected[path]={**old['owners'][path],**dict(canonicalOwner=owner,canonicalCostOwner=owner,ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='PGD936_EXACT_CURRENT11_REVIEWED_SUBJECT_CONTRACT_NOT_CHANGE_OWNER; ORIGINAL_SCOPE_COST_RUN_AND_ACCEPTANCE_UNCHANGED')}
        require(row['after']==expected[path] and row['sha256']==old['owners'][path]['sha256'] and len(row['originalCases'])==count,'actual before/after/hash/case references')
        p=read(row['originalPost']);require(p['actualExit']==0 and p['source']==current['source'],'original same source successful post, not replay')
        for c in row['originalCases']:
            require(c in p['cases'] and c['result']=='PASS' and not c['nonPass'],'actual prior TestID')
            cases.add((c['classname'],c['name']))
    require(len(cases)==63 and len({c for c,n in cases})==10 and proof['originalMethodsReferenced']==63 and proof['originalSuitesReferenced']==10,'references only, no new success')
    for path,pin in proof['sourceHashes'].items():require(data.sha((data.ROOT/path).read_bytes())==pin,'exact current source inputs')
    unchanged=[k for k in old if k not in {'invocation','owners','ownerStatusCounts','unknownOwnerPaths'}]
    def contract(v):
        require(all(wire(v[k])==wire(old[k]) for k in unchanged),'every case/counter/CRC/run/old proof/resource/cost semantics unchanged')
        require(wire(v['owners'])==wire(expected),'exact eleven candidate rows and all others unchanged')
        require(wire(v['ownerStatusCounts'])==wire(dict(BASELINE_LOGICAL_REFERENCE=277,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=215,UNKNOWN=103)) and type(v['unknownOwnerPaths']) is int and v['unknownOwnerPaths']==103,'exact candidate-only count')
        require(v['ownershipOverlayPreviousRegistry']==list(PREV) and v['ownershipOverlayPreviousPost']==list(PPOST) and v['ownershipRuleRevision']=='PG-D936_EXACT11_V2_CANDIDATE_ONLY' and v['ownershipContractVectors']==58,'both prior proofs/58 baseline-rejection contracts')
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
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=current['source'],invocation=invocation,registryManifestSha256=REG[1],previousRegistrySha256=PREV[1],previousPostSha256=PPOST[1],ownershipProofSha256=current['ownershipProofSha256'],summary=summary,ownershipReclassifiedCandidates=11,allOtherOwnerRowsUnchanged=True,originalMethodsReferenced=63,originalSuitesReferenced=10,resolverContractVectors=58,metadataNegativeVectors=len(labels),negativeLabels=labels,historicalCostsReallocated=False,productTestsExecuted=0,newTestIds=0,newSourcePrograms=0,newCoverage=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
