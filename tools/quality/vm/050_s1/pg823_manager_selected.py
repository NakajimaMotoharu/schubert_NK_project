"""New-only source-fixed manager selection; numeric run and original failures remain distinct."""
import argparse
from pathlib import Path
from pg818_manager_selected import source, TESTS
R = Path(__file__).resolve().parent
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, type=int)
    number = parser.parse_args().run
    assert number >= 823
    for name in TESTS['batch']:
        assert len(list((R.parents[3] / 'src/schubert-nk-batch/src/test').rglob(name + '.java'))) == 1
    raw = source().replace('pg818', 'pg' + str(number)).replace('PG743', 'PG' + str(number))
    exec(compile(raw, '<source-fixed new-only manager selection>', 'exec'),
         {'__file__': str(R / 'pg823_manager_selected.py'), '__name__': '__main__'})
