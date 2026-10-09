"""Independent new-source full24/full32/retained/resource post, read-only."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg878_terminal_final.py').read_text()
    for a,b in (('pg877_stop_binding','pg963_current_stop_binding'),('Pg877','Pg963'),('pg877','pg963'),('PG878','PG968'),('pg878','pg968'),('pg875','pg960'),('pg862','pg932')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<968 new current full retained post>','exec'),{'__file__':str(R/'pg968_current_terminal_final.py'),'__name__':'__main__'})
