"""Own synthetic retention wire fixture; fixed Main/old tests, original finite run only."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT, W, BASE

OLD = '2b2e4f70746bd1e1e405e18427dfd45616f51623'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RetentionWireBoundaryTest.java'
SLOT = 'pg6878-retention-wire-selected-v1'
EXPECTED = (29, 10)


def inventory():
    return profile.inventory({'batch': {'batch.file.RetentionWireBoundaryTest',
      'batch.file.MorningBackupRetentionTest', 'batch.file.MorningGateEvidenceTest'}}, EXPECTED)


def guard(source):
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if changed != [TEST]:
        raise ValueError('only one new two-method Test; all Main and old oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all build/quality/Current inputs fixed')


def read_original():
    run = W / SLOT
    source = json.loads((run / 'begin.safe.json').read_bytes())['source']
    guard(source)
    cases, _ = inventory()
    return prior.qualification_definition()(source, run, cases, EXPECTED, set(),
      BASE / 'PG6854-web-deadline-original-v1/manifest.json', '69dba2782be8034e9efac8505b5019d466da0100bd1a3bc105f57760b61466fd',
      W / 'pg6854-web-deadline-original-v1/manifest.safe.json', W / 'pg6854-web-deadline-original-v1/findings.safe.json',
      'pg6880-retention-wire-original-v1', 'PG6880-retention-wire-original-v1', expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'read'))
    if parser.parse_args().action == 'read':
        return read_original()
    cases, counts = inventory()
    scope = {**vars(profile), 'runner': prior.runner}
    exec(compile(inspect.getsource(profile.execute), '<finite retention wire>', 'exec'), scope)
    return scope['execute'](SLOT, guard, cases, counts, EXPECTED, {'batch': ['batch/file/MorningGateEvidence']})


if __name__ == '__main__':
    main()
