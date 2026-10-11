"""New-only full post bound to corrected1334 stop bundle/1336 normal stop."""
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1332_published_owned_stop_independent_post import payload as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    code=previous(seals).replace('pg1328','pg1334').replace('pg1332-published-terminal-post-v1','pg1337-published-terminal-post-v2')
    code=code.replace('normalPG877NewScopesSealed','normalCurrentOwnedStopScopesSealed')
    compile(code,'<actual corrected normal-stop fullpost>','exec');return code

def main():
    code=inspect.getsource(transport.main)
    for old,new in [('pg1256-stop-v1.exit','pg1336-stop-v1.exit'),('pg1254-frozen-v1.safe.json','pg1335-frozen-v1.safe.json'),('pg1253','pg1334'),('pg1257-fresh-terminal-post-v1','pg1337-published-terminal-post-v2')]:
        if old not in code:raise ValueError('one corrected fullpost binding required')
        code=code.replace(old,new)
    env=dict(transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(code,'<new-only corrected stop fullpost>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
