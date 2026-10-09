"""Fresh selection after821 initial test compile failure; old failure preserved."""
from pathlib import Path
from pg818_manager_selected import source, TESTS
R = Path(__file__).resolve().parent
if __name__ == '__main__':
    for name in TESTS['batch']:
        assert len(list((R.parents[3] / 'src/schubert-nk-batch/src/test').rglob(name + '.java'))) == 1
    raw = source().replace('pg818-manager-selected-v1', 'pg822-manager-selected-v1')
    exec(compile(raw, '<822 source fixed test contracts>', 'exec'),
         {'__file__': str(R / 'pg822_manager_selected.py'), '__name__': '__main__'})
