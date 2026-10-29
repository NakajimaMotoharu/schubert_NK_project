"""Bind eleven original completed current-source posts plus a separate scope-only supplement without replay; natural0/noCode are not four100."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL_PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
POSTS={
 'PG14244-delivery-metadata-whole-two-post-v1':('14f6fb3937435588c58bfa0cdbe7fa6b0ef04b0b3eed7436b4918cd1f15a63bd',2,1),
 'PG14254-inbound-primary-whole-five-post-v1':('d1c31c2b14489e72fe15ab7a72188746a8ec7ce78439c3ebab659dcaad4a08f6',5,1),
 'PG14258-protocol-carrier-whole-eight-post-v1':('2b9ce8ebf4b329a2e36d329bcf7cb91a9396fbe2c40dd6be09fdaa1247ac1e9a',8,2),
 'PG14272-web-three-forms-whole-twenty-four-post-v1':('09fe225e89c4366efb79605456382c56aa4cde8e7392017cb2ae785b19250c0b',24,3),
 'PG14294-web-user-create-whole-eight-post-v1':('0b744221948357f4aadf98a89bddee5fd97988d42ad1c8b4a9e7059da6a3de5b',8,1),
 'PG14298-web-target-mutation-whole-twenty-four-post-v1':('2836720bd34b54355f65fff51f67c6a1f0ccf2a6d4f3791ffcb99260f7803012',24,2),
 'PG14314-web-business-wire-whole-twelve-post-v1':('06f8b8d26d79ec31f64c588144f6c7d54b74a35bfa72ef44fe72ca2e53e0719e',12,1),
 'PG14318-web-memory-coordinator-whole-seventeen-post-v1':('7b2205bf1d214dc1262512fc8d46b184ab7ff13294742e96476e35f004b7985d',17,3),
 'PG14324-protocol-field-whole-nine-post-v1':('05f5e0ddaba5a9d006bd18efbd80db6834642b6b8906b786320b446c7cabb5ad',9,2),
 'PG14328-protocol-frame-payload-whole-twenty-four-post-v1':('8099de1c6e2169ff4102f81db07c679b924966e2e502b2dac16155ad4fdb8d3f',24,5),
 'PG14346-protocol-header-layout-whole-fourteen-post-v1':('6a7fbff5dd2ebf7acac4690c9717354df4dd6e0bbac88c2973e747e795a63d77',14,3),
 'PG14362-protocol-semantic-whole-thirty-one-post-v1':('f03bb6730c2491b463c9400972de775f65a389c54a4e65d24c8a6aa1d3fef177',31,7),
 'PG14366-protocol-file-time-topology-whole-twenty-post-v1':('f0853ef479bb0cec0c665a985d10109f01720a048a16421a72277590df29f565',20,4)}
SCOPE='PG14342-current-frame-value-object-counter-v1'
SCOPE_PIN='33aab1ab9c5d919e481f1f0789c07428ec789601a3e3332421b10caff9c4e2a3'
INPUTS={**POSTS,SCOPE:(SCOPE_PIN,24,5)}
GENERATED={'dev/codex/schubert/nk/protocol/file/MediaDescriptorValidator$1':('MediaDescriptorValidator.java',1,55),'dev/codex/schubert/nk/protocol/codec/PayloadCodec$1':('PayloadCodec.java',1,55),'dev/codex/schubert/nk/protocol/layout/FieldDefinition$1':('FieldDefinition.java',1,55),'dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$1':('LayoutFieldCatalog.java',2,124)}
OUT=data.BASE/'PG14374-current-thirteen-host198-registry-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

CONTEXT_REVIEW=('PG14370-monitor-seven-fourteen-context-v1','018896b9e94f61bc2e6024afd12da36f1d6f887b08654d6b1455a2a3666de166')
CONTEXT_POST=('PG14372-monitor-seven-fourteen-post-v1','b9666f840b0c0e081ede68ca45f71aa058ecd5821c39e15a4507ea884a5a2aad')

def context_reference(hashes):
    review,post=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in (CONTEXT_REVIEW,CONTEXT_POST)]
    require(all(v['actualExit']==0 and v['source']==SOURCE and v['sourceContexts']==14 and v['sourceFiles']==7 and v['productTestsExecuted']==0 and v['qualityGatePass'] is False for v in (review,post)),'fixed source contexts never Product qualification')
    require(post['reviewManifestSha256']==CONTEXT_REVIEW[1] and post['reviewSha256']==review['reviewSha256'] and post['metadataNegativeVectors']==18 and post['sourceGuardNegativeVectors']==23,'actual independent source contract check')
    rows=data.read_checked(data.BASE/CONTEXT_REVIEW[0]/'review.json',review['reviewSha256'])['rows']
    require(len(rows)==len({v['id'] for v in rows})==14 and len({v['path'] for v in rows})==7,'exact source reason IDs')
    require(all(hashes[v['path']]==v['sourceSha256'] and v['source']==SOURCE and v['rawRetained'] is v['currentWholeJoinPending'] is True and v['qualityGatePass'] is False and v['productTestsExecuted']==0 for v in rows),'no raw erasure or PT conversion')
    return dict(review=CONTEXT_REVIEW,post=CONTEXT_POST,sourceContexts=14,sourceFiles=7,ids=sorted(v['id'] for v in rows),currentWholeJoinPending=True,productTestsExecuted=0,qualityGatePass=False)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only source registry')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL_PIN)
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current normal source, no historical PT transfer')
    hashes=normal['begin']['inputHashes'];require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all current input hashes fixed')
    require(all(data.sha(__import__('pathlib').Path(j['path']).read_bytes())==j['sha256'] for j in normal['jars'].values()),'all six compiled jars unchanged')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    cases=[];suites=set();units={};owners={};entries=[];metadata_classes={};supplements={};scope_refs=[]
    for name,(pin,count,suite_count) in INPUTS.items():
        post=data.read_checked(data.BASE/name/'manifest.json',pin)
        require(post['source']==SOURCE and post['normalManifestSha256']==NORMAL_PIN and post['actualExit']==0,'same-source genuine post')
        require(post['tests']==count and post['suites']==suite_count and all(post[k]==0 for k in ('failures','errors','skipped','reruns','newTestIds','newAccepted')),'exact actual original case counts')
        require(post['singleSession'] is True and post['crcMismatch']==0 and post['priorProductResultsReused'] is False and post['oldCoverageTransferred'] is False,'one exec CRC without old result transfer')
        require(post['whole451Accepted'] is post['wholeF03Accepted'] is post['formalUpdated'] is False,'no whole/formal promotion')
        require(post['completeSourceCoverageMeasured'] is True and len(post['cases'])==count and len(post['fullSourceUnits'])==post['targetSourceUnits'],'complete scoped source measurement, not automatically four100')
        for name_meta in post.get('metadataClasses',[]):
            info=post['sourcePhysicalInventory'][name_meta];has_code=any(m['hasCode'] for m in info['methods'])
            if has_code:
                require(name_meta in GENERATED and info['flags']==4128 and info['sourceFile']==GENERATED[name_meta][0] and post.get('metadataKind')=='COMPILER_SYNTHETIC_ENUM_SWITCH_STANDARD_JACOCO_FILTER_NOT_NO_CODE','only recorded standard filtered synthetic')
                require(info['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=GENERATED[name_meta][2])],'recorded original generated bytecode length')
                kind='COMPILER_SYNTHETIC_STANDARD_FILTER'
            else:kind='NO_CODE'
            require(post['officialGeneratedFiltersUnchanged'] is True and post['manualCounterExclusions']==[],'no manual metadata exclusion')
            require(name_meta not in metadata_classes,'metadata belongs to one complete source')
            metadata_classes[name_meta]=dict(kind=kind,sha256=post['physicalClasses'][name_meta],postSha256=pin)
        if 'supplementalOwnershipCandidate' in post:
            candidate=post['supplementalOwnershipCandidate'];require(candidate['path'] not in supplements and candidate['historicalRuntimeNotTransferred'] is True and candidate['currentBaselineOwnerStillUnknown'] is True,'separate owner candidate, not old runtime')
            require(candidate['sha256']==hashes[candidate['path']] and candidate['status']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','same-byte prior candidate only')
            supplements[candidate['path']]=candidate
        local={(r['classname'],r['name']) for r in post['cases']}
        require(len(local)==count and all(r['result']=='PASS' and not r['nonPass'] for r in post['cases']),'unique successful original methods')
        if name==SCOPE:
            require(post['currentSourceExistingExecReanalyzed'] is post['originalTestsCountedElsewhere'] is True and post['newProductExecutions']==0,'scope-only, original cases/exec already counted')
            require(set(local)<=set(cases) and any(e['sha256']==post['originalQualificationPostSha256'] and e['execSha256']==post['execSha256'] and e['sessionIdentity']==post['sessionIdentity'] for e in entries),'supplement matches exact previously-counted exec and every case')
        else:
            cases.extend(sorted(local));suites.update(r[0] for r in local)
        for p,owned in post['owners'].items():
            require(hashes[p]==owned['sha256'] and all(owned[k]==v for k,v in canonical(p,logical).items()),'preserve exact known/unknown canonical owner')
            if p in owners:require(owners[p]==owned,'consistent shared owner')
            owners[p]=owned
        for source_name,unit in post['fullSourceUnits'].items():
            require(source_name not in units,'source counters belong to a single original exec, never a union')
            counters=unit['totals'];require(set(counters)=={'LINE','METHOD','CLASS','BRANCH'},'four explicit counters')
            require(all(type(v[k]) is int and v[k]>=0 for v in counters.values() for k in ('covered','missed')),'typed measured counters')
            qualified=all(v['missed']==0 and v['covered']>0 for v in counters.values())
            require(unit['four100'] is qualified,'measured four100 including explicit misses')
            metadata=set(unit['physical'])<=set(post.get('metadataClasses',[]))
            natural=not metadata and counters['BRANCH']==dict(missed=0,covered=0)
            require(set(unit['physical'])<=set(post['physicalClasses']) and all(n in post['executable'] or n in post.get('metadataClasses',[]) for n in unit['physical']),'full declared physical closure including metadata')
            if metadata:
                require(all(v==dict(missed=0,covered=0) for v in counters.values()),'noCode has no invented counters')
                require(all(not m['hasCode'] for n in unit['physical'] for m in post['sourcePhysicalInventory'][n]['methods']),'all metadata methods without code')
            if natural:require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'natural0 retains full executable coverage')
            units[source_name]=dict(post=name,postSha256=pin,physical=unit['physical'],counters=counters,four100=qualified,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],metadataOnly=metadata,branchNaturallyZero=natural)
        if name==SCOPE:scope_refs.append(dict(name=name,sha256=pin,testsAlreadyCounted=count,newTests=0,newExecs=0,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ADDITIONAL_SOURCE_SAME_ALREADY_COUNTED_EXEC'))
        else:entries.append(dict(name=name,sha256=pin,tests=count,suites=suite_count,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    require(len(cases)==len(set(cases))==198 and len(suites)==35 and len(units)==107,'thirteen original executions/198 methods/35 suites/107 complete Source units')
    require(sum(u['four100'] for u in units.values())==49 and sum(len(u['physical']) for u in units.values())==120,'49 qualified Source units, all120 physical closures')
    require(sum(u['branchNaturallyZero'] for u in units.values())==56 and sum(u['metadataOnly'] for u in units.values())==1,'separate natural branch0 and noCode')
    pending={n:u for n,u in units.items() if not u['four100'] and not u['branchNaturallyZero'] and not u['metadataOnly']}
    require(len(pending)==1 and next(iter(pending)).endswith('/InboundTransactions'),'retain actual incomplete Source')
    remain=next(iter(pending.values()))['counters']
    require(remain['LINE']['missed']==10 and remain['METHOD']['missed']==2,'incomplete actual ten lines/two methods unchanged')
    require(len(owners)==143 and sum(v['canonicalOwner'] is None for v in owners.values())==38,'105 baseline-known and38 unknown paths, no invented canonical')
    require(len(metadata_classes)==5 and sum(v['kind']=='NO_CODE' for v in metadata_classes.values())==1 and len(supplements)==1,'noCode and code-bearing synthetic remain distinct')
    contexts=context_reference(hashes)
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_PIN,originalPostReferences=entries,additionalScopeReferences=scope_refs,additionalSourceContractReference=contexts,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted(suites),tests=198,suites=35,originalExecs=13,fullSourceUnits=units,measuredSourcePrograms=107,measuredPhysical=120,executablePhysical=115,metadataPhysical=5,generatedMetadataPhysical=4,four100SourcePrograms=49,four100Physical=61,four100ExecutablePhysical=57,naturalZeroBranchSourcePrograms=56,naturalZeroBranchPhysical=57,metadataSourcePrograms=1,incompleteSourcePrograms=1,owners=owners,unknownOwnerPaths=38,metadataClasses=metadata_classes,supplementalOwnershipCandidates=supplements,priorSource0061TestsTransferred=False,coverageExecUnion=False,originalTestsReexecutedByRegistry=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
