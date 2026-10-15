"""Independent v5 post with actual native public-query/private-noaction trace."""
import pg3232_legacy_negative_post as current
import pg3226_legacy_negative_post as transport
from pg1446_current_cold_stage import W


def build():
    raw = current.build().replace('pg3230-legacy-negative-v1', 'pg3236-legacy-negative-v1').replace('cohort-v4', 'cohort-v5').replace('cohort-native-v4.exec', 'cohort-native-v5.exec').replace('PG3230-LFACT-v4', 'PG3236-LFACT-v5')
    old = "v['actualSystemctlShowExecs']>0"
    if raw.count(old) != 1: raise ValueError('one prior process-path claim required')
    return raw.replace(old, "v['actualPublicNativeReadConnects']>0 and v['privateManagerConnects']==0")


if __name__ == '__main__':
    transport.OUT = W / 'pg3238-legacy-negative-post-v1'
    transport.EXECUTION_SLOT = 'pg3236-legacy-negative-v1'
    transport.CODE = build()
    transport.main()
