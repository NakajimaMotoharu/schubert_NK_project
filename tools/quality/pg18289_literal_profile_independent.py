"""Independent saved tool-result/profile witness; no selftest or Product re-execution."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PIN='c37e66f0a8d7bb0bc5cb1cc5d8bac9671df1dfa903b0566028f088f0a770f1c1'
OUT=data.BASE/'PG18289-literal-profile-independent-v1'
def require(ok,reason):
    if not ok:raise ValueError(reason)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m=data.read_checked(data.BASE/'PG18288-literal-profile-qualification-v1/manifest.json',PIN)
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE,'source and genuine exit')
        require(v['runtimeVersion']=='v24.19.0' and v['runtimeSha256']=='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12','pinned runtime')
        require(v['result']==dict(actualExit=0,toolPositiveVectors=15,toolNegativeVectors=31,independentScanVectors=15,boundaryAndSnapshotChecks=4,productTestsExecuted=0,externalActions=0,formalUpdated=False),'actual tool result only')
        require(v['stage']['actualExit']==0 and not v['stage']['timedOut'] and v['stage']['command']==[str(data.ROOT.parent/'toolchain/node-v24.19.0/bin/node'),str(data.ROOT/'tools/quality/pg18288_literal_profile_replace_test.mjs')],'exact tool command and terminal')
        require(v['toolSourceHashes']=={'tools/quality/literal_profile_replace_v2.mjs':'3370b22463c9e46781511d0de63e216c8d207f425a4fe3cf8c91d4bc7aa08df2','tools/quality/pg18288_literal_profile_replace_test.mjs':'a7f197117d7173b701b08dd7f6a2350c4b5425fcc55acbdf43b6f1b2213382a6'},'exact whole tool hashes')
        require(v['sourceParserOrQualityGateClaimed'] is v['oldHelperChanged'] is v['generatedCodeExecuted'] is v['formalUpdated'] is False and v['actualProductTestsExecuted']==v['actualVmActions']==v['actualDatabaseActions']==v['actualNetworkActions']==v['newAccepted']==0 and v['effortPercent'] is None,'no Product/sandbox/quality claims')
    contract(m);labels=[]
    for key,value in [('source','OLD'),('actualExit',True),('runtimeVersion','unknown'),('runtimeSha256','0'*64),('result',{}),('toolSourceHashes',{}),('sourceParserOrQualityGateClaimed',True),('oldHelperChanged',True),('generatedCodeExecuted',True),('actualProductTestsExecuted',1),('newAccepted',1),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false tool qualification')
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg18288-literal-profile-qualification-v1'
    require(data.sha((slot/'literal-profile-selftest.stdout').read_bytes())==m['stage']['stdoutSha256'],'original stdout')
    require(data.sha((slot/'literal-profile-selftest.stderr').read_bytes())==m['stage']['stderrSha256'],'original stderr')
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in m['toolSourceHashes'].items()),'source unchanged')
    require(data.sha(Path(m['stage']['command'][0]).read_bytes())==m['runtimeSha256'],'runtime whole bytes')
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,qualifiedManifestSha256=PIN,metadataNegativeVectors=len(labels),negativeLabels=labels,selftestsReexecuted=0,productTestsExecuted=0,securitySandboxClaimed=False,trustedLiteralArrayInputOnly=True,proxiesOrAccessorsAssessed=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
