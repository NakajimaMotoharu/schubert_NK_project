"""Independent original772 XML and complete source scopes with single-exec Catalog replacement history."""
import copy
from collections import Counter
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14636_current_thirty_nine_host772_registry import SOURCE,NORMAL_PIN,INPUTS,SCOPE,GENERATED,CONTEXT_REVIEW,CONTEXT_POST

OUT=data.BASE/'PG14638-current-thirty-nine-host772-registry-post-v1'
PIN='a657d2fead98629001f67b0e842b94adfd86a041b10651f624f7d6cd4c76adfe'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(value):return json.dumps(value,sort_keys=True)

def contract(value,expected):
    require(all(k in value and wire(value[k])==wire(v) for k,v in expected.items()),'exact actual source/XML/unit counts, flags and unresolved states')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only post')
    m=data.read_checked(data.BASE/'PG14636-current-thirty-nine-host772-registry-v1/manifest.json',PIN);verify(m['invocation'])
    n=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL_PIN)
    require(n['source']==SOURCE and n['actualExit']==n['testsExecuted']==0,'current normal source')
    hashes=n['begin']['inputHashes'];require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all current inputs unchanged')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    cases=[];suites=set();units={};owners={};entries=[];metadata_classes={};supplements={};scope_refs=[]
    for name,(pin,count,suite_count) in INPUTS.items():
        post=data.read_checked(data.BASE/name/'manifest.json',pin);require(post['actualExit']==0 and post['source']==SOURCE,'actual input post')
        for name_meta in post.get('metadataClasses',[]):
            info=post['sourcePhysicalInventory'][name_meta]
            if any(row['hasCode'] for row in info['methods']):
                require(name_meta in GENERATED and info['flags']==4128 and info['sourceFile']==GENERATED[name_meta][0] and info['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=GENERATED[name_meta][2])],'only actual recorded synthetic switch')
                kind='COMPILER_SYNTHETIC_STANDARD_FILTER'
            else:kind='NO_CODE'
            require(post['officialGeneratedFiltersUnchanged'] and post['manualCounterExclusions']==[] and name_meta not in metadata_classes,'no excludes or duplicate metadata')
            metadata_classes[name_meta]=dict(kind=kind,sha256=post['physicalClasses'][name_meta],postSha256=pin)
        if 'supplementalOwnershipCandidate' in post:
            item=post['supplementalOwnershipCandidate'];require(item['sha256']==hashes[item['path']] and item['historicalRuntimeNotTransferred'] is True and item['currentBaselineOwnerStillUnknown'] is True,'current-byte old candidate not runtime')
            supplements[item['path']]=item
        local=[]
        for filename,digest in post['xmlHashes'].items():
            raw=(data.BASE/name/filename).read_bytes();require(data.sha(raw)==digest,'original returned public XML hash')
            root=ET.fromstring(raw);require(int(root.get('tests'))==len(root.findall('testcase')) and all(int(root.get(k))==0 for k in ('failures','errors','skipped')),'actual XML FES0')
            for case in root.findall('testcase'):
                require(not list(case),'non-PASS XML cannot enter registry');local.append((case.get('classname'),case.get('name')))
        require(len(local)==count and len(set(c for c,_ in local))==suite_count,'exact original XML methods/suites')
        require(set(local)=={(r['classname'],r['name']) for r in post['cases']},'post and actual XML identities')
        if name==SCOPE:
            require(post['currentSourceExistingExecReanalyzed'] is post['originalTestsCountedElsewhere'] is True and post['newProductExecutions']==0,'scope-only, original cases/exec already counted')
            require(set(local)<=set(cases) and any(e['sha256']==post['originalQualificationPostSha256'] and e['execSha256']==post['execSha256'] and e['sessionIdentity']==post['sessionIdentity'] for e in entries),'supplement matches exact previously-counted exec and every case')
        else:
            cases.extend(local);suites.update(c for c,_ in local)
        for p,owned in post['owners'].items():
            require(hashes[p]==owned['sha256'] and all(owned[k]==v for k,v in canonical(p,logical).items()),'preserve actual known/unknown source ownership');owners[p]=owned
        for source_name,unit in post['fullSourceUnits'].items():
            require(source_name not in units,'no Source coverage union')
            require(post['singleSession'] is True and post['crcMismatch']==0 and post['priorProductResultsReused'] is False,'genuine single exec CRC')
            expected_four=all(v['missed']==0 and v['covered']>0 for v in unit['totals'].values())
            require(unit['four100'] is expected_four,'no missed-to-PASS normalization')
            metadata=set(unit['physical'])<=set(post.get('metadataClasses',[]))
            natural=not metadata and unit['totals']['BRANCH']==dict(missed=0,covered=0)
            if metadata:require(all(v==dict(missed=0,covered=0) for v in unit['totals'].values()),'exact noCode counters')
            if natural:require(all(unit['totals'][k]['missed']==0 and unit['totals'][k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'natural0 not four100')
            units[source_name]=dict(post=name,postSha256=pin,physical=unit['physical'],counters=unit['totals'],four100=expected_four,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],metadataOnly=metadata,branchNaturallyZero=natural)
        if name==SCOPE:scope_refs.append(dict(name=name,sha256=pin,testsAlreadyCounted=count,newTests=0,newExecs=0,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ADDITIONAL_SOURCE_SAME_ALREADY_COUNTED_EXEC'))
        else:entries.append(dict(name=name,sha256=pin,tests=count,suites=suite_count,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    require(len(cases)==len(set(cases))==772 and len(suites)==102 and len(units)==180,'no duplicate/lost original XML')
    roles=dict(Counter(v['ownershipStatus'] for v in owners.values()))
    require(roles=={'BASELINE_LOGICAL_REFERENCE':138,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':65},'actual owner roles, proposed never baseline/accepted')
    previous=data.read_checked(data.BASE/'PG14562-catalog-two-source-proof-resolution-v1/manifest.json','0eade5a1336d0c4a01bd6a951e1c1310278ee6a3376ee448a95903b904ec68ab')
    previous_post=data.read_checked(data.BASE/'PG14564-catalog-two-source-proof-resolution-post-v1/manifest.json','f404f58e3a886af3516fb30ac0db3e4704e105d69ff15ccd39729252f14b5b7f')
    require(previous_post['registryManifestSha256']=='0eade5a1336d0c4a01bd6a951e1c1310278ee6a3376ee448a95903b904ec68ab' and previous_post['summaryBoundToVerifiedActualFields'] and previous_post['metadataNegativeVectors']==23,'independent replacement provenance')
    verify(previous['invocation']);verify(previous_post['invocation'])
    require(previous['source']==previous_post['source']==SOURCE and previous['tests']==660 and previous['originalExecs']==31,'old same-source registry')
    require({(c['classname'],c['name']) for c in previous['cases']}<set(cases),'old original cases retained')
    require(all(owners[p]==v for p,v in previous['owners'].items()),'old owners retained')
    history=previous['qualificationReplacedUnitHistory']
    for name,prior in history.items():
        require(units[name]==prior,'exact old pre-replacement proof independently reconstructed')
        units[name]=previous['fullSourceUnits'][name]
    require(len(history)==2 and sum(u['four100'] for u in units.values())==113,'same two single-exec replacements')
    pending={n:u for n,u in units.items() if not u['four100'] and not u['branchNaturallyZero'] and not u['metadataOnly']}
    require(set(pending)=={'dev/codex/schubert/nk/api/messaging/inbound/InboundTransactions','dev/codex/schubert/nk/api/application/admin/UserQueryRequest','dev/codex/schubert/nk/api/application/log/LogRequest'},'genuine Inbound and two backend gaps retained')
    previous_unique=data.read_checked(data.BASE/'PG14602-current-thirty-five-host724-registry-v1/manifest.json','cb752b18897912632a0787498e4d08982756123861b950ab0fa10dbd58fff89b')
    previous_unique_post=data.read_checked(data.BASE/'PG14604-current-thirty-five-host724-registry-post-v1/manifest.json','323a092c12394d44289c34332c22a5d5bf5a4a760668056793f41a01670d2936')
    require(previous_unique['source']==previous_unique_post['source']==SOURCE and previous_unique_post['registryManifestSha256']=='cb752b18897912632a0787498e4d08982756123861b950ab0fa10dbd58fff89b','immediate current724 provenance')
    verify(previous_unique['invocation']);verify(previous_unique_post['invocation'])
    require(previous_unique['tests']==previous_unique_post['originalXmlMethods']==724 and previous_unique['originalExecs']==35,'previous unique counts not repeated qualification')
    require({(v['classname'],v['name']) for v in previous_unique['cases']}<set(cases),'old724 case subset retained')
    require(all(units[n]==v for n,v in previous_unique['fullSourceUnits'].items()) and all(owners[n]==v for n,v in previous_unique['owners'].items()),'all old724 units and owner roles identical')
    require(previous_unique['qualificationReplacedUnitHistory']==history and previous_unique['additionalQualificationReferences']==previous['additionalQualificationReferences'],'Catalog qualification history retained')
    qualification_fields={k:previous[k] for k in ('additionalQualificationReferences','qualificationReplacedUnitHistory','additionalQualificationExecs','sourceReplacementPreservesOriginalCases')}
    qualification_fields.update(previousUniqueRegistryReference=['PG14602-current-thirty-five-host724-registry-v1','cb752b18897912632a0787498e4d08982756123861b950ab0fa10dbd58fff89b'],previousRegistryPostReference=['PG14604-current-thirty-five-host724-registry-post-v1','323a092c12394d44289c34332c22a5d5bf5a4a760668056793f41a01670d2936'],totalProductExecs=40,totalMethodExecutions=828,uniqueProductMethodDelta=48,sourceProgramDelta=8)
    creview,cpost=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in (CONTEXT_REVIEW,CONTEXT_POST)]
    require(type(cpost['metadataNegativeVectors']) is int and cpost['metadataNegativeVectors']==18 and type(cpost['sourceGuardNegativeVectors']) is int and cpost['sourceGuardNegativeVectors']==23,'BUG2101 independent original proof roles18/23, not group21')
    crows=data.read_checked(data.BASE/CONTEXT_REVIEW[0]/'review.json',creview['reviewSha256'])['rows']
    require(cpost['actualExit']==creview['actualExit']==0 and cpost['source']==creview['source']==SOURCE and cpost['reviewManifestSha256']==CONTEXT_REVIEW[1] and cpost['reviewSha256']==creview['reviewSha256'],'independent actual context provenance')
    require(len(crows)==len({v['id'] for v in crows})==14 and len({v['path'] for v in crows})==7,'exact14 source IDs')
    require(all(v['currentWholeJoinPending'] is v['rawRetained'] is True and v['qualityGatePass'] is False and type(v['productTestsExecuted']) is int and v['productTestsExecuted']==0 and hashes[v['path']]==v['sourceSha256'] for v in crows),'every reviewed source unchanged and unresolved quality retained')
    contexts=dict(review=CONTEXT_REVIEW,post=CONTEXT_POST,sourceContexts=14,sourceFiles=7,ids=sorted(v['id'] for v in crows),currentWholeJoinPending=True,productTestsExecuted=0,qualityGatePass=False)
    expected=dict(actualExit=0,source=SOURCE,sourceContextProofCounterNegativeVectors=5,normalManifestSha256=NORMAL_PIN,originalPostReferences=entries,additionalScopeReferences=scope_refs,additionalSourceContractReference=contexts,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted(suites),tests=772,suites=102,originalExecs=39,fullSourceUnits=units,measuredSourcePrograms=180,measuredPhysical=239,executablePhysical=233,metadataPhysical=6,generatedMetadataPhysical=4,four100SourcePrograms=113,four100Physical=170,four100ExecutablePhysical=165,naturalZeroBranchSourcePrograms=63,naturalZeroBranchPhysical=65,metadataSourcePrograms=1,incompleteSourcePrograms=3,owners=owners,ownerStatusCounts=roles,unknownOwnerPaths=65,metadataClasses=metadata_classes,supplementalOwnershipCandidates=supplements,priorSource0061TestsTransferred=False,coverageExecUnion=False,originalTestsReexecutedByRegistry=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None,**qualification_fields)
    contract(m,expected);labels=[]
    for label,mutate in [('source',lambda v:v.update(source='0'*40)),('test-count',lambda v:v.update(tests=171)),('exec-count',lambda v:v.update(originalExecs=2)),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('incomplete-erased',lambda v:v.update(incompleteSourcePrograms=0)),('four100-inflated',lambda v:v.update(four100SourcePrograms=21)),('owner-invented',lambda v:next(x for x in v['owners'].values() if x['canonicalOwner'] is None).update(canonicalOwner='WBS-P005-03')),('union',lambda v:v.update(coverageExecUnion=True)),('old-transfer',lambda v:v.update(priorSource0061TestsTransferred=True)),('bool-counter',lambda v:v.update(originalTestsReexecutedByRegistry=False)),('natural0-erased',lambda v:v.update(naturalZeroBranchSourcePrograms=0)),('metadata-as-four100',lambda v:v.update(metadataSourcePrograms=0)),('generated-erased',lambda v:v.update(generatedMetadataPhysical=0)),('code-metadata-inflated',lambda v:v.update(executablePhysical=64)),('candidate-erased',lambda v:v.update(supplementalOwnershipCandidates={})),('formal',lambda v:v.update(formalUpdated=True)),('accepted',lambda v:v.update(newAccepted=1)),('scope-erased',lambda v:v.update(additionalScopeReferences=[])),('scope-counted-twice',lambda v:v['additionalScopeReferences'][0].update(newTests=24)),('context-count-as-PT',lambda v:v['additionalSourceContractReference'].update(productTestsExecuted=14)),('context-whole-erased',lambda v:v['additionalSourceContractReference'].update(currentWholeJoinPending=False)),('candidate-erased-role',lambda v:v['ownerStatusCounts'].update(NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=0)),('candidate-as-baseline',lambda v:next(x for x in v['owners'].values() if x['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED').update(ownershipStatus='BASELINE_LOGICAL_REFERENCE'))]:
        bad=copy.deepcopy(m);mutate(bad)
        try:contract(bad,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('false metadata accepted: '+label)
    extra_vectors=[('qualification-erased',lambda v:v.update(additionalQualificationReferences=[])),('history-erased',lambda v:v.update(qualificationReplacedUnitHistory={})),('qualification-as-new',lambda v:v.update(tests=828)),('qualification-as-first',lambda v:v.update(originalExecs=40))]
    for label,mutate in extra_vectors:
        bad=copy.deepcopy(m);mutate(bad)
        try:contract(bad,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('false Catalog history accepted: '+label)
    require(len(labels)==27,'23 established plus four qualification-history negatives')
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    summary=dict(actualExit=0,source=SOURCE,invocation=invocation,sourceContextProofCounterNegativeVectors=5,registryManifestSha256=PIN,ownerStatusCounts=roles,sourceContractContexts=contexts['sourceContexts'],additionalScopes=len(scope_refs),originalXmlMethods=772,originalXmlSuites=102,originalExecs=39,four100SourcePrograms=113,naturalZeroBranchSourcePrograms=63,generatedMetadataPhysical=4,four100ExecutablePhysical=165,metadataSourcePrograms=1,incompleteSourcePrograms=3,unknownOwnerPaths=65,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,oldSourceResultsTransferred=False,coverageExecUnion=False,originalTestsReexecuted=0,additionalQualificationExecs=1,totalProductExecs=40,totalMethodExecutions=828,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False)
    bindings=dict(source=m['source'],ownerStatusCounts=m['ownerStatusCounts'],sourceContractContexts=m['additionalSourceContractReference']['sourceContexts'],additionalScopes=len(m['additionalScopeReferences']),originalXmlMethods=m['tests'],originalXmlSuites=m['suites'],originalExecs=m['originalExecs'],four100SourcePrograms=m['four100SourcePrograms'],naturalZeroBranchSourcePrograms=m['naturalZeroBranchSourcePrograms'],generatedMetadataPhysical=m['generatedMetadataPhysical'],four100ExecutablePhysical=m['four100ExecutablePhysical'],metadataSourcePrograms=m['metadataSourcePrograms'],incompleteSourcePrograms=m['incompleteSourcePrograms'],unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),additionalQualificationExecs=m['additionalQualificationExecs'],totalProductExecs=m['totalProductExecs'],totalMethodExecutions=m['totalMethodExecutions'])
    def verify_summary(value):
        require(all(wire(value[k])==wire(v) for k,v in bindings.items()),'summary must bind verified actual fields, not stale literals')
    verify_summary(summary)
    summary_negatives=0
    for key,bad in [('unknownOwnerPaths',12),('originalExecs',True),('source','OLD_SOURCE')]:
        wrong=copy.deepcopy(summary);wrong[key]=bad
        try:verify_summary(wrong)
        except ValueError:summary_negatives+=1
        else:raise ValueError('stale summary accepted')
    require(summary_negatives==3,'all summary negative fields')
    summary['postSummaryNegativeVectors']=summary_negatives
    summary['summaryBoundToVerifiedActualFields']=True
    summary['qualificationHistoryPreserved']=True
    data.write(OUT/'manifest.json',summary)
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
