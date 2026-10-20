"""BUG1538 fixture-only serial contract correction; new-only genuine Web925 retry."""
import inspect
import subprocess
import pg6080_web_factory_selected as original

SOURCE = '870010d6681d74519237be7a7ca6381a190f471a'


def runner_source(total=None, suites=None):
    raw = original.runner_source()
    old = "head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()"
    if raw.count(old) != 1:
        raise ValueError('one fixed source snapshot identity,not later operator HEAD')
    return raw.replace(old, 'head='+repr(SOURCE), 1)


def main():
    run = inspect.getsource(original.main)
    old = "'SLOT': 'pg6080-web-factory-selected-v1'"
    if run.count(old) != 1:
        raise ValueError('one explicit new-only retry namespace')
    run = run.replace(old, "'SLOT': 'pg6086-web-factory-selected-v2'", 1)
    if subprocess.check_output(['git', 'diff', 'd75a9178bd726ffec950ad360786c9e908128f06', 'HEAD', '--',
                                 'src/schubert-nk-web/src/main', 'pom.xml', '.mvn', 'mvnw',
                                 'tools/quality/static', 'program/characterization'], cwd=original.ROOT):
        raise ValueError('same Production/quality gates after fixture serial correction')
    if subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', 'src'], cwd=original.ROOT):
        raise ValueError('canonical Main/Test fixed')
    scope = {**vars(original), 'runner_source': runner_source, 'SOURCE': SOURCE}
    exec(compile(run, '<same Main925 fixture corrected>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
