"""Finite source-only JaCoCo inheritance compatibility review, never Product or fixture execution."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17600-fork-agent-static-review-v1'
GROUPS={
'api/bootstrap':['ApiProcessLifetimeTest','ApiProcessMainTest','BootstrapAdminMainTest'],
'batch/file':['ExternalEntryRejectionTest','MorningStartupRetainOwnerTest','RootServiceEnvironmentTest'],
'bootstrap/api/file':['ServiceNativeReleaseTest','ServiceOwnedReleaseTest'],
'bootstrap/bootstrap':['FixedNativeCoverageCheckpointTest','FixedNativeCoverageStopHoldTest'],
'web/bootstrap':['WebAdmissionRemainderTest','WebProcessLifetimeTest','WebProcessMainTest','WebRuntimeExecutionRetentionTest','WebRuntimePendingFailureRetentionTest','WebStartupRetentionTest','WebUnknownRetentionTest']}
def path_for(group,name):
    if group.startswith('bootstrap/api/'):
        return 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/'+name+'.java'
    if group=='bootstrap/bootstrap':
        return 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/'+name+'.java'
    module,package=group.split('/',1)
    return 'src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+module+'/'+package+'/'+name+'.java'
def require(ok,why):
    if not ok:raise ValueError(why)
def assess(v):
    require(v['reviewScope']=='AGENT_ARGUMENT_BUILDER_AND_HELPER_ONLY_NOT_WHOLE_TEST' and v['productTestsExecuted']==0 and v['actualCorruptionObserved'] is False and v['holdReleased'] is False,'static scope, no result extrapolation')
    require((v['targets'],v['unchangedForwarding'],v['explicitAppendFalseGuard'],v['metadataOnlyNonApplicable'])==(17,15,1,1),'all finite seventeen classified')
    require(v['source']==SOURCE and v['currentQualifiedCasesFromTargets']==0 and v['whole451Accepted'] is v['formalUpdated'] is False and v['newAccepted']==0,'no current Product qualification affected or newly accepted')
    require(v['ordinaryMavenContractAllowsAppend'] is True and v['currentSelectedAppendFalseIncompatible'] is True and v['pastProofsInvalidated'] is False and v['productDefectDemonstrated'] is False,'compatibility is not demonstrated past corruption')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only static metadata')
    normal_path=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json'
    normal=data.read_checked(normal_path,'1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'existing normal source proof, no compile replay')
    registry=data.read_checked(data.BASE/'PG17588-current2762-retained-audit-caddy-registry-v1/manifest.json','c45a5c686a95d6a67c297fed02b56832446a7558d89ced8acc1ace58b48031dd')
    rows=[]
    for group,names in GROUPS.items():
        for name in names:
            path=path_for(group,name);blob=(data.ROOT/path).read_bytes();text=blob.decode();require(data.sha(blob)==normal['begin']['inputHashes'][path],'fixed current original Test bytes')
            require('getInputArguments()' in text,'actual lexical candidate')
            if name=='FixedNativeCoverageCheckpointTest':
                require('ProcessBuilder' not in text,'metadata-only JVM argument read, no child forwarding');kind='METADATA_ONLY_NON_APPLICABLE'
            elif name=='MorningStartupRetainOwnerTest':
                guard='assertFalse(agents.getFirst().contains("append=false"));';forward='arguments.add(agents.getFirst());'
                require(guard in text and forward in text and text.index(guard)<text.index(forward),'explicit before-child false rejection');kind='APPEND_FALSE_EXPLICITLY_REJECTED'
            else:
                require(any(x in text for x in ['command.addAll(agents);','.forEach(command::add);','if (option.startsWith("-javaagent:")) command.add(option);','return agents.getFirst();']),'direct unchanged selected-agent forwarding')
                require('destfile=' not in text and 'command.set(' not in text and 'arguments.set(' not in text,'no detected destination rewrite in reviewed builder context');kind='FORWARDED_UNCHANGED_MAVEN_APPEND_CONTRACT_NOT_SELECTED_FALSE_COMPATIBLE'
            suite=path.split('/src/test/java/')[1][:-5].replace('/','.')
            qualified=sum(c['classname']==suite for c in registry['cases']);require(qualified==0,'no historical unqualified test reclassified as current success')
            rows.append(dict(path=path,sha256=data.sha(blob),kind=kind,currentQualifiedCases=qualified,agentReadLines=[i+1 for i,line in enumerate(text.splitlines()) if 'getInputArguments()' in line],reviewScope='AGENT_ARGUMENT_BUILDER_AND_HELPER_ONLY_NOT_WHOLE_TEST',dynamicStatus='NOT_EXECUTED_HOLD_UNCHANGED'))
    docs=['evidence/01_PT/018_NK-OPS-001/1001_外部main引数・OS所有なし拒否の独立PT仕様.md','evidence/01_PT/018_NK-OPS-001/1003_SSC299三entry終了要求・実CLI限定PT結果.md']
    require('generic JaCoCo同run agent' in (data.ROOT/docs[0]).read_text(),'original normal Maven contract, not standalone false')
    raw=(data.ROOT/'tools/quality/scoped_prometheus_host.py').read_text();require("+',append=false,sessionid='+SESSION_ID" in raw,'current raw one-session contract remains unchanged')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,reviewScope='AGENT_ARGUMENT_BUILDER_AND_HELPER_ONLY_NOT_WHOLE_TEST',targets=len(rows),unchangedForwarding=sum(x['kind'].startswith('FORWARDED_') for x in rows),explicitAppendFalseGuard=sum(x['kind']=='APPEND_FALSE_EXPLICITLY_REJECTED' for x in rows),metadataOnlyNonApplicable=sum(x['kind']=='METADATA_ONLY_NON_APPLICABLE' for x in rows),currentQualifiedCasesFromTargets=sum(x['currentQualifiedCases'] for x in rows),ordinaryMavenContractAllowsAppend=True,currentSelectedAppendFalseIncompatible=True,pastProofsInvalidated=False,productDefectDemonstrated=False,actualCorruptionObserved=False,productTestsExecuted=0,holdReleased=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,originalContractHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in docs},officialAppendDefaultStaticObservation=dict(originalToolResponse='53c597',originalExit=0,command=['javap','-classpath','org.jacoco.core-0.8.15.jar','-c','org.jacoco.core.runtime.AgentOptions'],methodBytecode=['ldc append','iconst_1','invokespecial getOption:(Ljava/lang/String;Z)Z','ireturn'],jarSha256='ade1e0fdb4cd80d8537b57c6edb70a1360c47fdc518c20c65314517479bc4d0d',toolReexecuted=False))
    assess(value);negatives=[]
    for key,badvalue in [('productTestsExecuted',1),('actualCorruptionObserved',True),('holdReleased',True),('targets',0),('unchangedForwarding',0),('explicitAppendFalseGuard',0),('metadataOnlyNonApplicable',0),('source','OLD'),('currentQualifiedCasesFromTargets',1),('whole451Accepted',True),('formalUpdated',True),('newAccepted',1),('ordinaryMavenContractAllowsAppend',False),('currentSelectedAppendFalseIncompatible',False),('pastProofsInvalidated',True),('productDefectDemonstrated',True)]:
        bad=dict(value);bad[key]=badvalue
        try:assess(bad)
        except ValueError:negatives.append(key)
        else:raise ValueError('false static conclusion accepted '+key)
    require(data.sha(Path('/home/mini/codex/project1/work/toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar').read_bytes())==value['officialAppendDefaultStaticObservation']['jarSha256'],'official library byte provenance, no Product class loaded')
    verify(invocation);OUT.mkdir();data.write(OUT/'target-contexts.safe.json',rows);value.update(targetContextSha256=data.sha((OUT/'target-contexts.safe.json').read_bytes()),metadataNegativeVectors=len(negatives),negativeLabels=negatives)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
