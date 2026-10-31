"""Independently reconstruct values4 registry with full 22-physical partial families and five true NoCode."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15962_current2088_expiry_scope_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='fe4e0cd55f6677b6797dea4644781ec91ee99a3c2c9597ed8712917f55c7393f'
OUT=data.BASE/'PG15964-current2088-expiry-scope-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15962-current2088-expiry-scope-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['semanticNegativeVectors']==negative_count and proof['tests']==count,'genuine whole-codec independent proof')
        require(p['onlyInjectedJdkResourcePortsAndAuditValues'] is proof['onlyInjectedJdkResourcePortsAndAuditValues'] is p['actualCompilerGeneratedTwrOracleInvoked'] is proof['actualCompilerGeneratedTwrOracleInvoked'] is True,'data constructors only, no enclosing operation')
        require(p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is p['actualFilesOpenedByProduct'] is proof['actualFilesOpenedByProduct'] is p['actualSecretKeysLoaded'] is proof['actualSecretKeysLoaded'] is p['actualPrivateFilesOpened'] is proof['actualPrivateFilesOpened'] is False,'no IO/crypto/private access')
        require(p['helperPreviousSourceProofs']==proof['previousHelperProofs'] and len(proof['previousHelperProofs'])==0 and all(old['fullSourceUnits'][n]==u for n,u in proof['previousHelperProofs'].items()),'all old complete/incomplete helper scopes unchanged')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&methods,'only new disjoint actual8/4');methods|=new
        require(len(p['fullSourceUnits'])==2 and p['singleSession'] is True and p['crcMismatch']==0 and len(p['metadataClasses'])==3,'full whole Source Code scope')
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and p['strictFour100GateExit']==1 and (proof['sourcePrograms'],proof['physicalClasses'],proof['four100SourcePrograms'],proof['naturallyBranchZeroSourcePrograms'],proof['incompleteSourcePrograms'])==(2,8,0,1,1),'whole Source/counter and actual caller categories')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,value in p['owners'].items():
            require(path not in owners or owners[path]==value,'shared owners unchanged');owners[path]=copy.deepcopy(value)
        for n in p['metadataClasses']:
            require(n not in metadata and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new NoCode interface unique')
            metadata[n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        refs.append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=('ORIGINAL_EXPIRY_SCOPE24_TWO_WHOLE_SOURCES_EIGHT_PHYSICAL_REAL_JDBC_UNEXECUTED')))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']+1==38 and len({n for name in incomplete for n in units[name]['physical']})==90,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+24,uniqueProductMethodDelta=24,newTestIds=24,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(2088,276,470,651,612,250,364,353,122,2196,176,191,6,38),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':385,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':229,'UNKNOWN':160},'actual owners distinct from change group; UNKNOWN retained')
    decl=read(('PG15950-g13-current-test-declaration-inventory-v1','0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139'))
    declpost=read(('PG15952-g13-current-test-declaration-post-v1','ae9eba3351785a9c5cf15bd8231b9622b8fd6ffe99581e6aa23cc6f546e37945'))
    require(decl['actualExit']==declpost['actualExit']==0 and decl['source']==declpost['source']==SOURCE,'fixed separately qualified ordinary declarations')
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',decl['files']['exact-ordinary-bindings.json'])
    declkeys={(b['className'],b['method']) for b in bindings}
    require(len(declkeys)==5786 and len(methods&declkeys)==2082 and len(methods-declkeys)==6,'independent normal/quality-fixture case domain split')
    declaration_reference=dict(source=SOURCE,inventoryManifestSha256='0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139',independentManifestSha256='ae9eba3351785a9c5cf15bd8231b9622b8fd6ffe99581e6aa23cc6f546e37945',ordinaryDeclarations=5786,ordinaryCaseReferences=2082,ordinaryWithoutCurrentCaseReference=3704,existingQualityFixtureCases=6,nonordinaryAnnotations=1,meaning='DECLARATION_REFERENCE_COUNTS_NOT_PHASE_OR_EFFORT_PERCENT',phaseCompletionPercent=None)
    changed={'currentOrdinaryTestDeclarationReference','lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','metadataClasses',*summary}
    def contract(v):
        require(v['currentOrdinaryTestDeclarationReference']==declaration_reference,'all declaration reference counts with fixture split')
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED' and v['postDisclosureCorrections']==old['postDisclosureCorrections'],'new PT marker and all previous digest errata retained')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(wire(v['metadataClasses'])==wire(metadata) and v['metadataPhysical']==39,'new explicit NoCode interface and all old metadata retained')
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
    import pg15960_expiry_scope_independent as domain
    domain.assess(p);natural_labels=[]
    for label,mutate in [('outer-probe-hidden',lambda v:v['executable']['dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$Stage']['counters']['METHOD'].update(covered=1)),('unexecuted-erased',lambda v:v.update(unexecutedCodeClasses=[])),('strict-whole-promoted',lambda v:v.update(strictFour100GateExit=0))]:
        bad=copy.deepcopy(p);mutate(bad)
        try:domain.assess(bad)
        except ValueError:natural_labels.append(label)
        else:raise ValueError('outer Code/scope hidden by data qualifier')
    declaration_labels=[]
    for key,value in [('ordinaryCaseReferences',2088),('existingQualityFixtureCases',0),('ordinaryWithoutCurrentCaseReference',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:declaration_labels.append(key)
        else:raise ValueError('ordinary declaration and fixture/phase roles must remain distinct')
    for v in [old,prior,m,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,ordinaryDeclarationNegativeVectors=len(declaration_labels),ordinaryDeclarationNegativeLabels=declaration_labels,currentOrdinaryTestDeclarationReference=declaration_reference,sourceCategoryNegativeVectors=len(natural_labels),sourceCategoryNegativeLabels=natural_labels,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=2,newUniqueMethods=24,newIncompleteSources=1,newIncompletePhysical=7,incompletePhysicalClasses=90,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
