"""New current read-only observer for ordinary noargs generation, start0."""
from pg1572_current_resume_observer import source as previous,R

def source():
    raw=previous().replace('pg1572','pg1597').replace('PG1572','PG1597')
    raw=raw.replace('pg1571-existing-runtime-independent-closing-v1/manifest.safe.json','pg1596-current-ordinary-before-v1/manifest.safe.json')
    compile(raw,'<current noargs readonly observer>','exec');return raw

def namespace():
    ns={'__file__':str(R/'pg1597_current_ordinary_observer.py'),'__name__':'current_ordinary_observer'}
    exec(compile(source(),'<current noargs readonly watch>','exec'),ns);return ns

if __name__=='__main__':namespace()['main']()
