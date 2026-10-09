"""New-only ADMIN compile after actual PG701 current21 readonly acceptance."""
from pathlib import Path
from pg702_sources import current

R = Path(__file__).resolve().parent
if __name__ == '__main__':
    raw = current((R / 'pg662_compile.py').read_text().replace('pg662', 'pg664').replace('Pg662', 'Pg664'))
    exec(compile(raw, str(R / 'pg702_compile.py'), 'exec'),
         {'__name__': '__main__', '__file__': str(R / 'pg702_compile.py')})
