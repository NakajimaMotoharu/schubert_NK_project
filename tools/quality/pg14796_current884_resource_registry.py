"""Incremental original fourteen methods; resource domains never become Java Main counters."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14750_current860_joint_registry import SOURCE,read,require

PREV=('PG14768-current870-question-registry-v1','fe795c59b97c818fdfceaef5963586a28439143f87b782ede4c74375b83fa814')
PREV_POST=('PG14770-current870-question-registry-post-v1','f03e30f707bfe57e69369ae8105988d656d875ed4b3b5754e09cbf92ec2a9537')
REFS=[
 ('PG14780-web-four-script-resources-post-v1','93523a10ae49e619195a4a228a528a822c32184adb218cb78268eb998752ef05',5,4,'RESOURCE_NODE_WRAPPERS'),
 ('PG14788-web-messaging-exception-three-post-v1','cb20070827af4aea51616d9e62b0f14fe3212c87e2b29abf6450e55932cd1d30',3,1,'PURE_EXCEPTION_VALUES'),
 ('PG14792-music-hierarchy-template-six-post-v1','056734806be65ff09bb99d5636ab02649ff25e9045e067e7871104ce568b2447',6,1,'RESOURCE_DOM_WRAPPERS')]
EXTRA=('PG14782-web-four-script-resources-independent-v1','e9e6bb114098d6d02d38b502822916dd350b1db70c4de1f0e81d0e8775a5a70d')
NEW={
 'dev/codex/schubert/nk/web/messaging/ProtectedReadWireException',
 'dev/codex/schubert/nk/web/messaging/ScenarioWireException'}
OUT=data.BASE/'PG14796-current884-resource-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only884 registry')
    old,prior=[read(v) for v in [PREV,PREV_POST]];proof=read(EXTRA)
    require(prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==21,'independent old870')
    require(proof['postSha256']==REFS[0][1] and proof['semanticNegativeVectors']==14 and proof['tapNegativeVectors']==5 and proof['javaSourceProgramsQualified']==0,'separate resource domain independent witness')
    result=copy.deepcopy(old);cases={(v['classname'],v['name']) for v in old['cases']};old_cases=set(cases)
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all fixed normal input unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result['resourceOnlyReferences']=[];witnesses=[]
    for folder,pin,count,suites,kind in REFS:
        p=read((folder,pin));witnesses.append(p)
        require(p['source']==SOURCE and p['actualExit']==0 and p['tests']==count and p['suites']==suites and p['formalUpdated'] is False and p['newAccepted']==0,'same source original actual terminal')
        local={(v['classname'],v['name']) for v in p['cases']}
        require(len(local)==count and not local&cases,'no duplicated new original methods');cases.update(local)
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical/UNKNOWN owner matches all resource and Test paths')
            require(path not in result['owners'] or result['owners'][path]==owned,'shared role unchanged');result['owners'][path]=owned
        if kind=='PURE_EXCEPTION_VALUES':
            require(p['singleSession'] is True and p['crcMismatch']==0 and set(p['fullSourceUnits'])==NEW|{'dev/codex/schubert/nk/web/messaging/JmsRequestReplyException'},'whole three Source single exec, only two new')
            for name in NEW:
                u=p['fullSourceUnits'][name];require(name not in result['fullSourceUnits'] and u['physical']==[name,name+'$Reason'] and u['threeCounter100'] is True and u['branchNaturallyZero'] is True and u['four100'] is False,'whole two-class Source natural zero, never four100')
                result['fullSourceUnits'][name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
            result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=suites,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL3_EXCEPTION_VALUES_EXISTING_JMS_PROOF_RETAINED'))
        else:
            require(p['javaSourceProgramsQualified']==0,'resources do not qualify zero-scope Java Main')
            result['resourceOnlyReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=suites,domain=kind,javaSourceProgramsQualified=0,actualBrowser=False))
    result['javascriptResourceDomain']=dict(post=list(REFS[0][:2]),independentPost=list(EXTRA),resources=witnesses[0]['productionJavascriptResources'],resourcePrograms=4,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,javaSourceProgramsQualified=0)
    units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']};meta=result['metadataClasses'];four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'physical classes remain disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+3,totalProductExecs=old['totalProductExecs']+3,totalMethodExecutions=old['totalMethodExecutions']+14,uniqueProductMethodDelta=len(cases-old_cases),sourceProgramDelta=len(NEW),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),resourceOnlyJavaMethods=11,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True)
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['naturalZeroBranchSourcePrograms'],len(natural),result['totalProductExecs'],result['totalMethodExecutions'])==(884,128,211,285,273,130,195,76,84,57,964),'exact independent domains, identities, Source totals')
    require(all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and result['jointQualificationReferences']==old['jointQualificationReferences'] and result['jointQualificationReplacedUnitHistory']==old['jointQualificationReplacedUnitHistory'] and result['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'] and result['additionalQualificationReferences']==old['additionalQualificationReferences'],'all old Source/Jms/Catalog/joint qualification histories unchanged')
    for v in [old,prior,proof,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
