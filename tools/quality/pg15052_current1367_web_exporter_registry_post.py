"""Independent actual12/class2 reconciliation, prior332 Source/cost and non-Java domains immutable."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15050_current1367_web_exporter_registry import SOURCE,PREV,PREV_POST,REFS,read,require

PIN='6524ae373d11f4eb8cb691deaff85aee31dc7a64b1839a59ae69bb79a923b0f6'
OUT=data.BASE/'PG15052-current1367-web-exporter-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1367 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15050-current1367-web-exporter-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==33,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[]
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['semanticNegativeVectors']==negative_count and proof['tests']==count,'genuine whole-codec independent proof')
        attempt={(c['classname'],c['name']) for c in p['cases']};repeated=attempt&methods;new=attempt-methods
        expected_repeated={(c['classname'],c['name']) for c in old['cases'] if c['classname']=='dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest'}
        require(len(attempt)==count==62 and len(new)==p['newUniqueMethods']==proof['newUniqueMethods']==48 and repeated==expected_repeated and len(repeated)==p['repeatedOriginalMethods']==proof['repeatedOriginalMethods']==14 and proof['necessaryDependencyReplayNotConfirmation'] is True,'exact new48 and only necessary sameexec repeated14');methods|=new
        require(len(p['fullSourceUnits'])==4 and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'one complete Source no metadata exclusions')
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and (u['four100'] or u['branchNaturallyZero'] and u['threeCounter100']),'whole Source/class nonempty four100')
            units[name]=dict(post=folder,postSha256=pin,physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,value in p['owners'].items():
            require(path not in owners or owners[path]==value,'shared owners unchanged');owners[path]=copy.deepcopy(value)
        refs.append(dict(name=folder,sha256=pin,tests=count,suites=4,newUniqueMethods=48,repeatedOriginalMethods=14,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_WEB_EXPORTER_JOINT62_NEW48_NECESSARY_REPEAT14_FOUR_WHOLE_SOURCE_FOUR100'))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=old['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    summary=copy.deepcopy(prior['summary']);summary.update(tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+62,totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods']+14,uniqueProductMethodDelta=48,newTestIds=48,sourceProgramDelta=4,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(1367,179,336,447,429,175,273,263,71,1461,151,163,6,4),'exact independent category/method/JVM counts')
    require(old['totalRepeatedOriginalMethods']==80 and summary['totalRepeatedOriginalMethods']==94 and summary['totalMethodExecutions']==summary['tests']+94,'old80 plus necessary14, not unique or old history rewriting')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':270,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':168,'UNKNOWN':103},'actual owners distinct from change group; UNKNOWN retained')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences',*summary}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old Catalog/SQLjoint/JS/metadata/cost/formal untouched')
    contract(m);negative=[]
    for key,value in [('tests',914),('suites',132),('totalProductExecs',61),('totalMethodExecutions',994),('totalRepeatedOriginalMethods',92),('uniqueProductMethodDelta',0),('sourceProgramDelta',0),('four100SourcePrograms',131),('four100Physical',196),('naturalZeroBranchSourcePrograms',145),('measuredSourcePrograms',287),('measuredPhysical',365),('executablePhysical',347),('metadataPhysical',0),('metadataSourcePrograms',0),('fullSourceUnits',{}),('metadataClasses',{}),('cases',old['cases']),('originalPostReferences',old['originalPostReferences']),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('javascriptResourceDomain',{}),('unknownOwnerPaths',99),('ownerStatusCounts',{'BASELINE_LOGICAL_REFERENCE':283,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':103}),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false1367 registry accepted '+key)
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
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=4,newUniqueMethods=48,necessaryRepeatedMethods=14,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
