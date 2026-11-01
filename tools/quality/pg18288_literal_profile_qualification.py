"""Qualify pure literal-profile helper; never execute Product methods or generated code."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as runner
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NODE=data.ROOT.parent/'toolchain/node-v24.19.0/bin/node'
PINS={'tools/quality/literal_profile_replace_v2.mjs':'3370b22463c9e46781511d0de63e216c8d207f425a4fe3cf8c91d4bc7aa08df2','tools/quality/pg18288_literal_profile_replace_test.mjs':'a7f197117d7173b701b08dd7f6a2350c4b5425fcc55acbdf43b6f1b2213382a6'}
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg18288-literal-profile-qualification-v1'
OUT=data.BASE/'PG18288-literal-profile-qualification-v1'
def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    assert data.sha(NODE.read_bytes())=='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in PINS.items())
    helper=(data.ROOT/'tools/quality/literal_profile_replace_v2.mjs').read_text()
    assert not any(t in helper for t in ['import ','eval(','Function(','fetch(','node:','process.','require('])
    SLOT.mkdir();runner.SLOT=SLOT
    command=[str(NODE),str(data.ROOT/'tools/quality/pg18288_literal_profile_replace_test.mjs')]
    stage=runner.step('literal-profile-selftest',command,SLOT,timeout=60)
    data.write(SLOT/'selftest-stage.safe.json',stage)
    assert stage['actualExit']==0 and not stage['timedOut']
    result=json.loads((SLOT/'literal-profile-selftest.stdout').read_bytes())
    assert result==dict(actualExit=0,toolPositiveVectors=15,toolNegativeVectors=31,independentScanVectors=15,boundaryAndSnapshotChecks=4,productTestsExecuted=0,externalActions=0,formalUpdated=False)
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in PINS.items())
    assert data.sha((data.ROOT/'tools/quality/literal_template_replace_v1.mjs').read_bytes())=='dfdd02e8efe08d3b6a4c215fc0afad5206b2efb1a104303e5f58301e3b45f070'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),toolSourceHashes=PINS,runtimeVersion='v24.19.0',runtimeSha256='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12',stage=stage,result=result,sourceParserOrQualityGateClaimed=False,oldHelperChanged=False,generatedCodeExecuted=False,actualProductTestsExecuted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
