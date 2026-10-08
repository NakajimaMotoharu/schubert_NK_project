"""Closed new-only v4/v5 XML seal; historical unknown v1 cause remains explicit."""
import pathlib
import re
import runpy
import sys


def policy(source_commit, version):
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    assert version in ('v4', 'v5')
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg594_collect_selected.py')))['policy']()
    replacements = {
        'pg594-real-db-drift-v2': 'pg594-real-db-drift-' + version,
        'PG594-real-db-drift-v2': 'PG594-real-db-drift-' + version,
        '10cb76870df5d7b48cd3a6b11beabb78d6b73012': source_commit,
        "('MorningDatabaseSessionTest',28)": "('MorningDatabaseSessionTest',29)",
        "'selectedTests':37,'newTests':1": "'selectedTests':38,'newTests':2",
        "'selectedPT':37,'newTests':1": "'selectedPT':38,'newTests':2",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 3
    exec(compile(policy(sys.argv[1], sys.argv[2]), '<PG594 acknowledged fixture seal>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
