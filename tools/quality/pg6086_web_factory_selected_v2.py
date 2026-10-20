"""BUG1538 fixture-only serial contract correction; new-only genuine Web925 retry."""
import inspect
import subprocess
import pg6080_web_factory_selected as original


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
    scope = dict(vars(original))
    exec(compile(run, '<same Main925 fixture corrected>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
