"""Independent69 additional Source scopes with unchanged original methods and Product executions."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14852_current908_named69_registry import SOURCE,PREV,PREV_POST,QUAL,QUAL_POST,read,require

PIN='46d6f90a7c719ef536105cd9233c5653c834291255e04f10dbdf58334d41345a'
OUT=data.BASE/'PG14854-current908-named69-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only69 source registry post')
    old,prior,p,proof,m=[read(pair) for pair in [PREV,PREV_POST,QUAL,QUAL_POST,('PG14852-current908-named69-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof,m]) and prior['registryManifestSha256']==PREV[1] and proof['postSha256']==QUAL[1],'genuine source-bound independent proofs')
    require(proof['newUniqueMethods']==proof['productTestsExecuted']==0 and proof['originalXmlMethodsAlreadyCounted']==31 and proof['newSourcePrograms']==69 and proof['semanticNegativeVectors']==20,'69 new Source, zero new tests, original31 already counted')
    require(len(p['cases'])==31 and {(v['classname'],v['name']) for v in p['cases']}<={(v['classname'],v['name']) for v in old['cases']} and p['singleSession'] is True and p['crcMismatch']==0 and not p['metadataClasses'],'same actual existing exec/CRC and no fake metadata')
    units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners'])
    for name,u in p['fullSourceUnits'].items():
        require(name not in units and u['physical']==[name],'only new whole one-class scopes')
        counters=copy.deepcopy(p['executable'][name]['counters']);require(counters==u['totals'] and counters['BRANCH']==dict(missed=0,covered=0) and all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'actual69 independent class totals, B0 N/A')
        units[name]=dict(post=QUAL[0],postSha256=QUAL[1],physical=[name],counters=counters,four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
    require(len(p['fullSourceUnits'])==69,'all69 included')
    for path,owned in p['owners'].items():
        require(path not in owners or owners[path]==owned,'old shared owner immutable');owners[path]=owned
    scopes=copy.deepcopy(old['additionalScopeReferences']);scopes.append(dict(name=QUAL[0],sha256=QUAL[1],independentPost=list(QUAL_POST),domain='SAVED_CURRENT_EXEC_ADDITIONAL_SOURCE_SCOPE',sourcePrograms=69,tests=31,originalTestsAlreadyCounted=True,newUniqueMethods=0,newProductExecutions=0,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],coverageExecUnion=False))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=old['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all280 Source closures disjoint')
    summary=copy.deepcopy(prior['summary']);summary.update(measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),uniqueProductMethodDelta=0,sourceProgramDelta=69)
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'])==(908,131,280,354,342,130,195,145,153,60,988),'Source-only extension independently computed')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','fullSourceUnits','owners','additionalScopeReferences',*summary}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all typed independently derived counts')
        require(wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and v['additionalScopeReferences']==scopes,'every old/new proof/owner/scope retained')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'all old cases/executions/Catalog/SQLjoint/JS metadata/formal fields unchanged')
    contract(m);labels=[]
    for label,key,value in [('31-as-new','tests',939),('new-JVM','totalProductExecs',61),('new-method-exec','totalMethodExecutions',1019),('repeat31','totalRepeatedOriginalMethods',111),('unique-credit','uniqueProductMethodDelta',31),('source69-erased','sourceProgramDelta',0),('four-fake','four100SourcePrograms',199),('fourphysical-fake','four100Physical',264),('natural-erased','naturalZeroBranchSourcePrograms',76),('source-count','measuredSourcePrograms',211),('physical-count','measuredPhysical',285),('code-count','executablePhysical',273),('Source-erased','fullSourceUnits',{}),('scope-erased','additionalScopeReferences',old['additionalScopeReferences']),('Catalog-erased','qualificationReplacedUnitHistory',{}),('SQL-erased','jointQualificationReplacedUnitHistory',{}),('JS-erased','javascriptResourceDomain',{}),('unknown-erased','unknownOwnerPaths',0),('oldsource','priorSource0061TestsTransferred',True),('union','coverageExecUnion',True),('formal','formalUpdated',True),('acceptance','newAccepted',1),('effort','effortPercent',75),('bool-delta','uniqueProductMethodDelta',False)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false69 Source registry accepted '+label)
    for value in [old,prior,p,proof,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,allOldCasesAndSourceProofsPreserved=True,resourcePrograms=4,resourceOnlyOriginalMethods=35,newSourcePrograms=69,alreadyCountedOriginalMethods=31,newUniqueMethods=0,newProductExecutions=0,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
