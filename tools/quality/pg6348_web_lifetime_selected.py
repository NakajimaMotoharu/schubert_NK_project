"""New host-only lifetime fixture on byte-identical qualified Production Main; no real owner."""
import subprocess
import pg6264_outbox_failure_red as previous

ROOT = previous.ROOT
OLD = 'aed19c6dca368e9717309d6f744d7917c6b7b32c'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebProcessLifetimeTest.java'


def inventory():
    engine = previous.prior.engine
    cases = {m: set(v) for m, v in engine.CASES.items()}
    cases['web'].update(('web.bootstrap.WebProcessLifetimeTest', 'web.bootstrap.WebUnknownRetentionTest'))
    counts = {engine.PACKAGE+n: len(previous.prior.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+n).replace('.', '/')+'.java')))
              for m, names in cases.items() for n in names}
    if (sum(counts.values()), len(counts)) != (18, 9):
        raise ValueError('actual12 baseline plus5 lifetime and1 retained fixture, not child/matrix inflation')
    return cases, counts


def runner():
    raw = previous.runner()
    for before, after in (
        ('runner_source(18,8,target_count=16)', 'runner_source(18,9,target_count=15)'),
        ('pg6264-outbox-failure-red-v1', 'pg6348-web-lifetime-selected-v1'),
        ('def run_red():', 'def run_selected():'),
        ("scope['targets']['api'].extend(('api/messaging/outbound/OutboxJmsSender','api/messaging/outbound/OutboxDispatcher'))",
         "scope['targets']['web'].append('web/bootstrap/WebProcessLifetime')")):
        if raw.count(before) != 1:
            raise ValueError('one explicit host lifetime binding '+before)
        raw = raw.replace(before, after, 1)
    return raw


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('exact one Test change; all851 Main and other Test inputs fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates and Current unchanged')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed one Test/operator first')
    guard_source('HEAD')
    scope = {**vars(previous.prior), 'inventory': inventory}
    exec(compile(runner(), '<one owned host Web lifetime fixture>', 'exec'), scope)
    return scope['run_selected']()


if __name__ == '__main__':
    raise SystemExit(main())
