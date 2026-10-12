"""New-only current-generation stage/once stop, exact ABI and fullseal join."""
import sys
import pg1336_published_owned_stop_dispatch_v2 as prior
from pg1579_current_owned_stop_sources import sources,SOURCE,BEFORE,TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=prior.STAGE
for old,new in [('pg1336','pg1581'),('PG1336','PG1581'),('pg1334-native-tools-v1',TOOLS),
                ('0.1.0-PG1292','0.1.0-PG1544'),('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d')]:
    if old not in STAGE:raise ValueError('current immutable stage boundary absent')
    STAGE=STAGE.replace(old,new)
compile(STAGE,'<current immutable owned stop stage>','exec')

def source():
    raw=prior.source()
    for old,new in [('pg1336','pg1581'),('Pg1334','Pg1579'),('pg1334-native-tools-v1',TOOLS),
                    ('pg1335','pg1580'),
                    ('pg1338-published-stop-preflight-v2.safe.json','pg1582-current-stop-preflight-v1.safe.json'),
                    ('0.1.0-PG1292','0.1.0-PG1544')]:
        if old not in raw:raise ValueError('current once dispatcher boundary absent')
        raw=raw.replace(old,new)
    compile(raw,'<current reserved owned stop>','exec');return raw

def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('only exact stage/stop allowed')
    env={**prior.previous.previous.__dict__,'GUEST':GUEST,'STAGE':STAGE,
         'sources':sources,'SOURCE':SOURCE,'BEFORE':BEFORE}
    exec(compile(source(),'<actual current once stage-stop>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
