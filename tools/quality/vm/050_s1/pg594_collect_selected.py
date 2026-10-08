"""Seal actual XML only; unexplained previous failure remains a quality hold, not flaky PASS."""
import pathlib
import runpy


def policy():
    source = runpy.run_path(str(pathlib.Path(__file__).with_name('pg592_collect_selected.py')))['policy']()
    replacements = {
        'pg592-session-transition-faults-v2': 'pg594-real-db-drift-v2',
        'PG592-session-transition-faults-v2': 'PG594-real-db-drift-v2',
        '00a0f2247fbe243d8c9ab336bd8be2c5736f6330': '10cb76870df5d7b48cd3a6b11beabb78d6b73012',
        "('MorningDatabaseSessionTest',27)": "('MorningDatabaseSessionTest',28)",
        "'selectedTests':36,'newTests':1": "'selectedTests':37,'newTests':1",
        "'selectedPT':36,'newTests':1": "'selectedPT':37,'newTests':1",
        "'FESFlaky':0": "'xmlFESFlakyIndicators':0,'FESFlaky':None,'qualityAcceptanceHeld':True,'unexplainedEarlierFailure':'BUG-878'",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<PG594 XML-seal quality held>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
