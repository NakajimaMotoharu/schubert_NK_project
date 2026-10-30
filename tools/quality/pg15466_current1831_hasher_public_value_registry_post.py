"""Independent Hasher3/publicValue18 seven Sources; preserve all old proofs and costs."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15464_current1831_hasher_public_value_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='a5f265660960abfe3014bb08d7e9ba46b3e2e30ba3d3dbddbf3532a106c4f1a0'
OUT=data.BASE/'PG15466-current1831-hasher-public-value-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15464-current1831-hasher-public-value-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['semanticNegativeVectors']==negative_count and proof['tests']==count,'genuine whole-codec independent proof')
        require(p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is True and p['actualSecretKeysLoaded'] is proof['actualSecretKeysLoaded'] is False and p['ownFreshJvmProviderStateOnly'] is proof['ownFreshJvmProviderStateOnly'] is True,'dedicated true SHA256/no actual keys/child-only registry proof')
        if count==3:
            require(p['publicSyntheticTestPasswordsUsed'] is proof['publicSyntheticTestPasswordsUsed'] is True and p['cryptoOperationKind']=='PBKDF2_HMACSHA256_PUBLIC_SYNTHETIC_PASSWORD_AND_SALT','explicit synthetic password')
        else:
            require(count==18 and p['publicReceiptIdentifierRandomnessOnly'] is proof['publicReceiptIdentifierRandomnessOnly'] is p['testOwnNewSlotPublicEvidenceWrites'] is proof['testOwnNewSlotPublicEvidenceWrites'] is True and p['forbiddenProductProbeHits']==proof['forbiddenProductProbeHits']==0 and p['cryptoOperationKind']=='CSPRNG_PUBLIC_RECEIPT_IDENTIFIER_ONLY_NO_KEYS','explicit public ID entropy/own evidence only')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&methods,'only new disjoint actual8/4');methods|=new
        require(len(p['fullSourceUnits'])==(1 if count==3 else 6) and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'full whole Source Code scope')
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and p['strictFour100GateExit']==(0 if count==3 else 1) and (proof['sourcePrograms'],proof['physicalClasses'],proof['four100SourcePrograms'],proof['naturallyBranchZeroSourcePrograms'],proof['incompleteSourcePrograms'],proof['baselineMainOwnerRows'],proof['unknownTestOwnerRows'])==((1,1,1,0,0,1,1) if count==3 else (6,6,4,2,0,6,4)),'whole Source/counter and actual caller categories')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,value in p['owners'].items():
            require(path not in owners or owners[path]==value,'shared owners unchanged');owners[path]=copy.deepcopy(value)
        for n in p['metadataClasses']:
            require(n not in metadata and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new NoCode interface unique')
            metadata[n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        refs.append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=('ORIGINAL_PASSWORD_HASHER3_FULL_ONE_SOURCE_PUBLIC_SYNTHETIC_PASSWORD' if count==3 else 'ORIGINAL_PUBLIC_VALUES18_FULL_SIX_SOURCE_PUBLIC_IDENTIFIER_ENTROPY_OWN_PUBLIC_TEST_OUTPUTS')))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']==8 and len({n for name in incomplete for n in units[name]['physical']})==13,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+2,totalProductExecs=old['totalProductExecs']+2,totalMethodExecutions=old['totalMethodExecutions']+21,uniqueProductMethodDelta=21,newTestIds=21,sourceProgramDelta=7,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(1831,226,392,516,495,218,324,313,96,1939,160,173,6,8),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':307,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':227,'UNKNOWN':110},'actual owners distinct from change group; UNKNOWN retained')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','metadataClasses',*summary}
    def contract(v):
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
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=7,newUniqueMethods=21,newIncompleteSources=0,newIncompletePhysical=0,incompletePhysicalClasses=13,newProductExecutions=2,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
