"""Current new genuine Root only; immutable stage/owned reverse TERM, never start."""
import ast,sys
from pathlib import Path
from pg877_native_stop import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    for a,b in (('pg877_stop_binding','pg963_current_stop_binding'),('Pg877','Pg963'),('pg877','pg963'),('PG862','PG932'),('pg875','pg960'),('pg876','pg961')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    assert sys.argv[1:] in (['stage'],['stop'])
    exec(compile(source(),'<966 actual new-source owned stop>','exec'),{'__file__':str(R/'pg966_current_owned_stop.py'),'__name__':'__main__'})
