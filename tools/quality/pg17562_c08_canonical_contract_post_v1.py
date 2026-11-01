"""Independent finite C08 obligation metadata and original-receipt join; no Product or recovery calls."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT=('PG17560-c08-canonical-contract-join-v1','e93c53baa373aff56f636cea7004c3bb8e55ee2acfb5fd278bdfe83e3a96aae5')
OUT=data.BASE/'PG17562-c08-canonical-contract-post-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(data.BASE/PARENT[0]/'manifest.json',PARENT[1]);matrix=data.read_checked(data.BASE/PARENT[0]/'matrix.safe.json',p['matrixSha256'])
    require(len(matrix['rows'])==12 and len(matrix['scopeLimits'])==4,'finite entire matrix')
    expected={'C08-C01':['argumentsAndPlaceholders'],'C08-C02':['releaseClasspathAndIsolation'],'C08-C03':['statusMapping'],'C08-C04':['statusMapping'],'C08-C05':['malformedReceipts'],'C08-C06':['statusMapping'],'C08-C07':['statusMapping','malformedReceipts','argumentsAndPlaceholders','realMainBridge'],'C08-C08':['renderedShellCheck'],'C08-R01':['baseUnitAndSyntax'],'C08-R02':['previousProfiles'],'C08-R03':['releaseClasspathAndIsolation'],'C08-R04':['realMainBridge']}
    require({r['id']:r['methods'] for r in matrix['rows']}==expected,'explicit twelve obligation-to-original-method mapping')
    require(sum(r['kind']=='OWNED_SCRIPT' for r in matrix['rows'])==8 and sum(r['kind']=='RELATED_OWNER_NOT_NEW_C08_ARTIFACT' for r in matrix['rows'])==4,'other owner artifacts not added to C08')
    post=data.read_checked(data.BASE/'PG17504-inspector-deployment-eight-post-v2/manifest.json','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f')
    methods={c['name'] for c in post['cases']};require({m for names in expected.values() for m in names}==methods and all(c['result']=='PASS' for c in post['cases']),'all eight original successful methods referenced, not rerun')
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE,'actual source and terminal')
        require(v['canonicalCommit']=='8b91944df5820535e23ba2469740f1c0aa94c447' and v['canonicalDesignHashes']['documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']=='39708837ac8fc5e9245d8633eb40580ddb048e517ddf8ec19c8192e434a34719','canonical full design not dev blanks normalized')
        require((v['contractRows'],v['ownedRows'],v['relatedRows'],v['originalMethodsJoined'],v['existingToolReceipts'])==(12,8,4,8,50),'actual original domains')
        require(v['ownedArtifact']=='src/deployment/operations/inbox-inspector.sh.template' and v['ownedSha256']=='4069033ac536e63c4d9507f31a8d152ee1dd8a89e211d3bb17100dac9e8cc6c3','one exact owned artifact')
        require(v['originalTestSha256']=='60c3a7e9a4da798ca5c70d9dee0462e645d8f8721c6ffcddd0395af21baf11fa' and v['matrixSha256']==data.sha((data.BASE/PARENT[0]/'matrix.safe.json').read_bytes()),'original test and whole matrix bytes')
        require(v['criteriaEvidenceReady']==['WBS-C08:contract','WBS-C08:scope'] and v['qualityScopeReviewComplete'] is True and v['qualityCriterionAccepted'] is False,'evidence readiness is not accepted quality/criteria')
        require(v['criteriaAccepted']==v['newAcceptedLeaves']==[] and len(v['acceptanceHoldReasons'])==2,'whole trace and formal quality not waived')
        require(v['shellFourCounterCoverageClaimed'] is v['javaCounterCoverageClaimed'] is v['holdReleased'] is v['formalUpdated'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no numeric coverage/acceptance/HOLD transition')
        require(all(type(v[k]) is int and v[k]==0 for k in ['actualRecoveryActions','actualVmActions','actualDatabaseActions','actualServiceActions','productTestsReexecuted']),'no actual recovery or Product execution')
        require(all(data.sha((data.ROOT/k).read_bytes())==h for k,h in v['wbsHashes'].items()) and len(v['wbsHashes'])==4,'four WBS files unchanged')
    contract(p);labels=[]
    for k,value in [('actualExit',True),('source','OLD'),('canonicalCommit','OLD'),('contractRows',0),('ownedRows',12),('relatedRows',0),('originalMethodsJoined',0),('existingToolReceipts',0),('ownedArtifact','OTHER'),('ownedSha256','0'*64),('originalTestSha256','0'*64),('matrixSha256','0'*64),('criteriaEvidenceReady',[]),('qualityScopeReviewComplete',False),('qualityCriterionAccepted',True),('criteriaAccepted',['WBS-C08:scope']),('newAcceptedLeaves',['WBS-C08']),('acceptanceHoldReasons',[]),('shellFourCounterCoverageClaimed',True),('javaCounterCoverageClaimed',True),('holdReleased',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('actualRecoveryActions',1),('actualVmActions',1),('actualDatabaseActions',1),('actualServiceActions',1),('productTestsReexecuted',1),('wbsHashes',{})]:
        bad=copy.deepcopy(p);bad[k]=value;require(bad!=p,'nondegenerate '+k)
        try:contract(bad)
        except ValueError:labels.append(k)
        else:raise ValueError('false C08 conclusion accepted '+k)
    verify(post['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PARENT[1],metadataNegativeVectors=len(labels),negativeLabels=labels,contractRows=12,originalMethodsJoined=8,existingToolReceipts=50,allFourWbsFilesUnchanged=True,productTestsExecuted=0,actualRecoveryActions=0,holdReleased=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
