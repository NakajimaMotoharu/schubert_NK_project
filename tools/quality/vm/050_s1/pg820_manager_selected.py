"""Fresh same-source selection after819 static refusal; no VM action or formal acceptance."""
from pathlib import Path
from pg818_manager_selected import source, TESTS
R = Path(__file__).resolve().parent
if __name__ == '__main__':
    for name in TESTS['batch']:
        assert len(list((R.parents[3] / 'src/schubert-nk-batch/src/test').rglob(name + '.java'))) == 1
    raw = source().replace('pg818-manager-selected-v1', 'pg820-manager-selected-v1')
    exec(compile(raw, '<820 independent owner and whole budget>', 'exec'),
         {'__file__': str(R / 'pg820_manager_selected.py'), '__name__': '__main__'})
