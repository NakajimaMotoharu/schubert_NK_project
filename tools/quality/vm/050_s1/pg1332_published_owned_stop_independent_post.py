"""Current769 normal-stop independent full post; no old cohort seal substitution."""
import inspect
import pg1257_fresh_independent_terminal_post as previous
from pg1328_published_owned_stop_sources import SOURCE,CHANGES


def payload(seals):
    code=previous.payload(seals)
    for old,new in CHANGES:code=code.replace(old,new)
    code=code.replace('pg1257-fresh-terminal-post-v1','pg1332-published-terminal-post-v1').replace('PG1257-fresh-terminal-post-v1','PG1332-published-terminal-post-v1')
    compile(code,'<full current normal ownedstop post>','exec');return code


def main():
    code=inspect.getsource(previous.main)
    for old,new in [('pg1256-stop-v1.exit','pg1331-stop-v1.exit'),('pg1254-frozen-v1.safe.json','pg1329-frozen-v1.safe.json'),('pg1253','pg1328'),('pg1257-fresh-terminal-post-v1','pg1332-published-terminal-post-v1')]:
        if old not in code:raise ValueError('complete current post source binding required')
        code=code.replace(old,new)
    env=dict(previous.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(code,'<new-only current fullpost transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
