"""Current typed pool60/six Main four counters/static, exact six historical-source rationale rows."""
import json
import scoped_prometheus_post as post
import pg8844_typed_pool_binding_fixed_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8844-typed-pool-binding-fixed-host-v1'
    post.RAW_SHA='fafa64a10e6cead62f1509ff9e607a15b3263601b2c6359428ce94820383a435'
    post.SLOT=post.host.W/'pg8846-typed-pool-binding-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8846-typed-pool-binding-fixed-post-v1'
    api='dev/codex/schubert/nk/api/monitoring/'
    web='dev/codex/schubert/nk/web/monitoring/'
    types={'api':['ApiDbPoolMetricBinding','DbPoolMetricCollector','ApiMetricHttpHandler'],'web':['WebDbPoolMetricBinding','WebDbPoolMetricCollector','WebMetricHttpHandler']}
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={f'dev/codex/schubert/nk/{role}/monitoring/{name}' for role,names in types.items() for name in names}
    post.CLASS_MODULES={api+name:'api' for name in types['api']}
    post.CLASS_MODULES[api+'package-info']='api'
    post.COMPONENT_METADATA={api+'package-info'}
    post.SOURCE_PATHS={f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{name}.java' for role,names in types.items() for name in names}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8844-TYPED-POOL-BINDING'
    witness='PG8845-typed-pool-binding-context-v1/manifest.json'
    digest='cf3d5cf4bbf752478679b6d41e6c942b59f69474924a889858930582650229f3'
    assert post.host.sha(post.host.BASE/witness)==digest
    evidence=json.loads((post.host.BASE/witness).read_text())
    assert evidence['source']==original.SOURCE and evidence['actualExit']==0 and evidence['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=evidence['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==6 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
