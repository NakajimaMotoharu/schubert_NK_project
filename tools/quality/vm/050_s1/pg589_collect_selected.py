"""Exact PG589 run profile on independent PG586 selected-run policy."""
import pathlib
import runpy


def policy():
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg588_collect_selected.py')))['policy']()
    replacements = {
        'pg588-session-readback-v2': 'pg589-session-sql-close-v1',
        'PG588-session-readback-v2': 'PG589-session-sql-close-v1',
        '6ccb6704bb3fb1c3118880a0968352bacad9ca73': '0e0739a04ac5c9be641d54fc0849c34b6f4cf439',
        "('MorningDatabaseSessionTest',23)": "('MorningDatabaseSessionTest',25)",
        "'selectedTests':32,'newTests':3": "'selectedTests':34,'newTests':2",
        "'selectedPT':32,'newTests':3": "'selectedPT':34,'newTests':2",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<sealed PG589 collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
