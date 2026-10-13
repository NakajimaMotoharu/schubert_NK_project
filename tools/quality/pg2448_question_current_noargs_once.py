"""One new source ordinary noargs run; preserve old native but do not accept it."""
import inspect
import pg2178_newsource_noargs_once as prior
from pg2446_question_current_observer import namespace,SOURCE,BOM
from pg2444_question_normal_publication_post import payload as full_post

SLOT='pg2448-question-current-noargs-once-v1'


def body():
    raw=prior.body()
    for a,b in [('pg2176','pg2446'),('pg2178-newsource-noargs-once-v1',SLOT),
                ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE),
                ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM),
                ('PG2126','PG2428'),('require(len(records)==38)','require(len(records)==16)')]:raw=raw.replace(a,b)
    return raw


def payload(hashes):
    raw=inspect.getsource(prior.payload).replace('pg2174-normal-publication-full-post-v1','pg2444-question-normal-publication-post-v1')
    ns={**prior.__dict__,'full_post':full_post,'body':body}
    exec(compile(raw,'<new current full admission projection>','exec'),ns)
    return ns['payload'](hashes)


def main():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg2176','pg2446'),('pg2174-normal-publication-full-post-v1','pg2444-question-normal-publication-post-v1')]:raw=raw.replace(a,b)
    ns={**prior.__dict__,'namespace':namespace,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new current once admission entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
