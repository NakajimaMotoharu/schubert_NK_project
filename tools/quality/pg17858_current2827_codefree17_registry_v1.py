"""Metadata population correction:17 inert interfaces,37 annotations separate, no PT delta."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17825-current2827-admission-joint-registry-v2','8110527ffbaa8152c358418fab5b113f48ec2568bde424778766d2a66c395d2c')
PREV_POST=('PG17827-current2827-admission-joint-registry-post-v2','b447111a774a3dc635937ec9f3a61b39153175714c53f1d8d054c3c3b70b1a1a')
POST=('PG17854-codefree-official-passive54-recovery-v3','6eb6c989f53530b4e6eb3d991c31561809aa0066b6600e08e5299713e9569cb7')
INDEPENDENT=('PG17856-codefree-definitions-independent-v1','b19e91ce027660ce7b6aa8e1159b34e8280f469ca8b121f4268358ec746a8df6')
OUT=data.BASE/'PG17858-current2827-codefree17-registry-v1'
SCOPE='MEASUREMENT_POPULATION_CORRECTION_CODEFREE17_PACKAGE_INFO37_NOT_IMPLEMENTATION_OR_PT_COMPLETION'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['source']==SOURCE and v['actualExit']==0 for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and q['semanticNegativeVectors']==24,'genuine current independent inputs')
    require(p['tests']==p['productTestsExecuted']==0 and p['interfaceZeroCounterSourceCount']==17 and p['officialPackageInfoDefinitionCount']==37 and p['officialFiltersUnchanged'] is True and p['executableCounterExclusions']==[],'zero counters are not PT or percent')
    m=copy.deepcopy(old);require(not set(p['fullSourceUnits'])&old['fullSourceUnits'].keys() and not set(p['physicalClasses'])&old['metadataClasses'].keys(),'only new code-free definitions, no old proof rewrite')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for name,u in p['fullSourceUnits'].items():
        require(u['metadataOnly'] is True and u['four100'] is u['branchNaturallyZero'] is False and all(v==dict(covered=0,missed=0) for v in u['totals'].values()),'inert full Source only')
        m['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=False,execSha256=p['originalExecSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=True,branchNaturallyZero=False)
        for n in u['physical']:m['metadataClasses'][n]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][n])
        path=u['path'];require(data.sha((data.ROOT/path).read_bytes())==u['sourceSha256'],'exact source bytes')
        row=dict(sha256=u['sourceSha256'],**canonical(path,logical))
        if path in old['owners']:require(row==old['owners'][path],'old owner meaning unchanged')
        else:m['owners'][path]=row
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=0,newExecs=0,newSourceNames=sorted(p['fullSourceUnits']),newMeasuredCodefreeSources=17,newExecutablePrograms=0,sourceProgramsAcceptedByThisScope=0,officialPackageInfoDefinitions=copy.deepcopy(p['officialPackageInfoDefinitions']),packageInfoReferenceOnly=True,packageInfoNotCountedAsProgramsOrPt=True,coverageExecUnion=False))
    units=m['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'whole physical closure nonoverlap')
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=17,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-m['metadataClasses'].keys()),metadataPhysical=len(m['metadataClasses']),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(2827,422,212,2962,135,51,4,587,1020,822,198,292,437,185,200,87),'classification only, no test/Code/acceptance delta')
    require(sum(u['metadataOnly'] for u in units.values())==23 and m['owners'].keys()>=old['owners'].keys(),'23 inert Source definitions including old six')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','ownerStatusCounts','unknownOwnerPaths','lastUpdateKind','fullSourceUnits','metadataClasses','owners','additionalScopeReferences'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(m['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()) and all(m['metadataClasses'][n]==v for n,v in old['metadataClasses'].items()) and all(m['owners'][n]==v for n,v in old['owners'].items()),'all old source proofs/cases/cost/formal unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
