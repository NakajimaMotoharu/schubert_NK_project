"""Separate current stop complete/24DB/32config/187/native/lock post; no mutation."""
import pg1340_published_stop_independent_post_v4 as prior
from pg1579_current_owned_stop_sources import CHANGES,SOURCE,TOOLS

def payload(seals):
    raw=prior.payload(seals)
    # Bind full qualified oracle, not old observations or old stop commands.
    for old,new in CHANGES:raw=raw.replace(old,new)
    raw=raw.replace('702983','108847').replace('PG1292','PG1544')
    raw=raw.replace('pg1579-native-tools-v1',TOOLS)
    raw=raw.replace('PG1340-published-terminal-post-v4','PG1583-current-terminal-post-v1')
    raw=raw.replace('pg1340-published-terminal-post-v4','pg1583-current-terminal-post-v1')
    if any(x in raw for x in ['702983','PG1292','cbca8738','pg1334','pg1340']):raise ValueError('old authority in current independent post')
    compile(raw,'<current all field independent terminal post>','exec');return raw

def source():
    raw=prior.source()
    for old,new in [('pg1336-stop-v1.exit','pg1581-stop-v1.exit'),('pg1335-frozen-v1.safe.json','pg1580-frozen-v1.safe.json'),
                    ("replace('1216','1334')","replace('1216','1579')"),('pg1334-native-tools-v1',TOOLS),
                    ('pg1334','pg1579'),('pg1340-published-terminal-post-v4','pg1583-current-terminal-post-v1')]:
        if old not in raw:raise ValueError('current separate post host boundary absent')
        raw=raw.replace(old,new)
    compile(raw,'<current independent terminal host>','exec');return raw

def main():
    env={**prior.previous.transport.__dict__,'SOURCE':SOURCE,'payload':payload}
    exec(compile(source(),'<actual separate current post>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
