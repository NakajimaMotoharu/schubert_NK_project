"""Independent current Inbox15/full14Source: nine four100/three natural/two gaps, old history retained."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15604_current1903_checksum_capacity_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='eb3aa009a2892cffbac916a23e6dbd5c4d59b1a98476007dcbe2046e98088d72'
OUT=data.BASE/'PG15606-current1903-checksum-capacity-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15604-current1903-checksum-capacity-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['semanticNegativeVectors']==negative_count and proof['tests']==count,'genuine whole-codec independent proof')
        require(p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is True and p['publicSyntheticTestKeysUsed'] is proof['publicSyntheticTestKeysUsed'] is p['childLocalJcaRegistryRestorationTested'] is proof['childLocalJcaRegistryRestorationTested'] is p['ownFreshJvmProviderStateOnly'] is proof['ownFreshJvmProviderStateOnly'] is p['actualSecretKeysLoaded'] is proof['actualSecretKeysLoaded'] is False,'truthful public SHA comparison/no key or JCA mutation')
        require(p['actualJmsConnectionsCreated']==proof['actualJmsConnectionsCreated']==p['actualJmsContextsCreated']==proof['actualJmsContextsCreated']==0 and p['actualBrokerOrListenerStarted'] is proof['actualBrokerOrListenerStarted'] is p['actualFilesOpenedByProduct'] is proof['actualFilesOpenedByProduct'] is p['actualCredentialValuesUsed'] is proof['actualCredentialValuesUsed'] is p['actualAuthenticationOrSessionIssued'] is proof['actualAuthenticationOrSessionIssued'] is False and proof['previousHelpersNotReaccepted'] is True and p['cryptoOperationKind']==proof['cryptoOperationKind']=='MESSAGEDIGEST_ISEQUAL_PUBLIC_LITERAL_SHA_TEXT_ONLY','no live/private/auth/helper reacceptance')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&methods,'only new disjoint actual8/4');methods|=new
        require(len(p['fullSourceUnits'])==4 and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'full whole Source Code scope')
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and p['strictFour100GateExit']==1 and (proof['sourcePrograms'],proof['physicalClasses'],proof['four100SourcePrograms'],proof['naturallyBranchZeroSourcePrograms'],proof['incompleteSourcePrograms'],proof['baselineMainOwnerRows'],proof['unknownTestOwnerRows'])==(4,7,2,2,0,4,2),'whole Source/counter and actual caller categories')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,value in p['owners'].items():
            require(path not in owners or owners[path]==value,'shared owners unchanged');owners[path]=copy.deepcopy(value)
        for n in p['metadataClasses']:
            require(n not in metadata and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new NoCode interface unique')
            metadata[n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        refs.append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=('ORIGINAL_CHECKSUM_CAPACITY9_FULL_FOUR_SOURCE_TWO_FOUR_TWO_NATURAL')))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']+0==13 and len({n for name in incomplete for n in units[name]['physical']})==22,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+9,uniqueProductMethodDelta=9,newTestIds=9,sourceProgramDelta=4,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(1903,242,425,557,536,239,349,338,104,2011,167,180,6,13),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':340,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':227,'UNKNOWN':126},'actual owners distinct from change group; UNKNOWN retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','metadataClasses',*summary}
    def contract(v):
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED' and v['postDisclosureCorrections']==old['postDisclosureCorrections'],'new PT marker and all previous digest errata retained')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(wire(v['metadataClasses'])==wire(metadata) and v['metadataPhysical']==21,'new explicit NoCode interface and all old metadata retained')
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
    for v in [old,prior,m,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=4,newUniqueMethods=9,newIncompleteSources=0,newIncompletePhysical=0,incompletePhysicalClasses=22,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
