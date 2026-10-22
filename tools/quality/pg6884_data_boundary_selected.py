"""Synthetic value diagnostics/argument rejection, not root authentication or native execution."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT, W, BASE

OLD = 'a9d073e067a4400c7b68c94bb0e91a9b0903ace5'
TESTS = {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CurrentObservationValueTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ServiceDeadlineArgumentTest.java'}
SLOT = 'pg6884-data-boundary-selected-v1'
EXPECTED = (42, 11)


def inventory():
    return profile.inventory({'batch': {'batch.file.CurrentObservationValueTest', 'batch.platform.ServiceDeadlineArgumentTest',
      'batch.platform.RootStartupContextTest', 'batch.file.RootCurrentPermitPreflightTest'}}, EXPECTED)


def guard(source):
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changed) != TESTS or len(changed) != 2:
        raise ValueError('only two new one-method Tests; all Main and old oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all build/quality/Current inputs fixed')


def read_original():
    run = W / SLOT
    source = json.loads((run / 'begin.safe.json').read_bytes())['source']
    guard(source)
    cases, _ = inventory()
    return prior.qualification_definition()(source, run, cases, EXPECTED, set(),
      BASE / 'PG6880-retention-wire-original-v2/manifest.json', '8b33234201d16c5ae4c236fb0b7f0052953dbab88f723c712bb0439ec92bf3d7',
      W / 'pg6880-retention-wire-original-v2/manifest.safe.json', W / 'pg6880-retention-wire-original-v2/findings.safe.json',
      'pg6886-data-boundary-original-v1', 'PG6886-data-boundary-original-v1', expected_phase_exits=(0, 0, 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'read'))
    if parser.parse_args().action == 'read':
        return read_original()
    cases, counts = inventory()
    scope = {**vars(profile), 'runner': prior.runner}
    exec(compile(inspect.getsource(profile.execute), '<finite pure data boundaries>', 'exec'), scope)
    return scope['execute'](SLOT, guard, cases, counts, EXPECTED, {'batch': ['batch/platform/RootStartupContext']})


if __name__ == '__main__':
    main()
