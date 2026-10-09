"""Independent current ownedstop full post; no second STOP or historic qualifications."""
from pathlib import Path
from pg697_terminal_final import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg696','pg728'),('Pg696','Pg728'),('pg693','pg725'),
        ('pg697-terminal-final-v1','pg729-terminal-final-v1'),('PG697-terminal-final-v1','PG729-terminal-final-v1'),
        ('pg682-manifest.sig','pg715-manifest.sig'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<current independent wholepost>','exec'),
         {'__file__':str(R/'pg729_terminal_final.py'),'__name__':'__main__'})
