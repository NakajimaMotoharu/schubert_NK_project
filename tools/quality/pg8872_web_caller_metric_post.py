"""Current36 exact API Binding/collector/HTTP four counters and source-fixed PMD rows."""
import json
import scoped_prometheus_post as post
import pg8870_web_caller_metric_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8870-web-caller-metric-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg8872-web-caller-metric-post-v1'
    post.OUT=post.host.BASE/'PG8872-web-caller-metric-post-v1'
    post.MODULE='web'
    post.PREFIX='dev/codex/schubert/nk/web/monitoring/'
    names=['WebDbPoolMetricBinding','WebDbPoolMetricCollector','WebMetricHttpHandler']
    post.NAMES={post.PREFIX+name for name in names}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-web/src/main/java/'+post.PREFIX+name+'.java' for name in names}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8870-WEB-CALLER-METRIC'
    witness='PG8871-web-caller-metric-context-v1/manifest.json'
    digest=post.host.sha(post.host.BASE/witness)
    evidence=json.loads((post.host.BASE/witness).read_text())
    assert evidence['source']==original.SOURCE and evidence['actualExit']==0 and evidence['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=evidence['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==3 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
