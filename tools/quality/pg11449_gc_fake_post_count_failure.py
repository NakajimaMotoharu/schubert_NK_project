"""Preserve rejected independent-post prediction and original48/XML44; no product or analyzer replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='495313cd8e724d5f1906fca64d9d9fd3516aae50'
OUT=data.BASE/'PG11449-gc-fake-post-count-failure-v1'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    tool=data.ROOT/'tools/quality/pg11450_gc_fake_guard_post.py'
    assert data.sha(tool.read_bytes())=='36e04bbe5ead538088c96ce56c28ddfc9eebcb0047364c342fe4024fe7512191'
    host=data.read_checked(data.BASE/'PG11446-gc-fake-guard-host-v1/manifest.json','c849836c6b0356430eaaf4426718bc8307bc1d8cd5581eb659cd776e8a529e74')
    static=data.read_checked(data.BASE/'PG11448-gc-fake-guard-static-v1/manifest.json','4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185')
    assert host['source']==static['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==48
    assert static['actualExit']==1 and static['reports']['pmd']['findings']==44 and static['reports']['pmd']['processingErrors']==0
    assert data.sha((data.BASE/'PG11448-gc-fake-guard-static-v1/pmd.xml').read_bytes())==static['reports']['pmd']['sha256']
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg11450-gc-fake-guard-post-v1'
    assert not slot.exists() and not (data.BASE/'PG11450-gc-fake-guard-post-v1').exists()
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,relatedBugs=['BUG-1914'],relatedYkt=['YKT-1663'],
        rejectedToolPath=str(tool.relative_to(data.ROOT)),rejectedToolSha256=data.sha(tool.read_bytes()),rejectedPostActualExit=1,
        rejectedPostSlotNotCreated=True,predictedRawRejected=20,actualRaw=44,actualStaticExit=1,originalPtTests=48,originalPtActualExit=0,
        originalHostManifestSha256='c849836c6b0356430eaaf4426718bc8307bc1d8cd5581eb659cd776e8a529e74',
        originalStaticManifestSha256='4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185',
        productTestsExecuted=0,rawAnalyzerReissued=False,coverage=None,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
