"""Legacy Receipt data-only defaults, one new Test and all fixed finite guards."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT, W, BASE

OLD = '2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3f'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/LegacyReceiptValueTest.java'
SLOT = 'pg6910-legacy-receipt-selected-v1'
EXPECTED = (25, 9)


def inventory():
    return profile.inventory({'batch': {'batch.platform.LegacyReceiptValueTest', 'batch.platform.MorningBackupUnitCycleTest'}}, EXPECTED)


def guard(source):
    changes = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if changes != [TEST]:
        raise ValueError('one new one-method Test, every Main and old oracle fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/quality/Current fixed')


def read_original():
    run = W / SLOT
    source = json.loads((run / 'begin.safe.json').read_bytes())['source']
    guard(source)
    cases, _ = inventory()
    return prior.qualification_definition()(source, run, cases, EXPECTED, set(),
      BASE / 'PG6886-data-boundary-original-v1/manifest.json', '2814d78fe5ee54672c9a40a6aeaac151a125a75d3a68a4e48ab94390decaac78',
      W / 'pg6886-data-boundary-original-v1/manifest.safe.json', W / 'pg6886-data-boundary-original-v1/findings.safe.json',
      'pg6912-legacy-receipt-original-v1', 'PG6912-legacy-receipt-original-v1', expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'read'))
    if parser.parse_args().action == 'read':
        return read_original()
    cases, counts = inventory()
    scope = {**vars(profile), 'runner': prior.runner}
    exec(compile(inspect.getsource(profile.execute), '<finite legacy receipt data>', 'exec'), scope)
    return scope['execute'](SLOT, guard, cases, counts, EXPECTED, {'batch': ['batch/platform/MorningBackupUnitCycle$Receipt']})


if __name__ == '__main__':
    main()
