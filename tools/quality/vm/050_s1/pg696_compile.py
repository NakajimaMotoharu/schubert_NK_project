"""Current source ABI stop tools, only after actual genuine PG693, no VM action."""
from pathlib import Path
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg642_compile.py').read_text(),(
        ('pg640','pg693'),('PG640','PG693'),('pg642','pg696'),('Pg642','Pg696'),
        ('pg630-retention-factory-six-host-v1','pg680-owner-six-host-v1'),('pg631-release-v1','pg682-release-v1'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new current stop compile>','exec'),
         {'__file__':str(R/'pg696_compile.py'),'__name__':'__main__'})
