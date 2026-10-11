"""New-only actual post with public run identity equal to its execution slot."""
import pg1339_published_stop_independent_post_v3 as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    code=previous.payload(seals)
    if code.count('PG1332-published-terminal-post-v1')!=1:raise ValueError('one old public run literal required')
    code=code.replace('PG1332-published-terminal-post-v1','PG1340-published-terminal-post-v4')
    code=code.replace('pg1337-published-terminal-post-v2','pg1340-published-terminal-post-v4')
    compile(code,'<correct current public run>','exec');return code

def source():
    code=previous.source().replace('pg1339-published-terminal-post-v3','pg1340-published-terminal-post-v4')
    compile(code,'<correct current host file slot>','exec');return code

def main():
    env=dict(previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<actual current matched run/file post>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
