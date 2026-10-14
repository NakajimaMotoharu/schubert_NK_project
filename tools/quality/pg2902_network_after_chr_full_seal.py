"""Necessary refreshed post-CHR seal: authorized anonymous HTTP changes, no Root replay."""
import inspect
import json
import pg2886_network_newcurrent_full_seal as prior
from pg1446_current_cold_stage import W

SLOT='pg2902-network-after-chr-full-seal-v1'


def payload(binding):
    return prior.payload(binding).replace(prior.SLOT,SLOT)


def main():
    browser=json.loads((W/'pg2900-chr-a01-native-v1.safe.json').read_bytes())
    if browser.get('actualExit')!=0 or browser.get('productionSource')!=prior.SOURCE or browser.get('noRootReplay')is not True:
        raise ValueError('actual authorized browser HTTP change required; no gratuitous reseal')
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<fresh required post-Browser current seal>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
