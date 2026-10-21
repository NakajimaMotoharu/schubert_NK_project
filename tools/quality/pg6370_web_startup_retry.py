"""New-only related54 after SS324 stale-Test correction; never reuse interrupted PASS as full."""
import json
import subprocess
import xml.etree.ElementTree as ET
import pg6364_web_startup_green as previous
from pg5940_private_lock_compile import ROOT, W, BASE, sha

OLD = '11ecc762fddd6a4812a7cd644cdaa437b2ae636b'
TESTS = {'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/'+n+'.java'
         for n in ('WebLogApplicationRuntimeTest', 'WebStartupRetentionTest')}
inventory = previous.inventory


def interrupted():
    run = W/'pg6364-web-startup-selected-v1'; manifest = run/'manifest.safe.json'
    value = json.loads(manifest.read_bytes())
    path = run/'source/src/schubert-nk-web/target/surefire-reports/TEST-dev.codex.schubert.nk.web.bootstrap.WebStartupRetentionTest.xml'
    root = ET.parse(path).getroot()
    if not (sha(manifest) == 'a6f2ba42bde0d81b71d5526e955e8d9e5bc7f2779940b8375e11143e9abde896'
            and value['source'] == OLD and value['actualExit'] == value['mavenActualExit'] == 1
            and value['sourceFixed'] and not value['selectedQualified'] and (value['tests'], value['suites']) == (24, 9)
            and sha(path) == 'f82d008bd6f920862dfe962997d466dd5c7961891080bbee1303639b0f18df1c'
            and [int(root.get(k)) for k in ('tests', 'failures', 'errors', 'skipped')] == [2, 0, 0, 0]):
        raise ValueError('genuine interrupted original and limited new2 XML, not all54 success')
    receipt = json.loads((BASE/'PG6364-web-startup-interrupted-v1/manifest.json').read_bytes())
    if not (receipt['state'] == 'INTERRUPTED_BY_AGENT_FOR_BUG1575_STALE_TEST_ORACLE'
            and receipt['interruption']['pidfdTerminalWithin10Seconds'] and not receipt['all54Qualified']
            and all(receipt['independentPost'][k] for k in ('maven1339091Absent', 'shell1340141Absent', 'surefire1340143Absent'))):
        raise ValueError('saved scoped interruption/post, never live original replay')


def guard_source(source):
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != TESTS:
        raise ValueError('exact two Test-only SS324 corrections; all Main and other old oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates/Current fixed')


def runner():
    raw = previous.red.runner()
    for before, after in (('runner_source(20,10,target_count=16)', 'runner_source(54,15,target_count=16)'),
                          ('pg6360-web-startup-red-v1', 'pg6370-web-startup-retry-v1'),
                          ('def run_red():', 'def run_retry():')):
        if raw.count(before) != 1:
            raise ValueError('one explicit corrected54 binding '+before)
        raw = raw.replace(before, after, 1)
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed corrected Test/operator first')
    interrupted(); guard_source('HEAD')
    scope = {**vars(previous.red.previous.previous.prior), 'inventory': inventory}
    exec(compile(runner(), '<new54 after registered stale-oracle correction>', 'exec'), scope)
    return scope['run_retry']()


if __name__ == '__main__':
    raise SystemExit(main())
