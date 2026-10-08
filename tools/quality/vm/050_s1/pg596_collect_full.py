"""Grouped fixture/retained-anchor source regression; exact source and six fresh XML groups."""
import pathlib
import re
import runpy
import sys


def policy(source_commit):
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg593_collect_full.py')))['policy']()
    replacements = {
        'pg593-grouped-six-host-v1': 'pg596-fixture-retained-six-host-v1',
        'PG593-grouped-six-host-v1': 'PG596-fixture-retained-six-host-v1',
        'afc470b47a422fb8029c23a96f647889d47a2e9e': source_commit,
        "assert int(session.attrib['tests']) == 27": "assert int(session.attrib['tests']) == 30",
        "'totalSessionCases':27,'additionalCasesVsPG585':12": "'totalSessionCases':30,'additionalCasesVsPG585':15,'historicalV1QualityHold':'BUG-878'",
        "result['tests']==3447": "result['tests']==3450",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2
    exec(compile(policy(sys.argv[1]), '<PG596 fresh full collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
