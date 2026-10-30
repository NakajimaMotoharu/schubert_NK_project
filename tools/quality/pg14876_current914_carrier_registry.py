"""Bind six new pure-value methods/seven complete Source scopes; no replay or coverage union."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG14852-current908-named69-registry-v1','46d6f90a7c719ef536105cd9233c5653c834291255e04f10dbdf58334d41345a')
PREV_POST=('PG14854-current908-named69-registry-post-v1','12d557e00d0b8c4e95001a4666f52bb228b9124a82332f7be0964ce8cb65176b')
QUAL=('PG14871-protocol-carrier-boundary-six-post-v2','87d29dc4e02b03e422270d4f9ebfc5a8b68456804f837c1c338ba1d8b8986696')
QUAL_POST=('PG14872-protocol-carrier-boundary-independent-v1','12915c28abce5e6e951ac923a4bdf5ec7373bdae449317689f036a6fe4f9c78f')
OUT=data.BASE/'PG14876-current914-carrier-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only914 registry')
    old,prior,p,proof=[read(pair) for pair in [PREV,PREV_POST,QUAL,QUAL_POST]]
    require(all(v['source']==SOURCE and v['actualExit']==0 for v in [old,prior,p,proof]) and prior['registryManifestSha256']==PREV[1] and proof['postSha256']==QUAL[1],'all genuine independent same-source witnesses')
    require(proof['newUniqueMethods']==6 and proof['sourcePrograms']==7 and proof['physicalClasses']==11 and proof['semanticNegativeVectors']==22 and proof['coverageExecUnion'] is False,'whole new six/source proof')
    result=copy.deepcopy(old);cases={(v['classname'],v['name']) for v in old['cases']};new={(v['classname'],v['name']) for v in p['cases']}
    require(len(new)==6 and not cases&new and p['newProductExecutions']==1 and p['singleSession'] is True and p['crcMismatch']==0,'only one new own JVM, no overlap/CRC mismatch');cases.update(new)
    units=result['fullSourceUnits'];require(not units.keys()&p['fullSourceUnits'].keys() and len(p['fullSourceUnits'])==7,'new complete seven scopes only')
    for name,u in p['fullSourceUnits'].items():
        units[name]=dict(post=QUAL[0],postSha256=QUAL[1],physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=u['metadataOnly'],branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    for name in p['metadataClasses']:
        require(name not in result['metadataClasses'] and p['metadataKinds'][name]=='NO_CODE','only new actual interface metadata')
        result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=QUAL[1],sha256=p['physicalClasses'][name])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'fixed whole normal unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,owned in p['owners'].items():
        require(data.sha((data.ROOT/path).read_bytes())==owned['sha256'],'every exact owner source byte')
        if path.startswith('src/'):require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical baseline/UNKNOWN unchanged')
        else:require(path=='tools/quality/architecture/ProtocolCarrierBoundaryTest.java' and owned['canonicalOwner'] is owned['canonicalCostOwner'] is None and owned['ownershipStatus']=='UNKNOWN','exact new tool PT keeps UNKNOWN')
        require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
    result['originalPostReferences'].append(dict(name=QUAL[0],sha256=QUAL[1],tests=6,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='NEW_FIXED_ORACLE_CARRIER6_FULL_SEVEN_SOURCE_NO_OLD_EXEC_UNION'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all Source physical closures disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=7,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),metadataSourcePrograms=sum(u['metadataOnly'] for u in units.values()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],len(meta),result['metadataSourcePrograms'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['naturalZeroBranchSourcePrograms'],len(natural),result['incompleteSourcePrograms'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(914,132,287,365,347,18,6,131,196,186,146,158,4,60,61,994),'exact independently pinned category counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':265,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':99},'only seven baseline and one UNKNOWN tool PT owner added')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','metadataClasses','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','metadataSourcePrograms','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'every old280/Catalog/SQLjoint/JS/cost/history/formal field immutable')
    for v in [old,prior,p,proof]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
