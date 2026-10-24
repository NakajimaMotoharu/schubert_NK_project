"""Offline public Prometheus configuration semantics; no daemon, socket, VM or database."""
import copy
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest
from host_tool_invocation import capture, verify

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT = BASE / 'PG8140-prometheus-config-pt-v1'
DIRECTORY = 'src/deployment/monitoring/prometheus/'
NAMES = ('debug.yml.template', 'standard.yml.template', 'debug-arguments.json.template')
BASELINE = 'e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
SPEC = 'evidence/01_PT/018_NK-OPS-001/1730_Prometheus配布設定_単体テスト仕様書.md'
GLOBAL = {'scrape_interval': '15s', 'scrape_timeout': '5s'}
# Entire expected data is independently transcribed from1730 and SS342, not production code.
DEBUG = {
    'global': {'scrape_interval': '15s', 'scrape_timeout': '5s'},
    'scrape_configs': [
        {'job_name': 'schubert-nk-web', 'metrics_path': '/actuator/prometheus', 'scheme': 'http',
         'follow_redirects': False, 'proxy_from_environment': False, 'honor_labels': False,
         'honor_timestamps': False, 'static_configs': [{'targets': ['127.0.0.1:8081']}]},
        {'job_name': 'schubert-nk-api', 'metrics_path': '/actuator/prometheus', 'scheme': 'http',
         'follow_redirects': False, 'proxy_from_environment': False, 'honor_labels': False,
         'honor_timestamps': False, 'static_configs': [{'targets': ['127.0.0.1:8091']}]}
    ]}
STANDARD = {'global': {'scrape_interval': '15s', 'scrape_timeout': '5s'}, 'scrape_configs': []}
ARGUMENTS = [
    '--web.listen-address=127.0.0.1:9090',
    '--config.file=/etc/schubert-nk/monitoring/prometheus/debug.yml',
    '--storage.tsdb.path=/var/lib/schubert-nk/monitoring/prometheus',
    '--storage.tsdb.retention.time=15d',
    '--storage.tsdb.retention.size=5000000000B']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(actual, expected):
    # Typed JSON encoding distinguishes False/0 and1/1.0; arrays preserve semantic ordering.
    if json.dumps(actual, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('configuration differs from independent declared contract')


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate public configuration key')
        result[key] = value
    return result


def nonfinite(_):
    raise ValueError('nonfinite public configuration number')


def parse(text):
    return json.loads(text, object_pairs_hook=object_pairs, parse_constant=nonfinite)


def document(name):
    return parse((ROOT / DIRECTORY / name).read_text())


class ConfigurationTest(unittest.TestCase):
    mutation_checks = 0

    def reject(self, actual, expected):
        with self.assertRaises((ValueError, TypeError)):
            exact(actual, expected)
        type(self).mutation_checks += 1

    def test_PROMCFG001_debug_all_fields(self):
        exact(document(NAMES[0]), DEBUG)
        self.assertEqual(2, len(document(NAMES[0])['scrape_configs']))

    def test_PROMCFG002_standard_no_collection(self):
        exact(document(NAMES[1]), STANDARD)
        self.assertEqual([], document(NAMES[1])['scrape_configs'])

    def test_PROMCFG003_arguments_are_nonexecuting_data(self):
        exact(document(NAMES[2]), ARGUMENTS)
        self.assertEqual(5, len(document(NAMES[2])))

    def test_PROMCFG004_reader_and_profile_faults(self):
        self.reject(document(NAMES[1]), DEBUG)
        self.reject(document(NAMES[0]), STANDARD)
        for wrong in (None, {}, [], '', False):
            self.reject(wrong, DEBUG)
        for raw in ('{"global":{},"global":{}}', '{"x":NaN}', '{"x":Infinity}',
                    '{"x":-Infinity}', '{} {}', '', 'null'):
            if raw == 'null':
                self.reject(parse(raw), STANDARD)
            else:
                with self.assertRaises((ValueError, TypeError)):
                    parse(raw)
                type(self).mutation_checks += 1

    def test_PROMCFG005_target_and_key_mutations(self):
        for index in (0, 1):
            for key, value in (
                ('metrics_path', '/actuator/env'), ('scheme', 'https'),
                ('follow_redirects', True), ('proxy_from_environment', True),
                ('honor_labels', True), ('honor_timestamps', True),
                ('authorization', {'type': 'Bearer'}), ('params', {'extra': ['value']}),
                ('http_sd_configs', [{'url': 'http://example.invalid'}]),
                ('job_name', 'arbitrary-service')):
                changed = copy.deepcopy(DEBUG)
                changed['scrape_configs'][index][key] = value
                self.reject(changed, DEBUG)
            for target in ('0.0.0.0:8081', '[::1]:8081', 'localhost:8081',
                           '127.0.0.1:8080', '127.0.0.1:8090', 'example.invalid:8081'):
                changed = copy.deepcopy(DEBUG)
                changed['scrape_configs'][index]['static_configs'][0]['targets'] = [target]
                self.reject(changed, DEBUG)
        for key, value in (('remote_write', []), ('remote_read', []),
                           ('rule_files', []), ('external_labels', {'unexpected': 'value'})):
            changed = copy.deepcopy(DEBUG)
            changed[key] = value
            self.reject(changed, DEBUG)
        exact(document(NAMES[0]), DEBUG)

    def test_PROMCFG006_retention_listen_and_argv_mutations(self):
        for index, replacements in (
            (0, ('0.0.0.0:9090', '[::]:9090', 'example.invalid:9090', '127.0.0.1:9091')),
            (1, ('/tmp/debug.yml', '/etc/schubert-nk/monitoring/prometheus/standard.yml')),
            (2, ('data', '/tmp/data')),
            (3, ('0', '14d', '16d')),
            (4, ('5GB', '5GiB', '0', '-1B', '5000000001B'))):
            for value in replacements:
                changed = list(ARGUMENTS)
                changed[index] = changed[index].split('=', 1)[0] + '=' + value
                self.reject(changed, ARGUMENTS)
        for value in ('--web.enable-lifecycle', '--web.enable-admin-api', '--log.level=debug'):
            self.reject(ARGUMENTS + [value], ARGUMENTS)
        self.reject(ARGUMENTS[:-1], ARGUMENTS)
        self.reject(list(reversed(ARGUMENTS)), ARGUMENTS)

    def test_PROMCFG007_types_global_and_collection_faults(self):
        for value in ('0s', '1s', None, 15, True):
            changed = copy.deepcopy(DEBUG)
            changed['global']['scrape_interval'] = value
            self.reject(changed, DEBUG)
        for value in (None, [], False, 0):
            changed = copy.deepcopy(DEBUG)
            changed['global'] = value
            self.reject(changed, DEBUG)
        for value in (None, {}, [], DEBUG['scrape_configs'][:1],
                      DEBUG['scrape_configs'] * 2, list(reversed(DEBUG['scrape_configs']))):
            changed = copy.deepcopy(DEBUG)
            changed['scrape_configs'] = value
            self.reject(changed, DEBUG)
        for value in (0, 1, None, 'false', []):
            changed = copy.deepcopy(DEBUG)
            changed['scrape_configs'][0]['follow_redirects'] = value
            self.reject(changed, DEBUG)
        for value in (None, '127.0.0.1:8081', [], [None], ['127.0.0.1:8081', '127.0.0.1:8091']):
            changed = copy.deepcopy(DEBUG)
            changed['scrape_configs'][0]['static_configs'][0]['targets'] = value
            self.reject(changed, DEBUG)

    def test_PROMCFG008_exact_source_trace_and_no_other_production_delta(self):
        expected = {DIRECTORY + p for p in (*NAMES, 'README.md')}
        changed = set(subprocess.check_output(
            ['git', 'diff', '--name-only', BASELINE, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines())
        self.assertEqual(expected, changed)
        dirty = subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=normal', '--', 'src'], cwd=ROOT, text=True)
        self.assertEqual('', dirty)
        for name in expected:
            path = ROOT / name
            self.assertTrue(path.is_file() and not path.is_symlink())
            self.assertFalse(os.access(path, os.X_OK))
        readme = (ROOT / DIRECTORY / 'README.md').read_text()
        for term in ('PROMCFG001..008', 'PG-D580', 'UNRUN/HOLD', 'STANDARD', '5000000000B'):
            self.assertIn(term, readme)


def main():
    invocation = capture(Path(__file__))
    if OUT.exists():
        raise ValueError('new-only config evidence, never replay a saved success')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files = [DIRECTORY + p for p in (*NAMES, 'README.md')] + [SPEC]
    inputs = {p: sha(ROOT / p) for p in files}
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigurationTest))
    static = subprocess.run([sys.executable, '-B', '-m', 'pyflakes', str(Path(__file__))],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    actual = 0 if result.wasSuccessful() and result.testsRun == 8 and not result.skipped and static.returncode == 0 else 1
    if inputs != {p: sha(ROOT / p) for p in files}:
        raise ValueError('source inputs changed during own config PT')
    verify(invocation)
    names = [f'PROMCFG{n:03d}' for n in range(1, 9)]
    value = dict(actualExit=actual, source=source, baselineJavaByteSource=BASELINE, invocation=invocation,
        branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
        startUTC=started, endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(os=platform.platform(),python=sys.version, executable=sys.executable,
                         configParser='Python strict JSON subset only; actual Prometheus/promtool UNRUN'),
        inputHashes=inputs, testsRun=result.testsRun, failed=len(result.failures), errors=len(result.errors),
        skipped=len(result.skipped), mutationChecks=ConfigurationTest.mutation_checks,
        cases=[dict(testId=n, result='PASS' if result.wasSuccessful() else 'NOT_QUALIFIED',
                    oracle='1730 independently fixed entire typed JSON document or described mutation',
                    actual='all assertions passed' if result.wasSuccessful() else 'see own public log') for n in names],
        log=log.getvalue(), static=dict(command=static.args,actualExit=static.returncode,
              stdout=static.stdout,stderr=static.stderr),
        statementCoverage=None,methodCoverage=None,classCoverage=None,branchCoverage=None,
        coverageApplicability='DATA_ARTIFACT_HAS_NO_EXECUTABLE_COUNTERS_NOT_A_JAVA_EXCLUSION',
        javaProductTestsExecuted=0, promtoolExecuted=False, daemonExecuted=False, actualScrapes=0,
        actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualRetentionQualified=False,
        actualServiceOwnershipQualified=False, formalUpdated=False,newAccepted=0,effortPercent=None,
        whole451Accepted=False,ptAlternative=0,qa051Final='HELD',bugs=[])
    os.umask(0o077)
    OUT.mkdir()
    with (OUT / 'manifest.json').open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write('\n')
    print(json.dumps(dict(actualExit=actual,source=source,tests=result.testsRun,failed=len(result.failures),
                         errors=len(result.errors),mutations=ConfigurationTest.mutation_checks,
                         manifestSha256=sha(OUT/'manifest.json'))))
    raise SystemExit(actual)

if __name__ == '__main__':
    main()
