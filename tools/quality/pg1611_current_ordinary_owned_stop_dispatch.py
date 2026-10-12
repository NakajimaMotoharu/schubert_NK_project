"""New-only same-generation stage and durable once normal owned stop."""
import sys
import pg1581_current_owned_stop_dispatch as prior
from pg1609_current_ordinary_owned_stop_sources import sources,SOURCE,BEFORE,TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
def rebind(raw):
    return raw.replace('1581','1611').replace('1579','1609').replace('1580','1610').replace('1582-current-stop-preflight-v1','1612-current-ordinary-stop-preflight-v1').replace('pg1609-current-owned-stop-tools-v1',TOOLS)

STAGE=rebind(prior.STAGE)
def source():return rebind(prior.source())

def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('only exact stage/stop allowed')
    env={**prior.prior.previous.previous.__dict__,'GUEST':GUEST,'STAGE':STAGE,'sources':sources,'SOURCE':SOURCE,'BEFORE':BEFORE}
    exec(compile(source(),'<current ordinary once stage-stop>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
