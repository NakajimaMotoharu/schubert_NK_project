"""Corrected whole stage/current/ABI join; stage0 is mandatory before stop."""
import sys
import pg1331_published_owned_stop_dispatch as previous
from pg1334_published_owned_stop_sources_v2 import sources,SOURCE,BEFORE

GUEST='/var/lib/pgpt-s1-preservation/pg1334-native-tools-v1'
STAGE=previous.STAGE.replace('pg1331','pg1336').replace('PG1331','PG1336').replace('pg1328','pg1334').replace('0.1.0-PG1068','0.1.0-PG1292')
compile(STAGE,'<actual current stage corrected release join>', 'exec')

def source():
    code=previous.source().replace('pg1331','pg1336').replace('Pg1328','Pg1334').replace('pg1328','pg1334').replace('pg1329','pg1335')
    code=code.replace('pg1330-published-stop-preflight-v1.safe.json','pg1338-published-stop-preflight-v2.safe.json')
    compile(code,'<whole corrected current stop dispatcher>','exec');return code

def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('closed stage/stop only')
    env=dict(previous.previous.__dict__,GUEST=GUEST,STAGE=STAGE,sources=sources,SOURCE=SOURCE,BEFORE=BEFORE)
    exec(compile(source(),'<whole corrected current stage/stop>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
