"""Current Batch formatter single Main same-run four counters and unmodified static rules."""
import scoped_prometheus_post as post
import pg8912_batch_full_text_static_fixed_host as original
if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8912-batch-full-text-static-fixed-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg8914-batch-full-text-static-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8914-batch-full-text-static-fixed-post-v1'
    post.MODULE='batch'
    post.PREFIX='dev/codex/schubert/nk/batch/monitoring/'
    post.NAMES={post.PREFIX+'BatchMetricText'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-batch/src/main/java/'+post.PREFIX+'BatchMetricText.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8912-BATCH-FULL-TEXT'
    post.PMD_CONTEXT=[]
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
