"""New normal owned-stop post with fresh private seals; readonly, no old run."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg643_terminal_final.py').read_text()
    for old,new in (('pg642','pg655'),('Pg642','Pg655'),('pg640','pg653'),('pg643-terminal-final-v2','pg656-terminal-final-v1'),('PG643-terminal-final-v2','PG656-terminal-final-v1')):
        assert old in raw;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg656_terminal_final.py'),'exec'),{'__file__':str(R/'pg656_terminal_final.py'),'__name__':'__main__'})
