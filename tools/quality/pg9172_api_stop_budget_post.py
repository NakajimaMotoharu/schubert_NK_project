"""Full one-Main RO owner actual coverage/static/CRC/current XML; real DB/worker/native unqualified."""
import json
import scoped_api_bootstrap_post as post
import pg9170_api_stop_budget_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9170-api-stop-budget-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9172-api-stop-budget-post-v1'
    post.OUT=post.host.BASE/'PG9172-api-stop-budget-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/bootstrap/'
    post.NAMES={post.PREFIX+'ApiStopBudget'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.PACKAGE_METADATA=set()
    assert not (post.host.ROOT/'src/schubert-nk-api/src/main/java'/post.PREFIX/'package-info.java').exists()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiStopBudget.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9170-API-STOP-BUDGET'
    witness='PG9171-api-stop-budget-review-v1/manifest.json'
    digest='b80b4184cc24ad6264aee4855225f7aebd8baff87cae77f265e649842e2b7f8b'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=json.loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==2 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
