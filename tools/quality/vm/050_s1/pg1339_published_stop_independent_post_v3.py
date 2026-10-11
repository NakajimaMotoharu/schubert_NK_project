"""Current post host helper-name expression qualified too; never re-stop."""
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1337_published_stop_independent_post_v2 import payload
from pg1334_published_owned_stop_sources_v2 import SOURCE

def source():
    code=inspect.getsource(transport.main)
    for old,new in [('pg1256-stop-v1.exit','pg1336-stop-v1.exit'),('pg1254-frozen-v1.safe.json','pg1335-frozen-v1.safe.json'),("replace('1216','1253')","replace('1216','1334')"),('pg1253','pg1334'),('pg1257-fresh-terminal-post-v1','pg1339-published-terminal-post-v3')]:
        if old not in code:raise ValueError('complete current host helper source binding required')
        code=code.replace(old,new)
    compile(code,'<actual current full host post>','exec');return code

def main():
    env=dict(transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<current full host post helper namespace>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
