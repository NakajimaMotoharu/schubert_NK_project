"""Current fresh-run before-only SS selectors; no DB result generated as expected."""
import inspect
from pyflakes.api import check
import pg1768_next_day_inbox_oracle as prior
from pg1446_current_cold_stage import W
from pg2208_current_newboot_cold_sources import BOOT

SLOT='pg2238-newboot-before-selectors-v1'


def payload(binding,before_sha):
    raw=prior.payload()
    raw=raw.replace('pg1768-next-day-inbox-oracle-v1',SLOT).replace('pg1759-next-day-ordinary-once-v1','pg2227-newboot-fresh-day-once-v1')
    start=raw.index('\nCUT=');end=raw.index('\n',start+1)
    raw=raw[:start]+'\nCUT='+repr(binding['cutoff'])+raw[end:]
    marker="raw=p.read_bytes();before=json.loads(raw);expected=candidates(before['rows'],CUT)"
    if raw.count(marker)!=1:raise ValueError('one sealed before-only selector input required')
    raw=raw.replace(marker,"raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()=="+repr(before_sha)+");frozen=json.loads(raw);before=frozen['current'];require(frozen['newJstDate']==instant(CUT).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat());expected=candidates(before['rows'],CUT)")
    raw="import pathlib\nif pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()!="+repr(BOOT)+":raise ValueError('current boot required')\n"+raw
    if check(raw,'<actual current before-only independent selector>'):raise ValueError('whole selector exports required')
    compile(raw,'<current fresh before selector>','exec');return raw


def main():
    import json
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    before=json.loads((W/'pg2226-newboot-fresh-day-before-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or before['actualExit']!=0:raise ValueError('actual current admission and binding required')
    raw=inspect.getsource(prior.prior.prior.main).replace('pg1766-next-day-independent-candidates-v1',SLOT)
    ns={**prior.prior.prior.__dict__,'payload':lambda:payload(live['binding'],before['guest']['privateBeforeSha256'])}
    exec(compile(raw,'<newboot before-only selector transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
