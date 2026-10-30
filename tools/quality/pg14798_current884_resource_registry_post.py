"""Independent XML/counter/domain join; preserve every old proof without counter union."""
import copy
from collections import Counter
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14796_current884_resource_registry import SOURCE,PREV,PREV_POST,REFS,EXTRA,NEW,read,require

PIN='7418311af8225dc268023b9d8465b918e878109cb97a8b507a2261f57b425135'
OUT=data.BASE/'PG14798-current884-resource-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent884 post')
    old,prior,m,extra=[read(v) for v in [PREV,PREV_POST,('PG14796-current884-resource-registry-v1',PIN),EXTRA]]
    require(prior['registryManifestSha256']==PREV[1] and extra['postSha256']==REFS[0][1] and extra['resourcePrograms']==4 and extra['javaSourceProgramsQualified']==0,'old qualified witness and separate JS proof')
    cases={(v['classname'],v['name']) for v in old['cases']};owners=copy.deepcopy(old['owners']);units=copy.deepcopy(old['fullSourceUnits']);expected_resources=[];posts=[]
    for folder,pin,count,suites,kind in REFS:
        p=read((folder,pin));posts.append(p);local=[]
        require(p['actualExit']==0 and p['source']==SOURCE and p['formalUpdated'] is False and p['newAccepted']==0,'genuine current source post')
        for filename,digest in p['xmlHashes'].items():
            value=(data.BASE/folder/filename).read_bytes();require(data.sha(value)==digest,'actual original returned XML hash')
            tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all original XML PASS')
            for case in tree.findall('testcase'):
                require(not list(case),'no non-PASS case');local.append((case.get('classname'),case.get('name')))
        require(len(local)==len(set(local))==count and len({c for c,n in local})==suites and set(local)=={(v['classname'],v['name']) for v in p['cases']} and not set(local)&cases,'all fourteen are new original methods, no Node child inflation');cases.update(local)
        for path,owned in p['owners'].items():
            require(path not in owners or owners[path]==owned,'all shared owners unchanged');owners[path]=owned
        if kind=='PURE_EXCEPTION_VALUES':
            require(p['singleSession'] is True and p['crcMismatch']==0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False,'one actual exception exec, no transfer')
            for name in NEW:
                u=p['fullSourceUnits'][name];closure=[name,name+'$Reason']
                require(u['physical']==closure and all(n in p['executable'] for n in closure),'full two-class Source')
                counters={k:dict(missed=sum(p['executable'][n]['counters'][k]['missed'] for n in closure),covered=sum(p['executable'][n]['counters'][k]['covered'] for n in closure)) for k in ['LINE','METHOD','CLASS','BRANCH']}
                require(counters==u['totals'] and counters['BRANCH']==dict(missed=0,covered=0) and all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'actual counters natural branch0 notfour100')
                require(name not in units,'only two new Source scopes');units[name]=dict(post=folder,postSha256=pin,physical=closure,counters=counters,four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
        else:
            require(p['javaSourceProgramsQualified']==0,'no Java scope from resource tests')
            expected_resources.append(dict(name=folder,sha256=pin,tests=count,suites=suites,domain=kind,javaSourceProgramsQualified=0,actualBrowser=False))
    resource=posts[0]
    for name,row in resource['productionJavascriptResources'].items():
        value=(data.BASE/REFS[0][0]/row['tapPath']).read_bytes();require(data.sha(value)==row['tapSha256'],'actual V8 TAP hash')
        lines=[line[2:].split('|') for line in value.decode().splitlines() if line.startswith('# ') and '|' in line and line[2:].split('|')[0].strip()==name+'.js']
        require(len(lines)==1 and [v.strip() for v in lines[0][1:]]==['100.00','100.00','100.00',''] and row['coverage']==dict(linePercent=100,branchPercent=100,functionPercent=100,classCounter='NOT_APPLICABLE_JAVASCRIPT_RESOURCE'),'exact per-file actual JS coverage, not Java')
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=old['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint physical scope')
    summary=dict(tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+3,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),generatedMetadataPhysical=old['generatedMetadataPhysical'],four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),metadataSourcePrograms=old['metadataSourcePrograms'],incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),additionalQualificationExecs=old['additionalQualificationExecs'],totalProductExecs=old['totalProductExecs']+3,totalMethodExecutions=old['totalMethodExecutions']+14,uniqueProductMethodDelta=14,sourceProgramDelta=2,necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods'],totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods'],resourceOnlyJavaMethods=11,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True)
    require((summary['tests'],summary['suites'],len(units),len(physical),summary['four100SourcePrograms'],len(four),summary['naturalZeroBranchSourcePrograms'],len(natural),summary['totalProductExecs'],summary['totalMethodExecutions'])==(884,128,211,285,130,195,76,84,57,964),'independently derived exact summary')
    exception=posts[1];expected_original_refs=old['originalPostReferences']+[dict(name=REFS[1][0],sha256=REFS[1][1],tests=3,suites=1,execSha256=exception['execSha256'],sessionIdentity=exception['sessionIdentity'],scope='ORIGINAL3_EXCEPTION_VALUES_EXISTING_JMS_PROOF_RETAINED')]
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences',*summary}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'typed counts independently match actual domains')
        require(wire(v['cases'])==wire([dict(classname=c,name=n) for c,n in sorted(cases)]) and v['suiteNames']==sorted({c for c,n in cases}),'all exact case IDs')
        require(wire(v['fullSourceUnits'])==wire(units) and wire(v['owners'])==wire(owners),'every old/new Source proof and canonical/UNKNOWN owner preserved')
        require(v['resourceOnlyReferences']==expected_resources and v['originalPostReferences']==expected_original_refs,'original vs resource domains disjoint')
        require(v['javascriptResourceDomain']==dict(post=list(REFS[0][:2]),independentPost=list(EXTRA),resources=resource['productionJavascriptResources'],resourcePrograms=4,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,javaSourceProgramsQualified=0),'JS resource proof retained, not Main')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'every unaffected history/metadata/formal/HOLD semantic unchanged')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact predecessor chain')
    contract(m);labels=[]
    for label,key,value in [('children-as-java','tests',914),('resource-as-Main','measuredSourcePrograms',215),('four-faked','four100SourcePrograms',132),('four-physical','four100Physical',199),('branch0-erased','naturalZeroBranchSourcePrograms',74),('physical','measuredPhysical',281),('exec-count','totalProductExecs',54),('repeats','totalRepeatedOriginalMethods',0),('node-join','nodeChildrenNotAddedToJavaMethods',False),('resources-erased','resourceOnlyReferences',[]),('JS-erased','javascriptResourceDomain',{}),('old-source','priorSource0061TestsTransferred',True),('union','coverageExecUnion',True),('formal','formalUpdated',True),('newacceptance','newAccepted',1),('effort','effortPercent',25),('Jms-overwrite','fullSourceUnits',{}),('Catalog-erased','qualificationReplacedUnitHistory',{}),('SQL-history-erased','jointQualificationReplacedUnitHistory',{}),('UNKNOWN-erased','unknownOwnerPaths',0),('metadata-erased','metadataClasses',{}),('bool-count','uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false resource registry accepted '+label)
    for v in [old,prior,m,extra,*posts]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,allOldCasesAndSourceProofsPreserved=True,resourcePrograms=4,resourceOnlyOriginalMethods=11,newSourcePrograms=2,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
