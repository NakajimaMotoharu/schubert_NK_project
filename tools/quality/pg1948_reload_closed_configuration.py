"""Exact post-reload auxiliary reset only; never changes historical Unit state."""
RESET_UNITS=frozenset(('artemis.service','caddy.service','schubert-nk-api.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-morning-controller.service','schubert-nk-web.service'))
CLOSED=('n/a','n/a','0','(null)','0/0')


def reload_configuration_same(unit,expected,actual,parse):
    if type(expected)is not dict or type(actual)is not dict or set(expected)!=set(actual)or len(expected)!=32:return False
    if any(type(v)is not str for v in (*expected.values(),*actual.values())):return False
    for key in expected:
        if expected[key]==actual[key]:continue
        if key!='ExecStart'or unit not in RESET_UNITS:return False
        before=parse(expected[key]);after=parse(actual[key])
        if before is None or after is None or tuple(before[:3])!=tuple(after[:3])or tuple(after[3:])!=CLOSED:return False
    return True
