"""Independent original24 XML join and complete preservation of every old Source/domain/history."""
import copy
from collections import Counter
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14836_current908_resource_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='af91672ea724386906cce9ad70ae6e85e33f68455fcc14db020715da5b0033dd'
OUT=data.BASE/'PG14838-current908-resource-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only908 independent post')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG14836-current908-resource-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1],'genuine old/current same source receipts')
    cases={(v['classname'],v['name']) for v in old['cases']};owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['resourceOnlyReferences']);proofs=[]
    for folder,pin in REFS:
        p=read((folder,pin));proofs.append(p);actual=[]
        require(p['actualExit']==0 and p['source']==SOURCE and p['javaSourceProgramsQualified']==0 and p['javaCounterCoverageClaimed'] is p['resourceCounterCoverageClaimed'] is False,'genuine resource-only, no Main/coverage fabrication')
        require(all(p[k]==0 for k in ['actualBrowserActions','actualNetworkActions','actualVmActions','actualDatabaseActions','actualServiceActions','productTestsReexecutedByPost','newAccepted']),'no external action/replay/newacceptance')
        for name,digest in p['xmlHashes'].items():
            value=(data.BASE/folder/name).read_bytes();require(data.sha(value)==digest,'returned original XML hash')
            tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all original XML FES0')
            for case in tree.findall('testcase'):
                require(not list(case),'no non-PASS case');actual.append((case.get('classname'),case.get('name')))
        require(len(actual)==len(set(actual))==8 and len({c for c,n in actual})==1 and set(actual)=={(v['classname'],v['name']) for v in p['cases']} and not set(actual)&cases,'exact new original8 each, no repeated/newcredit confusion');cases.update(actual)
        for path,owned in p['owners'].items():
            require(path not in owners or owners[path]==owned,'shared owner remains exact');owners[path]=owned
        refs.append(dict(name=folder,sha256=pin,tests=8,suites=1,domain='RESOURCE_DOM_WRAPPERS',javaSourceProgramsQualified=0,actualBrowser=False))
    summary={k:v for k,v in prior['summary'].items()}
    summary.update(tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+3,totalProductExecs=old['totalProductExecs']+3,totalMethodExecutions=old['totalMethodExecutions']+24,uniqueProductMethodDelta=24,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),resourceOnlyJavaMethods=old['resourceOnlyJavaMethods']+24)
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['resourceOnlyJavaMethods'])==(908,131,211,285,130,195,60,988,35),'actual derived Source and method domains')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','owners','resourceOnlyReferences',*summary}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'typed independent actual summary')
        require(v['cases']==[dict(classname=c,name=n) for c,n in sorted(cases)] and v['suiteNames']==sorted({c for c,n in cases}),'exact unique original IDs')
        require(v['owners']==owners and v['resourceOnlyReferences']==refs,'all owners and resource references retained')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact predecessor chain')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'every old211 Source/physical/counter/JS/Catalog/SQLjoint/history/formal/semantic unchanged')
    contract(m);labels=[]
    for label,key,value in [('cases-inflated','tests',938),('Main-credit','measuredSourcePrograms',214),('physical-credit','measuredPhysical',288),('four-credit','four100SourcePrograms',133),('four-physical','four100Physical',198),('resource-role-erased','resourceOnlyJavaMethods',0),('node-as-Java','nodeChildrenNotAddedToJavaMethods',False),('JS-erased','javascriptResourceDomain',{}),('resource-ref-erased','resourceOnlyReferences',[]),('Source-overwrite','fullSourceUnits',{}),('repeat-erased','totalRepeatedOriginalMethods',0),('repeat-faked','necessaryJointRepeatedMethods',0),('exec-erased','totalProductExecs',57),('Catalog-erased','qualificationReplacedUnitHistory',{}),('SQL-erased','jointQualificationReplacedUnitHistory',{}),('UNKNOWN-erased','unknownOwnerPaths',0),('oldsource','priorSource0061TestsTransferred',True),('union','coverageExecUnion',True),('formal','formalUpdated',True),('acceptance','newAccepted',1),('effort','effortPercent',50),('bool-count','uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false908 registry accepted '+label)
    for v in [old,prior,m,*proofs]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,allOldCasesAndSourceProofsPreserved=True,resourcePrograms=4,resourceOnlyOriginalMethods=35,newSourcePrograms=0,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
