"""Independent stream5 registry and global/perSource disclosure annotation; no old proof or counter replacement."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15892_current2060_scenario_stream_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='c9edd9a200ac7e24583872ed715368439346d9cb5c0243722f164eba6bf60f49'
OUT=data.BASE/'PG15894-current2060-scenario-stream-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15892-current2060-scenario-stream-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['semanticNegativeVectors']==negative_count and proof['tests']==count,'genuine whole-codec independent proof')
        require(p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is p['onlyPublicScenarioStreamContracts'] is proof['onlyPublicScenarioStreamContracts'] is p['testOwnedTemporaryFixtureWrites'] is proof['testOwnedTemporaryFixtureWrites'] is True,'own fixture/digest effects retained')
        require(p['testOwnNewSlotPublicEvidenceWrites'] is proof['testOwnNewSlotPublicEvidenceWrites'] is p['actualSecretKeysLoaded'] is proof['actualSecretKeysLoaded'] is p['actualPrivateFilesOpened'] is proof['actualPrivateFilesOpened'] is False,'temporary fixture IO not explicit evidence output or secret IO')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&methods,'only new disjoint actual8/4');methods|=new
        require(len(p['fullSourceUnits'])==1 and p['singleSession'] is True and p['crcMismatch']==0 and len(p['metadataClasses'])==0,'full whole Source Code scope')
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and p['strictFour100GateExit']==0 and (proof['sourcePrograms'],proof['physicalClasses'],proof['four100SourcePrograms'],proof['naturallyBranchZeroSourcePrograms'],proof['incompleteSourcePrograms'])==(1,1,1,0,0),'whole Source/counter and actual caller categories')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,value in p['owners'].items():
            require(path not in owners or owners[path]==value,'shared owners unchanged');owners[path]=copy.deepcopy(value)
        for n in p['metadataClasses']:
            require(n not in metadata and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new NoCode interface unique')
            metadata[n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        refs.append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=('ORIGINAL_SCENARIO_RECORD_STREAM5_ONE_WHOLE_SOURCE_ONE_CODE_FOUR100')))
    correction_name='PG15889-reader-temporary-fixture-disclosure-erratum-v1';correction_sha='4f9439fb32a5f5876e07bbe731a4864e3c9b46da3e946b18428b46df2f54773f'
    correction=read((correction_name,correction_sha));require(correction['actualExit']==0 and witnesses[-1]['disclosureErratumSha256']==correction_sha and witnesses[-1]['disclosureCorrectionNegativeVectors']==5,'same independently verified metadata correction')
    corrected_post=correction['originalPostSha256'];expected_corrections=copy.deepcopy(old['postDisclosureCorrections'])
    correction_ref=dict(manifest=str((data.BASE/correction_name/'manifest.json').relative_to(data.ROOT)),sha256=correction_sha,bug='BUG2151',horizontal='YKT1898',originalPostSha256=corrected_post,effectiveDisclosure=copy.deepcopy(correction['effectiveDisclosure']),originalQualificationAndCountersUnchanged=True)
    expected_corrections[corrected_post]=copy.deepcopy(correction_ref)
    corrected_names=['dev/codex/schubert/nk/web/storage/ScenarioRecordReader','dev/codex/schubert/nk/web/storage/FileIntegrityException']
    for name in corrected_names:
        require(units[name]['postSha256']==corrected_post and 'effectDisclosureCorrection' not in units[name],'correct original shared test-body metadata only')
        units[name]['effectDisclosureCorrection']=copy.deepcopy(correction_ref)
    verify(correction['invocation'])
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']+0==32 and len({n for name in incomplete for n in units[name]['physical']})==61,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+5,uniqueProductMethodDelta=5,newTestIds=5,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(2060,274,463,621,590,250,364,353,120,2168,175,190,6,32),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':378,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':229,'UNKNOWN':158},'actual owners distinct from change group; UNKNOWN retained')
    changed={'postDisclosureCorrections','lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','metadataClasses',*summary}
    def contract(v):
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED' and wire(v['postDisclosureCorrections'])==wire(expected_corrections),'all old corrections plus exact narrow new correction only')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(wire(v['metadataClasses'])==wire(metadata) and v['metadataPhysical']==31,'new explicit NoCode interface and all old metadata retained')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old Catalog/SQLjoint/JS/metadata/cost/formal untouched')
    contract(m);negative=[]
    for key,value in [('tests',914),('suites',132),('totalProductExecs',61),('totalMethodExecutions',994),('totalRepeatedOriginalMethods',92),('uniqueProductMethodDelta',0),('sourceProgramDelta',0),('four100SourcePrograms',131),('four100Physical',196),('incompleteSourcePrograms',4),('naturalZeroBranchSourcePrograms',145),('measuredSourcePrograms',287),('measuredPhysical',365),('executablePhysical',347),('metadataPhysical',0),('metadataSourcePrograms',0),('fullSourceUnits',{}),('metadataClasses',{}),('cases',old['cases']),('originalPostReferences',old['originalPostReferences']),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('javascriptResourceDomain',{}),('unknownOwnerPaths',99),('ownerStatusCounts',{'BASELINE_LOGICAL_REFERENCE':283,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':103}),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false1697 registry accepted '+key)
    for label in ['typed-counter-bool','typed-four100-int','typed-suite-bool']:
        bad=copy.deepcopy(m)
        if label=='typed-counter-bool':
            next(iter(bad['fullSourceUnits'].values()))['counters']['LINE']['missed']=False
        elif label=='typed-four100-int':
            unit=next(u for u in bad['fullSourceUnits'].values() if u['four100'] is True);unit['four100']=1
        else:
            reference=next(r for r in bad['originalPostReferences'] if r['suites']==1);reference['suites']=True
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('numeric and boolean roles must not alias '+label)
    import pg15890_scenario_record_stream_five_independent as domain
    domain.assess(p);natural_labels=[]
    for label,mutate in [('whole-four-erased',lambda v:v['fullSourceUnits'][domain.NAME].update(four100=False)),('fixture-evidence-conflated',lambda v:v.update(testOwnNewSlotPublicEvidenceWrites=True)),('strict-whole-erased',lambda v:v.update(strictFour100GateExit=1))]:
        bad=copy.deepcopy(p);mutate(bad)
        try:domain.assess(bad)
        except ValueError:natural_labels.append(label)
        else:raise ValueError('source class/effect category mismatch accepted')
    correction_labels=[]
    for label,mutate in [('old-reader-field-correction-erased',lambda v:v['postDisclosureCorrections'].pop(corrected_post)),('per-source-correction-erased',lambda v:v['fullSourceUnits'][corrected_names[0]].pop('effectDisclosureCorrection')),('old-reader-counter-changed',lambda v:v['fullSourceUnits'][corrected_names[0]]['counters']['LINE'].update(missed=1))]:
        bad=copy.deepcopy(m);mutate(bad)
        try:contract(bad)
        except ValueError:correction_labels.append(label)
        else:raise ValueError('old reader qualification/correction mismatch accepted')
    for v in [old,prior,m,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,sourceCategoryNegativeVectors=len(natural_labels),sourceCategoryNegativeLabels=natural_labels,disclosureCorrectionNegativeVectors=len(correction_labels),disclosureCorrectionNegativeLabels=correction_labels,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=1,newUniqueMethods=5,newIncompleteSources=0,newIncompletePhysical=0,incompletePhysicalClasses=61,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
