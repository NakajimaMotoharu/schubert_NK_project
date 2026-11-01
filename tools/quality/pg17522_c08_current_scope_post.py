"""Independent current C08 inventory readiness; canonical main exact bytes, no acceptance promotion."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PIN='d8fe0b0fe7111339479ec1252e96761687e37b6338375baeb8c4f429e3cb6e31'
CANONICAL='8b91944df5820535e23ba2469740f1c0aa94c447'
OUT=data.BASE/'PG17522-c08-current-scope-post-v1'
OWN='src/deployment/operations/inbox-inspector.sh.template'
DESIGN='documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md'
POST=('PG17504-inspector-deployment-eight-post-v2','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f')
REG=('PG17510-current2746-inspector-deployment-registry-post-v1','a36a52c7f9929cc941898d04794ba361ffbb5bb1a437b2ca9948846300107ba2')
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m=data.read_checked(data.BASE/'PG17521-c08-current-scope-v2/manifest.json',PIN)
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    plan=data.ROOT/'documents/400_PGPT/470_PMO'
    paths=[plan/'481_PGPT詳細WBS.json',plan/'484_WBSコスト枠・細分化.json',plan/'485_WBS網羅性・受入対応.json',*plan.glob('486_*.json')]
    require(len(paths)==4,'all four actual WBS files')
    hashes={str(path.relative_to(data.ROOT)):data.sha(path.read_bytes()) for path in paths}
    stack=[json.loads(paths[0].read_bytes())];found=[]
    while stack:
        item=stack.pop()
        if isinstance(item,dict):
            if item.get('id')=='WBS-C08':found.append(item)
            stack.extend(item.values())
        elif isinstance(item,list):stack.extend(item)
    require(len(found)==1,'independent exact C08 node');node=found[0]
    require(node['acceptance']['status']=='NOT_ACCEPTED' and node['ownedArtifacts']==[OWN] and node['sharedClassReferences']==[],'actual owned one/none and untouched acceptance')
    require({v['id'] for v in node['acceptanceChecks']}=={'WBS-C08:scope','WBS-C08:contract','WBS-C08:quality'} and node['evidencePlan']['designFiles']==[DESIGN],'three unchanged actual criteria')
    require(subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()==CANONICAL,'frozen actual master')
    master=subprocess.check_output(['git','show',CANONICAL+':'+DESIGN],cwd=data.ROOT);working=(data.ROOT/DESIGN).read_bytes()
    require(master!=working and [x for x in master.splitlines() if x.strip()]==[x for x in working.splitlines() if x.strip()] and len(master.splitlines())==len(working.splitlines())+3,'only actual empty-line delta, never canonical normalization')
    comparisons={DESIGN:dict(workingSha256=data.sha(working),canonicalSha256=data.sha(master),byteEqual=False,nonemptyLinesEqual=True,canonicalExtraEmptyLines=3)}
    for path,pin in p['approvedDesignHashes'].items():
        approved=subprocess.check_output(['git','show',CANONICAL+':'+path],cwd=data.ROOT)
        require(data.sha(approved)==data.sha((data.ROOT/path).read_bytes())==pin,'other three exact designs')
        comparisons[path]=dict(workingSha256=pin,canonicalSha256=pin,byteEqual=True)
    own=data.sha((data.ROOT/OWN).read_bytes())
    require(own==p['readOnlyPublicInputs'][OWN]==data.sha(subprocess.check_output(['git','show',SOURCE+':'+OWN],cwd=data.ROOT)) and p['owners'][OWN]['canonicalOwner']==p['owners'][OWN]['canonicalCostOwner']=='WBS-C08','actual Source/run/master ownership')
    related={path:dict(sha256=pin,owner=p['owners'][path]['canonicalOwner']) for path,pin in p['readOnlyPublicInputs'].items() if path!=OWN}
    require(len(related)==4 and {v['owner'] for v in related.values()}=={'WBS-C02','WBS-F02'},'related source scope not silently enlarged')
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in [POST,REG]],SOURCE)
    expected=dict(actualExit=0,source=SOURCE,invocation=m['invocation'],sourceEvidenceBindings=bindings,inputs=hashes,
        approvedDesignSha256=data.sha(master),approvedDesignPath=DESIGN,canonicalDesignCommit=CANONICAL,designReadBasis='FROZEN_ORIGIN_MAIN_NOT_DEVELOPMENT_BRANCH',designByteComparisons=comparisons,wbsNodeSnapshot=node,
        ownedArtifactRows=[dict(path=OWN,sha256=own,owner='WBS-C08',costOwner='WBS-C08',currentSourceRunJoined=True)],
        ownedArtifactCount=1,ownedArtifactJoinedCount=1,missingOwnedArtifacts=[],relatedInputs=related,
        currentSourceOwnedInventoryEvidenceReady=True,comprehensiveDependencyTraceAccepted=False,
        criteriaEvidenceReady=['WBS-C08:scope'],criteriaAccepted=[],newAcceptedLeaves=[],
        criteriaStatus={'WBS-C08:scope':'OWNED_INVENTORY_JOIN_READY_FULL_ACCEPTANCE_NOT_CHANGED','WBS-C08:contract':'COMPREHENSIVE_SS353_OBLIGATION_JOIN_NOT_COMPLETED','WBS-C08:quality':'RESOURCE_TESTS_AND_TOOL_SYNTAX_PASSED_FULL_APPLICABILITY_NOT_CLOSED'},
        missingComprehensiveDesignJoins=[DESIGN],existingOriginalMethods=8,existingToolReceipts=50,
        newProductExecutions=0,existingResultsReexecuted=False,wbsAcceptanceChanged=False,estimateChanged=False,
        actualRecoveryActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,
        privateDataRead=False,holdReleased=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    def contract(v):require(wire(v)==wire(expected),'independent entire actual criterion/source/cost object')
    contract(m);negative=[]
    vectors=[('actualExit',True),('source','OLD'),('inputs',{}),('wbsNodeSnapshot',{}),('ownedArtifactRows',[]),('ownedArtifactCount',2),('ownedArtifactJoinedCount',0),('missingOwnedArtifacts',['unknown']),('criteriaEvidenceReady',[]),('criteriaAccepted',['WBS-C08:scope']),('newAcceptedLeaves',['WBS-C08']),('comprehensiveDependencyTraceAccepted',True),('missingComprehensiveDesignJoins',[]),('existingOriginalMethods',9),('existingToolReceipts',49),('newProductExecutions',1),('existingResultsReexecuted',True),('wbsAcceptanceChanged',True),('estimateChanged',True),('privateDataRead',True),('holdReleased',True),('newAccepted',1),('formalUpdated',True),('effortPercent',100),('canonicalDesignCommit','0'*40),('designReadBasis','DEVELOPMENT_BRANCH'),('designByteComparisons',{}),('approvedDesignSha256','0'*64),('actualRecoveryActions',1),('criteriaStatus',{})]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value;require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false C08 readiness '+key)
    require(len(negative)==30,'all thirty independent metadata negatives')
    require(all(data.sha((data.ROOT/path).read_bytes())==pin for path,pin in hashes.items()),'all WBS inputs unchanged')
    verify(m['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,scopeManifestSha256=PIN,metadataNegativeVectors=len(negative),negativeLabels=negative,ownedInventoryJoined=1,ownedInventoryTotal=1,criteriaEvidenceReady=['WBS-C08:scope'],criteriaAccepted=[],newAccepted=0,formalUpdated=False,wbsAcceptanceChanged=False,estimateChanged=False,sourceAndDesignAcceptedByNormalization=False,canonicalDesignCommit=CANONICAL,canonicalDesignSha256=data.sha(master),workingDesignByteEqual=False,existingResultsReexecuted=False,productTestsExecuted=0,holdReleased=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
