"""Exact PG590 new-only source/35 XML profile; no fresh full-source claim."""
import pathlib
import runpy


def policy():
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg589_collect_selected.py')))['policy']()
    replacements = {
        'pg589-session-sql-close-v1': 'pg590-cleanup-expiry-db-v1',
        'PG589-session-sql-close-v1': 'PG590-cleanup-expiry-db-v1',
        '0e0739a04ac5c9be641d54fc0849c34b6f4cf439': 'e6c1c2cad01d2e92c400dac275ea62c294897d38',
        "('MorningDatabaseSessionTest',25)": "('MorningDatabaseSessionTest',26)",
        "'selectedTests':34,'newTests':2": "'selectedTests':35,'newTests':1",
        "'selectedPT':34,'newTests':2": "'selectedPT':35,'newTests':1",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<sealed PG590 collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
