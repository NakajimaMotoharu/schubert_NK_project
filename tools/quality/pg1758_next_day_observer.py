"""New immutable readonly observer for next-day Root; no start/stop authority."""
from pg1698_new_current_ordinary_observer import source as previous,R

def source():
    raw=previous().replace('pg1698','pg1758').replace('PG1698','PG1758')
    raw=raw.replace('pg1697-new-current-ordinary-before-v1/manifest.safe.json','pg1757-next-business-day-before-v1/manifest.safe.json')
    compile(raw,'<current next-day readonly observer>','exec');return raw

def namespace():
    ns={'__file__':str(R/'pg1758_next_day_observer.py'),'__name__':'next_day_readonly_observer'}
    exec(compile(source(),'<immutable next-day observer>','exec'),ns);return ns

if __name__=='__main__':namespace()['main']()
