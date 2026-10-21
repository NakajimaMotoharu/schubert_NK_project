"""Own finite JDBC proxy counterexample; no database or operational entry point."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
import finite_selected_profile as profile

OLD = '1b663c1b0271c3e9318701a16e12b378e1ffaa5d'
RED_SOURCE = None
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/JdbcTransactionFatal329Test.java'
MAINS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java'}
TARGETS = {'api': ['api/error/TemporaryInfrastructureException', 'api/dispatch/JdbcSyncRequestProcessor']}


def inventory():
    return profile.inventory({'api': {'api.dispatch.JdbcTransactionFatal329Test'}}, (20, 8))


def guard_source(source, phase):
    path = BASE/'PG6540-jdbc-graph-qualification-v1/manifest.json'
    if sha(path) != '34fa4259f6c8a0ab250c1aba63b2e03346dd5d75364f9d5f4ce41bb4f4255222':
        raise ValueError('original qualified23 first')
    value = json.loads(path.read_bytes())
    if value['source'] != OLD or value['actualExit'] != 0:
        raise ValueError('exact previous Main source')
    changes = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'],
                                        cwd=ROOT, text=True).splitlines())
    if changes != ({TEST} if phase == 'red' else {TEST} | MAINS):
        raise ValueError('independent Test only or localized two Main PG')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw',
                               'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('fixed build/static/Current')
    if phase == 'green' and (RED_SOURCE is None or subprocess.check_output(
            ['git', 'diff', RED_SOURCE, source, '--', ':(glob)src/*/src/test/**'], cwd=ROOT)):
        raise ValueError('independent red oracle bytes must remain fixed')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=('red', 'green'))
    phase = parser.parse_args().phase
    cases, counts = inventory()
    slot = 'pg6544-jdbc-transaction-red-v1' if phase == 'red' else 'pg6546-jdbc-transaction-green-v1'
    return profile.execute(slot, lambda source: guard_source(source, phase), cases, counts, (20, 8), TARGETS)


if __name__ == '__main__':
    raise SystemExit(main())
