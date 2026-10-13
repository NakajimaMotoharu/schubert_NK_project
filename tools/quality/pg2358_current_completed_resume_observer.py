"""New read-only observer after the actual normal verification plus independent post."""
from pg2224_newboot_current_observer import source as previous,R


def source():
    raw=previous().replace('pg2224','pg2358').replace('PG2224','PG2358')
    old='pg2218-current-newboot-cold-independent-post-v1/manifest.safe.json'
    if raw.count(old)!=1:raise ValueError('one actual wholepost admission required')
    return raw.replace(old,'pg2356-current-runtime-verification-post-v1/manifest.safe.json')


def namespace():
    ns={'__file__':str(R/'pg2358_current_completed_resume_observer.py'),'__name__':'current_completed_resume_observer'}
    exec(compile(source(),'<actual current completed observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
