"""Two pure observation value diagnostics, immutable public inputs and no native observation."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT, W, BASE

OLD = 'd093491984ce16914a5c545dbc683c11fb7db868'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'
SLOT = 'pg6916-observation-values-selected-v1'
EXPECTED = (17, 9)


def inventory():
    return profile.inventory({'batch': {'batch.file.ObservationValueRedactionTest', 'batch.mq.ArtemisStartupObservationTest'}}, EXPECTED)


def guard(source):
    paths = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if paths != [TEST]:
        raise ValueError('one new two-method Test, all Main and old oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/quality/Current fixed')


def read_original():
    run = W / SLOT
    source = json.loads((run / 'begin.safe.json').read_bytes())['source']
    guard(source)
    cases, _ = inventory()
    return prior.qualification_definition()(source, run, cases, EXPECTED, set(),
      BASE / 'PG6912-legacy-receipt-original-v1/manifest.json', 'b03ac4ea16c71beb4c42f96d3c1e7e5f4282ed64e2ca37f88b3ed9b648f2bd9c',
      W / 'pg6912-legacy-receipt-original-v1/manifest.safe.json', W / 'pg6912-legacy-receipt-original-v1/findings.safe.json',
      'pg6918-observation-values-original-v1', 'PG6918-observation-values-original-v1', expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'read'))
    if parser.parse_args().action == 'read':
        return read_original()
    cases, counts = inventory()
    scope = {**vars(profile), 'runner': prior.runner}
    exec(compile(inspect.getsource(profile.execute), '<finite observation value records>', 'exec'), scope)
    return scope['execute'](SLOT, guard, cases, counts, EXPECTED,
      {'batch': ['batch/file/RootServiceFacts$Facts', 'batch/file/MorningBrokerExecution$Observations']})


if __name__ == '__main__':
    main()
