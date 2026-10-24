"""Only fixed public profiles and owned offline product-parser children; never start a daemon."""
import json
import re
import scoped_prometheus_host as run

SOURCE = 'f817b004781e6c32aa2d384dd12855cad7175ddc'
COMPILE = run.host.W / 'pg8632-api-web-custom-payload-six-compile-v1'
COMPILE_SHA = '8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'
COUNTS = {'PrometheusProfileParserTest': 8}
PROFILES = {'debug': 'df964a0793af23bc61d3531fa516d0dd4787a5a5595cda64e96d3f0e01f43f6a', 'standard': '52e6254d2eb82f4f3072f8c5a96a2b21b2fee350480a8ebe3f4018f53d8716e8'}
TOOL = run.host.TC / 'promtool-3.13.5-linux-amd64/promtool'
TOOL_SHA = '4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff'

def preflight():
    """Exact object equality is a closed allowlist, including no file/auth/discovery references."""
    assert run.host.sha(TOOL) == TOOL_SHA
    for mode, digest in PROFILES.items():
        path = run.host.ROOT / ('src/deployment/monitoring/prometheus/' + mode + '.yml.template')
        assert run.host.sha(path) == digest
        jobs = []
        if mode == 'debug':
            for role, port in (('web',8081),('api',8091)):
                jobs.append(dict(job_name='schubert-nk-' + role, metrics_path='/actuator/prometheus', scheme='http', follow_redirects=False, proxy_from_environment=False, honor_labels=False, honor_timestamps=False, static_configs=[dict(targets=['127.0.0.1:' + str(port)])]))
        assert json.loads(path.read_text()) == {'global': {'scrape_interval':'15s','scrape_timeout':'5s'}, 'scrape_configs': jobs}
    helper = run.host.ROOT / 'tools/quality/architecture/PrometheusProfileParserJunitLauncher.java'
    selections = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',helper.read_text(),re.S)
    assert len(selections)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selections[0]) == ['dev.codex.schubert.nk.web.monitoring.PrometheusProfileParserTest']

if __name__ == '__main__':
    preflight()
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8652-prometheus-profile-parser-host-v1'
    run.OUT = run.host.BASE / 'PG8652-prometheus-profile-parser-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/PrometheusProfileParserJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/PrometheusProfileParserTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8652-PROMETHEUS-PROFILE-PARSER'
    run.FIXTURES = {}
    run.main()
