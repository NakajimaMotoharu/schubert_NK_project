"""Immutable read-only current observer for distinct noargs newrun admission."""
from pg2010_fresh_completed_resume_observer import source as previous,R,SOURCE as SOURCE,BOM as BOM
__all__=['SOURCE','BOM','source','namespace']


def source():
    raw=previous().replace('pg2010','pg2070').replace('PG2010','PG2070')
    old='pg2006-existing-runtime-independent-post-v1/manifest.safe.json'
    if raw.count(old)!=1:raise ValueError('one current retired/Backup post prerequisite required')
    raw=raw.replace(old,'pg2068-retained-backup-replay-history-post-v1/manifest.safe.json')
    compile(raw,'<current newrun immutable observer>','exec');return raw


def namespace():
    ns={'__file__':str(R/'pg2070_current_newrun_observer.py'),'__name__':'current_newrun_observer'}
    exec(compile(source(),'<current newrun observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
