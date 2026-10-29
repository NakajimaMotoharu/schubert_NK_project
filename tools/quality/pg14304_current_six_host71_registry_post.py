"""Independent original71 XML, complete scopes and distinct natural0/noCode categories; no execution."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14302_current_six_host71_registry import SOURCE,NORMAL_PIN,POSTS

OUT=data.BASE/'PG14304-current-six-host71-registry-post-v1'
PIN='6fff0d2718570d7f15f6c2427163a7226ababd28656d23960cea3f54b66a852d'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(value):return json.dumps(value,sort_keys=True)

def contract(value,expected):
    require(all(k in value and wire(value[k])==wire(v) for k,v in expected.items()),'exact actual source/XML/unit counts, flags and unresolved states')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only post')
    m=data.read_checked(data.BASE/'PG14302-current-six-host71-registry-v1/manifest.json',PIN);verify(m['invocation'])
    n=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL_PIN)
    require(n['source']==SOURCE and n['actualExit']==n['testsExecuted']==0,'current normal source')
    hashes=n['begin']['inputHashes'];require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all current inputs unchanged')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    cases=[];suites=set();units={};owners={};entries=[]
    for name,(pin,count,suite_count) in POSTS.items():
        post=data.read_checked(data.BASE/name/'manifest.json',pin);require(post['actualExit']==0 and post['source']==SOURCE,'actual input post')
        local=[]
        for filename,digest in post['xmlHashes'].items():
            raw=(data.BASE/name/filename).read_bytes();require(data.sha(raw)==digest,'original returned public XML hash')
            root=ET.fromstring(raw);require(int(root.get('tests'))==len(root.findall('testcase')) and all(int(root.get(k))==0 for k in ('failures','errors','skipped')),'actual XML FES0')
            for case in root.findall('testcase'):
                require(not list(case),'non-PASS XML cannot enter registry');local.append((case.get('classname'),case.get('name')))
        require(len(local)==count and len(set(c for c,_ in local))==suite_count,'exact original XML methods/suites')
        require(set(local)=={(r['classname'],r['name']) for r in post['cases']},'post and actual XML identities')
        cases.extend(local);suites.update(c for c,_ in local)
        for p,owned in post['owners'].items():
            require(hashes[p]==owned['sha256'] and all(owned[k]==v for k,v in canonical(p,logical).items()),'preserve actual known/unknown source ownership');owners[p]=owned
        for source_name,unit in post['fullSourceUnits'].items():
            require(source_name not in units,'no Source coverage union')
            require(post['singleSession'] is True and post['crcMismatch']==0 and post['priorProductResultsReused'] is False,'genuine single exec CRC')
            expected_four=all(v['missed']==0 and v['covered']>0 for v in unit['totals'].values())
            require(unit['four100'] is expected_four,'no missed-to-PASS normalization')
            metadata=set(unit['physical'])<=set(post.get('metadataClasses',[]))
            natural=not metadata and unit['totals']['BRANCH']==dict(missed=0,covered=0)
            if metadata:require(all(v==dict(missed=0,covered=0) for v in unit['totals'].values()),'exact noCode counters')
            if natural:require(all(unit['totals'][k]['missed']==0 and unit['totals'][k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'natural0 not four100')
            units[source_name]=dict(post=name,postSha256=pin,physical=unit['physical'],counters=unit['totals'],four100=expected_four,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],metadataOnly=metadata,branchNaturallyZero=natural)
        entries.append(dict(name=name,sha256=pin,tests=count,suites=suite_count,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    require(len(cases)==len(set(cases))==71 and len(suites)==10 and len(units)==17,'no duplicate/lost original XML')
    expected=dict(actualExit=0,source=SOURCE,normalManifestSha256=NORMAL_PIN,originalPostReferences=entries,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted(suites),tests=71,suites=10,originalExecs=6,fullSourceUnits=units,measuredSourcePrograms=17,measuredPhysical=21,executablePhysical=20,metadataPhysical=1,four100SourcePrograms=9,four100Physical=13,naturalZeroBranchSourcePrograms=6,metadataSourcePrograms=1,incompleteSourcePrograms=1,owners=owners,unknownOwnerPaths=12,priorSource0061TestsTransferred=False,coverageExecUnion=False,originalTestsReexecutedByRegistry=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    contract(m,expected);labels=[]
    for label,mutate in [('source',lambda v:v.update(source='0'*40)),('test-count',lambda v:v.update(tests=72)),('exec-count',lambda v:v.update(originalExecs=2)),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('incomplete-erased',lambda v:v.update(incompleteSourcePrograms=0)),('four100-inflated',lambda v:v.update(four100SourcePrograms=10)),('owner-invented',lambda v:next(x for x in v['owners'].values() if x['canonicalOwner'] is None).update(canonicalOwner='WBS-P005-03')),('union',lambda v:v.update(coverageExecUnion=True)),('old-transfer',lambda v:v.update(priorSource0061TestsTransferred=True)),('bool-counter',lambda v:v.update(originalTestsReexecutedByRegistry=False)),('natural0-erased',lambda v:v.update(naturalZeroBranchSourcePrograms=0)),('metadata-as-four100',lambda v:v.update(metadataSourcePrograms=0)),('formal',lambda v:v.update(formalUpdated=True)),('accepted',lambda v:v.update(newAccepted=1))]:
        bad=copy.deepcopy(m);mutate(bad)
        try:contract(bad,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('false metadata accepted: '+label)
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,originalXmlMethods=71,originalXmlSuites=10,originalExecs=6,four100SourcePrograms=9,naturalZeroBranchSourcePrograms=6,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=12,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,oldSourceResultsTransferred=False,coverageExecUnion=False,originalTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
