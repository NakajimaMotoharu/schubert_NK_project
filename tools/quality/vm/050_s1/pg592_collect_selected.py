"""Corrected PG592 source, 36 actually selected cases and sealed byte-aligned diagnostics."""
import pathlib
import runpy


def policy():
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg590_collect_selected.py')))['policy']()
    replacements = {
        'pg590-cleanup-expiry-db-v1': 'pg592-session-transition-faults-v2',
        'PG590-cleanup-expiry-db-v1': 'PG592-session-transition-faults-v2',
        'e6c1c2cad01d2e92c400dac275ea62c294897d38': '00a0f2247fbe243d8c9ab336bd8be2c5736f6330',
        "('MorningDatabaseSessionTest',26)": "('MorningDatabaseSessionTest',27)",
        "'selectedTests':35,'newTests':1": "'selectedTests':36,'newTests':1",
        "'selectedPT':35,'newTests':1": "'selectedPT':36,'newTests':1",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<sealed PG592 collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
