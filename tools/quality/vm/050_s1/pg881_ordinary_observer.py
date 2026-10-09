"""Second-run new-only observer, no operation authority."""
from pathlib import Path
from pg871_ordinary_observer import source as previous
R=Path(__file__).resolve().parent
def source():return previous().replace('pg871','pg881').replace('PG871','PG881').replace('pg870-ordinary-before-v1','pg880-ordinary-before-v1')
if __name__=='__main__':exec(compile(source(),'<881 new second e016 ordinary observer>','exec'),{'__file__':str(R/'pg881_ordinary_observer.py'),'__name__':'__main__'})
