"""Independent actual-case/whole-Source category registry reconciliation; all previous domains retained."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14876_current914_carrier_registry import SOURCE,PREV,PREV_POST,QUAL,QUAL_POST,read,require

PIN='f75bcddfec1b33a972f607881b2de07a129ac5bb0d01f344bb5ce0f5cf74979b'
OUT=data.BASE/'PG14878-current914-carrier-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only914 independent registry')
    old,prior,p,proof,m=[read(pair) for pair in [PREV,PREV_POST,QUAL,QUAL_POST,('PG14876-current914-carrier-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof,m]) and prior['registryManifestSha256']==PREV[1] and proof['postSha256']==QUAL[1] and proof['semanticNegativeVectors']==22,'all genuine same-source independent receipts')
    old_cases={(v['classname'],v['name']) for v in old['cases']};new={(v['classname'],v['name']) for v in p['cases']};require(len(new)==6 and not old_cases&new,'actual six disjoint methods')
    cases=[dict(classname=c,name=n) for c,n in sorted(old_cases|new)];units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);meta=copy.deepcopy(old['metadataClasses'])
    require(len(p['fullSourceUnits'])==7 and not units.keys()&p['fullSourceUnits'].keys() and p['newProductExecutions']==1 and p['singleSession'] is True and p['crcMismatch']==0,'whole new seven scopes/one exec')
    for name,u in p['fullSourceUnits'].items():
        units[name]=dict(post=QUAL[0],postSha256=QUAL[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=u['metadataOnly'],branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    for name in p['metadataClasses']:
        require(name not in meta and p['metadataKinds'][name]=='NO_CODE','actual new true-interface metadata')
        meta[name]=dict(kind='NO_CODE',postSha256=QUAL[1],sha256=p['physicalClasses'][name])
    for path,value in p['owners'].items():
        require(path not in owners or owners[path]==value,'all shared owners unchanged');owners[path]=copy.deepcopy(value)
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()) and len(meta)==18 and sum(v['kind']=='NO_CODE' for v in meta.values())==13,'all physical disjoint and six actual new metadata')
    summary=copy.deepcopy(prior['summary']);summary.update(tests=len(cases),suites=len({v['classname'] for v in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=7,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),metadataSourcePrograms=sum(u['metadataOnly'] for u in units.values()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'],summary['totalProductExecs'],summary['totalMethodExecutions'])==(914,132,287,365,347,131,196,146,158,6,4,61,994),'independent exact current914 category and execution counts')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',m['normalManifestSha256']));protocol={path.split('/src/main/java/',1)[1][:-5] for path in normal['begin']['inputHashes'] if path.startswith('src/schubert-nk-protocol/src/main/java/') and path.endswith('.java') and not path.endswith('package-info.java')}
    require(len(protocol)==158 and protocol=={n for n in units if '/protocol/' in n} and all(units[n]['four100'] or units[n]['branchNaturallyZero'] or units[n]['metadataOnly'] for n in protocol),'all158 actual normal protocol Main Source, not whole451/module acceptance')
    refs=copy.deepcopy(old['originalPostReferences']);refs.append(dict(name=QUAL[0],sha256=QUAL[1],tests=6,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='NEW_FIXED_ORACLE_CARRIER6_FULL_SEVEN_SOURCE_NO_OLD_EXEC_UNION'))
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','metadataClasses',*summary}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all actual typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and v['fullSourceUnits']==units and v['owners']==owners and v['metadataClasses']==meta and v['originalPostReferences']==refs,'all old/new actual proof rows')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact predecessor roles')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old Catalog/joint/JS/cost/history/formal immutable')
    contract(m);negative=[]
    for key,value in [('tests',908),('suites',131),('totalProductExecs',60),('totalMethodExecutions',988),('totalRepeatedOriginalMethods',86),('uniqueProductMethodDelta',0),('sourceProgramDelta',0),('four100SourcePrograms',137),('four100Physical',206),('naturalZeroBranchSourcePrograms',145),('measuredSourcePrograms',280),('measuredPhysical',354),('executablePhysical',342),('metadataPhysical',12),('metadataSourcePrograms',1),('fullSourceUnits',{}),('metadataClasses',{}),('cases',old['cases']),('originalPostReferences',old['originalPostReferences']),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('javascriptResourceDomain',{}),('unknownOwnerPaths',98),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false914 registry accepted '+key)
    for v in [old,prior,p,proof,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,protocolWhole451OrModuleAcceptanceClaimed=False,newSourcePrograms=7,newUniqueMethods=6,newProductExecutions=1,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
