"""Read-only C08 current artifact/criterion readiness; no acceptance, test, or recovery action."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG17504-inspector-deployment-eight-post-v2','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f')
REG=('PG17510-current2746-inspector-deployment-registry-post-v1','a36a52c7f9929cc941898d04794ba361ffbb5bb1a437b2ca9948846300107ba2')
OUT=data.BASE/'PG17520-c08-current-scope-v1'
PLAN=data.ROOT/'documents/400_PGPT/470_PMO'
DESIGN='documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md'
OWN='src/deployment/operations/inbox-inspector.sh.template'
def require(ok,why):
    if not ok:raise ValueError(why)
def find_nodes(value,key):
    if isinstance(value,dict):
        found=[value] if value.get('id')==key else []
        return found+[n for child in value.values() for n in find_nodes(child,key)]
    if isinstance(value,list):return [n for child in value for n in find_nodes(child,key)]
    return []
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    names=['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS集計snapshot.json']
    # Resolve actual snapshot spelling without changing or assuming its content.
    if not (PLAN/names[-1]).exists():
        matches=list(PLAN.glob('486_*.json'));require(len(matches)==1,'one actual486');names[-1]=matches[0].name
    inputs={str((PLAN/n).relative_to(data.ROOT)):data.sha((PLAN/n).read_bytes()) for n in names}
    w=json.loads((PLAN/names[0]).read_bytes());nodes=find_nodes(w,'WBS-C08');require(len(nodes)==1,'one exact C08')
    node=nodes[0];require(node['ownedArtifacts']==[OWN] and node['sharedClassReferences']==[] and node['acceptance']['status']=='NOT_ACCEPTED','frozen owned scope and acceptance')
    require({r['id'] for r in node['acceptanceChecks']}=={'WBS-C08:contract','WBS-C08:scope','WBS-C08:quality'} and node['evidencePlan']['designFiles']==[DESIGN],'all three actual criteria, not a newly narrowed scope')
    sources=bind([(data.BASE/n/'manifest.json',h) for n,h in [POST,REG]],SOURCE)
    p=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    require((p['tests'],p['suites'],p['publicToolReceiptCount'],p['javaSourceProgramsQualified'])==(8,1,50,0) and p['childJavaCoverageClaimed'] is False,'current limited qualification')
    raw=data.read_checked(data.BASE/'PG17500-inspector-deployment-eight-pt-v1/manifest.json',p['originalManifestSha256'])
    own_pin=data.sha((data.ROOT/OWN).read_bytes())
    git_blob=subprocess.check_output(['git','show',SOURCE+':'+OWN],cwd=data.ROOT)
    require(p['readOnlyPublicInputs'][OWN]==raw['begin']['readOnlyPublicInputs'][OWN]==raw['begin']['sourceHashes'][OWN]==data.sha(git_blob)==own_pin,'current/source/run exact owned file')
    require(p['owners'][OWN]['canonicalOwner']==p['owners'][OWN]['canonicalCostOwner']=='WBS-C08','original artifact/cost owner')
    design=(data.ROOT/DESIGN).read_bytes();approved=subprocess.check_output(['git','show','origin/main:'+DESIGN],cwd=data.ROOT)
    require(design==approved,'approved design bytes, no modification')
    gaps=[path for path in node['evidencePlan']['designFiles'] if path not in p['approvedDesignHashes']]
    require(gaps==[DESIGN],'precise missing comprehensive runbook join, not design defect')
    related={path:dict(sha256=pin,owner=p['owners'][path]['canonicalOwner']) for path,pin in p['readOnlyPublicInputs'].items() if path!=OWN}
    require(len(related)==4,'C02 three Unit inputs plus F02 POM, not extra C08 ownership')
    verify(p['invocation']);verify(raw['begin']['invocation']);verify(invocation)
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in inputs.items()),'all four WBS files unchanged')
    result=dict(actualExit=0,source=SOURCE,invocation=invocation,sourceEvidenceBindings=sources,inputs=inputs,
        approvedDesignSha256=data.sha(design),approvedDesignPath=DESIGN,wbsNodeSnapshot=node,
        ownedArtifactRows=[dict(path=OWN,sha256=own_pin,owner='WBS-C08',costOwner='WBS-C08',currentSourceRunJoined=True)],
        ownedArtifactCount=1,ownedArtifactJoinedCount=1,missingOwnedArtifacts=[],relatedInputs=related,
        currentSourceOwnedInventoryEvidenceReady=True,comprehensiveDependencyTraceAccepted=False,
        criteriaEvidenceReady=['WBS-C08:scope'],criteriaAccepted=[],newAcceptedLeaves=[],
        criteriaStatus={'WBS-C08:scope':'OWNED_INVENTORY_JOIN_READY_FULL_ACCEPTANCE_NOT_CHANGED','WBS-C08:contract':'COMPREHENSIVE_SS353_OBLIGATION_JOIN_NOT_COMPLETED','WBS-C08:quality':'RESOURCE_TESTS_AND_TOOL_SYNTAX_PASSED_FULL_APPLICABILITY_NOT_CLOSED'},
        missingComprehensiveDesignJoins=gaps,existingOriginalMethods=8,existingToolReceipts=50,
        newProductExecutions=0,existingResultsReexecuted=False,wbsAcceptanceChanged=False,estimateChanged=False,
        actualRecoveryActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,
        privateDataRead=False,holdReleased=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
