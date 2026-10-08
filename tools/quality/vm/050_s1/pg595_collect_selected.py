"""Closed corrected retained-anchor matrix; independent prior-failure hold remains."""
import pathlib
import runpy
import sys


def policy(source_commit):
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg594_collect_ack_selected.py')))['policy'](source_commit, 'v5')
    replacements = {
        'pg594-real-db-drift-v5': 'pg595-retained-expiry-anchor-v3',
        'PG594-real-db-drift-v5': 'PG595-retained-expiry-anchor-v3',
        "('MorningDatabaseSessionTest',29)": "('MorningDatabaseSessionTest',30)",
        "'selectedTests':38,'newTests':2": "'selectedTests':39,'newTests':1",
        "'selectedPT':38,'newTests':2": "'selectedPT':39,'newTests':1",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2
    exec(compile(policy(sys.argv[1]), '<PG595 sealed original-anchor matrix>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
