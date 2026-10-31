"""Register original Expiry24 with full two-family partial denominator and separate Test declaration references."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15908-current2064-observation-values-registry-v1','a2df9a72bc19eca2b725aaff0d5bee234c8da7cdb50e3ec3ce9cf0d5823b3c53')
PREV_POST=('PG15910-current2064-observation-values-registry-post-v1','fec109e9fc8e9e1cfb8b3dd7bb5a009e3f91b63a9a8c1e5df46af405acb84134')
REFS=[['PG15958-expiry-successful-scope-whole24-post-v1','772283e4544eca7dca600fc21f2d2b58b471c543f226559b3dc48ccdb7d4af98','PG15960-expiry-successful-scope-independent-v1','295610c421f4757e933797ecad29f65f3a5a8c8c882c84b1b5c5887e7ed54845',24,24]]
OUT=data.BASE/'PG15962-current2088-expiry-scope-registry-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior=read(PREV),read(PREV_POST)
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'exact independently qualified1760/owner11')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all current frozen inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,ind,indpin,count,negative in REFS:
        p,q=read((folder,pin)),read((ind,indpin));witnesses.extend([p,q])
        require(p['actualExit']==q['actualExit']==0 and p['source']==q['source']==SOURCE and q['postSha256']==pin and p['tests']==q['tests']==count and q['semanticNegativeVectors']==negative,'exact independent original proofs')
        require((q['sourcePrograms'],q['physicalClasses'],q['executablePhysicalClasses'],q['metadataPhysicalClasses'],q['four100SourcePrograms'],q['naturallyBranchZeroSourcePrograms'],q['incompleteSourcePrograms'])==(2,8,5,3,0,1,1),'full five partial Source families, not nested-only denominator')
        require(p['onlyInjectedJdkResourcePortsAndAuditValues'] is q['onlyInjectedJdkResourcePortsAndAuditValues'] is p['actualCompilerGeneratedTwrOracleInvoked'] is q['actualCompilerGeneratedTwrOracleInvoked'] is True and p['strictFour100GateExit']==1,'only declared data constructors, outer operations remain held')
        require(p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is p['actualSecretKeysLoaded'] is q['actualSecretKeysLoaded'] is p['actualPrivateFilesOpened'] is q['actualPrivateFilesOpened'] is p['actualFilesOpenedByProduct'] is q['actualFilesOpenedByProduct'] is False,'no files/crypto/secret or native observation')
        require(p['previousHelpersNotReaccepted'] is q['oldHelperProofsPreserved'] is True and wire(p['helperPreviousSourceProofs'])==wire(q['previousHelperProofs']) and all(old['fullSourceUnits'][n]==u for n,u in q['previousHelperProofs'].items()),'old mixed complete/incomplete helpers retained, never reaccepted')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and len(p['metadataClasses'])==3,'new distinct current cases/full Code only');cases|=new
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name],'whole new Source closure')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,row in p['owners'].items():
            require(row['sha256']==hashes[path] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual new canonical rows, not change-owner inference')
            require(path not in result['owners'] or result['owners'][path]==row,'all shared owner rows preserved');result['owners'][path]=copy.deepcopy(row)
        for n in p['metadataClasses']:
            require(n not in result['metadataClasses'] and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new exact NoCode mapper')
            result['metadataClasses'][n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_EXPIRY_SCOPE24_TWO_WHOLE_SOURCES_EIGHT_PHYSICAL_REAL_JDBC_UNEXECUTED'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(incomplete)==38 and len({p for n in incomplete for p in units[n]['physical']})==90,'disjoint whole Source closures and actual incomplete7/12')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+24,uniqueProductMethodDelta=24,newTestIds=24,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),metadataPhysical=len(meta),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({p for u in units.values() if u['branchNaturallyZero'] for p in u['physical']}),incompleteSourcePrograms=len(incomplete),ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())),unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2088,276,470,651,612,250,364,353,121,122,2196,176,191),'exact current17/9Source/10physical classification')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=385,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=160),'old215 candidates preserved/new9baseline5UNKNOWN')
    declaration=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/manifest.json','0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    declaration_post=data.read_checked(data.BASE/'PG15952-g13-current-test-declaration-post-v1/manifest.json','ae9eba3351785a9c5cf15bd8231b9622b8fd6ffe99581e6aa23cc6f546e37945')
    require(declaration['actualExit']==declaration_post['actualExit']==0 and declaration['source']==declaration_post['source']==SOURCE,'fixed ordinary declaration denominator')
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',declaration['files']['exact-ordinary-bindings.json'])
    keys={(b['className'],b['method']) for b in bindings}
    require(len(keys)==len(bindings)==5786 and len(cases&keys)==2082 and len(cases-keys)==6,'ordinary/quality-fixture domain split, no name normalization')
    result['currentOrdinaryTestDeclarationReference']=dict(source=SOURCE,inventoryManifestSha256='0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139',independentManifestSha256='ae9eba3351785a9c5cf15bd8231b9622b8fd6ffe99581e6aa23cc6f546e37945',ordinaryDeclarations=5786,ordinaryCaseReferences=2082,ordinaryWithoutCurrentCaseReference=3704,existingQualityFixtureCases=6,nonordinaryAnnotations=1,meaning='DECLARATION_REFERENCE_COUNTS_NOT_PHASE_OR_EFFORT_PERCENT',phaseCompletionPercent=None)
    result['lastUpdateKind']='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED'
    require(result['postDisclosureCorrections']==old['postDisclosureCorrections'] and result['postDisclosureCorrections'],'all prior digest errata retained')
    changed={'currentOrdinaryTestDeclarationReference','lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','metadataClasses','metadataPhysical'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(result['owners'][n]==v for n,v in old['owners'].items()),'all old history/candidate215/cost/domain/formal/metadata semantics unchanged')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
