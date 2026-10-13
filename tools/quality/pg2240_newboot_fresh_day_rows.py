"""Independent all24 fresh-day DB postconditions; no business/DB write."""
import inspect
import json
from pyflakes.api import check
import pg1769_next_day_rows_oracle as model
import pg2023_fresh_resume_rows_oracle as transport
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE
from pg2208_current_newboot_cold_sources import BOOT

SLOT='pg2240-newboot-fresh-day-rows-v1'


def oracle_source():
    raw=model.oracle_source()
    old="r['business_date']=='2026-10-13'"
    if raw.count(old)!=1:raise ValueError('one business-date data boundary required')
    return raw.replace(old,"r['business_date']==start.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()")


def payload(binding,before_sha,oracle_sha):
    raw=model.payload();i=raw.index('\nRUN=')
    raw=oracle_source()+raw[i:]
    raw=raw.replace("RUN="+repr(model.EXPECTED['run']),"RUN="+repr(binding['run'])).replace("CUT="+repr(model.EXPECTED['cutoff']),"CUT="+repr(binding['cutoff']))
    for old,new in [('pg1759-next-day-ordinary-once-v1','pg2227-newboot-fresh-day-once-v1'),('pg1768-next-day-inbox-oracle-v1','pg2238-newboot-before-selectors-v1'),('pg1769-next-day-rows-oracle-v1',SLOT),('a919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e',before_sha),('a1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030',oracle_sha)]:
        if old not in raw:raise ValueError('exact fresh-day input boundary required '+old)
        raw=raw.replace(old,new)
    raw=raw.replace('before=json.loads(br)','before=json.loads(br)[\'current\']')
    raw=raw.replace("require(os.geteuid()==0)","require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=="+repr(BOOT)+")")
    if check(raw,'<actual all24 current fresh-day independent oracle>'):raise ValueError('whole rows exports required')
    compile(raw,'<actual current fresh rows>','exec');return raw


def main():
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    before=json.loads((W/'pg2226-newboot-fresh-day-before-v1/manifest.safe.json').read_bytes())
    oracle=json.loads((W/'pg2238-newboot-before-selectors-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 for v in [live,before,oracle]):raise ValueError('all actual current oracle inputs required')
    raw=inspect.getsource(transport.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2234-newboot-fresh-day-terminal-v1')
    ns={**transport.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':lambda:payload(live['binding'],before['guest']['privateBeforeSha256'],oracle['guest']['privateOracleSha256'])}
    exec(compile(raw,'<current fresh all24 readonly transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
