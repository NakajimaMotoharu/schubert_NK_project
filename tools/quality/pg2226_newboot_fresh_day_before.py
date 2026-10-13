"""Independent lawful fresh-JST-day preflight, not a retry of old run or permission.

PT-OPS-2226-001. Apply only on a genuine day with no successful Inspector step.
"""
import inspect
from pyflakes.api import check
import pg1455_current_day_before as prior
from pg2218_current_newboot_cold_post import payload as full_post
from pg2208_current_newboot_cold_sources import bindings

SLOT='pg2226-newboot-fresh-day-before-v1'


def payload():
    raw='import datetime\n'+full_post().replace('PG2218-current-newboot-cold-independent-post-v1','PG2226-newboot-fresh-day-before-v1').replace('pg2218-current-newboot-cold-independent-post-v1',SLOT)
    marker='print(json.dumps(result,sort_keys=True))'
    publication="with(SAVE/'result.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())"
    if raw.count(marker)!=1 or raw.count(publication)!=1:raise ValueError('one current independent result boundary required')
    raw=raw.replace(publication,'').replace(marker,inspect.getsource(prior.ordinary_argv)+'\n'+bindings(prior.EXTRA))
    if check(raw,'<newboot true fresh-day whole before>'):raise ValueError('whole actual exports required')
    compile(raw,'<newboot fresh-day before>','exec');return raw


def day_guard():
    # Independent admission data; no clock change, test expectation update or start.
    return "import datetime,json\nprint(json.dumps({'jstDate':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()}))\n"


def main():
    import json
    import subprocess
    from pg1446_current_cold_stage import SSH
    r=subprocess.run(SSH+['python3','-B','-'],input=day_guard().encode(),capture_output=True,timeout=10)
    if r.returncode or json.loads(r.stdout)['jstDate']<'2026-10-14':
        raise ValueError('genuine fresh day required; no operation issued, independent work continues')
    raw=inspect.getsource(prior.main).replace('pg1455-current-day-before-v1',SLOT)
    ns={**prior.__dict__,'payload':payload}
    exec(compile(raw,'<true day before transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
