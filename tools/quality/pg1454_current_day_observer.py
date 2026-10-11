"""Current boot/source immutable readonly observer; separate stage/watch, start0."""
import sys
from pathlib import Path
R=Path(__file__).resolve().parent/'vm/050_s1'
sys.path.insert(0,str(R))
from pg1318_published_source_observer import source as previous


def source():
    raw=previous()
    for old,new in [('pg1318','pg1454'),('PG1318','PG1454'),
                    ('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),
                    ('pg1315-ordinary-publication-independent-v1.safe.json','pg1453-current-cold-independent-post-v1/manifest.safe.json')]:
        if old not in raw:raise ValueError('fixed observer binding absent')
        raw=raw.replace(old,new)
    compile(raw,'<current-day observer>','exec');return raw


def namespace():
    env={'__file__':str(R/'pg1454_current_day_observer.py'),'__name__':'current_day_observer'}
    exec(compile(source(),'<current readonly observer>','exec'),env);return env


if __name__=='__main__':namespace()['main']()
