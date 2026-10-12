"""Fresh same-current observer, no runtime/start/stop authority."""
from pg1454_current_day_observer import source as previous,R

def source():
    s=previous()
    for a,b in [('pg1454','pg1572'),('PG1454','PG1572'),('pg1453-current-cold-independent-post-v1/manifest.safe.json','pg1571-existing-runtime-independent-closing-v1/manifest.safe.json'),('769ddb15cd735c25fef581b5f9850ef9d0053c0f','4d6bcbddb417b76d27e52d5d9640752c300edccf'),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99','e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'),('PG1292','PG1544')]:
        if a not in s:raise ValueError('fixed current observer binding refused')
        s=s.replace(a,b)
    compile(s,'<fresh current resume observer>','exec');return s

def namespace():
    env={'__file__':str(R/'pg1572_current_resume_observer.py'),'__name__':'current_resume_observer'}
    exec(compile(source(),'<current observer>','exec'),env);return env

if __name__=='__main__':namespace()['main']()
