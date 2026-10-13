"""Read-only observer of the newly published current, no business authority."""
from pg2176_newsource_normal_observer import source as previous,R
from pg2440_question_normal_publication_sources import production,BOM,BOOT

SOURCE=production()


def source():
    raw=previous()
    for a,b in [('pg2176','pg2446'),('PG2176','PG2446'),
                ('pg2174-normal-publication-full-post-v1','pg2444-question-normal-publication-post-v1'),
                ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE),
                ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM),
                ('PG2126','PG2428'),('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)]:raw=raw.replace(a,b)
    compile(raw,'<new current whole immutable observer>','exec');return raw


def namespace():
    ns={'__file__':str(R/'pg2446_question_current_observer.py'),'__name__':'question_current_observer'}
    exec(compile(source(),'<new current observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
