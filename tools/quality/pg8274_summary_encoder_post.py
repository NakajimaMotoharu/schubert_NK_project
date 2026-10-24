"""Exact58/5, all eight current executable classes across bootstrap/API, one actual exec."""
import json
import scoped_prometheus_post as post
import pg8272_summary_encoder_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8272-summary-encoder-host-v1'
    post.RAW_SHA = '8e7c770b0f2bd0f5059211f27f5bb9cc172a305b47fa7628c2e5241d512f78ae'
    post.SLOT = post.host.W / 'pg8274-summary-encoder-post-v1'
    post.OUT = post.host.BASE / 'PG8274-summary-encoder-post-v1'
    api = post.PREFIX
    bootstrap = 'dev/codex/schubert/nk/bootstrap/monitoring/'
    post.NAMES = {api + 'ExactDurationMeterRegistry', api + 'ExactDurationMeterRegistry$ExactSummary',
                  api + 'DbQueryDurationMetricRecorder', api + 'DbQueryDurationMetricRecorder$Query',
                  api + 'DbQueryDurationMetricRecorder$Outcome', api + 'MqProcessingDurationMetricRecorder',
                  api + 'MqProcessingDurationMetricRecorder$Outcome', bootstrap + 'PrometheusSummaryExporter'}
    post.CLASS_MODULES = {bootstrap + name: 'bootstrap' for name in ('PrometheusSummaryExporter', 'package-info')}
    post.COMPONENT_METADATA = {bootstrap + 'package-info'}
    post.MARKERS = {api + 'ExactDurationSupport': 'Empty package-local pure capability interface, no fields/methods/initialization; explicit bytecode proof, never exclude executable code.'}
    post.SOURCE_PATHS = {'src/schubert-nk-' + post.CLASS_MODULES.get(name, 'api') + '/src/main/java/' + name.split('$', 1)[0] + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {api + name: ['values', 'valueOf'] for name in ('DbQueryDurationMetricRecorder$Query', 'DbQueryDurationMetricRecorder$Outcome', 'MqProcessingDurationMetricRecorder$Outcome')}
    post.ENUM_TYPES = set(post.GENERATED)
    post.WITNESS_CASE_PREFIXES = ('dbTime003', 'mqTime003')
    post.EXPECTED_SESSION = 'PG8272-SUMMARY-ENCODER'
    post.PMD_CONTEXT_WITNESS = dict(path='PG8044-exact-duration-review-v5/manifest.json', sha256='3fe26a811d5a734b2e1dd81deff673c809ae6241061de19016a825a325364001')
    path = post.host.BASE / post.PMD_CONTEXT_WITNESS['path']
    post.require(post.host.sha(path) == post.PMD_CONTEXT_WITNESS['sha256'], 'full immutable original private-lock per-row rationale')
    prior = json.loads(path.read_text())
    post.PMD_CONTEXT = [r for r in prior['staticDispositions'] if r['sourcePath'] in post.SOURCE_PATHS]
    post.require(len(post.PMD_CONTEXT) == 2 and {r['raw']['method'] for r in post.PMD_CONTEXT} == {'record', 'takeSnapshot'}, 'exact two current source-byte identical private atomic observation lock findings')
    post.main()
